from datetime import datetime
from dash import ctx
from graph_domain.BaseNode import BaseNode
from graph_domain.expert_annotations.AnnotationInstanceNode import (
    AnnotationInstanceNodeDeep,
    AnnotationInstanceNodeFlat,
)
from graph_domain.expert_annotations.AnnotationTimeseriesMatcherNode import (
    AnnotationTimeseriesMatcherNodeFlat,
)
from graph_domain.factory_graph_ogm_matches import OGM_CLASS_FOR_NODE_TYPE

from util.log import logger
from frontend.app import app
from dash.dependencies import Input, Output, State
from frontend import api_client

from dash.exceptions import PreventUpdate

from frontend.main_column.factory_graph.GraphSelectedElement import GraphSelectedElement
from graph_domain.factory_graph_types import NodeTypes

logger.info("Initializing annotation extension callbacks...")

HIDE = "hide-content"
SHOW = ""
SIDEBAR_SHOWN = "collapsable-horizontal"
SIDEBAR_HIDDEN = "collapsable-horizontal collapsed-horizontal"
LIST_RESULT_PREFIX = "↪ "

DATETIME_STRF_FORMAT = "%Y_%m_%d_%H_%M_%S_%f"


##########################################
# Navigation and info:
##########################################


@app.callback(
    Output("annotation-information-collapse", "is_open"),
    Output("annotation-create-collapse", "is_open"),
    Output("annotation-confirmation-collapse", "is_open"),
    Input("create-annotation-button", "n_clicks"),
    Input("confirm-cancel-annotation-creation", "submit_n_clicks"),
    Input("annotation-creation-saved", "data"),
    State("annotation-creation-store-step", "data"),
    Input("status-unconfirmed-annotation-detection", "modified_timestamp"),
    State("status-unconfirmed-annotation-detection", "data"),
    Input("annotation-detection-confirmed", "modified_timestamp"),
    Input("annotation-detection-declined", "modified_timestamp"),
    prevent_initial_call=False,
)
def annotation_create_collapse(
    n_clicks_create,
    n_clicks_cancel,
    n_clicks_save,
    step,
    detection_time_stamp,
    new_detection,
    detection_confirmed,
    detection_declined,
):
    trigger_id = ctx.triggered_id
    if trigger_id in [
        "annotation-detection-confirmed",
        "annotation-detection-declined",
    ]:
        return True, False, False
    elif new_detection is not None and new_detection:
        return False, False, True
    elif trigger_id == "create-annotation-button":
        return False, True, False
    elif trigger_id in [
        "confirm-cancel-annotation-creation",
        "annotation-creation-saved",
    ]:
        return True, False, False
    elif step is not None:
        return False, True, False
    else:
        return True, False, False


@app.callback(
    Output("annotations-info-total-count", "children"),
    Output("annotations-info-scan-sum", "children"),
    Output("annotations-info-unconfirmed-detections", "children"),
    Output("annotations-info-confirmed-detections", "children"),
    Input("annotation-information-collapse", "is_open"),
    Input("left-sidebar-collapse-annotations", "className"),
    prevent_initial_call=False,
)
def annotation_info(info_open, sidebar_open_classname):
    if info_open and sidebar_open_classname == SIDEBAR_SHOWN:
        status_dict = api_client.get_json("/annotation/status")
        if status_dict is not None:
            return (
                status_dict.get("total_annotations_count"),
                status_dict.get("sum_of_scans"),
                status_dict.get("unconfirmed_detections"),
                status_dict.get("confirmed_detections"),
            )

    return None, None, None, None


@app.callback(
    Output("annotation-instance-scan-toggle-container", "is_open"),
    Output("annotation-instance-scanning-toggle", "value"),
    Input("selected-graph-element-store", "data"),
    prevent_initial_call=False,
)
def show_instance_scan_toggle_switch(selected_el_json):
    if selected_el_json is None:
        return False, []

    selected_el: GraphSelectedElement = GraphSelectedElement.from_json(selected_el_json)
    if selected_el.type == NodeTypes.ANNOTATION_INSTANCE.value:
        node_details_json = api_client.get_json("/node_details", iri=selected_el.iri)
        node_class = OGM_CLASS_FOR_NODE_TYPE.get(selected_el.type)
        node: AnnotationInstanceNodeFlat = node_class.from_dict(node_details_json)

        return True, [True] if node.activate_occurance_scan else []
    else:
        return False, []


@app.callback(
    Output("annotation-instance-scan-toggled", "data"),
    Input("annotation-instance-scanning-toggle", "value"),
    State("selected-graph-element-store", "data"),
    prevent_initial_call=True,
)
def toggle_instance_scan(toggle_value, selected_el_json):
    activated = True in toggle_value
    selected_el: GraphSelectedElement = GraphSelectedElement.from_json(selected_el_json)

    api_client.patch(
        "/annotation/instance/toggle_occurance_scan",
        instance_iri=selected_el.iri,
        active=activated,
    )

    return datetime.now()


@app.callback(
    Output("annotation-matcher-settings-container", "is_open"),
    Output("annotation-matcher-precission-slider", "value"),
    Input("selected-graph-element-store", "data"),
    prevent_initial_call=False,
)
def show_annotation_matcher_settings(selected_el_json):
    if selected_el_json is None:
        return False, 0

    selected_el: GraphSelectedElement = GraphSelectedElement.from_json(selected_el_json)
    if selected_el.type == NodeTypes.ANNOTATION_TS_MATCHER.value:
        node_details_json = api_client.get_json("/node_details", iri=selected_el.iri)
        node_class = OGM_CLASS_FOR_NODE_TYPE.get(selected_el.type)
        node: AnnotationTimeseriesMatcherNodeFlat = node_class.from_dict(
            node_details_json
        )

        return True, node.detection_precision
    else:
        return False, 0


@app.callback(
    Output("annotation-matcher-settings-changed", "data"),
    Input("annotation-matcher-precission-slider", "value"),
    State("selected-graph-element-store", "data"),
    prevent_initial_call=True,
)
def change_matcher_settings(value, selected_el_json):
    selected_el: GraphSelectedElement = GraphSelectedElement.from_json(selected_el_json)

    api_client.patch(
        "/annotation/ts_matcher/detection_precision",
        matcher_iri=selected_el.iri,
        detection_precision=value,
    )

    return datetime.now()


##########################################
# Deleting:
##########################################


@app.callback(
    Output("delete-annotation-button", "disabled"),
    Input("selected-graph-element-store", "data"),
    Input("annotation-deleted", "modified_timestamp"),
    prevent_initial_call=False,
)
def annotation_delete_button_activate(selected_el_json, deleted):
    if ctx.triggered_id == "annotation-deleted":
        return True

    selected_el: GraphSelectedElement = (
        GraphSelectedElement.from_json(selected_el_json)
        if selected_el_json is not None
        else None
    )
    if (
        selected_el is not None
        and selected_el.type == NodeTypes.ANNOTATION_DEFINITION.value
    ):
        # Check, if instances of that definition exist:
        instances_count = api_client.get_int(
            "/annotation/instance/count", definition_iri=selected_el.iri
        )
        return instances_count != 0
    elif (
        selected_el is not None
        and selected_el.type == NodeTypes.ANNOTATION_INSTANCE.value
    ):
        return False
    else:
        return True


@app.callback(
    Output("annotation-deleted", "data"),
    Input("delete-annotation-button-confirm", "submit_n_clicks"),
    State("selected-graph-element-store", "data"),
    prevent_initial_call=True,
)
def delete_annotation(
    delete_button,
    selected_el_json,
):
    selected_el: GraphSelectedElement = GraphSelectedElement.from_json(selected_el_json)

    if selected_el.type == NodeTypes.ANNOTATION_INSTANCE.value:
        logger.info(f"Deleting annotation instance: {selected_el.id_short}")
        api_client.delete(
            "/annotation/instance",
            instance_iri=selected_el.iri,
        )
    elif selected_el.type == NodeTypes.ANNOTATION_DEFINITION.value:
        logger.info(f"Deleting annotation definition: {selected_el.id_short}")
        api_client.delete("/annotation/definition", definition_iri=selected_el.iri)
    else:
        logger.info("Tried to remove annotation, but different object selected")
        raise PreventUpdate

    return datetime.now()
