from enum import Enum
from dash import html, ctx
from dash.dependencies import Input, Output, State

from dash.exceptions import PreventUpdate
from frontend.app import app
from frontend.main_column.factory_graph.GraphSelectedElement import GraphSelectedElement
from frontend.right_sidebar.node_data_tab import node_data_layout
from frontend.right_sidebar.node_information_tab import node_information_layout
from util.log import logger

logger.info("Initializing extension collapsable callbacks...")

SIDEBAR_CONTAINER_NORMAL = ""
SIDEBAR_CONTAINER_EXTENDED = "left-sidebar-container-extended"

SIDEBAR_SHOWN = "collapsable-horizontal"
SIDEBAR_HIDDEN = "collapsable-horizontal collapsed-horizontal"

COLLAPSE_BUTTON_COLLAPSED = "vertical-button-left-collapse-icon"
COLLAPSE_BUTTON_UNCOLLAPSED = (
    "vertical-button-left-collapse-icon vertical-button-left-collapse-icon-expanded"
)


class CollapsableContainers(Enum):
    MAIN = 0
    PIPELINE = 1
    ANNOTATIONS = 2


@app.callback(
    Output("left-sidebar-collapsable-store", "data"),
    Input("similarity-pipeline-collapse-button", "n_clicks"),
    Input("annotation-detection-collapse-button", "n_clicks"),
    State("left-sidebar-collapsable-store", "data"),
    Input("status-unconfirmed-annotation-detection", "modified_timestamp"),
    State("status-unconfirmed-annotation-detection", "data"),
    prevent_initial_call=True,
)
def select_extension_sidebar(n_clicks_sim, n_clicks_an, store, _, new_detection):
    button_clicked = ctx.triggered_id

    if (
        new_detection is not None
        and new_detection
        and button_clicked
        not in [
            "similarity-pipeline-collapse-button",
            "annotation-detection-collapse-button",
        ]
    ):
        logger.info("New unconfirmed annotation detection!")
        return CollapsableContainers.ANNOTATIONS.value
    elif button_clicked == "similarity-pipeline-collapse-button":
        if store == CollapsableContainers.PIPELINE.value:
            return CollapsableContainers.MAIN.value
        else:
            return CollapsableContainers.PIPELINE.value
    elif button_clicked == "annotation-detection-collapse-button":
        if store == CollapsableContainers.ANNOTATIONS.value:
            return CollapsableContainers.MAIN.value
        else:
            return CollapsableContainers.ANNOTATIONS.value
    else:
        raise PreventUpdate


@app.callback(
    Output("left-sidebar-collapse-main", "className"),
    Output("left-sidebar-collapse-similarity-pipeline", "className"),
    Output("left-sidebar-collapse-annotations", "className"),
    Output("similarity-pipeline-button-icon", "className"),
    Output("annotation-detection-button-icon", "className"),
    Output("left-sidebar-container", "className"),
    Input("left-sidebar-collapsable-store", "data"),
    prevent_initial_call=False,
)
def left_sidebar_collapse(store):
    """
    Toggles the visibility of a left collapsable sidebar
    :param selected_el:
    :return:
    """

    if store is None or store == CollapsableContainers.MAIN.value:
        return (
            SIDEBAR_SHOWN,
            SIDEBAR_HIDDEN,
            SIDEBAR_HIDDEN,
            COLLAPSE_BUTTON_COLLAPSED,
            COLLAPSE_BUTTON_COLLAPSED,
            SIDEBAR_CONTAINER_NORMAL,
        )
    elif store == CollapsableContainers.PIPELINE.value:
        return (
            SIDEBAR_HIDDEN,
            SIDEBAR_SHOWN,
            SIDEBAR_HIDDEN,
            COLLAPSE_BUTTON_UNCOLLAPSED,
            COLLAPSE_BUTTON_COLLAPSED,
            SIDEBAR_CONTAINER_EXTENDED,
        )
    else:
        return (
            SIDEBAR_HIDDEN,
            SIDEBAR_HIDDEN,
            SIDEBAR_SHOWN,
            COLLAPSE_BUTTON_COLLAPSED,
            COLLAPSE_BUTTON_UNCOLLAPSED,
            SIDEBAR_CONTAINER_EXTENDED,
        )
