import requests


def get_next_task():
    url = 'http://localhost:8000/get_next_task'

    response = requests.get(url)
    json_response = response.json()
    observation = json_response.get("prompt_and_observation")

    formatted_observation = format_prompt(observation)

    return formatted_observation




def format_prompt(base_prompt):

    lines = base_prompt.split('\n')[:-1] # get rid of last >
    lines = [l.strip() for l in lines if len(l.strip()) > 0]

    formatted_lines = []

    previous_was_action = False
    previous_was_thought = False
    previous_thought_index = -1
    counter = 0
    for i, line in enumerate(lines):

        line_status = None
        new_line = ''
        curr_thought_index = -1
        if line[0] == '>':
            if len(line) >= 8 and line[:8] == '> think:':
                line_status = 'thought'
                curr_thought_index = counter
                new_line = 'Thought: ' + line[8:].strip()
            else:
                line_status = 'action'
                new_line = 'Action: ' + line[1:].strip()
        elif previous_was_action:
            line_status = 'observation'
            new_line = 'Observation: ' + line
        elif previous_was_thought:
            new_line = ''
        else:
            new_line = line


        if line_status == 'thought' and previous_was_thought:
            formatted_lines[previous_thought_index] = formatted_lines[previous_thought_index] + new_line[8:] # remove the "Thought:"
        elif new_line != '':
            if line_status == 'thought':
                previous_thought_index = curr_thought_index
            formatted_lines.append(new_line)
            counter += 1
        else:
            continue


        previous_was_action = line_status == 'action'
        previous_was_thought = line_status == 'thought'


    # now format the actions
    final_lines = []
    for fline in formatted_lines:
        if len(fline) < 7 or fline[:7] != 'Action:':
            final_lines.append(fline)
        else:
            action_str = fline[7:].strip()
            lc = '{'
            rc = '}'
            new_action_str = f'\n```\n{lc}\n  "action": "take_environment_action",\n  "action_input": "{action_str}"\n{rc}\n```'
            final_lines.append("Action: " + new_action_str)

    final_prompt = '\n'.join(final_lines)

    return final_prompt


