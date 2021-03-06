import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

import yfinance as yf
from scripts.functions import stock_chart, options_table, get_news_markdown

external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

period_list = ["1d", "1mo", "3mo", "1y", "2y", "5y", "10y", "ytd", "max"]
colors = {"background": "#FFFFFF", "text": "#000000"}

app.layout = html.Div(
    style={"backgroundColor": colors["background"]},
    children=[
        html.H2(
            "STOCK INFO VISUALIZER",
            style={"textAlign": "center", "color": colors["text"]},
        ),
        html.Br(),
        html.Div(
            [
                "Enter Stock Ticker Symbol ",
                dcc.Input(id="ticker", value="AAPL", type="text"),
            ],
            style={"color": colors["text"], "textAlign": "center"},
        ),
        html.Br(),
        html.Br(),

        html.Div([

            html.Div(
                id="hover-data",
                style={"color": colors["text"],
                       "fontSize": 48,
                       "padding-left": "5%",
                       "font-weight": "bold"},
                className="six columns"
            ),

            html.Div(
                [
                    "Select Time Period",
                    dcc.Dropdown(
                        id="period",
                        options=[{"label": i, "value": i} for i in period_list],
                        value="3mo",
                    ),
                ],
                style={
                    "width": "45%",
                    "color": colors["text"],
                    "textAlign": "left",
                    "align-items": "center",
                    "padding-left": "15%",
                },
                className="six columns"
            ),
        ], className="row"),

        dcc.Graph(id="stock-chart"),

        html.Div(
            [html.P("(Hover over the graph to get precise info)")],
            style={"textAlign": "center"},
        ),
        html.Br(),
        html.H3(
            "Options Info", style={"textAlign": "center", "color": colors["text"]},
        ),
        html.Br(),
        html.Div(
            ["Select Options Date", dcc.Dropdown(id="options-dates-dropdown")],
            style={
                "color": colors["text"],
                "textAlign": "left",
                "align-items": "center",
                "padding-left": "37.5%",
                "display": "inline-block",
            },
        ),
        html.Div(
            [
                "Select Options Kind",
                dcc.Dropdown(
                    id="options-kind-dropdown",
                    options=[
                        {"label": "Calls", "value": "calls"},
                        {"label": "Puts", "value": "puts"},
                    ],
                    value="calls",
                ),
            ],
            style={
                "color": colors["text"],
                "textAlign": "left",
                "align-items": "center",
                "padding-left": "5%",
                "display": "inline-block",
            },
        ),
        html.Br(),
        html.Br(),
        dcc.Graph(id="options-table"),
        html.H3(
            "Recent News", style={"textAlign": "center", "color": colors["text"]},
        ),
        html.Br(),
        dcc.Markdown(
            id='news-markdown',
            style={"white-space": "pre", "padding-left": "5%"}
        ),
        html.Br(),
        dcc.Markdown(
        """
        [Github Repo](https://github.com/vinaykale64/stocks_visualizer). Feel free to contribute !
        """,
            style={"textAlign": "center"}
        ),
        html.Br(),
    ],
)


@app.callback(
    dash.dependencies.Output("options-dates-dropdown", "options"),
    [dash.dependencies.Input("ticker", "value")],
)
def get_possible_dates(ticker):

    obj = yf.Ticker(ticker)
    return [{"label": i, "value": i} for i in obj.options]



@app.callback(
    dash.dependencies.Output("options-dates-dropdown", "value"),
    [dash.dependencies.Input("ticker", "value")],
)
def get_default_dates(ticker):
    obj = yf.Ticker(ticker)
    try:
        return obj.options[0]
    except:
        return ''


@app.callback(
    Output("stock-chart", "figure"),
    [Input("ticker", "value"), Input("period", "value")],
)
def update_figure(ticker, period):

    obj = yf.Ticker(ticker)
    fig = stock_chart(stock_object=obj, period=period)
    fig.update_layout(
        plot_bgcolor=colors["background"],
        paper_bgcolor=colors["background"],
        font_color=colors["text"],
    )
    return fig


@app.callback(
    Output("options-table", "figure"),
    [
        Input("ticker", "value"),
        Input("options-dates-dropdown", "value"),
        Input("options-kind-dropdown", "value"),
    ],
)
def update_table(ticker, date, kind):

    obj = yf.Ticker(ticker)
    fig = options_table(stock_object=obj, date=date, kind=kind)
    return fig


@app.callback(Output("hover-data", "children"),
              [Input("stock-chart", "hoverData"),
               Input("stock-chart", "figure"),
               Input("ticker", "value")]
             )

def display_hover_data(hoverData, figure, ticker):

    obj = yf.Ticker(ticker)
    if hoverData is None:
        return obj.ticker + ' ' + str(figure['data'][0]['y'][-1])
    else:
        return "{} {}".format(obj.ticker, hoverData["points"][0]["y"])


@app.callback(Output("news-markdown", "children"),
              [Input("ticker", "value")]
             )

def return_news(ticker):
    return get_news_markdown(ticker, 10)


if __name__ == "__main__":
    app.run_server(debug=True)
