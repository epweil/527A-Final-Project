import requests
import json


SUCCESS_OBSERVATION = 'You have successfully completed the task. Please inform the user of this as your Final Answer. Use the "final_answer" tool.'
FAIL_OBSERVATION = 'You have ran out of moves and are no longer able to complete the task. You failed. Please inform the user of this as your Final Answer. Use the "final_answer" tool.'
SUCCESS_ACTION = 'I have successfully completed the task.'
FAIL_ACTION = 'I have failed to complete the task.'
SUCCESS_THOUGHT = SUCCESS_ACTION + ' I need to inform the user of this fact.'
FAIL_THOUGHT = FAIL_ACTION + ' I need to inform the user of this fact.'

TAKE_ENVIRONMENT_ACTION = 'take_environment_action'
TAKE_ENVIRONMENT_ACTION_PARAM1 = 'action'
VIEW_DEBATE = 'view_debate'
FINAL_ANSWER = 'final_answer'
FINAL_ANSWER_PARAM1 = 'answer'

HINT_AFTER_DEBATE = 'Note: Be aware that AI affirm or AI negative could lie to you. For example, the only valid actions you can take are the ones you have previously seen, such as "go to". Do not try to ask another person for information.'
HINT_AFTER_ACTION = f'Hint: You can use the "{VIEW_DEBATE}" tool to get a better understanding of your situation and best action.'

THOUGHT_PREFIX = 'Thought:'
TOOL_PREFIX = 'Tool:'
OBSERVATION_PREFIX = 'Observation:'


def read_text_file(filename):
    with open(filename, "r") as f:
        text = f.read()
    return text


def read_json_file(filename):
    try:
        with open(filename, 'r') as f:
            obj = json.load(f)
        return obj
    except (json.JSONDecodeError, OSError, FileNotFoundError):
        return None


def write_text_file(filename, text):
    with open(filename, 'w') as f:
        f.write(text)


def write_json_file(filename, obj):
    with open(filename, 'w') as f:
        json.dump(obj, f, indent=2)
        f.flush()


def read_append_write_json(filename, data):
    obj = read_json_file(filename)
    if obj:
        obj.append(data)
        write_json_file(filename, obj)
    else:
        write_json_file(filename, [data])


def get_next_task(max_steps, do_debate=False):
    url = f'http://localhost:8000/get_next_task?max_steps={max_steps}'

    response = requests.get(url)
    json_response = response.json()
    examples = json_response.get("examples")
    task = json_response.get("task")
    task_index = json_response.get("task_index")

    formatted_examples = [format_prompt(ex) for ex in examples]
    formatted_task = format_prompt(task)

    if do_debate:
        formatted_examples = [insert_debates(fex) for fex in formatted_examples]

    # add the success observations, along with agent response.
    t = format_tool(FINAL_ANSWER, {FINAL_ANSWER_PARAM1: SUCCESS_ACTION})
    final_append = f'{SUCCESS_OBSERVATION}\n{THOUGHT_PREFIX} {SUCCESS_THOUGHT}\n{TOOL_PREFIX} {t}'
    formatted_examples = [f'{fex} {final_append}' for fex in formatted_examples]

    return formatted_examples, formatted_task, task_index




def format_prompt(prompt):

    lines = prompt.split('\n')
    lines = [l.strip() for l in lines if len(l.strip()) > 0] # strip lines and remove empty lines

    formatted_lines = []

    previous_was_tool = False
    previous_was_thought = False
    previous_thought_index = -1
    counter = 0
    for line in lines:

        line_status = None
        new_line = ''
        curr_thought_index = -1
        if line[0] == '>': # these are thought or tool lines
            if len(line) >= 8 and line[:8] == '> think:':
                line_status = 'thought'
                curr_thought_index = counter
                new_line = f'{THOUGHT_PREFIX} ' + line[8:].strip()
            else:
                line_status = 'tool'
                new_line = f'{TOOL_PREFIX} ' + line[1:].strip()
        elif previous_was_tool: # these are observations for an tool
            line_status = 'observation'
            new_line = f'{OBSERVATION_PREFIX} ' + line
        elif previous_was_thought: # these are "OK." in response to a thought. We delete these
            continue
        elif "You are in the middle of a room." in line: # we might want to prepend something to this
            new_line = line # right now don't do anything
        else:
            new_line = line


        if line_status == 'thought':
            if previous_was_thought:
                formatted_lines[previous_thought_index] = formatted_lines[previous_thought_index] + ' ' + new_line[8:].strip() # merge the thoughts
                continue
            else:
                previous_thought_index = curr_thought_index

        formatted_lines.append(new_line)
        counter += 1

        previous_was_tool = line_status == 'tool'
        previous_was_thought = line_status == 'thought'


    # now format the tools in some way
    final_lines = []
    len_substring = len(TOOL_PREFIX)
    for fline in formatted_lines:
        if len(fline) < len_substring or fline[:len_substring] != TOOL_PREFIX:
            final_lines.append(fline)
        else:
            tool_str = fline[len_substring:].strip()
            new_tool_str = format_tool(TAKE_ENVIRONMENT_ACTION, {TAKE_ENVIRONMENT_ACTION_PARAM1: tool_str})
            final_lines.append(f"{TOOL_PREFIX} " + new_tool_str)

    final_prompt = '\n'.join(final_lines)

    return final_prompt



def format_tool(tool_name, tool_inputs):
    '''
    tool_name is a string. tool_inputs is a dict of (argument_name, argument_value) key/value pairs
    
    currently the values are required to be strings
    '''

    formatted_tool = {
        "tool": tool_name,
        "tool_input": tool_inputs
    }

    formatted_tool_str = json.dumps(formatted_tool, indent=2)

    return f'\n```\n{formatted_tool_str}\n```'
    

def insert_debates(example):
    # 'example' is assumed to be a formatted example in string form

    len_substring = len(TOOL_PREFIX)
    lines = example.split('\n')
    tool_indices = [i for i, line in enumerate(lines) if TOOL_PREFIX == line[:len_substring]]

    with open("./prompts/placeholder_debate_example.txt", "r") as f:
        debate_example = f.read()

    for index in sorted(tool_indices, reverse=True):
        len_thought_prefix = len(THOUGHT_PREFIX)
        if lines[index - 1][:len_thought_prefix] == THOUGHT_PREFIX:
            lines[index - 1] = lines[index - 1] + f'{debate_example[len_thought_prefix:]}'
        else:
            lines.insert(index, debate_example)

    return '\n'.join(lines)



