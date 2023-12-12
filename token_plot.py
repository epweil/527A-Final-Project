import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

data = [('ReAct', 43), ('Self-consistency', 212), ('Debate (ours)', 95)]

# Extracting labels and values
labels, values = zip(*data)

# Converting values from thousands to actual values
values = [v * 1000 for v in values]

custom_color = '#0059ff'

# Creating the bar graph
plt.bar(labels, values, color=custom_color)

# Adding labels and title
plt.xlabel('Agents', fontsize=14, labelpad=10)
plt.ylabel('Tokens', fontsize=14)
# plt.title('Average Tokens Used per Task', fontsize=16)

# Function to format y-axis labels with 'k'
def format_func(value, tick_number):
    if value == 0:
        return "0"
    return f'{int(value/1000)}k'

# Apply the custom formatter to the y-axis ticks
plt.gca().yaxis.set_major_formatter(FuncFormatter(format_func))

plt.yticks(fontsize=12)
plt.xticks(fontsize=12)

# Adjusting layout to prevent y-axis label cutoff
plt.tight_layout()

plt.savefig('agent_tokens.png', dpi=1000)

# Displaying the bar graph
plt.show()