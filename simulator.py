from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import yaml
import alfworld
import alfworld.agents.environment
import os
from urllib.parse import urlparse, parse_qs
#!/opt/conda/bin/python

class Simulator():

    MAX_STEPS = 10
    MAX_RESETS = 134

    alfworld_root = os.environ['ALFWORLD_ROOT']
    alfworld_data = os.environ['ALFWORLD_DATA']
    react_root = os.environ['REACT_ROOT']

    split = "eval_out_of_distribution"

    total_steps = 0
    total_resets = 0
    finished = False
    env = None
    example_prompts = None

    with open(f'{react_root}base_config.yaml') as reader:
        config = yaml.safe_load(reader)
    env = getattr(alfworld.agents.environment, config["env"]["type"])(config, train_eval=split)
    env = env.init_env(batch_size=1)

    folder = f'{react_root}prompts/'
    prompt_file = 'alfworld_3prompts.json'
    with open(folder + prompt_file, 'r') as f:
        example_prompts = json.load(f)

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


    def __init__(self):
        if Simulator.env is None:
            self.init_env()

        if Simulator.example_prompts is None:
            self.init_example_prompts()

    def init_env(self):
        Simulator.total_resets = 0
        Simulator.finished = False

        with open(f'{Simulator.react_root}base_config.yaml') as reader:
            config = yaml.safe_load(reader)
        _env = getattr(alfworld.agents.environment, config["env"]["type"])(config, train_eval=Simulator.split)
        _env = _env.init_env(batch_size=1)

        Simulator.env = _env

    def init_example_prompts(self):
        folder = f'{Simulator.react_root}prompts/'
        prompt_file = 'alfworld_3prompts.json'
        with open(folder + prompt_file, 'r') as f:
            _example_prompts = json.load(f)

        Simulator.example_prompts = _example_prompts

    def process_ob(self, ob):
        if ob.startswith('You arrive at loc '):
            ob = ob[ob.find('. ')+2:]    
        return ob
    
    def reset(self, max_steps):

        if Simulator.total_resets >= Simulator.MAX_RESETS:
            self.init_env()

        Simulator.total_steps = 0
        Simulator.total_resets += 1
        Simulator.finished = False
        Simulator.MAX_STEPS = max_steps

        ob, info = Simulator.env.reset()
        ob = '\n'.join(ob[0].split('\n\n')[1:])
        name = '/'.join(info['extra.gamefile'][0].split('/')[-3:-1])
        examples = []
        for _, (k, v) in enumerate(Simulator.prefixes.items()):
            if name.startswith(k):
                examples = [
                    Simulator.example_prompts[f'react_{v}_1'],
                    Simulator.example_prompts[f'react_{v}_0']
                ]
                break
        
        return examples, ob

    def step(self, action):

        Simulator.total_steps += 1

        observation, reward, done, info = Simulator.env.step([action])
        observation, reward, done = self.process_ob(observation[0]), info['won'][0], done[0]

        # TODO might want to handle "Think: ..." actions

        if Simulator.total_steps >= Simulator.MAX_STEPS:
            done = True

        if done:
            Simulator.finished = True

        return observation, reward, done
    
    def is_finished(self):
        return Simulator.finished




class Handler(BaseHTTPRequestHandler):
    
    # State variable
    simulator = Simulator()

    def do_GET(self):

        parsed_url = urlparse(self.path)
        query_params = parse_qs(parsed_url.query)

        if parsed_url.path == '/get_next_task':

            max_steps = int(query_params.get('max_steps', [10])[0])

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()

            examples, task = Handler.simulator.reset(max_steps=max_steps)
            response_data = {
                "examples": examples,
                "task": task,
                "task_index": Handler.simulator.total_resets
            }
            response_data = json.dumps(response_data)
            self.wfile.write(response_data.encode('utf-8'))

            print(f'Task: {task}')
        elif parsed_url.path == '/reset_tasks':
            Handler.simulator.init_env()
            print('Reset tasks!')
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
        else:
            self.send_response(404)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()

            response = '404 Not Found'
            self.wfile.write(response.encode('utf-8'))

    def do_POST(self):
        if self.path == '/take_action':


            if Handler.simulator.is_finished():
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.end_headers()

                response_data = {
                    'observation': None,
                    'reward': None,
                    'done': None,
                    'message': 'You have exceeded the maximum number of allowed steps. Please try a new task.',
                }
                response_data = json.dumps(response_data)
                self.wfile.write(response_data.encode('utf-8'))
            else:

                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data.decode('utf-8'))

                action = data.get('action', None)

                if action is not None:
                    observation, reward, done = Handler.simulator.step(action)

                    response_data = {
                        'observation': observation,
                        'reward': reward,
                        'done': done,
                        'message': None,
                    }
                    response_data = json.dumps(response_data)
                    if done and not reward:
                        self.send_response(400)
                    else:
                        self.send_response(200)

                    self.send_header('Content-type', 'application/json')
                    self.end_headers()

                    self.wfile.write(response_data.encode('utf-8'))

                    print(f'Action: {action}')
                    print(f'Observation: {observation}')
                else:
                    self.send_response(400)
                    self.send_header('Content-type', 'text/plain')
                    self.end_headers()

                    response = '400 Bad Request: Missing "action" parameter'
                    self.wfile.write(response.encode('utf-8'))
        else:
            self.send_response(404)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()

            response = '404 Not Found'
            self.wfile.write(response.encode('utf-8'))

def run_server(port=8000):
    server_address = ('', port)
    httpd = HTTPServer(server_address, Handler)
    print(f'Starting server on port {port}...')
    httpd.serve_forever()

if __name__ == '__main__':
    run_server()
