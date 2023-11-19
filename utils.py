import requests
import json


SUCCESS_OBSERVATION = 'You have successfully completed the task. Please inform the user of this as your Final Answer in your next action.'
FAIL_OBSERVATION = 'You have ran out of moves and are no longer able to complete the task. You failed. Please inform the user of this as your Final Answer in your next action.'

SUCCESS_ANSWER = 'I have successfully completed the task.'
FAIL_ANSWER = 'I have failed to complete the task.'

ENVIRONMENT_ACTION_NAME = 'take_environment_action'
ENVIRONMENT_ACTION_PARAM1 = 'action'
DEBATE_ACTION_NAME = 'view_debate'




def get_next_task():
    url = 'http://localhost:8000/get_next_task'

    response = requests.get(url)
    json_response = response.json()
    examples = json_response.get("examples")
    task = json_response.get("task")

    formatted_examples = [format_prompt(ex) for ex in examples]
    formatted_task = format_prompt(task)

    # add the success observations, along with agent response.
    final_append = f'{SUCCESS_OBSERVATION}\nAction: {format_action("Final Answer", SUCCESS_ANSWER)}'
    formatted_examples = [f'{fex} {final_append}' for fex in formatted_examples]

    return formatted_examples, formatted_task




def format_prompt(prompt):

    lines = prompt.split('\n')
    lines = [l.strip() for l in lines if len(l.strip()) > 0] # strip lines and remove empty lines

    formatted_lines = []

    previous_was_action = False
    previous_was_thought = False
    previous_thought_index = -1
    counter = 0
    for line in lines:

        line_status = None
        new_line = ''
        curr_thought_index = -1
        if line[0] == '>': # these are thought or action lines
            if len(line) >= 8 and line[:8] == '> think:':
                line_status = 'thought'
                curr_thought_index = counter
                new_line = 'Thought: ' + line[8:].strip()
            else:
                line_status = 'action'
                new_line = 'Action: ' + line[1:].strip()
        elif previous_was_action: # these are observations for an action
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

        previous_was_action = line_status == 'action'
        previous_was_thought = line_status == 'thought'


    # now format the actions in some way
    final_lines = []
    for fline in formatted_lines:
        if len(fline) < 7 or fline[:7] != 'Action:':
            final_lines.append(fline)
        else:
            action_str = fline[7:].strip()
            new_action_str = format_action(ENVIRONMENT_ACTION_NAME, {ENVIRONMENT_ACTION_PARAM1: action_str})
            final_lines.append("Action: " + new_action_str)

    final_prompt = '\n'.join(final_lines)

    return final_prompt



def format_action(tool_name, tool_inputs):
    '''
    tool_name is a string. tool_inputs is a dict of (argument_name, argument_value) key/value pairs
    
    currently the values are required to be strings
    '''

    formatted_action = {
        "tool": tool_name,
        "tool_input": tool_inputs
    }

    formatted_action_str = json.dumps(formatted_action, indent=2)

    return f'\n```\n{formatted_action_str}\n```'
    





