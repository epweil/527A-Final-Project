from langchain.agents import AgentType, initialize_agent
from langchain.chat_models import ChatOpenAI
from langchain.tools import StructuredTool
import os
import requests
from utils import get_next_task


api_key = 'sk-............... INSERT YOUR KEY ..............'
os.environ['OPENAI_API_KEY'] = api_key


llm = ChatOpenAI(model='gpt-3.5-turbo', temperature=0)



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
            observation = "You have successfully completed the task. Please inform the user of this as your Final Answer in your next action."
        else:
            observation = "You have ran out of moves and are no longer able to complete the task. You failed. Please inform the user of this as your Final Answer in your next action."

    return observation


tool = StructuredTool.from_function(take_environment_action)


agent_executor = initialize_agent(
    [tool],
    llm,
    agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
)


task_prompt = get_next_task()

print(task_prompt)

res = agent_executor.run(task_prompt)

print(f'res: {res}')

