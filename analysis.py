from utils import read_json_file

results_filename = './results/results_2023-11-28_11-36-44.json'

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






fna = './results/results_2023-11-27_19-08-25.json'
fnb = './results/results_2023-11-27_22-44-13.json'

a = read_json_file(fna)
b = read_json_file(fnb)
count = 0
afalse_count = 0
tfalse_count = 0
for i, _ in enumerate(a):
    asucc = a[i]['success']
    bsucc = b[i]['success']

    if not asucc:
        tfalse_count += 1

    if asucc != bsucc:
        if not asucc:
            afalse_count += 1
        count += 1
        print(i + 1, asucc)
print(count)
print('total false', afalse_count)
print('total false when not matching', tfalse_count)