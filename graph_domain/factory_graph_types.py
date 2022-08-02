from enum import Enum
from itertools import chain


class NodeTypes(Enum):
    ASSET = "ASSET"
    TIMESERIES_INPUT = "TIMESERIES"
    SUPPLEMENTARY_FILE = "SUPPLEMENTARY_FILE"
    DATABASE_CONNECTION = "DATABASE_CONNECTION"
    RUNTIME_CONNECTION = "RUNTIME_CONNECTION"
    UNIT = "UNIT"
    TIMESERIES_CLUSTER = "TIMESERIES_CLUSTER"


class RelationshipTypes(Enum):
    HAS_TIMESERIES = "HAS_TIMESERIES"
    HAS_SUPPLEMENTARY_FILE = "HAS_SUPPLEMENTARY_FILE"
    TIMESERIES_DB_ACCESS = "TIMESERIES_DB_ACCESS"
    FILE_DB_ACCESS = "FILE_DB_ACCESS"
    SECONDARY_FORMAT = "SECONDARY_FORMAT"
    RUNTIME_ACCESS = "RUNTIME_ACCESS"
    HAS_UNIT = "HAS_UNIT"
    PART_OF_TS_CLUSTER = "PART_OF_TS_CLUSTER"
    ASSET_SIMILARITY = "ASSET_SIMILARITY"


NODE_TYPE_STRINGS = [nd_type.value for nd_type in NodeTypes]
RELATIONSHIP_TYPE_STRINGS = [rl_type.value for rl_type in RelationshipTypes]
ELEMENT_TYPE_STRINGS = list(chain(NODE_TYPE_STRINGS, RELATIONSHIP_TYPE_STRINGS))

UNSPECIFIED_LABEL = "UNSPECIFIED"

RELATIONSHIP_TYPES_FOR_NODE_TYPE = {
    NodeTypes.ASSET.value: [
        RelationshipTypes.HAS_TIMESERIES.value,
        RelationshipTypes.HAS_SUPPLEMENTARY_FILE.value,
    ],
    NodeTypes.TIMESERIES_INPUT.value: [
        RelationshipTypes.HAS_TIMESERIES.value,
        RelationshipTypes.HAS_UNIT.value,
        RelationshipTypes.RUNTIME_ACCESS.value,
        RelationshipTypes.TIMESERIES_DB_ACCESS.value,
        RelationshipTypes.PART_OF_TS_CLUSTER.value,
    ],
    NodeTypes.SUPPLEMENTARY_FILE.value: [
        RelationshipTypes.HAS_SUPPLEMENTARY_FILE.value,
        RelationshipTypes.FILE_DB_ACCESS.value,
        RelationshipTypes.SECONDARY_FORMAT.value,
    ],
    NodeTypes.DATABASE_CONNECTION.value: [
        RelationshipTypes.TIMESERIES_DB_ACCESS.value,
        RelationshipTypes.FILE_DB_ACCESS.value,
    ],
    NodeTypes.UNIT.value: [RelationshipTypes.HAS_UNIT.value],
    NodeTypes.RUNTIME_CONNECTION.value: [RelationshipTypes.RUNTIME_ACCESS.value],
    NodeTypes.TIMESERIES_CLUSTER.value: [RelationshipTypes.PART_OF_TS_CLUSTER.value],
}
