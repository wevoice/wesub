import pygal
from pygal.style import Style
import base64
import logging

logger = logging.getLogger("Graphs")

def plot(data, title=None, graph_type='Pie'):

    custom_style = Style(
        background='transparent',
        plot_background='transparent',
        foreground='FFFFFF',
        foreground_light='black',
        foreground_dark='#FFFFFF',
        opacity='.9',
        opacity_hover='.5',
        transition='400ms ease-in',
        colors=('#4d4d4d', '#5da5da', '#faa43a', '#60bd68', '#f17cb0', '#b2912f', '#b276b2', '#decf3f', '#f15854'))
    if graph_type == 'Pie':
        pie_chart = pygal.Pie(style=custom_style, inner_radius=.4)
    else:
        pie_chart = pygal.HorizontalBar(style=custom_style)
    if title:
        pie_chart.title = title
    data.sort(reverse=True, key=lambda x:x[1])
    for item in data:
        pie_chart.add(item[0], [{'value': item[1], 'label': item[0]}])
    return base64.b64encode(pie_chart.render())
