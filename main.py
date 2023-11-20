from langchain.agents import AgentExecutor, LLMSingleActionAgent, AgentOutputParser
from langchain.tools import Tool, StructuredTool
from langchain.prompts import StringPromptTemplate

from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain

from typing import List, Union
from langchain.schema import AgentAction, AgentFinish
import re
import langchain
import os
import json
import requests
from utils import *
from tools import take_environment_action, final_answer
from debate import view_debate_wrapper
from langchain.callbacks import FileCallbackHandler
from loguru import logger
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
generation_observation_history_filename = 'generation_observation_history.json'
log_count = 0
action_count = 0
agent_executor = None

class CustomPromptTemplate(StringPromptTemplate):
    # The template to use
    template: str
    # The list of tools available
    tools: List[Tool]

    def format(self, **kwargs) -> str:
        global log_count
        global agent_executor
        # Get the intermediate steps (AgentAction, Observation tuples)
        # Format them in a particular way
        intermediate_steps = kwargs.pop("intermediate_steps")

        history_lines = []
        last_action = None
        last_observation = None
        for action, observation in intermediate_steps:
            history_lines.append(action.log.strip())
            history_lines.append(f"{OBSERVATION_PREFIX} {observation}")
            last_action = action
            last_observation = observation

        history = '\n'.join(history_lines)
        if last_action and last_action.tool == TAKE_ENVIRONMENT_ACTION:
            system_hint = HINT_AFTER_ACTION
            history += '\n' + system_hint
            read_append_write_json(
                generation_observation_history_filename,
                f'{OBSERVATION_PREFIX} {last_observation}'
            )
        if last_action and last_action.tool == VIEW_DEBATE:
            system_hint = HINT_AFTER_DEBATE
            history += '\n' + system_hint
        # Set the agent_scratchpad variable to that value
        kwargs["agent_scratchpad"] = history
        # Create a tools variable from the list of tools provided
        tool_strings = []
        for tool in self.tools:
            s = f"{tool.name}: {tool.description}"
            params = [f'{param} - {info["description"]}' for param, info in tool.args.items()]
            s += ' Arguments: ' + ' '.join(params)
            tool_strings.append(s)
        kwargs["tools"] = "\n".join(tool_strings)
        # Create a list of tool names for the tools provided
        kwargs["tool_names"] = " or ".join([tool.name for tool in self.tools])
        p = self.template.format(**kwargs)
        if log_count == 0:
            info_logger.info(f"Step {log_count} ===")
            info_logger.info(p)
        else:
            info_logger.info(f"\nStep {log_count} ===")
            info_logger.info(f'Generation ---\n{last_action.log}')
            info_logger.info(f'Observation ---\n{last_observation}')
            info_logger.info(f'<only seen once by agent> {system_hint}')
        log_count += 1
        return p



class CustomOutputParser(AgentOutputParser):


    def parse(self, llm_output: str) -> Union[AgentAction, AgentFinish]:
        global action_count
        # if "Final Answer" in llm_output or FINAL_ANSWER in llm_output:
        #     return AgentFinish(
        #             return_values={'output': "Task finished."},
        #             log=llm_output
        #         )

        default_agent_finish = AgentFinish(
            return_values={'output': "Task finished."},
            log=llm_output
        )

        pattern = r'```(.*?)```'
        match = re.search(pattern, llm_output, re.DOTALL)

        try:
            if match:

                tool_info_str = match.group(1)
                try:
                    tool_info = json.loads(tool_info_str)
                    tool_name = tool_info['tool']
                    tool_input = tool_info['tool_input']
                except:
                    raise ValueError(f"Could not parse the JSON string describing the tool: `{tool_info_str}`")

                if tool_name == FINAL_ANSWER:
                    info_logger.info(f"\nStep {log_count} ===")
                    info_logger.info(f'Generation ---\n{llm_output}')
                    return AgentFinish(
                        return_values={'output': tool_input['answer']},
                        log=llm_output
                    )
                elif tool_name == VIEW_DEBATE:
                    return AgentAction(tool=tool_name, tool_input=tool_input, log=llm_output)
                elif tool_name == TAKE_ENVIRONMENT_ACTION:
                    action_count += 1
                    read_append_write_json(
                        generation_observation_history_filename,
                        'Action: ' + tool_input.get('action')
                    )
                    info_logger.info(f"\nAction Count {action_count} +++")
                    return AgentAction(tool=tool_name, tool_input=tool_input, log=llm_output)

            else:
                raise ValueError(f"Could not find text surrounded by 3 backticks: `{llm_output}`")
        except:
            return default_agent_finish





api_key = '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'
os.environ['OPENAI_API_KEY'] = api_key

langchain.debug = True
log_level = log_levels['all']
langchain_logging = False
do_debate = True
MAX_STEPS = 4

info_logger.setLevel(log_level)
if langchain_logging:
    handler = FileCallbackHandler(debug_filename)

results = []
num_tasks = 1 # 134

for _ in range(num_tasks):
    log_count = 0
    action_count = 0
    write_text_file(generation_observation_history_filename, '')



    #####################################
    #####################################
    ## GET THE TASK AND SETUP TEMPLATE ##
    #####################################
    #####################################

    tools = [
        take_environment_action,
        final_answer
    ]

    action_history = 'None'
    if do_debate:
        tools.append(view_debate_wrapper(action_history))

    # load the examples and task
    examples, task, task_index = get_next_task(MAX_STEPS, do_debate=do_debate)
    # examples = examples[:1]
    examples_str = '\n\n'.join([f'Example {i+1}:\n{ex}' for i, ex in enumerate(examples)])
    examples_str = examples_str.replace('{', '{{').replace('}', '}}')

    # load the prompt that tells how to format the actions
    formatting = read_text_file("./prompts/action_formatting.txt")
    # with open("./prompts/action_formatting.txt", "r") as f:
    #     formatting = f.read()

    # load the examples of failures
    failure_examples_str = read_text_file("./prompts/failure_examples.txt")
    # with open("./prompts/failure_examples.txt", "r") as f:
    #     failure_examples_str = f.read()

    debate_examples_str = ''
    debate_msg_1 = ''
    debate_msg_2 = ''
    if do_debate:
        debate_msg_1 = f'. Note that the parameters and observations corresponding to the "{VIEW_DEBATE}" tool are simply placeholders. This merely shows when the "{VIEW_DEBATE}" tool is supposed to be used.'
        debate_msg_2 = f'\n- IMPORTANT: Remember to use the "{VIEW_DEBATE}" tool to get a better understanding about your problem and proposed action BEFORE using "{TAKE_ENVIRONMENT_ACTION}".'
        debate_examples_str = '\n\n' + read_text_file("./prompts/debate_examples.txt")
        # with open("./prompts/debate_examples.txt", "r") as f:
        #     debate_examples_str = '\n\n' + f.read()

    template = read_text_file("prompts/prompt_template.txt")
    # with open("prompts/prompt_template.txt", "r") as f:
    #     template = f.read()

    template = template.format(
        formatting=formatting,
        success_examples=examples_str,
        failure_examples=failure_examples_str,
        debate_examples=debate_examples_str,
        debate_msg_1 = debate_msg_1,
        debate_msg_2 = debate_msg_2,
    )



    ###################################
    ###################################
    ## CREATE PROMPT AND SETUP AGENT ##
    ###################################
    ###################################




    # create the prompt
    prompt = CustomPromptTemplate(
        template=template,
        tools=tools,
        # This omits the `agent_scratchpad`, `tools`, and `tool_names` variables because those are generated dynamically
        # This includes the `intermediate_steps` variable because that is needed
        input_variables=["input", "intermediate_steps"]
    )

    llm = ChatOpenAI(model='gpt-3.5-turbo-16k', temperature=0)

    callbacks = None
    if langchain_logging:
        callbacks = [handler]
    llm_chain = LLMChain(
        llm=llm, 
        prompt=prompt, 
        callbacks=callbacks
    )
    tool_names = [tool.name for tool in tools]

    agent = LLMSingleActionAgent(
        llm_chain=llm_chain,
        output_parser=CustomOutputParser(),
        stop=[f"\n{OBSERVATION_PREFIX}"],
        allowed_tools=tool_names
    )

    agent_executor = AgentExecutor.from_agent_and_tools(agent=agent, tools=tools, verbose=True, max_iterations=2*MAX_STEPS + 1)
    # agent_iterator = AgentExecutorIterator(agent_executor=agent_executor, inputs=task)
    agent_iterator = agent_executor.iter(inputs=task)






    ###############################
    ###############################
    ## RUN TASK AND SAVE RESULTS ##
    ###############################
    ###############################


    read_append_write_json(
        generation_observation_history_filename,
        'Task: ' + task
    )
    result_dict = dict()
    result_dict['task'] = task
    result_dict['task_index'] = task_index
    result_dict['success'] = False
    total_steps = 0
    for step_num, step in enumerate(agent_iterator):
        step_num += 1
        total_steps += 1
        print(f'Task={task_index}, Step={step_num}')
        
        prev_ob = step.get('intermediate_step') # intermediate_step is a list of (action, observation) pairs
        
        if prev_ob is not None and SUCCESS_OBSERVATION in prev_ob[-1][1]:
            result_dict['success'] = True

    result_dict['total_steps'] = total_steps - 1 # -1 because we don't count final answer as a step
    result_dict['total_actions'] = action_count # the number of times take_environment_action was called
    results.append(result_dict)

    # save the results every time so we don't lose anything
    results_dir = './results/'
    filename = f"{results_dir}results_{timestamp}.json"
    if not os.path.exists(results_dir):
        os.makedirs(results_dir)
    write_json_file(filename, results)
    # with open(filename, 'w') as f:
    #     json.dump(results, f, indent=2)






















