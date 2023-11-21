"""


This ran palm (text-bison-32k) on all 134 tasks.
with_ was with debate, with a hint every other action (i.e. action_count % 2 == 0).
without was without debate, i.e., the default ReAct agent

In both cases, they got 20 maximum number of iterations.

"""

import json


def read_json_file(filename):
    try:
        with open(filename, 'r') as f:
            obj = json.load(f)
        return obj
    except (json.JSONDecodeError, OSError, FileNotFoundError):
        return None



with_filename = 'with_results_2023-11-21_12-55-42.json'
without_filename = 'without_results_2023-11-21_07-09-36.json'


with_results = read_json_file(with_filename)
without_results = read_json_file(without_filename)


with_success_count = 0
with_total_steps_when_success = 0

without_success_count = 0
without_total_steps_when_success = 0

for with_res in with_results:
    success = with_res['success']
    total_actions = with_res['total_actions']
    if success:
        with_success_count += 1
        with_total_steps_when_success += total_actions

print(f'with_accuracy={with_success_count/134}, with_avg_actions={with_total_steps_when_success / with_success_count}')

for without_res in without_results:
    success = without_res['success']
    total_actions = without_res['total_actions']
    if success:
        without_success_count += 1
        without_total_steps_when_success += total_actions

print(f'without_accuracy={without_success_count/134}, without_avg_actions={without_total_steps_when_success / without_success_count}')