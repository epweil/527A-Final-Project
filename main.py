

alfworld_root = "/opt/alfworld/"
react_root = "/opt/ReAct/"

import os
os.environ['ALFWORLD_ROOT'] = '/opt/alfworld'
os.environ['ALFWORLD_DATA'] = '/opt/alfworld/data'
# print("ALFWORLD_ROOT:", os.getenv("ALFWORLD_ROOT"))
# print("ALFWORLD_DATA:", os.getenv("ALFWORLD_DATA"))



#################################################################################



import os
import openai
 
openai.api_key = "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"

def llm(prompt, stop=["\n"]):
    # response = openai.Completion.create(
    #   model="text-davinci-002",
    #   prompt=prompt,
    #   temperature=0,
    #   max_tokens=100,
    #   top_p=1,
    #   frequency_penalty=0.0,
    #   presence_penalty=0.0,
    #   stop=stop
    # )
    # return response["choices"][0]["text"]

    return "Hi, my name is Jake!"



#################################################################################



import yaml
import alfworld
import alfworld.agents.environment
with open(f'{react_root}base_config.yaml') as reader:
    config = yaml.safe_load(reader)
    
split = "eval_out_of_distribution"

env = getattr(alfworld.agents.environment, config["env"]["type"])(config, train_eval=split)
env = env.init_env(batch_size=1)

def process_ob(ob):
    if ob.startswith('You arrive at loc '):
        ob = ob[ob.find('. ')+2:]    
    return ob



#################################################################################



import json
folder = f'{react_root}prompts/'
prompt_file = 'alfworld_3prompts.json'
with open(folder + prompt_file, 'r') as f:
    d = json.load(f)



#################################################################################



import sys

def alfworld_run(prompt, to_print=True, ob=''):
    init_prompt = prompt + ob + '\n>'
    prompt = ''
    if to_print:
        print(ob)
        sys.stdout.flush()
    for i in range(1, 50):
        action = llm(init_prompt + prompt, stop=['\n']).strip()
        observation, reward, done, info = env.step([action])
        observation, reward, done = process_ob(observation[0]), info['won'][0], done[0]
        if action.startswith('think:'):
            observation = 'OK.'
        if to_print:
            print(f'Act {i}: {action}\nObs {i}: {observation}')
            sys.stdout.flush()
        prompt += f' {action}\n{observation}\n>'
        if done:
            return reward
    return 0



#################################################################################



prefixes = {
    'pick_and_place': 'put',
    'pick_clean_then_place': 'clean',
    'pick_heat_then_place': 'heat',
    'pick_cool_then_place': 'cool',
    'look_at_obj': 'examine',
    'pick_two_obj': 'puttwo'
}
cnts = [0] * 6
rs = [0] * 6

for _ in range(134):
    ob, info = env.reset()
    ob = '\n'.join(ob[0].split('\n\n')[1:])
    name = '/'.join(info['extra.gamefile'][0].split('/')[-3:-1])
    print(name)
    for i, (k, v) in enumerate(prefixes.items()):
        if name.startswith(k):
            prompt = 'Interact with a household to solve a task. Here are two examples.\n' + d[f'react_{v}_1'] + d[f'react_{v}_0'] + '\nHere is the task.\n'
            print(k, v)
            r = alfworld_run(prompt, ob=ob)
            rs[i] += r
            cnts[i] += 1
            break
    print(_+1, 'r', r, 'rs', rs, 'cnts', cnts, 'sum(rs)/sum(cnts)', sum(rs) / sum(cnts))
    print('------------\n')