
from utils import *

# print(format_action("debate", {
#     "problem_statement": "here is my problem",
#     "answer": " I think the answer is yes because XYZ"
# }))


examples, task = get_next_task()

examples_str = '\n\n'.join([f'Example {i+1}:\n{ex}' for i, ex in enumerate(examples)])

with open('task_prompt.txt', 'w') as f:
    f.write(f'{examples_str}\n\n{task}')