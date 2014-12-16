import pygal
from pygal.style import Style
import base64
import logging

logger = logging.getLogger("Graphs")

def plot(data, title=None, graph_type='Pie', max_entries=None, other_label="Other", y_title=None, labels=False):
    logger.error(data)
    custom_style = Style(
        background='transparent',
        font_family='sans-serif',
        plot_background='transparent',
        foreground='FFFFFF',
        foreground_light='black',
        foreground_dark='#FFFFFF',
        opacity='.9',
        opacity_hover='.5',
        transition='400ms ease-in',
        colors=('#4d4d4d', '#5da5da', '#faa43a', '#60bd68', '#f17cb0', '#b2912f', '#b276b2', '#decf3f', '#f15854'))
    data.sort(reverse=True, key=lambda x:x[1])
    if graph_type == 'Pie':
        chart = pygal.Pie(style=custom_style, inner_radius=.4)
    else:
        chart = pygal.HorizontalBar(style=custom_style)
        if data:
            chart.y_labels = map(repr, range(data[len(data)-1][1] - 1, data[0][1] + 1))
            chart.value_formatter = lambda x: str(int(x))
    if title:
        chart.title = title
    data.sort(key=lambda x:x[1])
    if max_entries and (len(data) > max_entries):
        cut = len(data) - max_entries
        remaining_data = reduce(lambda x, y: ('',x[1]+y[1]), data[:cut])
        data = data[cut:]
        data.insert(0,(other_label,  remaining_data[1], 'Other'))
    for item in data:
        if labels:
            chart.add(item[0], [{'value': item[1], 'label': item[2]}])
        else:
            chart.add(item[0], [{'value': item[1], 'label': item[0]}])
    if y_title:
        chart.y_title = y_title
    return base64.b64encode(chart.render())
