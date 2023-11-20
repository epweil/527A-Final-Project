import requests
import json


SUCCESS_OBSERVATION = 'You have successfully completed the task. Please inform the user of this as your Final Answer. Use the "final_answer" tool.'
FAIL_OBSERVATION = 'You have ran out of moves and are no longer able to complete the task. You failed. Please inform the user of this as your Final Answer. Use the "final_answer" tool.'
SUCCESS_ACTION = 'I have successfully completed the task.'
FAIL_ACTION = 'I have failed to complete the task.'
SUCCESS_THOUGHT = SUCCESS_ACTION + ' I need to inform the user of this fact.'
FAIL_THOUGHT = FAIL_ACTION + ' I need to inform the user of this fact.'

ENVIRONMENT_ACTION_NAME = 'take_environment_action'
ENVIRONMENT_ACTION_PARAM1 = 'action'
DEBATE_ACTION_NAME = 'view_debate'


class SafeDict(dict):
    def __missing__(self, key):
        return '{' + key + '}'


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
    final_append = f'{SUCCESS_OBSERVATION}\nThought: {SUCCESS_THOUGHT}\nTool: {format_tool("final_answer", {"answer": SUCCESS_ACTION})}'
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
                new_line = 'Thought: ' + line[8:].strip()
            else:
                line_status = 'tool'
                new_line = 'Tool: ' + line[1:].strip()
        elif previous_was_tool: # these are observations for an tool
            line_status = 'observation'
            new_line = 'Observation: ' + line
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
    len_substring = len('Tool:')
    for fline in formatted_lines:
        if len(fline) < len_substring or fline[:len_substring] != 'Tool:':
            final_lines.append(fline)
        else:
            tool_str = fline[len_substring:].strip()
            new_tool_str = format_tool(ENVIRONMENT_ACTION_NAME, {ENVIRONMENT_ACTION_PARAM1: tool_str})
            final_lines.append("Tool: " + new_tool_str)

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

    len_substring = len('Tool:')
    lines = example.split('\n')
    tool_indices = [i for i, line in enumerate(lines) if 'Tool:' == line[:len_substring]]

    with open("./prompts/placeholder_debate_example.txt", "r") as f:
        debate_example = f.read()

    for index in sorted(tool_indices, reverse=True):
        if lines[index - 1][:8] == 'Thought:':
            lines[index - 1] = lines[index - 1] + f'{debate_example[8:]}'
        else:
            lines.insert(index, debate_example)

    return '\n'.join(lines)



