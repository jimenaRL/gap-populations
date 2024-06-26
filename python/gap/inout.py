import os
import yaml
from functools import lru_cache

import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix

def csvExport(df, path):

    df.to_csv(
        path+'.csv',
        index=False,
        sep=',',
        encoding='utf-8',
        lineterminator='\n')

def excelExport(df, path, sheet_name):
    # HOTFIX
    try:
        df.to_excel(
            path+'.xlsx',
            index=False,
            sheet_name=sheet_name,
            engine='xlsxwriter',
            float_format="%.2f")
    except:
        df = df.assign(
            description=df.description.apply(lambda s: s.replace('nµ', '')))
        df.to_excel(
            path+'.xlsx',
            index=False,
            sheet_name=sheet_name,
            engine='xlsxwriter',
            float_format="%.2f")

# Keep track of 3 different messages and then warn again
@lru_cache(3)
def warn_once(logger, msg):
    logger.info(msg)

class InOut:

    def __init__(
        self,
        params,
        country,
        n_latent_dimensions,
        output,
        survey,
        logger,
        ):

        self.params = params
        self.country = country
        self.survey = survey
        self.logger = logger
        self.setBasepath(output)
        self.setEmbFolder(n_latent_dimensions)
        self.setAttFolder(survey)

    def setBasepath(self, output):

        emb_folder = f"min_followers_{self.params['sources_min_followers']}"
        emb_folder += f"_min_outdegree_{self.params['sources_min_outdegree']}"

        self.basepath = os.path.join(output, self.country, emb_folder)

        os.makedirs(self.basepath, exist_ok=True)

        config_file = os.path.join(self.basepath, 'config.yaml')

        if not os.path.exists(config_file):
            with open(config_file, 'w') as file:
                yaml.dump(self.params, file)
            self.logger.info(f"INOUT: YAML config saved at {self.basepath}.")

    def setEmbFolder(self, n_latent_dimensions):
        self.emb_folder = os.path.join(
            self.basepath, f"ideN_{n_latent_dimensions}")
        os.makedirs(self.emb_folder, exist_ok=True)

    def setAttFolder(self, survey):
        self.att_folder = os.path.join(self.emb_folder, survey)
        os.makedirs(self.att_folder, exist_ok=True)


    def load_ide_embeddings(self):

        warn_once(
            self.logger,
            f"INOUT: Ideological embeddings loaded from {self.emb_folder}.")

        ide_sources = pd.read_csv(os.path.join(self.emb_folder, 'ide_sources.csv'))
        ide_targets = pd.read_csv(os.path.join(self.emb_folder, 'ide_targets.csv'))

        return ide_sources, ide_targets

    def save_experiment_data(
        self, X, targets_pids, sources_pids, sources_map_pids):

        # graph
        np.savez(os.path.join(self.basepath, "graph.npz"), X=X)
        # targets
        np.save(
            os.path.join(self.basepath, "targets_pids.npy"),
            targets_pids,
            allow_pickle=True)
        pd.DataFrame(data=targets_pids,columns=['entity']) \
            .to_csv(os.path.join(self.basepath, "targets_pids.csv"), index=False)
        # sources
        np.save(
            os.path.join(self.basepath, "sources_pids.npy"),
            sources_pids,
            allow_pickle=True)
        pd.DataFrame(data=sources_pids,columns=['entity']) \
            .to_csv(os.path.join(self.basepath, "sources_pids.csv"), index=False)
        # sources map pids
        np.save(
            os.path.join(self.basepath, "sources_map_pids.npy"),
            sources_map_pids,
            allow_pickle=True)
        self.logger.info(
            f"INOUT: Social graph, pseudo ids and counts saved at {self.basepath}.")

    def load_experiment_data(self):

        X = np.load(os.path.join(self.basepath, "graph.npz"))['X']
        targets_pids = np.load(
            os.path.join(self.basepath, "targets_pids.npy"),
            allow_pickle=True)
        sources_pids = np.load(
            os.path.join(self.basepath, "sources_pids.npy"),
            allow_pickle=True)
        sources_map_pids = np.load(
            os.path.join(self.basepath, "sources_map_pids.npy"),
            allow_pickle=True)

        return X, targets_pids, sources_pids, sources_map_pids

    def save_ide_embeddings(self, sources_embeddings, targets_embeddings):

        sources_embeddings.to_csv(
                os.path.join(self.emb_folder, 'ide_sources.csv'),
                index=False)

        targets_embeddings.to_csv(
                os.path.join(self.emb_folder, 'ide_targets.csv'),
                index=False)

        mssg = f"Ideological embeddings ({len(targets_embeddings)} targets and "
        mssg += f"{len(sources_embeddings)} sources) saved at folder "
        mssg += f"{self.emb_folder}."
        self.logger.info(mssg)


    def save_att_embeddings(self, att_source, att_targets):

        att_source.to_csv(
            os.path.join(self.att_folder, 'att_sources.csv'), index=False)
        att_targets.to_csv(
            os.path.join(self.att_folder, 'att_targets.csv'), index=False)

        mssg = f"Attitudinal embeddings ({len(att_targets)} targets and "
        mssg += f"{len(att_source)} sources) saved at folder {self.att_folder}."
        self.logger.info(mssg)

    def load_att_embeddings(self):

        warn_once(
            self.logger,
            f"INOUT: Attitudinal embeddings load from {self.att_folder}.")

        att_source = pd.read_csv(os.path.join(self.att_folder, 'att_sources.csv'))
        att_targets = pd.read_csv(os.path.join(self.att_folder, 'att_targets.csv'))

        return att_source, att_targets

