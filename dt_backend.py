"""
Main entry point for the application layer
Handles the sensor-connections and provides a API
Introducing services for querying the KG
Separated from api.py to avoid circular dependencies with endpoint
files importing the "app" instance.
"""

from datetime import timedelta
import time
import uvicorn

from dateutil import tz
from threading import Thread
from backend.annotation_detection.AnnotationDetectorContainer import (
    AnnotationDetectorContainer,
)
from util.environment_and_configuration import (
    ConfigGroups,
    get_configuration,
)
from backend.api.api import app
from backend.cleanup_thread import start_storage_cleanup_thread
from backend.knowledge_graph.KnowledgeGraphPersistenceService import (
    KnowledgeGraphPersistenceService,
)
from backend.knowledge_graph.dao.AssetNodesDao import AssetsDao
from backend.knowledge_graph.dao.TimeseriesNodesDao import TimeseriesNodesDao
from backend.runtime_connections.RuntimeConnectionContainer import (
    RuntimeConnectionContainer,
)
from backend.specialized_databases.DatabasePersistenceServiceContainer import (
    DatabasePersistenceServiceContainer,
)
from util.log import logger


# Import endpoint files (indirectly used through annotation)


# pylint: disable=unused-import
# noinspection PyUnresolvedReferences
from backend.api.rest_endpoints import status_endpoints

# noinspection PyUnresolvedReferences
from backend.api.rest_endpoints import timeseries_endpoints

# noinspection PyUnresolvedReferences
from backend.api.rest_endpoints import file_endpoints

# noinspection PyUnresolvedReferences
from backend.api.rest_endpoints import asset_endpoints

# noinspection PyUnresolvedReferences
from backend.api.rest_endpoints import annotation_endpoints

# noinspection PyUnresolvedReferences
from backend.api.rest_endpoints import graph_endpoints

# noinspection PyUnresolvedReferences
from backend.api.rest_endpoints import db_import_export_endpoints

# noinspection PyUnresolvedReferences
from backend.api.rest_endpoints import aas_endpoints

# noinspection PyUnresolvedReferences
#vfrom backend.api.rest_endpoints import similarity_pipeline_endpoints

from init_learning_factory_from_cypher_file import (
    import_binary_data,
    setup_knowledge_graph,
)
from util.environment_and_configuration import (
    get_environment_variable,
    get_environment_variable_int,
)

import util.inter_process_cache as cache


# #############################################################################
# Setup sensor connections and timeseries persistence
# #############################################################################


def init_database_data_if_not_available():
    asset_dao = AssetsDao.instance()
    assets_count = asset_dao.get_assets_count()

    if assets_count == 0:
        logger.info(
            "No assets found! Initializing databases in 60 seconds, if not canceled."
        )
        time.sleep(10)

        setup_knowledge_graph()
        import_binary_data()
        # generate_alternative_cad_format()
        logger.info("Finished initilization.")


def refresh_workers():
    runtime_con_container: RuntimeConnectionContainer = (
        RuntimeConnectionContainer.instance()
    )
    detectors_container: AnnotationDetectorContainer = (
        AnnotationDetectorContainer.instance()
    )
    runtime_con_container.refresh_connection_inputs_and_handlers()
    detectors_container.refresh_annotation_detectors()


def refresh_workers_thread_loop():
    while True:
        time.sleep(120)
        logger.info("Refreshing worker services...")

        refresh_workers()

        logger.info("Done refreshing worker services.")


# #############################################################################
# Launch backend
# #############################################################################


if __name__ == "__main__":
    logger.info("Initializing Knowledge Graph...")

    # pylint: disable=W0612
    kg_service = KnowledgeGraphPersistenceService.instance()

    logger.info("Done initializing Knowledge Graph.")

    logger.info("Checking, if data is present...")
    init_database_data_if_not_available()

    logger.info("Initializing specialized databases...")
    db_con_container: DatabasePersistenceServiceContainer = (
        DatabasePersistenceServiceContainer.instance()
    )
    logger.info("Done initializing specialized databases.")

    # logger.info(
    #     "Loading worker services: time-series inputs and connections as well as annotation detectors..."
    # )
    # refresh_workers()
    # logger.info("Done loading worker services.")

    # Thread checking regulary, if timeseries inputs, runtime-connections and annotation detectors have been added / removed
    # workers_refresh_thread = Thread(target=refresh_workers_thread_loop)
    # workers_refresh_thread.start()

    # Start cleanup thread deleting obsolete backups:
    start_storage_cleanup_thread()

    # Start getting the connectivity status for runtime connections
    # RuntimeConnectionContainer.instance().start_active_connections_status_thread()
    # Start getting the connectivity status for runtime connections

    # AnnotationDetectorContainer.instance().start_active_detectors_status_thread()

    # Run fast API
    # noinspection PyTypeChecker
    uvicorn.run(
        "dt_backend:app",
        host=get_environment_variable("FAST_API_HOST"),
        port=get_environment_variable_int("FAST_API_PORT"),
        workers=4,
        access_log=False,
    )
