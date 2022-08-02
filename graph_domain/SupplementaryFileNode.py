from dataclasses import dataclass
from enum import Enum
from typing import List

from dataclasses_json import dataclass_json
from py2neo.ogm import Property, RelatedTo

from graph_domain.BaseNode import BaseNode
from graph_domain.DatabaseConnectionNode import DatabaseConnectionNode
from graph_domain.ExtractedKeywordNode import ExtractedKeywordNode
from graph_domain.RuntimeConnectionNode import RuntimeConnectionNode
from graph_domain.UnitNode import UnitNode
from graph_domain.factory_graph_types import NodeTypes, RelationshipTypes
from backend.exceptions.GraphNotConformantToMetamodelError import (
    GraphNotConformantToMetamodelError,
)

LABEL = NodeTypes.SUPPLEMENTARY_FILE.value
DB_CONNECTION_RELATIONSHIP_LABEL = RelationshipTypes.FILE_DB_ACCESS.value
SECONDARY_FORMAT_RELATIONSHIP_LABEL = RelationshipTypes.SECONDARY_FORMAT.value
EXTRACTED_KEYWORD_RELATIONSHIP_LABEL = RelationshipTypes.KEYWORD_EXTRACTION.value


class SupplementaryFileTypes(Enum):
    IMAGE_JPG = "IMAGE_JPG"
    CAD_STEP = "CAD_STEP"
    CAD_STL = "CAD_STL"
    DOCUMENT_PDF = "DOCUMENT_PDF"


SUPPLEMENTARY_FILE_TYPES = [file_type.value for file_type in SupplementaryFileTypes]


@dataclass
@dataclass_json
class SupplementaryFileNodeFlat(BaseNode):
    """
    Flat supplementary file node without relationships, only containing properties
    """

    # Identifier for the node-type:
    __primarylabel__ = LABEL

    # Additional properties:
    file_name: str = Property()

    # Type of the value stored per time
    file_type: str = Property(
        key="type", default=SupplementaryFileTypes.DOCUMENT_PDF.value
    )

    def validate_metamodel_conformance(self):
        """
        Used to validate if the current node (self) and its child elements is conformant to the defined metamodel.
        Raises GraphNotConformantToMetamodelError if there are inconsistencies
        """
        super().validate_metamodel_conformance()

        if self.file_type is None:
            raise GraphNotConformantToMetamodelError(self, f"Missing file type.")

        if not self.file_type in SUPPLEMENTARY_FILE_TYPES:
            raise GraphNotConformantToMetamodelError(
                self,
                f"Unrecognized file type: {self.file_type}. Known types: {SUPPLEMENTARY_FILE_TYPES}.",
            )

        if self.file_name is None:
            raise GraphNotConformantToMetamodelError(self, f"Missing file name")


@dataclass
@dataclass_json
class SupplementaryFileNodeDeepNonRecursive(SupplementaryFileNodeFlat):
    """
    Deep supplementary file node with relationships, but no recursive attributes
    """

    __primarylabel__ = LABEL

    # The OGM framework does not allow constraining to only one item!
    # Can only be one unit (checked by metamodel validator)
    _db_connections: List[DatabaseConnectionNode] = RelatedTo(
        DatabaseConnectionNode, DB_CONNECTION_RELATIONSHIP_LABEL
    )

    @property
    def db_connection(self) -> DatabaseConnectionNode:
        return [connection for connection in self._db_connections][0]

    _extracted_keywords: List[ExtractedKeywordNode] = RelatedTo(
        ExtractedKeywordNode, EXTRACTED_KEYWORD_RELATIONSHIP_LABEL
    )

    @property
    def extracted_keywords(self) -> DatabaseConnectionNode:
        return [keyword for keyword in self._extracted_keywords]

    def validate_metamodel_conformance(self):
        """
        Used to validate if the current node (self) and its child elements is conformant to the defined metamodel.
        Raises GraphNotConformantToMetamodelError if there are inconsistencies
        """
        super().validate_metamodel_conformance()

        if not len(self._db_connections) == 1:
            raise GraphNotConformantToMetamodelError(
                self,
                f"Invalid number of referenced database connections: {len(self._db_connections)}",
            )

        self.db_connection.validate_metamodel_conformance()

        for keyword in self._extracted_keywords:
            keyword.validate_metamodel_conformance()


@dataclass
@dataclass_json
class SupplementaryFileNodeDeep(SupplementaryFileNodeDeepNonRecursive):
    """
    Deep supplementary file node with relationships
    """

    __primarylabel__ = LABEL

    _secondary_formats: List[SupplementaryFileNodeDeepNonRecursive] = RelatedTo(
        SupplementaryFileNodeDeepNonRecursive, SECONDARY_FORMAT_RELATIONSHIP_LABEL
    )

    @property
    def secondary_formats(self) -> List[SupplementaryFileNodeDeepNonRecursive]:
        return [suppl_file for suppl_file in self._secondary_formats]

    def validate_metamodel_conformance(self):
        """
        Used to validate if the current node (self) and its child elements is conformant to the defined metamodel.
        Raises GraphNotConformantToMetamodelError if there are inconsistencies
        """
        super().validate_metamodel_conformance()

        if not len(self._db_connections) == 1:
            raise GraphNotConformantToMetamodelError(
                self,
                f"Invalid number of referenced database connections: {len(self._db_connections)}",
            )

        self.db_connection.validate_metamodel_conformance()

        for suppl_file in self.secondary_formats:
            suppl_file.validate_metamodel_conformance()
