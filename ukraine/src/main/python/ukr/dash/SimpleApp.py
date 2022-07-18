import enum

import plotly.express as px
from dash import Dash, html, dcc, Input, Output, State, ctx, dash_table

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


class Kind(enum.Enum):
    Killed = 'killed'
    Injured = 'injured'


def last_date():
    return f'Last update: {"" if len(unhr.data) == 0 else unhr.data.last_valid_index().strftime("%d-%B-%Y")}'


app = Dash(__name__, external_stylesheets=['https://codepen.io/chriddyp/pen/bWLwgP.css'])

server = app.server

unhr = UNHR()

plot_type_radio = dcc.RadioItems(
    [t.name for t in PlotType],
    PlotType.Total.name,
    id='plot-type',
    labelStyle={'display': 'inline-block', 'marginTop': '5px', 'color': '#ffcc00'}
)

view_type_radio = dcc.RadioItems(
    [t.value for t in ViewType],
    ViewType.Cumulative.value,
    id='view-type',
    labelStyle={'display': 'inline-block', 'marginTop': '5px', 'color': '#0066cc'}
)

kind_radio = dcc.RadioItems(
    [t.value for t in Kind],
    Kind.Killed.value,
    id='kind',
    labelStyle={'display': 'inline-block', 'marginTop': '5px', 'color': '#ffcc00'}
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


def output_table(kind='killed'):
    df = unhr.data[kind].dropna().sort_index(ascending=False).reset_index().rename(columns={'index': 'date'})
    links = []
    for d in df.date:
        url = UNHR.url_at(d)
        parts = url.split('/')
        ukr_date = parts[-1].split('-')
        text = '.'.join(parts[2].split('.')[1:]) + '/.../' + ukr_date[0] + '-...-' + '-'.join(ukr_date[-3:])
        links.append(f'[{text}]({url})')
    df['date'] = links
    df.rename(columns={'date': 'source'}, inplace=True)
    return {'data': df.to_dict('records'),
            'columns': [{'name': c, 'id': c} | ({'presentation': 'markdown'} if c == 'source' else {})
                        for c in df.columns]}


app.layout = html.Div([
    html.H1("UNHR Ukraine Dashboard"),

    dcc.Tabs(
        [
            dcc.Tab(label='Plots', children=[
                html.Div([

                    html.Div([plot_type_radio],
                             style={'width': '49%', 'display': 'inline-block', 'backgroundColor': '#0066cc'}),

                    html.Div([view_type_radio],
                             style={'width': '49%', 'float': 'right', 'display': 'inline-block',
                                    'backgroundColor': '#ffcc00'})

                ], style={'padding': '10px 5px'}),

                html.Div([main_graph],
                         style={'width': '98%', 'display': 'inline-block', 'padding': '0 20'}),

            ]),
            dcc.Tab(label='Table', children=[
                html.Div([kind_radio],
                         style={'width': '25%', 'display': 'inline-block', 'backgroundColor': '#0066cc'}),
                html.Div([
                    html.Button('Export CSV', id='export-button'),
                    dcc.Download(id='export-csv')
                ], style={'width': '25%', 'display': 'inline-block', 'margin': '10px 10px 10px 10px'}),
                dash_table.DataTable(
                    id='data-table',
                    style_cell={'width': '3%'},
                    **output_table()
                ),
            ])
        ]
    ),

    html.Div([
        html.Button('Update', id='update-button'),
        html.Div(dcc.Loading(id='loading', children=html.Div([timestamp_label])),
                 style={'width': '24%', 'display': 'inline-block'}),
        html.Button('Save', id='save-button', disabled=True)
    ], style={'padding': '20px 20px 20px 20px'})
])


@app.callback(
    [Output(main_graph, 'figure'),
     Output('timestamp-label', 'children'),
     Output('save-button', 'disabled'),
     Output('data-table', 'data'),
     Output('data-table', 'columns')],
    [Input(plot_type_radio, 'value'),
     Input(view_type_radio, 'value'),
     Input(kind_radio, 'value'),
     State('save-button', 'disabled'),
     State(main_graph, 'figure'),
     State('data-table', 'data'),
     State('data-table', 'columns'),
     Input('update-button', 'n_clicks'),
     Input('save-button', 'n_clicks'),
     ]
)
def update(plot_type, view_type, kind_type, save_disabled, fig0, data, columns, *_):
    if ctx.triggered_id == 'save-button':
        unhr.store()
        return fig0, last_date(), True, data, columns
    elif ctx.triggered_id == 'kind':
        table = output_table(kind_type)
        return fig0, last_date(), save_disabled, table['data'], table['columns']

    if ctx.triggered_id == 'update-button':
        d = last_date()
        unhr.update(store=False)
        save_button_disabled = (d == last_date()) and save_disabled
        table = output_table(kind_type)
        data = table['data']
        columns = table['columns']
    else:
        save_button_disabled = save_disabled

    fig = create_graph(PlotType[plot_type],  ## plot_type is labeled by name
                       ViewType(view_type))  ## view_type is labeled by value

    return fig, last_date(), save_button_disabled, data, columns


def create_graph(plot_type, view_type):
    df = unhr.data

    if len(df) == 0:
        return px.line()

    if ViewType.is_daily(view_type):
        df = df.loc[:df.last_valid_index()].astype(float).interpolate().diff()
        if view_type == ViewType.MA7d:
            df = df.rolling('7D').mean()

    df = df.dropna().stack(level=0).reset_index().rename(columns={'level_0': 'date', 'level_1': 'kind'})

    kinds = ['killed', 'injured']
    dk = ['date', 'kind']
    cols_geo = ['DL', 'U', 'LDNR']
    cols_gender = {'m': ['men', 'boys'], 'f': ['women', 'girls'], 'u': ['adults', 'children']}
    cols_age = {'adults_total': ['men', 'women', 'adults'], 'children_total': ['boys', 'girls', 'children']}

    view_labels = {ViewType.Cumulative: '<b>Total</b>',
                   ViewType.Daily: '<b>Daily increment</b>',
                   ViewType.MA7d: '<b>7D average increment</b>'}

    if plot_type == PlotType.Total:

        count = df[df.date == df.date.max()][['kind', 'total']].set_index('kind').total
        title = f'{view_labels[view_type]}: ' \
                + ' and '.join([f'{round(count[kind]):,} <i>{kind}</i>' for kind in kinds])
        fig = px.line(df, x='date', y='total', color='kind', title=title)

    elif plot_type == PlotType.Geo:

        ddf = df[dk + cols_geo]
        count = ddf[ddf.date == ddf.date.max()][['kind'] + cols_geo].set_index('kind')
        title = f'{view_labels[view_type]}: ' \
                + ' and '.join([' '.join([f'{round(count.loc[kind][c]):,} [<b>{c}</b>]' for c in cols_geo])
                                + f' <i>{kind}</i>'
                                for kind in kinds])
        fig = px.line(ddf, x='date', y=cols_geo, facet_col='kind', title=title)

    elif plot_type == PlotType.Gender:

        ddf = df[dk + [ai for a in list(cols_gender.values()) for ai in a]].copy()
        for g, c in cols_gender.items():
            ddf[g] = ddf[c].sum(axis=1)
        ddf = ddf[dk + list(cols_gender)]
        count = ddf[ddf.date == ddf.date.max()][['kind'] + list(cols_gender)].set_index('kind')
        title = f'{view_labels[view_type]}: ' \
                + ' and '.join([' '.join([f'{round(count.loc[kind][c]):,} [<b>{c}</b>]' for c in cols_gender])
                                + f' <i>{kind}</i>'
                                for kind in kinds])
        fig = px.line(ddf, x='date', y=cols_gender, facet_col='kind', title=title)

    elif plot_type == PlotType.Age:

        ddf = df[dk + [ai for a in list(cols_age.values()) for ai in a]].copy()
        for g, c in cols_age.items():
            ddf[g] = ddf[c].sum(axis=1)
        ddf = ddf[dk + list(cols_age)]
        count = ddf[ddf.date == ddf.date.max()][['kind'] + list(cols_age)].set_index('kind')
        title = f'{view_labels[view_type]}: ' \
                + ' and '.join([' '.join([f'{round(count.loc[kind, c]):,} [<b>{c}</b>]' for c in cols_age])
                                + f' <i>{kind}</i>'
                                for kind in kinds])
        fig = px.line(ddf, x='date', y=cols_age, facet_col='kind', title=title)

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

    return fig


@app.callback(
    Output('export-csv', 'data'),
    Input('export-button', 'n_clicks'),
    prevent_initial_call=True
)
def export(_):
    kind = 'killed'
    df = unhr.data[kind].dropna().reset_index().rename(columns={'index': 'date'})
    df['source'] = [UNHR.url_at(d) for d in df.date]
    df['date'] = df.date.dt.date
    return dcc.send_data_frame(df.to_csv, f'{kind}-{df.date.iloc[-1]}.csv')


if __name__ == '__main__':
    app.run_server(debug=True)
