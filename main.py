from langchain.agents import Tool, AgentExecutor, LLMSingleActionAgent, AgentOutputParser
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
from utils import get_next_task, SUCCESS_OBSERVATION, FAIL_OBSERVATION
from tools import take_environment_action
from debate import view_debate
from langchain.callbacks import FileCallbackHandler
from loguru import logger
from langchain.agents.agent_iterator import AgentExecutorIterator
from datetime import datetime




class CustomPromptTemplate(StringPromptTemplate):
    # The template to use
    template: str
    # The list of tools available
    tools: List[Tool]

    def format(self, **kwargs) -> str:
        # Get the intermediate steps (AgentAction, Observation tuples)
        # Format them in a particular way
        intermediate_steps = kwargs.pop("intermediate_steps")
        history = ""
        for action, observation in intermediate_steps:
            history += action.log
            history += f"\nObservation: {observation}\n"
        # Set the agent_scratchpad variable to that value
        kwargs["agent_scratchpad"] = history
        # Create a tools variable from the list of tools provided
        kwargs["tools"] = "\n".join([f"{tool.name}: {tool.description}" for tool in self.tools])
        # Create a list of tool names for the tools provided
        kwargs["tool_names"] = " or ".join([tool.name for tool in self.tools])
        return self.template.format(**kwargs)



class CustomOutputParser(AgentOutputParser):

    def parse(self, llm_output: str) -> Union[AgentAction, AgentFinish]:
        
        # if "Final Answer" in llm_output:
        #     return AgentFinish(
        #             return_values={'output': "Task finished."},
        #             log=llm_output
        #         )

        pattern = r'```(.*?)```'
        match = re.search(pattern, llm_output, re.DOTALL)

        if match:

            tool_info_str = match.group(1)
            try:
                tool_info = json.loads(tool_info_str)
                tool_name = tool_info['tool']
                tool_input = tool_info['tool_input']
            except:
                raise ValueError(f"Could not parse the JSON string describing the tool: `{tool_info_str}`")
            
            if tool_name == 'Final Answer':
                return AgentFinish(
                    return_values={'output': tool_input},
                    log=llm_output
                )
            elif tool_name == 'view_debate':
                return AgentAction(tool=tool_name, tool_input=tool_input, log=llm_output)
            else:
                return AgentAction(tool=tool_name, tool_input=tool_input, log=llm_output)

        else:
            raise ValueError(f"Could not find text surrounded by 3 backticks: `{llm_output}`")









logfile = 'output.log'
logger.add(logfile, colorize=True, enqueue=True)
handler = FileCallbackHandler(logfile)

api_key = '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'
os.environ['OPENAI_API_KEY'] = api_key

langchain.debug = False
log_outputs = True
do_debate = True
MAX_STEPS = 10

results = []
num_tasks = 2 # 134

timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
for _ in range(num_tasks):



    #####################################
    #####################################
    ## GET THE TASK AND SETUP TEMPLATE ##
    #####################################
    #####################################

    tools = [
        Tool(
            name="take_environment_action",
            func=take_environment_action,
            description="Useful for when you want to take an action in the household environment. It takes 1 parameter called 'action'"
        ),
        Tool(
            name="Final Answer",
            func=lambda: None,
            description="Use this tool to output your final answer to the human. It takes 1 parameter called 'output'"
        )
    ]

    if do_debate:
        tools.append(Tool(
            name="view_debate",
            func=view_debate,
            description="Use this tool to view a debate on whether your action is the best or not. You should use this tool when you are unsure about what action is best. You should pass this tool as arguments the current problem or sub-goal you are trying to achieve, as well as your current best solution. You will receive a dialogue between 2 debaters who are arguing whether your proposed action is best or not.\n" +
            "Parameters: problem --- the problem you are trying to solve, proposed_solution --- the action you currently think is best."
        ))



    # load the examples and task
    examples, task, task_index = get_next_task(MAX_STEPS)
    # examples = examples[:1]
    examples_str = '\n\n'.join([f'Example {i+1}:\n{ex}' for i, ex in enumerate(examples)])
    examples_str = examples_str.replace('{', '{{').replace('}', '}}')

    # load the prompt that tells how to format the actions
    with open("./prompts/action_formatting.txt", "r") as f:
        formatting = f.read()

    # load the examples of failures
    with open("./prompts/failure_examples.txt", "r") as f:
        failure_examples_str = f.read()

    debate_examples = ''
    if do_debate:
        with open("./prompts/debate_examples.txt", "r") as f:
            debate_examples = '\n\n' + f.read()

    # create the template string
    template = f"""Your job is to take actions in a simulated household environment in order to complete some task. You have access to the following tools:

{'{tools}'}

Use the following format for your output:

{formatting}

Here are 2 examples of completing a task in the simulated household environment:

{examples_str}

Here are 2 examples of what failure looks like (note, only the end of the execution is given):

{failure_examples_str}{debate_examples}

Begin! Remember to ALWAYS respond with a valid json blob of a single tool. Format is Thought, Action:```$JSON_BLOB```, then Observation. 

IMPORTANT: You should always strive to produce Thought's after every Observation. Additionally, you should always strive to use the "view_debate" tool before using "take_environment_action".

{'{input}'}
{'{agent_scratchpad}'}
"""
    





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
    if log_outputs: 
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
        stop=["\nObservation:"],
        allowed_tools=tool_names
    )

    agent_executor = AgentExecutor.from_agent_and_tools(agent=agent, tools=tools, verbose=True, max_iterations=MAX_STEPS + 1 + 10) # the +1 is for the final answer
    agent_iterator = AgentExecutorIterator(agent_executor=agent_executor, inputs=task)








    ###############################
    ###############################
    ## RUN TASK AND SAVE RESULTS ##
    ###############################
    ###############################




    result_dict = dict()
    result_dict['task'] = task
    result_dict['task_index'] = task_index
    result_dict['success'] = False
    total_steps = 0
    for step_num, step in enumerate(agent_iterator):
        step_num += 1
        total_steps += 1
        print(f'Task={task_index}, Step={step_num}')
        
        last_observation = step.get('intermediate_step') # intermediate_step is a list of (action, observation) pairs
        
        if last_observation is not None and SUCCESS_OBSERVATION in last_observation[-1][1]:
                result_dict['success'] = True

    result_dict['total_steps'] = total_steps - 1 # -1 because we don't count final answer as a step
    results.append(result_dict)

    # save the results every time so we don't lose anything
    results_dir = './results/'
    filename = f"{results_dir}results_{timestamp}.json"
    if not os.path.exists(results_dir):
        os.makedirs(results_dir)
    with open(filename, 'w') as f:
        json.dump(results, f, indent=2)






















