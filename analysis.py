from utils import read_json_file

def get_single_results_stats(results_filename):

    extended_results = read_json_file(results_filename)
    results = extended_results['results']

    success_count = 0
    total_steps_when_success = 0
    total_tasks = 0
    total_tokens = 0

    for res in results:
        total_tasks += 1
        total_tokens += res['token_count']
        success = res['success']
        total_actions = res['total_actions']
        if success:
            success_count += 1
            total_steps_when_success += total_actions

    acc = success_count / total_tasks
    avg_steps_when_success = -1 if success_count == 0 else total_steps_when_success / success_count
    avg_tokens = total_tokens / total_tasks

    return acc, avg_steps_when_success, total_tokens, avg_tokens, total_tasks, success_count


helper_dict = {
    (True, False): 'a_success_b_failure_count',
    (False, True): 'a_failure_b_success_count',
    (True, True): 'a_success_b_success_count',
    (False, False): 'a_failure_b_failure_count'
}


def get_pair_results_stats(fna, fnb):

    a_stats = dict()
    b_stats = dict()
    both_stats = dict()
    for stats in [a_stats, b_stats]:
        stats['success_count'] = 0
        stats['failure_count'] = 0

    for v in helper_dict.values():
        both_stats[v] = 0

    both_stats['task_index_to_a_b'] = dict()

    a_ext_res = read_json_file(fna)
    b_ext_res = read_json_file(fnb)

    a_stats['timestamp'] = a_ext_res['timestamp']
    a_stats['description'] = a_ext_res['description']
    b_stats['timestamp'] = b_ext_res['timestamp']
    b_stats['description'] = b_ext_res['description']

    a_res = a_ext_res['results']
    b_res = b_ext_res['results']

    if len(a_res) != len(b_res):
        raise Exception('Cannot compare results of different sizes.')

    for ar, br in zip(a_res, b_res):
        a_task_index = ar['task_index']
        b_task_index = br['task_index']
        assert a_task_index == b_task_index
        a_success = ar['success']
        b_success = br['success']

        if a_success:
            a_stats['success_count'] += 1
        else:
            a_stats['failure_count'] += 1

        if b_success:
            b_stats['success_count'] += 1
        else:
            b_stats['failure_count'] += 1

        both_stats['task_index_to_a_b'][a_task_index] = (a_success, b_success)
        both_stats[helper_dict[(a_success, b_success)]] += 1

    return a_stats, b_stats, both_stats




"""
ENTER YOUR TIMESTAMPS IN THE CODE BELOW
"""


if __name__ == '__main__':

    """
    Uncomment if you want to view stats on a single file
    """
    timestamp = '2023-12-04_09-04-02'
    filename = f'./results/{timestamp}/results_{timestamp}.json'
    accuracy, avg_steps, total_tokens, avg_tokens, total_tasks, success_count = get_single_results_stats(filename)
    print('=====================================================')
    print(timestamp)
    print(f'Accuracy - {accuracy}, Avg steps - {avg_steps}, Total tokens - {total_tokens}, Avg tokens - {avg_tokens}, Total tasks - {total_tasks}, Success count - {success_count}')


    """
    Uncomment if you want to view stats between 2 files
    """
    a_timestamp = '2023-12-04_09-04-02'
    b_timestamp = '2023-12-04_09-04-40'
    a_filename = f'./results/{a_timestamp}/results_{a_timestamp}.json'
    b_filename = f'./results/{b_timestamp}/results_{b_timestamp}.json'
    a_accuracy, a_avg_steps, a_total_tokens, a_avg_tokens, a_total_tasks, _ = get_single_results_stats(a_filename)
    b_accuracy, b_avg_steps, b_total_tokens, b_avg_tokens, b_total_tasks, _ = get_single_results_stats(b_filename)
    a_stats, b_stats, both_stats = get_pair_results_stats(a_filename, b_filename)

    print('=====================================================')
    print(f'(a) {timestamp}')
    print(f'(a) Description - {a_stats["description"]}')
    print(f'(a) Success count - {a_stats["success_count"]}, Failure count - {a_stats["failure_count"]}')
    print(f'(a) Accuracy - {a_accuracy}, Avg steps - {a_avg_steps}, Total tokens - {a_total_tokens}, Avg tokens - {a_avg_tokens}, Total tasks - {a_total_tasks}')
    print(f'(b) {timestamp}')
    print(f'(b) Description - {b_stats["description"]}')
    print(f'(b) Success count - {b_stats["success_count"]}, Failure count - {b_stats["failure_count"]}')
    print(f'(b) Accuracy - {b_accuracy}, Avg steps - {b_avg_steps}, Total tokens - {b_total_tokens}, Avg tokens - {b_avg_tokens}, Total tasks - {b_total_tasks}')
    print(f'(BOTH) ---')
    for v in helper_dict.values():
        print(f'{v} - {both_stats[v]}')



