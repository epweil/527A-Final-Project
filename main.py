import vertexai
import json
from agent import run_experiment

"""
This file is where you define the experiments you want to run.
"""

PROJECT_ID = 'gen-lang-client-0382320190' # insert your own project id here
LOCATION = 'us-central1'
vertexai.init(project=PROJECT_ID, location=LOCATION)

"""
Define global parameters to use for all experiments
"""

MAX_STEPS = 3
agent_model = 'text-bison-32k'
debate_model = 'text-bison-32k'
langchain_debug = False
langchain_verbose = False
start_task = 1
num_tasks = 2 # 134 is maximum


"""
Define specific experiments
"""

experiments = [
    {
        'description': 'The baseline ReAct agent.',
        'do_debate': False,
        'MAX_VOTES': 1,
        'agent_temperature': 0,
        'MAX_STEPS': MAX_STEPS,
        'agent_model': agent_model,
        'num_tasks': num_tasks,
        'start_task': start_task,
        'langchain.debug': langchain_debug,
        'langchain_verbose': langchain_verbose,
    },

    {
        'description': 'The baseline majority vote agent.',
        'do_debate': False,
        'MAX_VOTES': 5,
        'MAX_STEPS': MAX_STEPS,
        'agent_model': agent_model,
        'num_tasks': num_tasks,
        'start_task': start_task,
        'langchain.debug': langchain_debug,
        'langchain_verbose': langchain_verbose,
    },

    {
        'description': 'A debate agent, nothing special. Default settings.',
        'do_debate': True,
        'MAX_VOTES': 1,
        'MAX_STEPS': MAX_STEPS,
        'agent_model': agent_model,
        'num_tasks': num_tasks,
        'start_task': start_task,
        'langchain.debug': langchain_debug,
        'langchain_verbose': langchain_verbose,
        'debate_params': {
            "total_iters": 2,
            "negative_first": False,
            "model": debate_model,
            "system_hint_mod": 15,
        }
    },

]

results_info = []

for experiment_index, experiment in enumerate(experiments):
    print("#######################################################################")
    print(f"Experiment {experiment_index} - {experiment['description']}")
    print("Parameters -")
    print(json.dumps(experiment, indent=2))

    timestamp, results_filename = run_experiment(experiment)
    results_info.append((timestamp, results_filename))
    print(f"Results - {results_filename}")

print('+++++++++++++++++++++++++++++++++++++++++++++++++++')
print(f'Done running experiments - {results_info}')
















