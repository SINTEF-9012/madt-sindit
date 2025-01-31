from datetime import datetime
import os
from sqlite3 import Cursor
import time
import shutil
from dateutil import tz
from util.environment_and_configuration import (
    ConfigGroups,
    get_configuration,
    get_environment_variable,
)
from typing import Any
import py2neo
import py2neo.ogm as ogm
from py2neo.errors import ConnectionBroken
from neo4j import GraphDatabase
from neo4j_backup import Extractor, Importer
from util.log import logger


SAFETY_BACKUP_PATH = "safety_backups/neo4j/"
DATETIME_STRF_FORMAT = "%Y_%m_%d_%H_%M_%S_%f"


class KnowledgeGraphPersistenceService(object):

    __instance = None

    @classmethod
    def instance(cls):
        if cls.__instance is None:
            cls()
        return cls.__instance

    def __init__(self):
        if self.__instance is not None:
            raise Exception("Singleton instantiated multiple times!")

        KnowledgeGraphPersistenceService.__instance: KnowledgeGraphPersistenceService = (
            self
        )
        self.connected = False
        self._connect()

    def _connect(self):
        self.uri_without_protocol = f"{get_environment_variable(key='NEO4J_DB_HOST', optional=False)}:{get_environment_variable(key='NEO4J_DB_PORT', optional=False)}"
        self.bolt_uri = f"bolt://{self.uri_without_protocol}"
        self.neo4j_uri = f"neo4j://{self.uri_without_protocol}"
        self.graph_name = get_environment_variable(key="NEO4J_DB_NAME", optional=False)
        self.user_name = get_environment_variable(key="NEO4J_DB_USER", optional=True)
        self.pw = get_environment_variable(key="NEO4J_DB_PW", optional=True)
        if self.user_name is not None and self.pw is not None:
            self.auth = (self.user_name, self.pw)
        elif self.user_name is not None:
            self.auth = (self.user_name, None)
        else:
            self.auth = None
        while not self.connected:
            try:
                logger.info("Connecting to Neo4J...")

                logger.info(
                    f"Trying to connect to uri {self.bolt_uri}. "
                    f"Using a user_name: {self.user_name is not None}, using a password: {self.pw is not None}"
                )

                self.graph = py2neo.Graph(
                    self.bolt_uri, name=self.graph_name, auth=self.auth
                )

                self._repo = ogm.Repository(
                    self.bolt_uri, name=self.graph_name, auth=self.auth
                )
                logger.info("Successfully connected to Neo4J!")
                self.connected = True
            except py2neo.ConnectionUnavailable:
                logger.info(
                    "Neo4J graph unavailable or Authentication invalid! Trying again in 10 seconds..."
                )
                time.sleep(10)

    def graph_run(self, cypher: any) -> Cursor:
        """Executes the graph.run command.
        Handles connection errors.
        """
        while True:
            try:
                return self.graph.run(cypher)
            except ConnectionBroken:
                self.connected = False
                self._connect()

    def graph_evaluate(self, cypher: Any) -> Any:
        """Executes the graph.evaluate command
        Handles connection errors.
        """
        while True:
            try:
                return self.graph.evaluate(cypher)
            except ConnectionBroken:
                self.connected = False
                self._connect()

    def graph_push(self, subgraph: Any) -> None:
        """Executes the graph.push command
        Handles connection errors.
        """
        while True:
            try:
                return self.graph.push(subgraph)
            except ConnectionBroken:
                self.connected = False
                self._connect()

    def graph_create(self, subgraph: Any) -> None:
        """Executes the graph.create command
        Handles connection errors.
        """
        while True:
            try:
                return self.graph.create(subgraph)
            except ConnectionBroken:
                self.connected = False
                self._connect()

    def graph_merge(self, subgraph: Any, label: Any | None = None) -> None:
        """Executes the graph.merge command
        Handles connection errors.
        """
        while True:
            try:
                return self.graph.merge(subgraph=subgraph, label=label)
            except ConnectionBroken:
                self.connected = False
                self._connect()

    def repo_match(self, model: Any, primary_value: Any | None = None) -> Any:
        """Executes the repo.match command
        Handles connection errors.
        """
        while True:
            try:
                return self._repo.match(model=model, primary_value=primary_value)
            except ConnectionBroken:
                self.connected = False
                self._connect()

    def backup(self, backup_path: str):
        logger.info("Backing up neo4j...")

        driver = GraphDatabase.driver(
            self.neo4j_uri,
            auth=self.auth,
            encrypted=False,
            trust="TRUST_ALL_CERTIFICATES",
        )

        extractor = Extractor(
            project_dir=backup_path,
            driver=driver,
            database=self.graph_name,
            input_yes=False,
            compress=True,
        )
        extractor.extract_data()

        logger.info("Finished backing up neo4j.")

    def restore(self, backup_path: str):
        logger.info("Restoring neo4j...")

        logger.info("Check, if the graph is empty...")
        contents = self.graph.match()
        if len(contents) > 0:
            logger.info("Creating a safety backup before overwriting the database...")
            safety_path = SAFETY_BACKUP_PATH + datetime.now().astimezone(
                tz.gettz(get_configuration(group=ConfigGroups.FRONTEND, key="timezone"))
            ).strftime(DATETIME_STRF_FORMAT)
            os.makedirs(safety_path)
            self.backup(backup_path=safety_path + "/neo4j")
            logger.info("Zipping the safety backup...")
            zip_file_path = safety_path + "/neo4j"
            shutil.make_archive(zip_file_path, "zip", safety_path + "/neo4j")
            shutil.rmtree(safety_path + "/neo4j")
            logger.info("Finished zipping the safety backup.")
            # Delete everything:
            logger.info("Deleting everything...")
            self.graph.delete_all()
            logger.info("Deleted everything.")
        logger.info("Restoring...")
        driver = GraphDatabase.driver(
            self.neo4j_uri,
            auth=self.auth,
            encrypted=False,
            trust="TRUST_ALL_CERTIFICATES",
        )

        importer = Importer(
            project_dir=backup_path,
            driver=driver,
            database=self.graph_name,
            input_yes=False,
        )
        importer.import_data()

        logger.info("Finished restoring neo4j.")
