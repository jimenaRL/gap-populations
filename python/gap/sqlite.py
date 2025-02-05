import os
import sqlite3
from copy import deepcopy
from string import Template
from functools import lru_cache


import numpy as np
import pandas as pd

# Keep track of 3 different messages and then warn again
@lru_cache(3)
def warn_once(logger, msg):
    logger.info(msg)

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

        mssg = f"SQLITE: Found {len(res)} links in preprocessed"
        mssg += f"mp<>follower graph "
        self.logger.info(mssg)
        return res

    def getAvailableSurveys(self):
        name = 'party_mapping'
        if not self.checkTableExists(name):
            raise ValueError(f"Table {name} doesn't exist at {self.DB}")
        res = self.retrieve(f"PRAGMA table_info({name});")
        surveys = [r[1].split('_party_acronym')[0].lower() for r in res]
        surveys.remove('epo')
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

    def getPartiesAttitudes(self, survey, dims_names, missing_values_strategy):


        valid_strategies = {'drop_parties', 'drop_dims'}
        if not missing_values_strategy in valid_strategies:
            error = "Wrong value for parameter missing_values_strategy "
            error += f"({missing_values_strategy}). "
            error += f"Must be one of {valid_strategies}."
            raise ValueError(error)

        survey_col = f'{survey.upper()}_party_acronym'
        columns = ['EPO_party_acronym', survey_col]+list(dims_names)
        table = Template(self.TABLES['attitude']['name']) \
            .substitute(attitude=survey)
        query = f"SELECT {','.join(columns)} FROM {table}"
        res = self.retrieve(query)
        dtypes = {'EPO_party_acronym': str,survey_col: str}
        df = pd.DataFrame(res, columns=columns)
        parties = set(df[survey_col].tolist())


        def remove_data(df, bad_map, missing_values_strategy):
            bad_df = bad_map(df)
            nb_bad_entries = bad_df.sum().sum()
            if nb_bad_entries > 0:

                dims_to_drop = df.columns[(bad_df.sum(axis=0) > 0)].tolist()
                temp = df[['EPO_party_acronym'] + dims_to_drop]

                # Drop rows with blanck spaces values.
                if missing_values_strategy == 'drop_parties':
                    df = df[bad_map(df[dims_names]).sum(axis=1) == 0]
                    dropped_parties = parties - set(df[survey_col].tolist())
                    info = f"SQLITE: dropping {len(dropped_parties)} parties "
                    info += f"{dropped_parties}, because corresponding rows "

                # Drop columns with blanck spaces values.
                else: # missing_values_strategy == 'drop_dims'
                    df = df.drop(dims_to_drop, axis=1)
                    info = f"SQLITE: dropping {len(dims_to_drop)} atittudinal dimensions "
                    info += f"{dims_to_drop}, because corresponding columns "

                info += "in survey have blanck or empty spaces for values."
                info += f"\n{temp}\n"
                info += f"Left {df.shape[0]} parties and {df.shape[1] - 2} dims."
                self.logger.info(info)

            return df

        # Deal with blanck values in survey
        df = remove_data(df, lambda df: (df == ' '), missing_values_strategy)
        # Deal with empty (NAN) values in survey
        df = remove_data(df, lambda df: df.isna(), missing_values_strategy)

        dims_names = set(df.columns) - {'EPO_party_acronym', survey_col}
        dtypes.update({d: np.float32 for d in dims_names})
        return df \
            .astype(dtypes) \
            .dropna(axis=1)

    def getAnnotations(self):
        table = f"mp_annotation"
        query = f"SELECT * FROM {table}"
        res = self.retrieve(query)
        columns = self.TABLES['annotation']['columns']
        m = f"SQLITE: Found {len(res)} entries in {table}."
        warn_once(self.logger, m)
        return pd.DataFrame(res, columns=columns)

    def getPartiesMapping(self, surveys, verbose=False):

        table = self.TABLES['mapping']['name']
        precolumns = deepcopy(self.TABLES['mapping']['columns'])
        precolumns.remove('EPO_party_acronym')
        columns = ['EPO_party_acronym']
        for cc in precolumns:
            if any([cc.startswith(ss.upper()) for ss in surveys]):
                columns.append(cc)
        query = f"SELECT {','.join(columns)} FROM {table}"
        res = self.retrieve(query)
        if verbose:
            m = f"SQLITE: Found {len(res)} entries in {table}."
            warn_once(self.logger, m)
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
        m = f"SQLITE: Found {len(res)} entries in {table}."
        warn_once(self.logger, m)
        return pd.DataFrame(res, columns=columns)

    def getLLMLabels(self, limit=-1, allow_missing=True):
        table = Template(self.TABLES['llm_labels']['name']).substitute(
            sources_min_followers=self.NB_MIN_FOLLOWERS,
            sources_min_outdegree=self.MIN_OUTDEGREE)
        # check available llm labels
        table_info = self.retrieve(f"PRAGMA table_info({table});")
        available_cols = [i[1] for i in table_info]
        columns = self.TABLES['llm_labels']['columns']
        if allow_missing:
            columns = available_cols
        else:
            columns = self.TABLES['llm_labels']['columns']
        query = f"SELECT * FROM {table}"
        res = self.retrieve(query)
        m = f"SQLITE: Found {len(res)} descriptions in {table} table."
        warn_once(self.logger, m)
        return pd.DataFrame(res, columns=columns)
