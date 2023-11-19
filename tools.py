import requests


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