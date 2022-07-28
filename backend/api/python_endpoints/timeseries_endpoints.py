import json
from datetime import datetime, timedelta
import pandas as pd

from backend.exceptions.IdNotFoundException import IdNotFoundException
from backend.knowledge_graph.KnowledgeGraphPersistenceService import (
    KnowledgeGraphPersistenceService,
)
from backend.knowledge_graph.dao.DatabaseConnectionsDao import DatabaseConnectionsDao
from backend.specialized_databases.DatabasePersistenceServiceContainer import (
    DatabasePersistenceServiceContainer,
)
from backend.specialized_databases.timeseries.TimeseriesPersistenceService import (
    TimeseriesPersistenceService,
)
from backend.specialized_databases.timeseries.influx_db.InfluxDbPersistenceService import (
    InfluxDbPersistenceService,
)


DB_SERVICE_CONTAINER: DatabasePersistenceServiceContainer = (
    DatabasePersistenceServiceContainer.instance()
)
DB_CON_NODE_DAO: DatabaseConnectionsDao = DatabaseConnectionsDao.instance()


def get_timeseries_current_range(
    iri: str,
    duration: float,
    aggregation_window_ms: int | None = None,
):
    """
    Queries the current measurements for the given duration up to the current time.
    :raises IdNotFoundException: If no data is available for that id at the current time
    :param id_uri:
    :param duration: timespan to query in seconds
    :return: Pandas Dataframe serialized to JSON featuring the columns "time" and "value"
    """
    return get_timeseries_range(
        iri=iri,
        duration=duration,
        date_time_str=datetime.now().isoformat(),
        aggregation_window_ms=aggregation_window_ms,
    )


def get_timeseries_range(
    iri: str,
    date_time: datetime,
    duration: float,
    aggregation_window_ms: int | None = None,
):
    """
    Queries the measurements for the given duration up to the given date and time.
    :raises IdNotFoundException: If no data is available for that id at the current time
    :param id_uri:
    :param date_time: date and time to be observed in iso format
    :param duration: timespan to query in seconds
    :return: Pandas Dataframe serialized to JSON featuring the columns "time" and "value"
    """

    try:
        # Get related timeseries-database service:
        ts_con_node: DatabaseConnectionsDao = (
            DB_CON_NODE_DAO.get_database_connection_for_node(iri)
        )

        if ts_con_node is None:
            print("Timeseries requested, but database connection node does not exist")
            return pd.DataFrame(columns=["time", "value"])

        ts_service: TimeseriesPersistenceService = (
            DB_SERVICE_CONTAINER.get_persistence_service(ts_con_node.iri)
        )

        # Read the actual measurements:
        readings_df = ts_service.read_period_to_dataframe(
            id_uri=iri,
            begin_time=date_time - timedelta(seconds=duration),
            end_time=date_time,
            aggregation_window_ms=aggregation_window_ms,
        )

        return readings_df
    except IdNotFoundException:
        return pd.DataFrame(columns=["time", "value"])


def get_timeseries_entries_count(iri: str, date_time_str: str, duration: float):
    """

    :raises IdNotFoundException: If no data is available for that id at the current time
    :param id_uri:
    :param date_time: date and time to be observed in iso format
    :param duration: timespan to query in seconds
    :return: Count of entries in that given range
    """
    date_time = datetime.fromisoformat(date_time_str)

    try:
        # Get related timeseries-database service:
        ts_con_node: DatabaseConnectionsDao = (
            DB_CON_NODE_DAO.get_database_connection_for_node(iri)
        )

        ts_service: TimeseriesPersistenceService = (
            DB_SERVICE_CONTAINER.get_persistence_service(ts_con_node.iri)
        )

        return ts_service.count_entries_for_period(
            id_uri=iri,
            begin_time=date_time - timedelta(seconds=duration),
            end_time=date_time,
        )
    except IdNotFoundException:
        return 0
