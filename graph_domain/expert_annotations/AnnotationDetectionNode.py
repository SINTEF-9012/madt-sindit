from dataclasses import dataclass
from datetime import datetime

from typing import List

from dataclasses_json import dataclass_json
from py2neo.ogm import Property, Related, RelatedTo

from graph_domain.BaseNode import BaseNode

from graph_domain.expert_annotations.AnnotationInstanceNode import (
    AnnotationInstanceNodeDeep,
)


from graph_domain.factory_graph_types import (
    NodeTypes,
    RelationshipTypes,
)
from backend.exceptions.GraphNotConformantToMetamodelError import (
    GraphNotConformantToMetamodelError,
)
from graph_domain.main_digital_twin.TimeseriesNode import TimeseriesNodeDeep
from util.datetime_utils import (
    datetime_to_neo4j_str,
    neo4j_str_or_datetime_to_datetime,
)

LABEL = NodeTypes.ANNOTATION_DETECTION.value


@dataclass
@dataclass_json
class AnnotationDetectionNodeFlat(BaseNode):
    """
    Flat expert annotation detection node without relationships, only containing properties
    """

    # Identifier for the node-type:
    __primarylabel__ = LABEL

    # Additional properties:
    _confirmation_date_time: str | datetime | None = Property(
        key="confirmation_date_time"
    )

    @property
    def confirmation_date_time(self) -> datetime | None:
        if self._confirmation_date_time is not None:
            return neo4j_str_or_datetime_to_datetime(self._confirmation_date_time)
        else:
            return None

    @confirmation_date_time.setter
    def confirmation_date_time(self, value):
        self._confirmation_date_time = datetime_to_neo4j_str(value)

    _occurance_start_date_time: str | datetime = Property(
        key="occurance_start_date_time"
    )

    @property
    def occurance_start_date_time(self) -> datetime:
        return neo4j_str_or_datetime_to_datetime(self._occurance_start_date_time)

    @occurance_start_date_time.setter
    def occurance_start_date_time(self, value):
        self._occurance_start_date_time = datetime_to_neo4j_str(value)

    _occurance_end_date_time: str | datetime = Property(key="occurance_end_date_time")

    @property
    def occurance_end_date_time(self) -> datetime:
        return neo4j_str_or_datetime_to_datetime(self._occurance_end_date_time)

    @occurance_end_date_time.setter
    def occurance_end_date_time(self, value):
        self._occurance_end_date_time = datetime_to_neo4j_str(value)

    def validate_metamodel_conformance(self):
        """
        Used to validate if the current node (self) and its child elements is conformant to the defined metamodel.
        Raises GraphNotConformantToMetamodelError if there are inconsistencies
        """
        super().validate_metamodel_conformance()

        if self.occurance_start_date_time is None:
            raise GraphNotConformantToMetamodelError(
                self, "Missing occurance start date."
            )

        if self.occurance_end_date_time is None:
            raise GraphNotConformantToMetamodelError(
                self, "Missing occurance end date."
            )


@dataclass
@dataclass_json
class AnnotationDetectionNodeDeep(AnnotationDetectionNodeFlat):
    """
    Deep expert annotation instance node with relationships
    """

    __primarylabel__ = LABEL

    _matched_ts: List[TimeseriesNodeDeep] = RelatedTo(
        TimeseriesNodeDeep,
        RelationshipTypes.MATCHING_TIMESERIES.value,
    )

    @property
    def matched_ts(self) -> List[TimeseriesNodeDeep]:
        return [match for match in self._matched_ts]

    # The OGM framework does not allow constraining to only one item!
    # Can only be one unit (checked by metamodel validator)
    _matching_instance: List[AnnotationInstanceNodeDeep] = Related(
        AnnotationInstanceNodeDeep, RelationshipTypes.MATCHING_INSTANCE.value
    )

    @property
    def matching_instance(self) -> AnnotationInstanceNodeDeep:
        if len(self._matching_instance) > 0:
            return [matching_instance for matching_instance in self._matching_instance][
                0
            ]
        else:
            return None

    # The OGM framework does not allow constraining to only one item!
    # Can only be one unit (checked by metamodel validator)
    _resulting_instance: List[AnnotationInstanceNodeDeep] = Related(
        AnnotationInstanceNodeDeep, RelationshipTypes.CREATED_OUT_OF.value
    )

    @property
    def resulting_instance(self) -> AnnotationInstanceNodeDeep | None:
        if len(self._resulting_instance) > 0:
            return [instance for instance in self._resulting_instance][0]
        else:
            return None

    def validate_metamodel_conformance(self):
        """
        Used to validate if the current node (self) and its child elements is conformant to the defined metamodel.
        Raises GraphNotConformantToMetamodelError if there are inconsistencies
        """
        super().validate_metamodel_conformance()

        if len(self._matched_ts) < 1:
            raise GraphNotConformantToMetamodelError(
                self, "Missing matched timeseries."
            )

        for ts in self.matched_ts:
            ts.validate_metamodel_conformance()

        if len(self._matching_instance) < 1:
            raise GraphNotConformantToMetamodelError(self, "Missing matching instance.")

        if len(self._matching_instance) > 1:
            raise GraphNotConformantToMetamodelError(
                self, "A detection can only refer to one matching instance."
            )
        self.matching_instance.validate_metamodel_conformance()

        if len(self._resulting_instance) > 1:
            raise GraphNotConformantToMetamodelError(
                self, "Only one instance can be created out of a detection."
            )

        if len(self._resulting_instance) == 1:
            self.resulting_instance.validate_metamodel_conformance()
