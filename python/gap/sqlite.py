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

    def populate(self, name, schema, ncols, data, verbose=False):

        qvals = ''.join('?,' * ncols)[:-1]

        if not os.path.exists(self.DB):
            self.logger.info(f"Creating new sqlite database at {self.DB}.")

        with sqlite3.connect(self.DB) as con:
            cur = con.cursor()
            cur.execute(f'''CREATE TABLE IF NOT EXISTS {name}({schema})''')
            cur.executemany(f"INSERT INTO {name} VALUES({qvals})", data)
            con.commit()
        if verbose:
            self.logger.info(
                f"SQLITE: table {name} populated with {len(data)} tuples.")

    def dropAndPopulate(self, name, schema, ncols, data):

        qvals = ''.join('?,' * ncols)[:-1]

        if not os.path.exists(self.DB):
            self.logger.info(f"SQLITE: Creating new sqlite database at {self.DB}.")

        with sqlite3.connect(self.DB) as con:
            cur = con.cursor()
            cur.execute(f"DROP TABLE IF EXISTS {name}")
            cur.execute(f'''CREATE TABLE {name}({schema})''')
            cur.executemany(f"INSERT INTO {name} VALUES({qvals})", data)
            self.logger.info(f"SQLITE: table {name} created and populated.")
            con.commit()

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


    def retrieveGraph(self, entity, valid_mps=None, valid_entities=None):

        table = Template(self.TABLES['raw_graph']['name']) \
            .substitute(entity=entity)
        columns = self.TABLES['raw_graph']['columns']
        columns = [
            Template(c).substitute(entity=entity) for c in columns]

        query = f"SELECT {','.join(columns)} FROM {table} "

        if valid_mps is not None and valid_entities is not None:
            query += 'WHERE '
            if valid_entities is not None:
                valid_entities = [f"'{vf}'" for vf in valid_entities]
                query += f"{entity}_pseudo_id IN ({','.join(valid_entities)}) "
                if valid_mps is not None:
                    valid_mps = [f"'{vf}'" for vf in valid_mps]
                    query += f"AND mp_pseudo_id IN ({','.join(valid_mps)})"
            else:
                valid_mps = [f"'{vf}'" for vf in valid_mps]
                query += f"mp_pseudo_id IN ({','.join(valid_mps)})"

        res = self.retrieve(query)

        mssg = f"SQLITE: found {len(res)} links in "
        mssg += f"mp<>{entity} graph "
        if valid_entities is not None:
            mssg += f"with valid {entity}s."
        self.logger.info(mssg)
        return res

    def retrievePidsFromGraph(self, followers=None):
        graph = self.retrieveGraph(followers)
        mp_graph_pids = [g[0] for g in graph]
        follower_graph_pids = [g[1] for g in graph]
        return mp_graph_pids, follower_graph_pids

    def retrieveTwitterIds(self, entity):
        table = 'lut'
        query = f"SELECT twitter_id FROM {table} WHERE is_{entity}=='1'"
        res = self.retrieve(query)
        mssg = f"SQLITE: found {len(res)} twitter_ids "
        mssg += f"in table {table}."
        self.logger.info(mssg)
        return [r[0] for r in res]

    def retrieveUsersMinIndegree(self, min_indegree):
        query = f"SELECT pseudo_id FROM metadata "
        query += f"WHERE followers >= {min_indegree}"
        res = self.retrieve(query)
        mssg = f"SQLITE: found {len(res)} users with at "
        mssg += f"least {min_indegree} followers."
        self.logger.info(mssg)
        return [r[0] for r in res]

    def getLut(self, entity=None):
        columns = ["twitter_id", "pseudo_id"]
        query = f"SELECT {','.join(columns)} FROM lut"
        if entity:
            query += f" WHERE is_{entity}=='1'"
        res = self.retrieve(query)
        mssg = f"SQLITE: found {len(res)} {entity} users in lut."
        self.logger.info(mssg)
        df = pd.DataFrame(res, columns=columns, dtype=str)
        return df

    def getMpParties(self, surveys, dropna=True):

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
                if g0 > g1:
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
            .dropna()

    def getDescriptions(self, entity, limit=-1):
        table = f"{entity}_metadata"
        columns = ['pseudo_id', 'description']
        query = f"SELECT {','.join(columns)} FROM {table}"
        if limit > 0:
            query += f" LIMIT {limit}"
        res = self.retrieve(query)
        self.logger.info(f"SQLITE: found {len(res)} entries in {table}.")
        return pd.DataFrame(res, columns=columns)

    def getPreprocessedMetadata(
        self, columns=["pseudo_id", "description"], limit=-1):

        table = self.ppSubstitution(
            self.TABLES['preprocessed_metadata']['name'])
        if not columns:
            columns = self.TABLES['preprocessed_metadata']['columns']
        query = f"SELECT {','.join(columns)} FROM {table}"
        if limit > 0:
            query += f" LIMIT {limit}"
        res = self.retrieve(query)
        self.logger.info(f"SQLITE: found {len(res)} entries in {table}.")
        return pd.DataFrame(res, columns=columns)

    def getTwitterIds(self, entity, pseudo_ids=[]):

        table = Template(self.TABLES['lut']['name']) \
            .substitute(entity=entity)
        columns = self.TABLES['lut']['columns']

        query = f"SELECT {','.join(columns)} FROM {table} "

        if pseudo_ids:
            pseudo_ids = [f"'{pid}'" for pid in pseudo_ids]
            query += f"WHERE pseudo_id IN ({','.join(pseudo_ids)})"

        res = self.retrieve(query)

        return pd.DataFrame(res, columns=columns)

    def getAnnotations(self):
        table = f"mp_annotation"
        query = f"SELECT * FROM {table}"
        res = self.retrieve(query)
        columns = self.TABLES['annotation']['columns']
        self.logger.info(f"SQLITE: found {len(res)} entries in {table}.")
        return pd.DataFrame(res, columns=columns)

    def getPartiesMapping(self, surveys):

        table = self.TABLES['mapping']['name']
        precolumns = deepcopy(self.TABLES['mapping']['columns'])
        precolumns.remove('MMS_party_acronym')
        columns = ['MMS_party_acronym']
        for cc in precolumns:
            if any([cc.startswith(ss.upper()) for ss in surveys]):
                columns.append(cc)
        query = f"SELECT {','.join(columns)} FROM {table}"
        res = self.retrieve(query)
        self.logger.info(f"SQLITE: found {len(res)} entries in {table}.")
        return pd.DataFrame(res, columns=columns)

    def getEnrichedMetadata(self, columns=None):

        table = self.ppSubstitution(self.TABLES['enrichment']['name'])
        if not columns:
            columns = self.TABLES['enrichment']['columns']
        query = f"SELECT {','.join(columns)} FROM {table}"
        res = self.retrieve(query)
        self.logger.info(f"SQLITE: found {len(res)} entries in {table}.")
        return pd.DataFrame(res, columns=columns)

    def getSentimentsPreprocessedMetadata(self, columns=None):

        table = self.ppSubstitution(self.TABLES['sentiments']['name'])
        if not columns:
            columns = self.TABLES['sentiments']['columns']
        query = f"SELECT {','.join(columns)} FROM {table}"
        res = self.retrieve(query)
        self.logger.info(f"SQLITE: found {len(res)} entries in {table}.")
        return pd.DataFrame(res, columns=columns)

    def checkTranslationsTableExists(self):
        table = self.ppSubstitution(self.TABLES['english_translation']['name'])
        return self.checkTableExists(table)

    def checkLLMAnnotationTableExists(self, issue):
        table = Template(self.TABLES['llm_answers']['name']).substitute(
            issue=issue,
            sources_min_followers=self.NB_MIN_FOLLOWERS,
            sources_min_outdegree=self.MIN_OUTDEGREE
        )
        return self.checkTableExists(table)

    def getEnglishTranslationsPreprocessedMetadata(
        self, columns=None, limit=-1):

        table = self.ppSubstitution(self.TABLES['english_translation']['name'])
        if not columns:
            columns = self.TABLES['english_translation']['columns']
        query = f"SELECT {','.join(columns)} FROM {table}"
        if limit > 0:
            query += f" LIMIT {limit}"
        res = self.retrieve(query)
        self.logger.info(
            f"SQLITE: Found {len(res)} descriptions in {table} table.")
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

    def getMetadata(self, columns=[]):
        table = self.TABLES['metadata']['name']
        if not columns:
            columns = self.TABLES['metadata']['columns']
        query = f"SELECT {','.join(columns)} FROM {table}"
        res = self.retrieve(query)
        self.logger.info(f"SQLITE: found {len(res)} entries in {table}.")
        return pd.DataFrame(res, columns=columns)

    def getLLMAnnotation(self, issue, limit=-1):
        table = Template(self.TABLES['llm_answers']['name']).substitute(
            issue=issue,
            sources_min_followers=self.NB_MIN_FOLLOWERS,
            sources_min_outdegree=self.MIN_OUTDEGREE)
        columns = [
            Template(c).substitute(issue=issue)
               for c in self.TABLES['llm_answers']['columns']]
        query = f"SELECT {','.join(columns)} FROM {table}"
        res = self.retrieve(query)
        self.logger.info(
            f"SQLITE: Found {len(res)} descriptions in {table} table.")
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
