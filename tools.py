import requests
from utils import SUCCESS_OBSERVATION, FAIL_OBSERVATION
from langchain.tools import tool
from pydantic import BaseModel, Field
from utils import TAKE_ENVIRONMENT_ACTION, FINAL_ANSWER, EMPTY_RESPONSE




class TakeEnvironmentAction(BaseModel):
    action: str = Field(description="The action to take.")


def take_environment_action_wrapper(context):
    @tool(TAKE_ENVIRONMENT_ACTION, args_schema=TakeEnvironmentAction)
    def take_environment_action(action: str) -> float:
        """Useful for when you want to take an action in the household environment."""
        if context.vote_count != 0:
            return EMPTY_RESPONSE

        context.vote_count = 0
        context.votes = []
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
                observation = f"{SUCCESS_OBSERVATION}"
            else:
                observation = f"{FAIL_OBSERVATION}"

        return observation
    return take_environment_action


class FinalAnswer(BaseModel):
    answer: str = Field(description="Your final answer.")


@tool(FINAL_ANSWER, args_schema=FinalAnswer)
def final_answer(answer: str) -> None:
    """Use this tool to output your final answer to the human."""
    pass
