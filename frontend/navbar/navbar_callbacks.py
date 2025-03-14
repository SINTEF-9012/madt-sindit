from datetime import datetime
from dash.dependencies import Input, Output, State
from dash import dcc, ctx
from frontend.app import app
from frontend import api_client
from dateutil import tz
from util.environment_and_configuration import (
    ConfigGroups,
    get_configuration,
)
from util.log import logger

logger.info("Initializing navbar callbacks...")

EXPORT_FILE_NAME_BASE = "sindit_database_export_"
AAS_EXPORT_FILE_NAME_BASE = "sindit_aas_"
DATETIME_STRF_FORMAT = "%Y_%m_%d_%H_%M_%S_%f"


@app.callback(
    Output("help-offcanvas", "is_open"),
    Input("help-button", "n_clicks"),
    [State("help-offcanvas", "is_open")],
    prevent_initial_call=True,
)
def toggle_offcanvas(n1, is_open):
    if n1:
        return not is_open
    return is_open


@app.callback(
    Output("import-export-dropdown", "is_open"),
    Output("exportable-databases-dropdown", "options"),
    Input("import-export-button", "n_clicks"),
    State("import-export-dropdown", "is_open"),
    Input("import-finished", "data"),
    prevent_initial_call=True,
)
def toggle_popover(n, is_open, import_finished):
    exportable_dbs = []
    if not is_open:
        # Load content
        options = api_client.get_json("/export/database_list")

        exportable_dbs = [
            {"value": option[0], "label": option[1]} for option in options
        ]

    return not is_open, exportable_dbs


@app.callback(
    Output("export-single-button", "disabled"),
    Input("exportable-databases-dropdown", "value"),
    prevent_initial_call=True,
)
def download_single_button_active(selected):
    if selected is not None:
        return False
    return True


@app.callback(
    Output("export-started-notifier", "is_open"),
    Input("export-all-button", "n_clicks"),
    Input("export-single-button", "n_clicks"),
    prevent_initial_call=True,
)
def download_notifier(n, m):
    # Separate callback to display the notifier before the end of the main callback!
    return True


@app.callback(
    Output("aas-export-started-notifier", "is_open"),
    Input("export-aaas-button", "n_clicks"),
    prevent_initial_call=True,
)
def download_notifier_aas(n, m):
    # Separate callback to display the notifier before the end of the main callback!
    return True


@app.callback(
    Output("import-started-notifier", "is_open"),
    Input("import-upload-button", "n_clicks"),
    prevent_initial_call=True,
)
def upload_notifier(n):
    # Separate callback to display the notifier before the end of the main callback!
    return True


@app.callback(
    Output("export-download", "data"),
    Input("export-single-button", "n_clicks"),
    Input("export-all-button", "n_clicks"),
    State("exportable-databases-dropdown", "value"),
    prevent_initial_call=True,
)
def download_export(n, m, selected_db):
    if ctx.triggered_id == "export-single-button":
        logger.info(f"Started export for single database: {selected_db}")
        multi_export = False
    else:
        logger.info("Started export for all databases")
        multi_export = True
    date_time_str = (
        datetime.now()
        .astimezone(
            tz.gettz(get_configuration(group=ConfigGroups.FRONTEND, key="timezone"))
        )
        .strftime(DATETIME_STRF_FORMAT)
    )
    file_name = EXPORT_FILE_NAME_BASE + date_time_str + ".zip"

    file_data = api_client.get_raw(
        relative_path="/export/database_dumps",
        database_iri=selected_db,
        all_databases=multi_export,
    )
    logger.info("Export finished.")
    return dcc.send_bytes(src=file_data, filename=file_name)


@app.callback(
    Output("aas-export-download", "data"),
    Input("export-aas-button", "n_clicks"),
    prevent_initial_call=True,
)
def aas_download_export(_):
    logger.info(f"Started AASX export")

    date_time_str = (
        datetime.now()
        .astimezone(
            tz.gettz(get_configuration(group=ConfigGroups.FRONTEND, key="timezone"))
        )
        .strftime(DATETIME_STRF_FORMAT)
    )
    file_name = AAS_EXPORT_FILE_NAME_BASE + date_time_str + ".aasx"

    file_data = api_client.get_raw(relative_path="/export/aas")
    logger.info("AASX export finished.")
    return dcc.send_bytes(src=file_data, filename=file_name)


@app.callback(
    Output("import-file-selected-info", "children"),
    Output("import-file-selected-info-collapse", "is_open"),
    Output("import-upload-button", "disabled"),
    # Input("upload-import", "contents"),
    Input("upload-import", "filename"),
    # State("upload-import", "last_modified"),
    prevent_initial_call=True,
)
def select_upload_file(filename):
    if filename is not None:
        return filename, True, False
    else:
        return None, False, True


@app.callback(
    Output("upload-import", "filename"),
    Output("import-finished", "data"),
    Input("import-upload-button", "n_clicks"),
    State("upload-import", "filename"),
    State("upload-import", "contents"),
    prevent_initial_call=True,
)
def upload_file(n, file_name: str, file_data):
    logger.info(f"Started import: {file_name} ...")

    if file_name.endswith(".zip"):
        logger.info(f"ZIP file detected. Starting database import...")
        response_body_text = api_client.post(
            relative_path="/import/database_dumps",
            data={"file_name": file_name, "file_data": file_data},
        )
        logger.info("Finished database import.")
    elif file_name.endswith(".aasx"):
        logger.info(f"AASX file detected. Starting AAS import...")
        response_body_text = api_client.post(
            relative_path="/import/aas",
            data={"file_name": file_name, "file_data": file_data},
        )
        logger.info("Finished AASX import.")
    else:
        logger.warn("Uploaded file type does not match allowed ZIP and AASX endings!")

    return None, datetime.now()
