from langchain.agents import Tool, AgentExecutor, LLMSingleActionAgent, AgentOutputParser
from langchain.prompts import StringPromptTemplate

from langchain import OpenAI
from langchain.chains import LLMChain
from langchain.tools import DuckDuckGoSearchRun

from typing import List, Union
from langchain.schema import AgentAction, AgentFinish
import re
import langchain
import os
import requests
from utils import *




api_key = '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'
os.environ['OPENAI_API_KEY'] = api_key





def take_environment_action(action: str) -> float:
    """Take an action within the household environment."""
    url = 'http://localhost:8000/take_action'
    data = {
        "action": action
    }

    response = requests.post(url, json=data)
    json_response = response.json()
    observation = json_response.get("observation")
    done = json_response.get("done")
    reward = json_response.get("reward")

    if done:
        if reward:
            observation = f"{observation} You have successfully completed the task. Please inform the user of this as your Final Answer in your next action."
        else:
            observation = f"{observation} You have ran out of moves and are no longer able to complete the task. You failed. Please inform the user of this as your Final Answer in your next action."

    return observation



tools = [
    Tool(
        name = "take_environment_action",
        func=take_environment_action,
        description="Useful for when you want to take an action in the household environment."
    )
]


# load the examples for this task type
examples, task = get_next_task()
examples_str = '\n\n'.join([f'Example {i+1}:\n{ex}' for i, ex in enumerate(examples)])

# load the prompt that tells how to format the actions
with open("react-multi-input-json.txt", "r") as f:
    formatting = f.read()



template = f"""Your job is to take actions in a simulated household environment in order to complete some task. You have access to the following tools:

{'{tools}'}

Use the following format for your output:

{formatting}

Here are 2 examples of completing a task in the simulated household environment:

{examples_str}

Begin! Remember to ALWAYS respond with a valid json blob of a single tool. Format is Action:```$JSON_BLOB```then Observation. 

{'{input}'}
{'{agent_scratchpad}'}
"""

print(template)

# task_prompt = get_next_task()

with open('scratch.txt', 'w') as f:
    f.write(template)
