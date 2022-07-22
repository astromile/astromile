import enum
import json
import logging

import pandas as pd
import plotly.express as px
from dash import Dash, html, dcc, Input, Output, State, dash_table, ctx
from dash.exceptions import PreventUpdate

from ukr.data import DB
from ukr.un import UNHR
from ukr.util import init_logging


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


app = Dash(__name__, external_stylesheets=[
    'https://codepen.io/chriddyp/pen/bWLwgP.css',
    'https://use.fontawesome.com/releases/v6.1.1/css/all.css'
])

server = app.server

init_logging(level=logging.DEBUG)

data_bean = DB()


def last_date(data):
    return f'Last update: {"" if len(data) == 0 else data.last_valid_index().strftime("%d-%B-%Y")}'


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


def output_table(kind, data):
    df = data[kind].dropna().sort_index(ascending=False).reset_index().rename(columns={'index': 'date'})
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


def load_data(unhr):
    reports = unhr.data.copy()
    reports.columns = [c[0] + '_' + c[1] for c in reports.columns]
    data = {
        'reports': reports.to_json(),
        'monthly': {d.strftime('%Y-%m-%d'): m.to_json() for d, m in unhr.summary.items()}
    }
    return json.dumps(data)


def extract_reports(data):
    reports = pd.read_json(json.loads(data)['reports'])
    reports.columns = pd.MultiIndex.from_tuples([c.split('_') for c in reports.columns])
    return reports


def extract_monthly(data):
    def resort(df):
        df = df[df.Period != 'Total'].copy()
        df['by'] = pd.to_datetime('2022-' + df.Period.str.split(' ').apply(lambda x: x[-1]).str[:3] + '-01')
        return df.sort_values('by').drop(columns='by')

    return {pd.to_datetime(d).date(): resort(pd.read_json(m))
            for d, m in json.loads(data)['monthly'].items()}


def build_unhr(data):
    data = json.loads(data)
    data['reports'] = pd.read_json(data['reports'])
    data['reports'].columns = pd.MultiIndex.from_tuples([c.split('_') for c in data['reports'].columns])
    data['monthly'] = {pd.to_datetime(d).date(): pd.read_json(m)
                       for d, m in data['monthly'].items()}

    unhr = UNHR(data_bean=data_bean, load=False)
    unhr.data = data['reports']
    unhr.summary = data['monthly']
    return unhr


def serve_layout():
    logging.debug('reloading page?')
    unhr = UNHR(data_bean=data_bean)
    data = load_data(unhr)

    return html.Div([
        html.H1("UNHR Ukraine Dashboard"),
        dcc.Store(id='store', data=data),

        dcc.Tabs(
            [
                dcc.Tab(label='Daily Reports Visualized', children=[
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
                dcc.Tab(label='Daily Reports Table', children=[

                    html.Div([kind_radio],
                             style={'width': '25%', 'display': 'inline-block', 'backgroundColor': '#0066cc'}),

                    html.Div([
                        html.Button('Export CSV', id='export-button', className='button-primary'),
                        dcc.Download(id='export-csv')
                    ], style={'width': '25%', 'display': 'inline-block', 'margin': '10px 10px 10px 10px'}),

                    dash_table.DataTable(
                        id='data-table',
                        style_cell={'width': '3%'},
                        **output_table(Kind.Killed.value, unhr.data)
                    ),

                ]),
                dcc.Tab(label='By Month', children=[
                    html.Div([
                        dcc.Slider(min=0, max=len(unhr.summary) - 1, step=1, value=len(unhr.summary) - 1,
                                   marks={i: str(d) for i, d in enumerate(sorted(unhr.summary.keys()))},
                                   id='monthly-version', vertical=True)
                    ], style={'minWidth': '83px', 'width': '15%', 'display': 'inline-block',
                              'verticalAlign': 'middle'}),

                    html.Div([dcc.Graph(
                        id='monthly-plot',
                        style={'height': '700px'},
                        config={"displaylogo": False}
                    )],
                        style={'width': '83%', 'display': 'inline-block', 'padding': '0 20',
                               'verticalAlign': 'middle'}),

                ], id='month-tab', disabled=len(unhr.summary) == 0)
            ]
        ),

        html.Div([
            html.Button(html.I(className='fa-regular fa-floppy-disk fa-2xl'),
                        id='save-button', className='strom-button-disabled', disabled=True,
                        ),
            html.Button(html.I(className='fa fa-rotate fa-2xl'),
                        id='update-button', className='button-primary'),
            html.Div(dcc.Loading(id='loading', children=html.Div([html.Label(
                last_date(unhr.data),
                id='timestamp-label',
                style={'padding': '0px 0px 0px 20px'}
            )])),
                     style={'display': 'inline-block'}),
        ], style={'padding': '20px 20px 20px 20px'})
    ])


app.layout = serve_layout


@app.callback(
    [Output('store', 'data'),
     Output('save-button', 'disabled'),
     Output('save-button', 'className'),
     Output('timestamp-label', 'children'), ],
    [State('store', 'data'),
     State('timestamp-label', 'children'),
     Input('update-button', 'n_clicks'),
     Input('save-button', 'n_clicks')],
    prevent_initial_call=True
)
def update_or_save_data(data, ts, *_):
    logging.debug(f'triggered by {ctx.triggered_id}')
    if not data or not ctx.triggered_id:
        logging.debug('preventing update')
        raise PreventUpdate

    unhr = build_unhr(data)

    if ctx.triggered_id == 'save-button':
        logging.debug('persisting data')
        unhr.store()
        return data, True, 'strom-button-disabled', ts

    d = last_date(unhr.data)

    logging.debug('updating data from UN')
    unhr.update(store=False)
    save_button_disabled = d == last_date(unhr.data)
    save_button_class = 'strom-button-disabled' if save_button_disabled else 'button-primary'
    if not save_button_disabled:
        data = load_data(unhr)  ## reload state

    return data, save_button_disabled, save_button_class, last_date(unhr.data)


@app.callback(
    Output(main_graph, 'figure'),
    [Input('store', 'data'),
     Input(plot_type_radio, 'value'),
     Input(view_type_radio, 'value'), ]
)
def update_figure(data, plot_type, view_type):
    logging.debug(f'triggered by {ctx.triggered_id}')
    return create_graph(PlotType[plot_type],  ## plot_type is labeled by name
                        ViewType(view_type),  ## view_type is labeled by value
                        extract_reports(data))


@app.callback(
    [Output('data-table', 'data'),
     Output('data-table', 'columns')],
    [Input('store', 'data'),
     Input(kind_radio, 'value')]
)
def update_report_table(data, kind):
    logging.debug(f'triggered by {ctx.triggered_id}')
    table = output_table(kind, extract_reports(data))
    return table['data'], table['columns']


@app.callback(
    [Output('monthly-version', 'max'),
     Output('monthly-version', 'marks'),
     Output('monthly-version', 'value'),
     Output('month-tab', 'disabled')],
    [Input('store', 'data')]
)
def update_monthly_version_slider(data):
    logging.debug(f'triggered by {ctx.triggered_id}')
    summary = json.loads(data)['monthly']
    monthly_version_max = len(summary) - 1
    monthly_version_marks = {i: str(d) for i, d in enumerate(sorted(summary.keys()))}
    month_tab_disabled = len(summary) == 0
    return monthly_version_max, monthly_version_marks, monthly_version_max, month_tab_disabled


def create_graph(plot_type, view_type, df):
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

        raise NotImplementedError(plot_type)

    return fig


@app.callback(
    Output('monthly-plot', 'figure'),
    [Input('monthly-version', 'value'),
     State('store', 'data')]
)
def update_monthly_plot(version, data):
    logging.debug(f'triggered by {ctx.triggered_id}')
    summary = extract_monthly(data)
    if version >= 0:
        version = sorted(summary.keys())[version]

    if version not in summary:
        return px.bar()

    df = summary[version]
    df = df[df.Period != 'Total'].copy()
    df.columns = [c[:1].upper() + c[1:] for c in df.columns]  ## capitalize column names

    fig = px.bar(df, x='Period', y=['Injured', 'Killed'], barmode='group')

    return fig


@app.callback(
    Output('export-csv', 'data'),
    [State('store', 'data'),
     State(kind_radio, 'value'),
     Input('export-button', 'n_clicks')],
    prevent_initial_call=True
)
def export(data, kind, _):
    logging.debug(f'triggered by {ctx.triggered_id}')

    data = pd.read_json(json.loads(data)['reports'])
    df = data[kind].dropna().reset_index().rename(columns={'index': 'date'})
    df['source'] = [UNHR.url_at(d) for d in df.date]
    df['date'] = df.date.dt.date
    return dcc.send_data_frame(df.to_csv, f'{kind}-{df.date.iloc[-1]}.csv')


if __name__ == '__main__':
    app.run_server(debug=True)
