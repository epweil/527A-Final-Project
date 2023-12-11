import vertexai
import json
from agent import run_experiment
from utils import PROJECT_ID, LOCATION

"""
This file is where you define the experiments you want to run.
"""

vertexai.init(project=PROJECT_ID, location=LOCATION)

"""
Define global parameters to use for all experiments
"""

MAX_STEPS = 30
agent_model = 'text-bison-32k'
debate_model = 'text-bison-32k'
langchain_debug = False
langchain_verbose = False
start_task = 1
num_tasks = 134 # 134 is maximum


"""
Define specific experiments
"""

experiments = [

    # JAKE RUN BELOW


    # {
    #     'description': 'The baseline ReAct agent. palm tokenizer',
    #     'do_debate': False,
    #     'MAX_VOTES': 1,
    #     'MAX_STEPS': MAX_STEPS,
    #     'agent_model': agent_model,
    #     'num_tasks': num_tasks,
    #     'start_task': start_task,
    #     'langchain.debug': langchain_debug,
    #     'langchain_verbose': langchain_verbose,
    # },

    # {
    #     'description': 'The baseline majority vote agent. palm tokenizer',
    #     'do_debate': False,
    #     'MAX_VOTES': 5,
    #     'MAX_STEPS': MAX_STEPS,
    #     'agent_model': agent_model,
    #     'num_tasks': num_tasks - 56 + 1,
    #     'start_task': 56,
    #     'langchain.debug': langchain_debug,
    #     'langchain_verbose': langchain_verbose,
    # },

    # {
    #     'description': 'A debate agent. 2 iters. affirm start. hint_mod=15. palm tokenizer',
    #     'do_debate': True,
    #     'MAX_VOTES': 1,
    #     'MAX_STEPS': MAX_STEPS,
    #     'agent_model': agent_model,
    #     'num_tasks': num_tasks,
    #     'start_task': start_task,
    #     'langchain.debug': langchain_debug,
    #     'langchain_verbose': langchain_verbose,
    #     'debate_params': {
    #         "total_iters": 2,
    #         "negative_first": False,
    #         "model": debate_model,
    #         "system_hint_mod": 15,
    #     }
    # },
    #
    # {
    #     'description': 'A debate agent. 2 iters. negative start. hint_mod=15. palm tokenizer',
    #     'do_debate': True,
    #     'MAX_VOTES': 1,
    #     'MAX_STEPS': MAX_STEPS,
    #     'agent_model': agent_model,
    #     'num_tasks': num_tasks,
    #     'start_task': start_task,
    #     'langchain.debug': langchain_debug,
    #     'langchain_verbose': langchain_verbose,
    #     'debate_params': {
    #         "total_iters": 2,
    #         "negative_first": True,
    #         "model": debate_model,
    #         "system_hint_mod": 15,
    #     }
    # },
    #
    # {
    #     'description': 'A debate agent. 2 iters. affirm start. hint_mod=5. palm tokenizer',
    #     'do_debate': True,
    #     'MAX_VOTES': 1,
    #     'MAX_STEPS': MAX_STEPS,
    #     'agent_model': agent_model,
    #     'num_tasks': num_tasks,
    #     'start_task': start_task,
    #     'langchain.debug': langchain_debug,
    #     'langchain_verbose': langchain_verbose,
    #     'debate_params': {
    #         "total_iters": 2,
    #         "negative_first": False,
    #         "model": debate_model,
    #         "system_hint_mod": 5,
    #     }
    # },
    #
    # {
    #     'description': 'A debate agent. 2 iters. negative start. hint_mod=5. palm tokenizer',
    #     'do_debate': True,
    #     'MAX_VOTES': 1,
    #     'MAX_STEPS': MAX_STEPS,
    #     'agent_model': agent_model,
    #     'num_tasks': num_tasks,
    #     'start_task': start_task,
    #     'langchain.debug': langchain_debug,
    #     'langchain_verbose': langchain_verbose,
    #     'debate_params': {
    #         "total_iters": 2,
    #         "negative_first": True,
    #         "model": debate_model,
    #         "system_hint_mod": 5,
    #     }
    # },


    # ETHAN RUN BELOW


    # {
    #     'description': 'A debate agent. 2 iters. affirm start. hint_mod=1000. palm tokenizer',
    #     'do_debate': True,
    #     'MAX_VOTES': 1,
    #     'MAX_STEPS': MAX_STEPS,
    #     'agent_model': agent_model,
    #     'num_tasks': num_tasks,
    #     'start_task': start_task,
    #     'langchain.debug': langchain_debug,
    #     'langchain_verbose': langchain_verbose,
    #     'debate_params': {
    #         "total_iters": 2,
    #         "negative_first": False,
    #         "model": debate_model,
    #         "system_hint_mod": 1000,
    #     }
    # },
    # 
    # {
    #     'description': 'A debate agent. 3 iters. affirm start. hint_mod=15. palm tokenizer',
    #     'do_debate': True,
    #     'MAX_VOTES': 1,
    #     'MAX_STEPS': MAX_STEPS,
    #     'agent_model': agent_model,
    #     'num_tasks': num_tasks,
    #     'start_task': start_task,
    #     'langchain.debug': langchain_debug,
    #     'langchain_verbose': langchain_verbose,
    #     'debate_params': {
    #         "total_iters": 3,
    #         "negative_first": False,
    #         "model": debate_model,
    #         "system_hint_mod": 15,
    #     }
    # },
    # 
    # {
    #     'description': 'A debate agent. 4 iters. affirm start. hint_mod=15. palm tokenizer',
    #     'do_debate': True,
    #     'MAX_VOTES': 1,
    #     'MAX_STEPS': MAX_STEPS,
    #     'agent_model': agent_model,
    #     'num_tasks': num_tasks,
    #     'start_task': start_task,
    #     'langchain.debug': langchain_debug,
    #     'langchain_verbose': langchain_verbose,
    #     'debate_params': {
    #         "total_iters": 4,
    #         "negative_first": False,
    #         "model": debate_model,
    #         "system_hint_mod": 15,
    #     }
    # },
    # 
    {
        'description': 'A debate agent. 5 iters. affirm start. hint_mod=15. palm tokenizer',
        'do_debate': True,
        'MAX_VOTES': 1,
        'MAX_STEPS': MAX_STEPS,
        'agent_model': agent_model,
        'num_tasks': num_tasks,
        'start_task': start_task,
        'langchain.debug': langchain_debug,
        'langchain_verbose': langchain_verbose,
        'debate_params': {
            "total_iters": 5,
            "negative_first": False,
            "model": debate_model,
            "system_hint_mod": 15,
        }
    },


    # ZHUOBING RUN BELOW

    # {
    #     'description': 'A debate agent. 2 iters. negative start. hint_mod=1000. palm tokenizer',
    #     'do_debate': True,
    #     'MAX_VOTES': 1,
    #     'MAX_STEPS': MAX_STEPS,
    #     'agent_model': agent_model,
    #     'num_tasks': num_tasks,
    #     'start_task': start_task,
    #     'langchain.debug': langchain_debug,
    #     'langchain_verbose': langchain_verbose,
    #     'debate_params': {
    #         "total_iters": 2,
    #         "negative_first": True,
    #         "model": debate_model,
    #         "system_hint_mod": 1000,
    #     }
    # },
    # 
    # {
    #     'description': 'A debate agent. 3 iters. negative start. hint_mod=15. palm tokenizer',
    #     'do_debate': True,
    #     'MAX_VOTES': 1,
    #     'MAX_STEPS': MAX_STEPS,
    #     'agent_model': agent_model,
    #     'num_tasks': num_tasks,
    #     'start_task': start_task,
    #     'langchain.debug': langchain_debug,
    #     'langchain_verbose': langchain_verbose,
    #     'debate_params': {
    #         "total_iters": 3,
    #         "negative_first": True,
    #         "model": debate_model,
    #         "system_hint_mod": 15,
    #     }
    # },
    # 
    # {
    #     'description': 'A debate agent. 4 iters. negative start. hint_mod=15. palm tokenizer',
    #     'do_debate': True,
    #     'MAX_VOTES': 1,
    #     'MAX_STEPS': MAX_STEPS,
    #     'agent_model': agent_model,
    #     'num_tasks': num_tasks,
    #     'start_task': start_task,
    #     'langchain.debug': langchain_debug,
    #     'langchain_verbose': langchain_verbose,
    #     'debate_params': {
    #         "total_iters": 4,
    #         "negative_first": True,
    #         "model": debate_model,
    #         "system_hint_mod": 15,
    #     }
    # },
    # 
    {
        'description': 'A debate agent. 5 iters. negative start. hint_mod=15. palm tokenizer',
        'do_debate': True,
        'MAX_VOTES': 1,
        'MAX_STEPS': MAX_STEPS,
        'agent_model': agent_model,
        'num_tasks': num_tasks,
        'start_task': start_task,
        'langchain.debug': langchain_debug,
        'langchain_verbose': langchain_verbose,
        'debate_params': {
            "total_iters": 5,
            "negative_first": True,
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
















