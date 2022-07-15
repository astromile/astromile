import enum

import plotly.express as px
from dash import Dash, html, dcc, Input, Output, ctx

from ukr.un import UNHR


class PlotType(enum.Enum):
    Total = 0
    Geo = 1
    Gender = 2
    Age = 3
    Gender_Age = 4
    Age_Gender = 5


class ViewType(enum.Enum):
    Cumulative = 'Cumulative'
    Daily = 'Daily'
    MA7d = '7D-MA'

    @classmethod
    def is_daily(cls, v):
        return v in [cls.Daily, cls.MA7d]


def last_date():
    return f'Last update: {unhr.data.last_valid_index().strftime("%d-%B-%Y")}'


app = Dash(__name__)

unhr = UNHR()

plot_type_radio = dcc.RadioItems(
    [t.name for t in PlotType],
    PlotType.Total.name,
    id='plot-type',
    labelStyle={'display': 'inline-block', 'marginTop': '5px', 'color': '#ffd700'}
)

view_type_radio = dcc.RadioItems(
    [t.value for t in ViewType],
    ViewType.Cumulative.value,
    id='view-type',
    labelStyle={'display': 'inline-block', 'marginTop': '5px', 'color': '#0057b7'}
)

main_graph = dcc.Graph(
    id='main-plot',
    style={'height': '700px'},
    config={"displaylogo": False}
    # hoverData={'points': [{'customdata': 'Japan'}]}
)

timestamp_label = html.Label(
    last_date(),
    id='timestamp-label',
    style={'padding': '0px 0px 0px 20px'}
)

app.layout = html.Div([
    html.Div([

        html.Div([plot_type_radio],
                 style={'width': '49%', 'display': 'inline-block', 'backgroundColor': '#0057b7'}),

        html.Div([view_type_radio],
                 style={'width': '49%', 'float': 'right', 'display': 'inline-block', 'backgroundColor': '#ffd700'})

    ], style={'padding': '10px 5px'}),

    html.Div([main_graph], style={'width': '98%', 'display': 'inline-block', 'padding': '0 20'}),

    html.Div([
        html.Button('Update', id='update-button'),
        timestamp_label
    ], style={'width': '49%', 'padding': '0px 20px 20px 20px'})
])


@app.callback(
    [Output(main_graph, 'figure'),
     Output('timestamp-label', 'children')],
    [Input(plot_type_radio, 'value'),
     Input(view_type_radio, 'value'),
     Input('update-button', 'n_clicks')]
)
def update_graph(plot_type, view_type, _):
    if ctx.triggered_id == 'update-button':
        timestamp_label.children = 'updating...'
        unhr.update(store=False)
    df = unhr.data
    plot_type = PlotType[plot_type]  ## plot_type is labeled by name
    view_type = ViewType(view_type)  ## view_type is labeled by value

    if ViewType.is_daily(view_type):
        df = df.loc[:df.last_valid_index()].astype(float).interpolate().diff()
        if view_type == ViewType.MA7d:
            df = df.rolling('7D').mean()
    df = df.dropna().stack(level=0).reset_index().rename(columns={'level_0': 'date', 'level_1': 'kind'})
    dk = ['date', 'kind']
    cols_geo = ['DL', 'U', 'LDNR']
    cols_gender = {'m': ['men', 'boys'], 'f': ['women', 'girls'], 'u': ['adults', 'children']}
    cols_age = {'adults_total': ['men', 'women', 'adults'], 'children_total': ['boys', 'girls', 'children']}
    if plot_type == PlotType.Total:
        total = unhr.data.T.xs('total', level=1).T
        total = total.loc[total.last_valid_index()]
        fig = px.line(df, x='date', y='total', color='kind',
                      title=f'Total {total.killed:,} killed and {total.injured:,} injured')
    elif plot_type == PlotType.Geo:
        ddf = df[dk + cols_geo]
        fig = px.line(ddf, x='date', y=cols_geo, facet_col='kind')
    elif plot_type == PlotType.Gender:
        ddf = df[dk + [ai for a in list(cols_gender.values()) for ai in a]].copy()
        for g, c in cols_gender.items():
            ddf[g] = ddf[c].sum(axis=1)
        ddf = ddf[dk + list(cols_gender)]
        fig = px.line(ddf, x='date', y=cols_gender, facet_col='kind')
    elif plot_type == PlotType.Age:
        ddf = df[dk + [ai for a in list(cols_age.values()) for ai in a]].copy()
        for g, c in cols_age.items():
            ddf[g] = ddf[c].sum(axis=1)
        ddf = ddf[dk + list(cols_age)]
        fig = px.line(ddf, x='date', y=cols_age, facet_col='kind')
    elif plot_type == PlotType.Gender_Age:
        ddf = df[dk + [ai for a in list(cols_gender.values()) for ai in a]]
        ddf = ddf.set_index(['date', 'kind']).stack().reset_index().rename(columns={'level_2': 'type', 0: 'value'})
        ddf['gender'] = None
        for g, c in cols_gender.items():
            ddf.loc[ddf['type'].isin(c), 'gender'] = g
        ddf['age'] = None
        for g, c in cols_age.items():
            ddf.loc[ddf['type'].isin(c), 'age'] = g.split('_')[0]
        fig = px.line(ddf, x='date', y='value', facet_col='kind', facet_row='age', color='gender')
    elif plot_type == PlotType.Age_Gender:
        ddf = df[dk + [ai for a in list(cols_gender.values()) for ai in a]]
        ddf = ddf.set_index(['date', 'kind']).stack().reset_index().rename(columns={'level_2': 'type', 0: 'value'})
        ddf['gender'] = None
        for g, c in cols_gender.items():
            ddf.loc[ddf['type'].isin(c), 'gender'] = g
        fig = px.line(ddf, x='date', y='value', facet_col='kind', facet_row='gender', color='type')
    else:
        fig = f'Not implemented for {plot_type}'

    return fig, last_date()


if __name__ == '__main__':
    app.run_server(debug=True)
