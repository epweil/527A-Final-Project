from utils import read_json_file

def get_single_results_stats(results_filename):

    extended_results = read_json_file(results_filename)
    results = extended_results['results']

    system_hint_mod = 1000000000
    if 'debate_params' in extended_results['params']:
        system_hint_mod = extended_results['params']['debate_params']['system_hint_mod']

    description = extended_results['description']

    success_count = 0
    failure_count = 0
    total_tasks = 0

    total_steps = 0
    total_steps_when_success = 0
    total_steps_when_failure = 0

    total_tokens = 0
    total_tokens_when_success = 0

    total_debates = 0
    total_debates_when_success = 0

    number_of_tasks_that_used_debate = 0
    number_of_tasks_that_used_debate_without_hint = 0

    for res in results:
        total_tasks += 1

        success = res['success']
        token_count = res['token_count']
        action_count = res['total_actions']
        debate_count = res['total_debates']

        total_tokens += token_count
        total_steps += action_count
        total_debates += debate_count

        if debate_count > 0:
            number_of_tasks_that_used_debate += 1
            if action_count < system_hint_mod:
                number_of_tasks_that_used_debate_without_hint += 1

        if success:
            success_count += 1
            total_tokens_when_success += token_count
            total_steps_when_success += action_count
            total_debates_when_success += debate_count
        else:
            failure_count += 1
            total_steps_when_failure += action_count


    acc = success_count / total_tasks

    avg_steps = total_steps / total_tasks
    avg_steps_when_success = -1 if success_count == 0 else total_steps_when_success / success_count
    avg_steps_when_failure = -1 if failure_count == 0 else total_steps_when_failure / failure_count

    avg_tokens = total_tokens / total_tasks
    avg_tokens_when_success = -1 if success_count == 0 else total_tokens_when_success / success_count

    avg_debates = total_debates / total_tasks
    avg_debates_when_success = -1 if success_count == 0 else total_debates_when_success / success_count

    res = {
        'Description': description,
        'Accuracy': acc,
        'Total steps': total_steps,
        'Avg steps': avg_steps,
        'Total steps when success': total_steps_when_success,
        'Avg steps when success': avg_steps_when_success,
        'Total steps when failure': total_steps_when_failure,
        'Avg steps when failure': avg_steps_when_failure,
        'Total debates': total_debates,
        'Avg debates': avg_debates,
        'Total debates when success': total_debates_when_success,
        'Avg debates when success': avg_debates_when_success,
        'Total tokens': total_tokens,
        'Avg tokens': avg_tokens,
        'Total tokens when success': total_tokens_when_success,
        'Avg tokens when success': avg_tokens_when_success,
        'Number tasks that used debate': number_of_tasks_that_used_debate,
        'Number tasks that used debate without hint': number_of_tasks_that_used_debate_without_hint
    }

    return res

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
        both_stats[v + '_and_debate'] = 0

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

        b_debate_count = br['total_debates']

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

        if b_debate_count > 0:
            both_stats[helper_dict[(a_success, b_success)] + '_and_debate'] += 1

    return a_stats, b_stats, both_stats




"""
ENTER YOUR TIMESTAMPS IN THE CODE BELOW
"""


if __name__ == '__main__':

    """
    Uncomment if you want to view stats on a single file
    """
    timestamp = '2023-12-05_10-59-54'
    filename = f'./results/{timestamp}/results_{timestamp}.json'
    res_dict = get_single_results_stats(filename)
    print('=====================================================')
    print(timestamp)
    print(res_dict.pop('Description'))
    print('Stats ---')
    for k, v in res_dict.items():
        print(f'  {k} - {v}')


    """
    Uncomment if you want to view stats between 2 files
    """
    # a_timestamp = '2023-12-04_19-52-21'
    # b_timestamp = '2023-12-05_10-59-54'
    # a_filename = f'./results/{a_timestamp}/results_{a_timestamp}.json'
    # b_filename = f'./results/{b_timestamp}/results_{b_timestamp}.json'
    # a_res_dict = get_single_results_stats(a_filename)
    # b_res_dict = get_single_results_stats(b_filename)
    # a_stats, b_stats, both_stats = get_pair_results_stats(a_filename, b_filename)
    #
    # print('=====================================================')
    # print(f'(a) {a_timestamp}')
    # print(f'(a) Description - {a_stats["description"]}')
    # print(f'(a) Success count - {a_stats["success_count"]}, Failure count - {a_stats["failure_count"]}')
    # print('(a) Stats ---')
    # for k, v in a_res_dict.items():
    #     print(f'  {k} - {v}')
    # print(f'(b) {b_timestamp}')
    # print(f'(b) Description - {b_stats["description"]}')
    # print(f'(b) Success count - {b_stats["success_count"]}, Failure count - {b_stats["failure_count"]}')
    # print('(b) Stats ---')
    # for k, v in b_res_dict.items():
    #     print(f'  {k} - {v}')
    # print(f'(BOTH) ---')
    # print(f'(a) {a_timestamp}')
    # print(f'(b) {b_timestamp}')
    # for v in helper_dict.values():
    #     print(f'{v} - {both_stats[v]}')
    # for v in helper_dict.values():
    #     print(f'{v + "_and_debate"} - {both_stats[v + "_and_debate"]}')



