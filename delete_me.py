
from utils import *





a = """

"Human: Your job is to take actions in a simulated household environment in order to complete some task. You have access to the following tools:\n\ntake_environment_action: Useful for when you want to take an action in the household environment.\n\nUse the following format for your output:\n\nUse a json blob to specify a tool by providing an tool key (tool name) and an tool_input key (tool input).\n\nValid \"tool\" values: take_environment_action\n\nProvide only ONE tool per $JSON_BLOB, as shown:\n\n```\n{\n  \"tool\": $TOOL_NAME,\n  \"tool_input\": $INPUT\n}\n```\n\nFollow this format:\n\nThought: consider previous and subsequent steps\nAction:\n```\n$JSON_BLOB\n```\nObservation: action result\n... (repeat Thought/Action/Observation N times)\nThought: I know what to respond\nAction:\n```\n{\n  \"tool\": \"Final Answer\",\n  \"tool_input\": \"Final response to human\"\n}\n```\n\nHere are 2 examples of completing a task in the simulated household environment:\n\nExample 1:\nYou are in the middle of a room. Looking quickly around you, you see a coffeetable 1, a diningtable 1, a drawer 4, a drawer 3, a drawer 2, a drawer 1, a dresser 1, a garbagecan 1, a sidetable 2, a sidetable 1, and a sofa 1.\nYour task is to: put two cellphone in sofa.\nThought: To solve the task, I need to find and take the first cellphone, then put it in sofa, then find and take the second cellphone, then put it in sofa. First I need to find the first cellphone. A cellphone is more likely to appear in coffeetable (1), diningtable (1), sidetable (1-2), drawer (1-4), sofa (1), dresser (1), garbagecan (1). I can check one by one, starting with coffeetable 1.\nAction: \n```\n{\n  \"tool\": \"take_environment_action\",\n  \"tool_input\": {\n    \"action\": \"go to coffeetable 1\"\n  }\n}\n```\nObservation: On the coffeetable 1, you see a box 1, a cellphone 3, and a plate 1.\nAction: \n```\n{\n  \"tool\": \"take_environment_action\",\n  \"tool_input\": {\n    \"action\": \"take cellphone 3 from coffeetable 1\"\n  }\n}\n```\nObservation: You pick up the cellphone 3 from the coffeetable 1.\nThought: Now I find the first cellphone (3). Next, I need to put it in/on sofa 1.\nAction: \n```\n{\n  \"tool\": \"take_environment_action\",\n  \"tool_input\": {\n    \"action\": \"go to sofa 1\"\n  }\n}\n```\nObservation: On the sofa 1, you see a newspaper 2, a pillow 1, a remotecontrol 2, and a remotecontrol 1.\nAction: \n```\n{\n  \"tool\": \"take_environment_action\",\n  \"tool_input\": {\n    \"action\": \"put cellphone 3 in/on sofa 1\"\n  }\n}\n```\nObservation: You put the cellphone 3 in/on the sofa 1.\nThought: Now I put the first cellphone in sofa. Next, I need to find the second cellphone. I have visited coffeetable (1), so the second cellphone is more likely to appear in diningtable (1), sidetable (1-2), drawer (1-4), sofa (1), dresser (1), garbagecan (1). I can check one by one, starting with coffeetable 1.\nAction: \n```\n{\n  \"tool\": \"take_environment_action\",\n  \"tool_input\": {\n    \"action\": \"go to diningtable 1\"\n  }\n}\n```\nObservation: On the diningtable 1, you see a cellphone 2, a keychain 2, a laptop 1, a statue 2, and a statue 1.\nThought: Now I find the second cellphone (2). Next, I need to take it.\nAction: \n```\n{\n  \"tool\": \"take_environment_action\",\n  \"tool_input\": {\n    \"action\": \"take cellphone 2 from diningtable 1\"\n  }\n}\n```\nObservation: You pick up the cellphone 2 from the diningtable 1.\nThought: Now I take the second cellphone (2). Next, I need to put it in/on sofa 1.\nAction: \n```\n{\n  \"tool\": \"take_environment_action\",\n  \"tool_input\": {\n    \"action\": \"go to sofa 1\"\n  }\n}\n```\nObservation: On the sofa 1, you see a cellphone 3, a newspaper 2, a pillow 1, a remotecontrol 2, and a remotecontrol 1.\nAction: \n```\n{\n  \"tool\": \"take_environment_action\",\n  \"tool_input\": {\n    \"action\": \"put cellphone 2 in/on sofa 1\"\n  }\n}\n```\nObservation: You put the cellphone 2 in/on the sofa 1. You have successfully completed the task. Please inform the user of this as your Final Answer in your next action.\nAction: \n```\n{\n  \"tool\": \"Final Answer\",\n  \"tool_input\": \"I have successfully completed the task.\"\n}\n```\n\nExample 2:\nYou are in the middle of a room. Looking quickly around you, you see a armchair 2, a armchair 1, a bed 1, a countertop 1, a diningtable 1, a drawer 2, a drawer 1, a dresser 1, a garbagecan 1, a laundryhamper 1, and a sidetable 1.\nYour task is to: put two creditcard in dresser.\nThought: To solve the task, I need to find and take the first creditcard, then put it in dresser, then find and take the second creditcard, then put it in dresser. First I need to find the first creditcard. A creditcard is more likely to appear in drawer (1-2), coutertop (1), sidetable (1), diningtable (1), armchair (1-2), bed (1). I can check one by one, starting with drawer 1.\nAction: \n```\n{\n  \"tool\": \"take_environment_action\",\n  \"tool_input\": {\n    \"action\": \"go to drawer 1\"\n  }\n}\n```\nObservation: The drawer 1 is closed.\nAction: \n```\n{\n  \"tool\": \"take_environment_action\",\n  \"tool_input\": {\n    \"action\": \"open drawer 1\"\n  }\n}\n```\nObservation: You open the drawer 1. The drawer 1 is open. In it, you see a book 1, a cd 1, and a pen 1.\nAction: \n```\n{\n  \"tool\": \"take_environment_action\",\n  \"tool_input\": {\n    \"action\": \"go to drawer 2\"\n  }\n}\n```\nObservation: The drawer 2 is closed.\nAction: \n```\n{\n  \"tool\": \"take_environment_action\",\n  \"tool_input\": {\n    \"action\": \"open drawer 2\"\n  }\n}\n```\nObservation: You open the drawer 2. The drawer 2 is open. In it, you see nothing.\nAction: \n```\n{\n  \"tool\": \"take_environment_action\",\n  \"tool_input\": {\n    \"action\": \"go to countertop 1\"\n  }\n}\n```\nObservation: On the countertop 1, you see a cellphone 2, a creditcard 4, a creditcard 3, a creditcard 2, a mirror 1, a pencil 2, and a pencil 1.\nThought: Now I find the first creditcard (2). Next, I need to take it. I can find the second creditcard (3) later in countertop 1.\nAction: \n```\n{\n  \"tool\": \"take_environment_action\",\n  \"tool_input\": {\n    \"action\": \"take creditcard 2 from countertop 1\"\n  }\n}\n```\nObservation: You pick up the creditcard 2 from the countertop 1.\nThought: Now I take the first creditcard (2). Next, I need to put it in/on dresser 1.\nAction: \n```\n{\n  \"tool\": \"take_environment_action\",\n  \"tool_input\": {\n    \"action\": \"go to dresser 1\"\n  }\n}\n```\nObservation: On the dresser 1, you see a mug 1, and a television 1.\nAction: \n```\n{\n  \"tool\": \"take_environment_action\",\n  \"tool_input\": {\n    \"action\": \"put creditcard 2 in/on dresser 1\"\n  }\n}\n```\nObservation: You put the creditcard 2 in/on the dresser 1.\nThought: Now I put the first creditcard in dresser. Next, I need to find the second creditcard. I can directly go to countertop 1.\nAction: \n```\n{\n  \"tool\": \"take_environment_action\",\n  \"tool_input\": {\n    \"action\": \"go to countertop 1\"\n  }\n}\n```\nObservation: On the countertop 1, you see a cellphone 2, a creditcard 4, a creditcard 3, a mirror 1, a pencil 2, and a pencil 1.\nThought: Now I find the second creditcard (3). Next, I need to take it.\nAction: \n```\n{\n  \"tool\": \"take_environment_action\",\n  \"tool_input\": {\n    \"action\": \"take creditcard 3 from countertop 1\"\n  }\n}\n```\nObservation: You pick up the creditcard 3 from the countertop 1.\nThought: Now I take the second creditcard (3). Next, I need to put it in/on dresser 1.\nAction: \n```\n{\n  \"tool\": \"take_environment_action\",\n  \"tool_input\": {\n    \"action\": \"go to dresser 1\"\n  }\n}\n```\nObservation: On the dresser 1, you see a creditcard 2, a mug 1, and a television 1.\nAction: \n```\n{\n  \"tool\": \"take_environment_action\",\n  \"tool_input\": {\n    \"action\": \"put creditcard 3 in/on dresser 1\"\n  }\n}\n```\nObservation: You put the creditcard 3 in/on the dresser 1. You have successfully completed the task. Please inform the user of this as your Final Answer in your next action.\nAction: \n```\n{\n  \"tool\": \"Final Answer\",\n  \"tool_input\": \"I have successfully completed the task.\"\n}\n```\n\nBegin! Remember to ALWAYS respond with a valid json blob of a single tool. Format is Action:```$JSON_BLOB```then Observation. \n\nyour task is to find the door"

"""

with open('task_prompt.txt', 'w') as f:
    f.write(a)





# print(format_action("debate", {
#     "problem_statement": "here is my problem",
#     "answer": " I think the answer is yes because XYZ"
# }))


# examples, task = get_next_task()

# examples_str = '\n\n'.join([f'Example {i+1}:\n{ex}' for i, ex in enumerate(examples)])

# with open('task_prompt.txt', 'w') as f:
#     f.write(f'{examples_str}\n\n{task}')

# tools = "hey there"

# a = """

# {tools}

# {{
#     "key": "value",
#     "anotha": {{
#         "key2": "val2"
#     }}
# }}

# """

# b = """


# {tools}

# """


# print(a.format(tools=tools))