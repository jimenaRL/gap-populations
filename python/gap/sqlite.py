import os
import sqlite3
import numpy as np
import pandas as pd
from string import Template
from copy import deepcopy


class SQLite:

    def __init__(
        self,
        db_path,
        tables,
        sources_min_followers,
        sources_min_outdegree,
        logger,
        country):

        self.country = country
        self.DB = os.path.abspath(db_path)
        self.TABLES = tables
        self.NB_MIN_FOLLOWERS =  sources_min_followers
        self.MIN_OUTDEGREE = sources_min_outdegree
        self.logger = logger

    def ppSubstitution(self, string_):
        return Template(string_).substitute(
            sources_min_followers=self.NB_MIN_FOLLOWERS,
            sources_min_outdegree=self.MIN_OUTDEGREE
        )

    def checkTableExists(self, name):

        query = f"""
        SELECT EXISTS (
            SELECT
                name
            FROM
                sqlite_master
            WHERE
                type='table' AND
                name='{name}'
        )"""

        with sqlite3.connect(self.DB) as con:
            cur = con.cursor()
            cur.execute(query)
            res = cur.fetchall()

        return res[0][0] == 1


    def get_tables(self):
        with sqlite3.connect(self.DB) as con:
            res = con.execute(
                "SELECT name FROM sqlite_master WHERE type='table'")
            tables = [name[0] for name in res]
        return tables

    def retrieve(self, query, verbose=False):

        if not os.path.exists(self.DB):
            raise FileNotFoundError(
                f"Unnable to find database at: '{self.DB}'.")

        if verbose:
            self.logger.info(
                f"SQLITE: Quering sqlite db at {self.DB} with `{query[:100]}`... ")

        with sqlite3.connect(self.DB) as con:
            cur = con.cursor()
            cur.execute(query)
            res = cur.fetchall()

        return res

    def getPreprocessedGraph(self, sources_min_followers, sources_min_outdegree):

        name = self.TABLES[f'preprocessed_graph']['name']
        entity = 'follower'
        table = Template(name).substitute(
            entity=entity,
            sources_min_followers=sources_min_followers,
            sources_min_outdegree=sources_min_outdegree)

        query = f"SELECT * FROM {table} "

        res = self.retrieve(query)

        mssg = f"SQLITE: found {len(res)} links in preprocessed"
        mssg += f"mp<>follower graph "
        self.logger.info(mssg)
        return res

    def getAvailableSurveys(self):
        res = self.retrieve("PRAGMA table_info(party_mapping);")
        surveys = [r[1].split('_party_acronym')[0].lower() for r in res]
        surveys.remove('mms')
        return surveys

    def getNParties(self, survey):
        surveycol = f'{survey.upper()}_party_acronym'
        parties_mapping = self.getPartiesMapping([survey])
        return parties_mapping[surveycol].notna().sum()

    def retrievePidsFromGraph(self, followers=None):
        graph = self.retrieveGraph(followers)
        mp_graph_pids = [g[0] for g in graph]
        follower_graph_pids = [g[1] for g in graph]
        return mp_graph_pids, follower_graph_pids

    def getMpParties(self, surveys, dropna=True, verbose=False):

        table = self.TABLES['party']['name']
        dtypes = str

        survey_columns = [f'{s.upper()}_party_acronym' for s in surveys]
        columns = ['mp_pseudo_id'] + survey_columns

        query = f"SELECT {','.join(columns)} FROM {table}"
        res = self.retrieve(query)

        targets_groups = pd.DataFrame(res, columns=columns)

        if dropna:
            for survey_column in survey_columns:
                g0 = len(targets_groups)
                mps_with_party_annotation = ~targets_groups[survey_column].isna()
                targets_groups = targets_groups[mps_with_party_annotation]
                g1 = len(targets_groups)
                if g0 > g1 and verbose:
                    mssg = f"SQLITE: Dropped {g0 - g1} mps with no "
                    mssg += f"values in {survey_column}."
                    self.logger.info(mssg)
            return targets_groups[['mp_pseudo_id']+survey_columns].astype(dtypes)

        return targets_groups[['mp_pseudo_id']+survey_columns]

    def getPartiesAttitudes(self, survey, dims_names):

        survey_col = f'{survey.upper()}_party_acronym'
        columns = ['MMS_party_acronym', survey_col]+list(dims_names)
        table = Template(self.TABLES['attitude']['name']) \
            .substitute(attitude=survey)
        query = f"SELECT {','.join(columns)} FROM {table}"

        res = self.retrieve(query)
        dtypes = {
            'MMS_party_acronym': str,
            survey_col: str
        }
        dtypes.update({d: np.float32 for d in dims_names})

        df = pd.DataFrame(res, columns=columns)

        # HOT FIX : drop rows with blanck spaces values.
        # This happens for some dimensions in GPS2019
        l0 = len(df)
        df = df[(df[dims_names] == ' ').sum(axis=1) == 0]
        l1 = len(df)
        if l1 < l0:
            self.logger.info("""
                SQLITE: HOT FIX drop rows with blanck spaces values.
                This happens for some dimensions in GPS2019
                """)

        return df \
            .astype(dtypes) \
            .dropna(axis=1)

    def getAnnotations(self):
        table = f"mp_annotation"
        query = f"SELECT * FROM {table}"
        res = self.retrieve(query)
        columns = self.TABLES['annotation']['columns']
        self.logger.info(f"SQLITE: found {len(res)} entries in {table}.")
        return pd.DataFrame(res, columns=columns)

    def getPartiesMapping(self, surveys, verbose=False):

        table = self.TABLES['mapping']['name']
        precolumns = deepcopy(self.TABLES['mapping']['columns'])
        precolumns.remove('MMS_party_acronym')
        columns = ['MMS_party_acronym']
        for cc in precolumns:
            if any([cc.startswith(ss.upper()) for ss in surveys]):
                columns.append(cc)
        query = f"SELECT {','.join(columns)} FROM {table}"
        res = self.retrieve(query)
        if verbose:
            self.logger.info(f"SQLITE: found {len(res)} entries in {table}.")
        return pd.DataFrame(res, columns=columns)

    def getKeywordsLabels(self, limit=-1):

        table = Template(self.TABLES['keywords']['name']).substitute(
            sources_min_followers=self.NB_MIN_FOLLOWERS,
            sources_min_outdegree=self.MIN_OUTDEGREE)
        columns = self.TABLES['keywords']['columns']
        query = f"SELECT {','.join(columns)} FROM {table}"
        if limit > 0:
            query += f" LIMIT {limit}"
        res = self.retrieve(query)
        self.logger.info(f"SQLITE: found {len(res)} entries in {table}.")
        return pd.DataFrame(res, columns=columns)

    def getLLMLabels(self, limit=-1):
        table = Template(self.TABLES['llm_labels']['name']).substitute(
            sources_min_followers=self.NB_MIN_FOLLOWERS,
            sources_min_outdegree=self.MIN_OUTDEGREE)
        columns = self.TABLES['llm_labels']['columns']
        query = f"SELECT {','.join(columns)} FROM {table}"
        res = self.retrieve(query)
        self.logger.info(
            f"SQLITE: Found {len(res)} descriptions in {table} table.")
        return pd.DataFrame(res, columns=columns)
