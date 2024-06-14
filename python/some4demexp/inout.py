import os
import yaml
import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix


def get_ide_ndims(parties_mapping, survey):
    surveycol = f'{survey.upper()}_party_acronym'
    parties_to_show = parties_mapping[parties_mapping[surveycol].notna()]
    n_latent_dimensions = parties_to_show[surveycol].nunique() - 1
    m = f"Ideological embedding dim set to {n_latent_dimensions} "
    m += f"for survey {survey}."
    return n_latent_dimensions

def load_ide_embeddings(folder, logger):

    logger.info(f"Ideological embeddings loaded from folder {folder}.")

    ide_sources = pd.read_csv(os.path.join(folder, 'ide_sources.csv'))
    ide_targets = pd.read_csv(os.path.join(folder, 'ide_targets.csv'))

    return ide_sources, ide_targets

def save_experiment_data(
    X, targets_pids, sources_pids, sources_map_pids, folder, logger):

    # graph
    np.savez(os.path.join(folder, "graph.npz"), X=X)
    # targets
    np.save(
        os.path.join(folder, "targets_pids.npy"),
        targets_pids,
        allow_pickle=True)
    pd.DataFrame(data=targets_pids,columns=['entity']) \
        .to_csv(os.path.join(folder, "targets_pids.csv"), index=False)
    # sources
    np.save(
        os.path.join(folder, "sources_pids.npy"),
        sources_pids,
        allow_pickle=True)
    pd.DataFrame(data=sources_pids,columns=['entity']) \
        .to_csv(os.path.join(folder, "sources_pids.csv"), index=False)
    # sources map pids
    np.save(
        os.path.join(folder, "sources_map_pids.npy"),
        sources_map_pids,
        allow_pickle=True)
    logger.info(f"Social graph, pseudo ids and counts saved at {folder}.")

def load_experiment_data(folder):

    X = np.load(os.path.join(folder, "graph.npz"))['X']
    targets_pids = np.load(
        os.path.join(folder, "targets_pids.npy"),
        allow_pickle=True)
    sources_pids = np.load(
        os.path.join(folder, "sources_pids.npy"),
        allow_pickle=True)
    sources_map_pids = np.load(
        os.path.join(folder, "sources_map_pids.npy"),
        allow_pickle=True)

    return X, targets_pids, sources_pids, sources_map_pids

def save_ide_embeddings(sources_embeddings, targets_embeddings, folder, logger):

    sources_embeddings.to_csv(
            os.path.join(folder, 'ide_sources.csv'),
            index=False)

    targets_embeddings.to_csv(
            os.path.join(folder, 'ide_targets.csv'),
            index=False)

    mssg = f"Ideological embeddings ({len(targets_embeddings)} targets and "
    mssg += f"{len(sources_embeddings)} sources) saved at folder {folder}."
    logger.info(mssg)


def save_att_embeddings(att_source, att_targets, folder, logger):

    att_source.to_csv(
        os.path.join(folder, 'att_sources.csv'), index=False)
    att_targets.to_csv(
        os.path.join(folder, 'att_targets.csv'), index=False)

    mssg = f"Attitudinal embeddings ({len(att_targets)} targets and "
    mssg += f"{len(att_source)} sources) saved at folder {folder}."
    logger.info(mssg)


def load_att_embeddings(folder):

    logger.info(f"Attitudinal embeddings load from folder {folder}.")

    att_source = pd.read_csv(os.path.join(folder, 'att_sources.csv'))
    att_targets = pd.read_csv(os.path.join(folder, 'att_targets.csv'))

    return att_source, att_targets


def set_output_folder(params, country, output, logger):

    emb_folder = f"min_followers_{params['sources_min_followers']}"
    emb_folder += f"_min_outdegree_{params['sources_min_outdegree']}"

    output_folder = os.path.join(output, country, emb_folder)

    os.makedirs(output_folder, exist_ok=True)

    config_file = os.path.join(output_folder, 'config.yaml')

    if not os.path.exists(config_file):
        with open(config_file, 'w') as file:
            yaml.dump(params, file)
        logger.info(f"YAML config saved at {output_folder}.")

    return output_folder


def set_output_folder_emb(
        params, country, n_latent_dimensions, output, logger):
    output_folder_emb = os.path.join(
        set_output_folder(params, country, output, logger),
        f"ideN_{n_latent_dimensions}")
    os.makedirs(output_folder_emb, exist_ok=True)
    return output_folder_emb


def set_output_folder_att(
    params, survey, country, n_latent_dimensions, output, logger):
    output_folder_att = os.path.join(
        set_output_folder_emb(
            params, country, n_latent_dimensions, output, logger),
            survey)
    os.makedirs(output_folder_att, exist_ok=True)
    return output_folder_att

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
