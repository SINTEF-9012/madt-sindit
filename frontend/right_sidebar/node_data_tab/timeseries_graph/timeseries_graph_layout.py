from dash import dcc
from dash import html
import plotly.subplots
import plotly.graph_objects as go


def get_layout():
    graph = html.Div(
        className="tab-content-inner-container",
        children=[
            dcc.Graph(id="timeseries-graph"),
            html.Div(
                id="timeseries-count-info-container",
                children=[
                    html.Div(
                        id="timeseries-graph-update-interval-passthrough", hidden=True
                    ),
                    html.Div(id="timeseries-graph-result-count-info", children=""),
                    html.Div(id="timeseries-graph-aggregate-info", children=""),
                ],
            ),
        ],
    )
    return graph


def get_figure():
    fig = plotly.subplots.make_subplots(
        rows=1,
        cols=1,
        vertical_spacing=0.2,
    )
    fig["layout"]["margin"] = {"l": 30, "r": 10, "b": 30, "t": 10}
    fig["layout"]["legend"] = {"x": 0, "y": 1, "xanchor": "left"}

    fig.update_layout(
        # Used to disable automatic reset of the zoom etc. at every refresh:
        uirevision="no_change",
        plot_bgcolor="#EBF2FA",
        paper_bgcolor="white",
        dragmode="zoom",
        selectdirection="any",
    )

    return fig
