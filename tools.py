import requests
from utils import SUCCESS_OBSERVATION, FAIL_OBSERVATION


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
            observation = f"{observation} {SUCCESS_OBSERVATION}"
        else:
            observation = f"{observation} {FAIL_OBSERVATION}"

    return observation