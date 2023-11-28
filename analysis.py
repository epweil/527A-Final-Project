from utils import read_json_file

results_filename = './results/results_2023-11-27_19-08-25.json'

results = read_json_file(results_filename)

success_count = 0
total_steps_when_success = 0
total_tasks = 0

for res in results:
    total_tasks += 1
    success = res['success']
    total_actions = res['total_actions']
    if success:
        success_count += 1
        total_steps_when_success += total_actions

print(f'accuracy={success_count/total_tasks}, avg_actions_when_success={total_steps_when_success / success_count}')