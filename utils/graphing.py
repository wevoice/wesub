import pygal
from pygal.style import LightGreenStyle
import base64
import logging

logger = logging.getLogger("Graphs")

def plot(data, title=None, graph_type='Pie'):
    if graph_type == 'Pie':
        pie_chart = pygal.Pie(style=LightGreenStyle)
    else:
        pie_chart = pygal.HorizontalBar(style=LightGreenStyle)
    if title:
        pie_chart.title = title
    data.sort(reverse=True, key=lambda x:x[1])
    for item in data:
        pie_chart.add(item[0], [{'value': item[1], 'label': item[0]}])
    return base64.b64encode(pie_chart.render())
