
base_prompt = "Interact with a household to solve a task. Here are two examples.\nYou are in the middle of a room. Looking quickly around you, you see a cabinet 4, a cabinet 3, a cabinet 2, a cabinet 1, a coffeemachine 1, a countertop 1, a diningtable 3, a diningtable 2, a diningtable 1, a drawer 1, a fridge 1, a garbagecan 1, a microwave 1, a sidetable 1, a sinkbasin 1, a stoveburner 4, a stoveburner 3, a stoveburner 2, a stoveburner 1, and a toaster 1.\nYour task is to: find some apple and put it in sidetable.\n> think: To solve the task, I need to find and take an apple, then put it in sidetable.\nOK.\n> think: First I need to find an apple. An apple is more likely to appear in fridges (1), diningtables (1-3), sidetables (1), countertops (1), sinkbasins (1), garbagecan (1). I can check one by one, starting with fridge 1.\nOK.\n> go to fridge 1\nThe fridge 1 is closed.\n> open fridge 1\nYou open the fridge 1. The fridge 1 is open. In it, you see a lettuce 2, a mug 2, a potato 2, and a tomato 1.\n> go to diningtable 1\nOn the diningtable 1, you see nothing.\n> go to diningtable 2\nOn the diningtable 2, you see a pineapple 1.\n> go to diningtable 3\nOn the diningtable 3, you see a bowl 2, a bowl 1, a bread 2, and a bread 1.\n> go to sidetable 1\nOn the sidetable 1, you see a cup 1, a lettuce 1, a peppershaker 3, a potato 1, and a saltshaker 1.\n> go to countertop 1\nOn the countertop 1, you see a butterknife 1, a dishsponge 1, and a soapbottle 1.\n> go to sinkbasin 1\nOn the sinkbasin 1, you see a cup 2, a egg 1, a mug 1, and a potato 3.\n> go to garbagecan 1\nOn the garbagecan 1, you see a apple 3, and a egg 3.\n> think: Now I find an apple (3). Next, I need to take it.\n> take apple 3 from garbagecan 1\nYou pick up the apple 3 from the garbagecan 1.\n> think: Now I find an apple (3). Next, I need to put it in/on sidetable 1.\nOK.\n> go to sidetable 1\nOn the sidetable 1, you see a cup 1, a lettuce 1, a peppershaker 3, a potato 1, and a saltshaker 1.\n> put apple 3 in/on sidetable 1\nYou put the apple 3 in/on the sidetable 1.\nYou are in the middle of a room. Looking quickly around you, you see a cabinet 4, a cabinet 3, a cabinet 2, a cabinet 1, a countertop 1, a garbagecan 1, a handtowelholder 2, a handtowelholder 1, a sinkbasin 2, a sinkbasin 1, a toilet 1, a toiletpaperhanger 1, and a towelholder 1.\nYour task is to: put some spraybottle on toilet.\n> think: To solve the task, I need to find and take a sparybottle, then put it on toilet.\nOK.\n> think: First I need to find a spraybottle. A spraybottle is more likely to appear in cabinet (1-4), countertop (1), toilet (1), sinkbasin (1-2), garbagecan (1). I can check one by one, starting with cabinet 1.\nOK.\n> go to cabinet 1\nOn the cabinet 1, you see a cloth 1, a soapbar 1, a soapbottle 1.\n> go to cabinet 2\nThe cabinet 2 is closed.\n> open cabinet 2\nYou open the cabinet 2. The cabinet 2 is open. In it, you see a candle 1, and a spraybottle 2.\n> think: Now I find a spraybottle (2). Next, I need to take it.\n> take spraybottle 2 from cabinet 2\nYou pick up the spraybottle 2 from the cabinet 2.\n> think: Now I take a spraybottle (2). Next, I need to put it in/on toilet 1.\nOK.\n> go to toilet 1\nOn the toilet 1, you see a soapbottle 2.\n> put spraybottle 2 in/on toilet 1\nYou put the spraybottle 2 in/on the toilet 1.\n\nHere is the task.\nYou are in the middle of a room. Looking quickly around you, you see a armchair 1, a cabinet 4, a cabinet 3, a cabinet 2, a cabinet 1, a drawer 5, a drawer 4, a drawer 3, a drawer 2, a drawer 1, a dresser 1, a garbagecan 1, a safe 1, a shelf 12, a shelf 11, a shelf 10, a shelf 9, a shelf 8, a shelf 7, a shelf 6, a shelf 5, a shelf 4, a shelf 3, a shelf 2, a shelf 1, a sidetable 1, and a sofa 1.\nYour task is to: put some vase on safe.\n>"
old_prompt = base_prompt
# old_prompt = old_prompt[:-1]



lines = base_prompt.split('\n')[:-1] # get rid of last >
lines = [l.strip() for l in lines if len(l.strip()) > 0]

formatted_lines = []

previous_was_action = False
previous_was_thought = False
previous_thought_index = -1
counter = 0
for i, line in enumerate(lines):

    line_status = None
    new_line = ''
    curr_thought_index = -1
    if line[0] == '>':
        if len(line) >= 8 and line[:8] == '> think:':
            line_status = 'thought'
            curr_thought_index = counter
            new_line = 'Thought: ' + line[8:].strip()
        else:
            line_status = 'action'
            new_line = 'Action: ' + line[1:].strip()
    elif previous_was_action:
        line_status = 'observation'
        new_line = 'Observation: ' + line
    elif previous_was_thought:
        new_line = ''
    else:
        new_line = line


    if line_status == 'thought' and previous_was_thought:
        formatted_lines[previous_thought_index] = formatted_lines[previous_thought_index] + new_line[8:] # remove the "Thought:"
    elif new_line != '':
        if line_status == 'thought':
            previous_thought_index = curr_thought_index
        formatted_lines.append(new_line)
        counter += 1
    else:
        continue


    previous_was_action = line_status == 'action'
    previous_was_thought = line_status == 'thought'


# now format the actions
final_lines = []
for fline in formatted_lines:
    if len(fline) < 7 or fline[:7] != 'Action:':
        final_lines.append(fline)
    else:
        action_str = fline[7:].strip()
        lc = '{'
        rc = '}'
        new_action_str = f'\n```\n{lc}\n  "action": "take_environment_action",\n  "action_input": "{action_str}"\n{rc}\n```'
        final_lines.append("Action: " + new_action_str)

final_prompt = '\n'.join(final_lines)

with open("final_prompt.txt", "w") as file:
    file.write(final_prompt)



# # remove OK's
# old_prompt = old_prompt.replace('\nOK.', '')
# # add Observation:
# old_prompt = old_prompt.replace('\n>', '(JAKE)')
# old_prompt = old_prompt.replace('\n', '\nObservation: ')
# old_prompt = old_prompt.replace('(JAKE)', '\n>')
# old_prompt = old_prompt[:-1]

# add_thought = old_prompt.replace("> think:", "Thought:")
# add_thought = add_thought.replace("\nOK.", "")
# add_action = add_thought.replace(">", "Action:")

# with open("base_prompt.txt", "w") as file:
#     file.write(base_prompt)

# with open("old_prompt.txt", "w") as file:
#     file.write(old_prompt)

# with open("add_thought.txt", "w") as file:
#     file.write(add_thought)

# with open("add_action.txt", "w") as file:
#     file.write(add_action)




# from langchain.chat_models import ChatOpenAI
# from langchain.chains import ReAct
# from langchain.tools import BaseTool
# from langchain.prompts import Prompt
# import requests

# # Define the custom tool that interacts with the virtual environment
# class EnvironmentActionTool(BaseTool):
#     def __init__(self, api_url):
#         self.api_url = api_url

#     def __call__(self, action):
#         # Make a POST request to the API with the action
#         response = requests.post(
#             self.api_url,
#             json={"action": action}
#         )
#         # Check if the request was successful
#         if response.status_code == 200:
#             return response.json()
#         else:
#             raise Exception(f"API request failed with status code {response.status_code}")

# # Initialize the LLM
# llm = ChatOpenAI(model='gpt-3.5-turbo', temperature=0)

# # Define the prompt for the structured-chat-zero-shot agent
# prompt = Prompt("I am an AI that can take actions in a virtual environment. You can tell me to do things like 'find the apple' and I will perform actions to complete the task. What would you like me to do?")

# # Create the ReAct agent
# react_agent = ReAct(
#     llm=llm,
#     prompt=prompt,
#     tools={
#         "take_environment_action": EnvironmentActionTool("http://localhost:8000/take_action")
#     },
#     structured=True
# )

# # Example usage of the ReAct agent
# # This should be replaced with the actual interaction logic
# if __name__ == "__main__":
#     problem = "find the apple"
#     response = react_agent(problem)
#     print(response)