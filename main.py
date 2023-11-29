from langchain.agents import AgentExecutor, LLMSingleActionAgent, AgentOutputParser
from langchain.tools import Tool, StructuredTool
from langchain.prompts import StringPromptTemplate

from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain

from typing import List, Union, Tuple
from langchain.schema import AgentAction, AgentFinish
import re
import langchain
import os
import json
import requests
from utils import *
from tools import take_environment_action_wrapper
from debate import view_debate_wrapper
from langchain.callbacks import FileCallbackHandler
import logging
from langchain.agents.agent_iterator import AgentExecutorIterator
from datetime import datetime
from pydantic import BaseModel, Field

timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
os.makedirs(f'./logs/{timestamp}', exist_ok=True)
info_filename = f'./logs/{timestamp}/info.log'
debug_filename = f'./logs/{timestamp}/debug.log'

logging.basicConfig(level=logging.NOTSET, handlers=[logging.NullHandler()])
info_logger = logging.getLogger('info_logger')

# Create an INFO file handler
file_handler_info = logging.FileHandler(info_filename)
file_handler_info.setLevel(logging.INFO)

# Create formatters and set them for the file handlers
formatter_info = logging.Formatter('%(message)s')
file_handler_info.setFormatter(formatter_info)

# Add the file handlers to the logger
info_logger.addHandler(file_handler_info)

# Example usage:
log_levels = {
    'none': logging.CRITICAL,
    'all': logging.INFO,
}

info_logger.info(timestamp)


class Context(BaseModel):
    generation_observation_history: List[str] = []
    log_count: int = 0
    action_count: int = 0
    debate_count: int = 0
    do_debate: bool = False
    system_hint_mod: int = 2
    max_votes: int = 1
    vote_count: int = 0
    votes: List[Tuple[str, str, str]] = []


class CustomPromptTemplate(StringPromptTemplate):
    # The template to use
    template: str
    # The list of tools available
    tools: List[Tool]
    # Context for information
    context: Context

    def format(self, **kwargs) -> str:
        # Get the intermediate steps (AgentAction, Observation tuples)
        # Format them in a particular way
        intermediate_steps = [(a, o) for a, o in kwargs.pop("intermediate_steps") if o != EMPTY_RESPONSE]

        # if recently finished voting, then vote count is 0
        done_voting = self.context.vote_count == 0

        history_lines = []
        last_action = None
        last_observation = None
        # create history to prompt agent
        for action, observation in intermediate_steps:
            history_lines.append(action.log.strip())
            history_lines.append(f"{OBSERVATION_PREFIX} {observation.strip()}")
            last_action = action
            last_observation = observation.strip()

        history = '\n'.join(history_lines)

        # append observation to list for debaters to use. Only append the environment observation, not debate observation
        # only do this if done voting, else we'll append it 'self.context.max_votes' many times
        if done_voting and last_action and last_action.tool == TAKE_ENVIRONMENT_ACTION:
            self.context.generation_observation_history.append(f'{OBSERVATION_PREFIX} {last_observation}')

        system_hint = None
        # append system hint for after taking action
        if (self.context.do_debate and
                last_action and
                last_action.tool == TAKE_ENVIRONMENT_ACTION and
                self.context.action_count % self.context.system_hint_mod == 0):
            system_hint = HINT_AFTER_ACTION
            history += '\n' + system_hint
        # append system hint for after viewing debate
        if (self.context.do_debate and
                last_action and
                last_action.tool == VIEW_DEBATE):
            system_hint = HINT_AFTER_DEBATE
            history += '\n' + system_hint

        # Set the agent_scratchpad variable to that value
        kwargs["agent_scratchpad"] = history
        # Create a tools variable from the list of tools provided
        tool_strings = []
        for tool in self.tools:
            s = f"{tool.name}: {tool.description}"
            params = [f'{param} - {info["description"]}' for param, info in tool.args.items()]
            s += ' Argument: ' + ' '.join(params)
            tool_strings.append(s)
        kwargs["tools"] = "\n".join(tool_strings)
        # Create a list of tool names for the tools provided
        kwargs["tool_names"] = " or ".join([tool.name for tool in self.tools])
        agent_prompt = self.template.format(**kwargs)

        # log some stuff
        if self.context.log_count == 0:
            info_logger.info(f"Step {self.context.log_count} ===")
            info_logger.info(agent_prompt)
            self.context.log_count += 1
        elif done_voting and self.context.log_count > 0 and last_action:
            info_logger.info(f"\nStep {self.context.log_count} ===")
            info_logger.info(f'Generation ---\n{last_action.log.strip()}')
            info_logger.info(f'Observation ---\n{last_observation}')
            if system_hint:
                info_logger.info(f'<only seen once by agent> {system_hint}')
            self.context.log_count += 1
        return agent_prompt


class CustomOutputParser(AgentOutputParser):
    # Context for information
    context: Context

    def parse(self, llm_output: str) -> Union[AgentFinish, AgentAction, list[AgentAction]]:

        default_agent_finish = AgentFinish(
            return_values={'output': "Task finished."},
            log=llm_output
        )

        # first, extract the answer and append it to the votes
        # this includes final answers, and even treats errors as an answer
        try:

            pattern = r'Tool: (.*)\nTool Input: (.*)'
            match = re.search(pattern, llm_output, re.DOTALL)

            # if the agent wants to do a final answer
            if "final answer" in llm_output.lower() or "final_answer" in llm_output.lower():
                self.context.vote_count += 1
                self.context.votes.append(('final answer', 'final answer', llm_output))
                # info_logger.info(f"\nStep {self.context.log_count} ===")
                # info_logger.info(f'Generation ---\n{llm_output}')
                # return AgentFinish(
                #     return_values={'output': "Task finished."},
                #     log=llm_output
                # )
            # else, look for a tool
            elif match:
                # extract the tool information
                tool_name: str = match.group(1)
                tool_input: str = match.group(2)

                # increment the votes
                self.context.vote_count += 1
                self.context.votes.append((tool_name, tool_input, llm_output))
            else:
                raise ValueError(f"Could not find 'Tool:' or 'Tool Input:' : `{llm_output}`")
        except Exception as e:
            self.context.vote_count += 1
            self.context.votes.append(('error', 'error', llm_output + f'\n ERROR === \n{e}'))
            # info_logger.info(f'\n ERROR === \n{e}')
            # return default_agent_finish

        # if not done voting, then don't take an action
        # the take_environment_action tool handles this
        if self.context.vote_count < self.context.max_votes:
            return AgentAction(tool=TAKE_ENVIRONMENT_ACTION, tool_input='empty param', log='empty tool')
        # if done voting, return majority vote and reset voting
        else:
            # log the votes
            info_logger.info("Casting votes... ===")
            for i, vote in enumerate(self.context.votes):
                info_logger.info(f"Vote {i} ---\n{vote}")

            # get the majority vote
            majority_tool_name, majority_tool_input, random_llm_output = get_majority_vote(self.context.votes)

            # reset the voting
            self.context.vote_count = 0
            self.context.votes = []

            # if the majority vote was a final answer or an error:
            if majority_tool_name == 'final answer' or majority_tool_name == 'error':
                return default_agent_finish
            # if the majority vote is a debate tool, then call that tool
            elif majority_tool_name == VIEW_DEBATE:
                self.context.debate_count += 1
                return AgentAction(tool=majority_tool_name, tool_input=majority_tool_input,
                                   log=random_llm_output)
            # if the majority vote is a environment action tool, then call that tool and log stuff
            elif majority_tool_name == TAKE_ENVIRONMENT_ACTION:
                # increment action count and log it
                self.context.action_count += 1
                info_logger.info(f"\nAction Count {self.context.action_count} +++")
                # add action to the history for debaters
                self.context.generation_observation_history.append('Action: ' + majority_tool_input)
                return AgentAction(tool=majority_tool_name, tool_input=majority_tool_input,
                                   log=random_llm_output)
            else:
                raise ValueError(f"An error occurred that should never occur: `{majority_tool_name}`")


# api_key = 'your key here'
# os.environ['OPENAI_API_KEY'] = api_key

langchain.debug = True
log_level = log_levels['all']
langchain_logging = False
do_debate = False
MAX_STEPS = 30
MAX_VOTES = 5
temperature = 0 if MAX_VOTES == 1 else 0.7
model = 'text-bison-32k'
model_type = 'text'

debate_params = {
    "total_iters": 2,
    "temperature": 0,
    "negative_first": False,
    "model": "text-bison-32k",
    "model_type": "text",  # alternative is "chat"
    "logger": info_logger
}

info_logger.setLevel(log_level)
if langchain_logging:
    handler = FileCallbackHandler(debug_filename)

results = []
num_tasks = 1  # 134

start_from_task = 134
for _ in range(1, start_from_task):
    print(_)
    get_next_task(MAX_STEPS)


run_title = f'do_debate={do_debate} Max steps: {MAX_STEPS}. Max votes: {MAX_VOTES}. model: {model}. Debate params: {debate_params}'
print(f'run_title: {run_title}')
for _ in range(num_tasks):

    # set up the context to pass around
    context = Context()
    # file that debaters will use to see agent history
    context.generation_observation_history = []
    # information to know when to log the full action count
    context.log_count = 0
    # information to know when to provide the system hint
    context.action_count = 0
    # count the number of debates
    context.debate_count = 0
    # only display the system hints if do_debate is true
    context.do_debate = do_debate
    # show the hints after every x many actions.
    context.system_hint_mod = 15
    # do majority voting
    context.max_votes = MAX_VOTES
    # count total votes so far
    context.vote_count = 0
    # store the votes
    context.votes = []

    # set up the available tools
    tools = [
        take_environment_action_wrapper(context)
    ]
    if do_debate:
        tools.append(view_debate_wrapper(context, **debate_params))

    # load the examples and task from ALFWorld
    examples, task, task_index = get_next_task(MAX_STEPS, do_debate=False) # not inserting debates even if in debate mode
    print(f'Task index: {task_index}')
    examples_str = '\n\n'.join([f'Example {i + 1}:\n{ex}' for i, ex in enumerate(examples)])
    examples_str = examples_str.replace('{', '{{').replace('}', '}}')
    info_logger.info(f'\n\n\n\n\n\n\n\n\nTask index: {task_index}')

    # load the prompt that tells how to format the actions
    formatting = read_text_file("./prompts/action_formatting.txt")

    # load the examples of failures
    failure_examples_str = read_text_file("./prompts/failure_examples.txt")

    # set up strings to insert if do_debate == True
    debate_examples_str = ''
    debate_msg_1 = ''
    debate_msg_2 = ''
    if do_debate:
        # debate_msg_1 = f'. Note that the parameters and observations corresponding to the "{VIEW_DEBATE}" tool are simply placeholders. This merely shows when the "{VIEW_DEBATE}" tool is supposed to be used.'
        debate_msg_2 = f'\n- IMPORTANT: Remember to use the "{VIEW_DEBATE}" tool to get a better understanding about your problem and proposed action BEFORE using "{TAKE_ENVIRONMENT_ACTION}".'
        debate_examples_str = '\n\n' + read_text_file("./prompts/debate_examples.txt")

    template = read_text_file("prompts/prompt_template.txt")

    # fill out the template
    template = template.format(
        formatting=formatting,
        success_examples=examples_str,
        failure_examples=failure_examples_str,
        debate_examples=debate_examples_str,
        debate_msg_1=debate_msg_1,
        debate_msg_2=debate_msg_2,
    )

    # create the prompt
    prompt = CustomPromptTemplate(
        template=template,
        tools=tools,
        # This omits the `agent_scratchpad`, `tools`, and `tool_names` variables because those are generated dynamically
        # This includes the `intermediate_steps` variable because that is needed
        input_variables=["input", "intermediate_steps"],
        context=context
    )

    # choose the language model
    # llm = ChatOpenAI(model='gpt-3.5-turbo-16k', temperature=0)
    import vertexai

    PROJECT_ID = 'gen-lang-client-0382320190'
    LOCATION = 'us-central1'
    vertexai.init(project=PROJECT_ID, location=LOCATION)
    from langchain.llms import VertexAI

    llm = VertexAI(
        model_name=model,
        temperature=temperature,
    )

    callbacks = None
    if langchain_logging:
        callbacks = [handler]
    llm_chain = LLMChain(
        llm=llm,
        prompt=prompt,
        callbacks=callbacks
    )
    agent = LLMSingleActionAgent(
        llm_chain=llm_chain,
        output_parser=CustomOutputParser(context=context),
        stop=[f"\n{OBSERVATION_PREFIX}"],
        allowed_tools=[tool.name for tool in tools]
    )

    agent_executor = AgentExecutor.from_agent_and_tools(
        agent=agent,
        tools=tools,
        verbose=True,
        max_iterations=2 * MAX_STEPS * context.max_votes + 1)
    agent_iterator = agent_executor.iter(inputs=task)

    # append to history for the debaters
    context.generation_observation_history.append('Task: ' + task)
    result_dict = dict()
    result_dict['task'] = task
    result_dict['task_index'] = task_index
    result_dict['success'] = False
    result_dict['run title'] = run_title
    total_steps = 0
    for step_num, step in enumerate(agent_iterator):

        # intermediate_step is a (action, observation) pair
        prev_ob = step.get('intermediate_step')
        if prev_ob:
            a, o = prev_ob[-1]
            if not o:
                break
            if FAIL_OBSERVATION in o:
                total_steps += 1
                break
            elif SUCCESS_OBSERVATION in o:
                total_steps += 1
                result_dict['success'] = True
                break
            elif EMPTY_RESPONSE not in o:
                total_steps += 1
        else:
            print("HERE")
            print(step)
            break

    result_dict['total_steps'] = total_steps
    # the number of times take_environment_action was called
    result_dict['total_actions'] = context.action_count
    results.append(result_dict)

    # save the results every time, so we don't lose anything
    results_dir = './results/'
    filename = f"{results_dir}results_{timestamp}.json"
    if not os.path.exists(results_dir):
        os.makedirs(results_dir)
    write_json_file(filename, results)
