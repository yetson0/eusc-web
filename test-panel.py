import os
import sys
from functools import partial

import plotly.express as px
import plotly.graph_objects as go

import panel as pn

import numpy as np
import pandas as pd

pn.extension(design='material')  # , template='fast')
pn.extension('plotly', 'ipywidgets', 'gridstack')

pzh_blue = '#35387f'
pzh_light_blue = '#30b7cf'
hail_colors = ['white', pzh_light_blue, pzh_blue, 'purple']
rainbow_colors = ['green', 'yellow', 'orange', 'red']
alarm_colors = hail_colors

indicator_names = ["Farrington", 'FarringtonFlex', 'CUSUM', 'RKI', 'CDC', 'RSI']
virus_names = ["A(H1N1)", "A(H3N1)", "B/Yamagata", "B/Victoria", "RSV", "parainfluenza", "metapneumovirus",
               "rhinovirus", "SARS-Cov-2", "SARS-Cov-1", "adenovirus", "bocavirus", "salmonella", "campylobactery"]


def get_indicators(names: list) -> pd.DataFrame:
    indicator_values = {v: np.random.randint(0, 4) for v in names}
    indicators = pd.DataFrame.from_dict({'day_0': indicator_values})
    for i in range(1, 4):
        indicators[f'day_{i:d}'] = indicators[f'day_{i - 1:d}'].apply(lambda x: x - 1 if x >= 1 else x)
    return indicators


def get_virus_cases(names: list) -> pd.DataFrame:
    virus_cases = {v: 10 for v in names}
    virus_cases_df = pd.DataFrame.from_dict({'cases': virus_cases})

    virus_cases_df['color'] = [alarm_colors[np.random.randint(0, 4)] for _i in range(len(virus_cases_df))]
    virus_cases_df['alarm'] = [np.random.randint(0, 4) for _i in range(len(virus_cases_df))]
    return virus_cases_df


SIDEBAR_WIDTH = 250


def plot_all_virus_status(indicator: str, day: pd.Timestamp, colors: list) -> go.Figure:

    virus_status = get_virus_cases(names=virus_names)
    fig = px.imshow(virus_status[['alarm']].transpose(),
                    color_continuous_scale=colors,
                    aspect=0.7,
                    )
    fig.update_layout(
        title_text='epi status  ' + day.strftime('%Y-%m-%d %H:%M') + ', wskaźnik: ' + indicator,
        width=800,
        height=300,
    )
    return fig


def get_alarm_color(value: int, colors: list, noalarm_color: str = 'forestgreen'):
    if value == 1:
        return colors[1]
    if value == 2:
        return colors[2]
    if value == 3:
        return colors[3]
    return noalarm_color


def plot_all_indicators_status(county: str,
                               virus: str,
                               day: pd.Timestamp,
                               # indicators: pd.DataFrame,
                               colors: list,
                               ):
    df = get_indicators(names=indicator_names)
    df.columns = [day - pd.Timedelta(days=int(col.split('_')[1])) for col in df.columns]
    fig = px.imshow(df,
                    color_continuous_scale=colors,
                    range_color=[0, 3]
                    )

    fig.update_layout(
        title_text='status wskaźników ' + day.strftime('%Y-%m-%d %H:%M') + f'<br>zarazek: {virus}, powiat {county}',
        height=330,
        showlegend=False,
        margin=dict(l=100, r=20, t=60, b=50),
        template='gridon',
    )
    return fig


width = SIDEBAR_WIDTH
align = 'center'
widg_virus = pn.widgets.Select(
    name='wirus',
    options=virus_names,
    value='SARS-Cov-2',
    # size=17,
    width=width,
    align=align,
)

counties = ['rzeszowski', 'olsztyński', 'warszawski', 'gdański']
widg_county = pn.widgets.Select(
    name='powiat',
    options=counties,
    value=counties[0],
    # size=17,
    width=width,
    align=align,
)

widg_indicators = pn.widgets.Select(
    name='wskaźnik',
    options=indicator_names,
    value='RSI',
    width=width,
    align=align,
)

virus_status_plot = partial(plot_all_virus_status,
                            day=pd.to_datetime('today'),
                            colors=alarm_colors)
virus_status_pane = pn.pane.Plotly(pn.bind(virus_status_plot, widg_indicators))

indicators_status_plot = partial(plot_all_indicators_status,
                                 day=pd.to_datetime('today').normalize(),
                                 colors=alarm_colors)

plot_indicators_pane = pn.pane.Plotly(pn.bind(indicators_status_plot,
                                              widg_county, widg_virus))

# layout
widgets = pn.WidgetBox(
    widg_virus,
    widg_indicators,
    widg_county,
)

all_plots = pn.Column(
    pn.Row(plot_indicators_pane, sizing_mode='stretch_width'),
    pn.layout.Divider(),
    pn.Row(virus_status_pane, sizing_mode='stretch_width'),
)

content = pn.Row(
    all_plots,
)

sidebar = pn.Column(widgets, sizing_mode='stretch_width')

template = pn.template.VanillaTemplate(
    site="",
    title="dummy panel",
    sidebar=sidebar,
    sidebar_width=250,
    main=all_plots,
    header_background=pzh_blue,
    # sidebar_width=500,
)
template.servable()
