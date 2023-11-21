import requests
from utils import SUCCESS_OBSERVATION, FAIL_OBSERVATION
from langchain.tools import tool
from pydantic import BaseModel, Field
from utils import TAKE_ENVIRONMENT_ACTION, FINAL_ANSWER



class TakeEnvironmentAction(BaseModel):
    action: str = Field(description="The action to take.")


@tool(TAKE_ENVIRONMENT_ACTION, args_schema=TakeEnvironmentAction)
def take_environment_action(action: str) -> float:
    """Useful for when you want to take an action in the household environment."""
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
            observation = f"{observation} {SUCCESS_OBSERVATION}"
        else:
            observation = f"{observation} {FAIL_OBSERVATION}"

    return observation


class FinalAnswer(BaseModel):
    answer: str = Field(description="Your final answer.")


@tool(FINAL_ANSWER, args_schema=FinalAnswer)
def final_answer(answer: str) -> None:
    """Use this tool to output your final answer to the human."""
    pass
