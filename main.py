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
from utils import get_next_task
from tools import take_environment_action
from langchain.callbacks import FileCallbackHandler
from loguru import logger

logfile = 'output.log'
logger.add(logfile, colorize=True, enqueue=True)
handler = FileCallbackHandler(logfile)





api_key = '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'
os.environ['OPENAI_API_KEY'] = api_key



MAX_STEPS = 2






###############
# Setup Tools #
###############



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





##################
# Setup Template #
##################



# load the examples for this task type
examples, task = get_next_task(MAX_STEPS)
examples_str = '\n\n'.join([f'Example {i+1}:\n{ex}' for i, ex in enumerate(examples)])
examples_str = examples_str.replace('{', '{{').replace('}', '}}')

# load the prompt that tells how to format the actions
with open("react-multi-input-json.txt", "r") as f:
    formatting = f.read()

# create the template string
template = f"""Your job is to take actions in a simulated household environment in order to complete some task. You have access to the following tools:

{'{tools}'}

Use the following format for your output:

{formatting}

Here are 2 examples of completing a task in the simulated household environment:

{examples_str}

Begin! Remember to ALWAYS respond with a valid json blob of a single tool. Format is Thought, Action:```$JSON_BLOB```, then Observation. 

{'{input}'}
{'{agent_scratchpad}'}
"""


# with open('scratch.txt', 'w') as f:
#     f.write(template)


# Set up a prompt template
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


# create the prompt
prompt = CustomPromptTemplate(
    template=template,
    tools=tools,
    # This omits the `agent_scratchpad`, `tools`, and `tool_names` variables because those are generated dynamically
    # This includes the `intermediate_steps` variable because that is needed
    input_variables=["input", "intermediate_steps"]
)

# with open('scratch.txt', 'w') as f:
#     f.write(prompt)





########################
# Setup output parsing #
########################



class CustomOutputParser(AgentOutputParser):

    previous_output: str = None

    def parse(self, llm_output: str) -> Union[AgentAction, AgentFinish]:

        temp_previous_output = self.previous_output
        self.previous_output = llm_output
        
        if "Final Answer" in llm_output:
            return AgentFinish(
                    return_values={'output': "Task finished."},
                    log=llm_output
                )


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
                    return_values={'output': tool_input['output']},
                    log=llm_output
                )
            else:
                return AgentAction(tool=tool_name, tool_input=tool_input, log=llm_output)

        else:
            raise ValueError(f"Could not find text surrounded by 3 backticks: `{llm_output}`")




llm = ChatOpenAI(model='gpt-3.5-turbo', temperature=0)

llm_chain = LLMChain(llm=llm, prompt=prompt, callbacks=[handler])
tool_names = [tool.name for tool in tools]

agent = LLMSingleActionAgent(
    llm_chain=llm_chain,
    output_parser=CustomOutputParser(),
    stop=["\nObservation:"],
    allowed_tools=tool_names
)

agent_executor = AgentExecutor.from_agent_and_tools(agent=agent, tools=tools, verbose=True, max_iterations=MAX_STEPS + 1 + 10)


langchain.debug = False

agent_executor.run(task)





















