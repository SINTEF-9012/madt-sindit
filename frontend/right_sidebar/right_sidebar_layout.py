import dash_bootstrap_components as dbc
from dash import dcc
from dash import html

from frontend.right_sidebar.graph_selector_info import graph_selector_info_layout


def get_layout():
    """
    Layout of the right sidebar. Contains context details for selected elements of the main graph
    :return:
    """
    return html.Div(
        id="right-sidebar-collapse-col",
        children=[
            dbc.Collapse(
                id="right-sidebar-collapse",
                children=[
                    # Selected node / edge:
                    graph_selector_info_layout.get_layout(),
                    # Tabs:
                    dcc.Tabs(
                        id="tabs-infos",
                        value="tab-node-information",
                        children=[
                            dcc.Tab(label="Node details", value="tab-node-information"),
                            dcc.Tab(label="Data visualization", value="tab-node-data"),
                        ],
                        persistence=True,
                        persistence_type="session",
                    ),
                    html.Div(id="tabs-content"),
                ],
            ),
        ],
    )
