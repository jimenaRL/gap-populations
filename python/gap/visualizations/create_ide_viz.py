import os
import yaml
from argparse import ArgumentParser
from itertools import combinations

from gap.inout import \
    get_ide_ndims, \
    set_output_folder_emb, \
    load_ide_embeddings

from gap.bivariate_marginal import visualize_ide
from gap.distributions import distributions

def plot_ideological_embedding(
    SQLITE,
    NB_MIN_FOLLOWERS,
    MIN_OUTDEGREE,
    country,
    survey,
    ideN,
    n_dims_to_viz,
    folder,
    emb_folder,
    vizparams,
    show,
    logger):

    # Load data from ideological embedding
    ide_sources, ide_targets = load_ide_embeddings(emb_folder, logger)

    # show by dim distributions
    distributions(
        ide_sources,
        ide_targets,
        "",
        country,
        show)

    palette = vizparams['palette']
    idevizparams = vizparams['ideological']
    mp_parties = SQLITE.getMpParties(['MMS', survey])
    targets_parties = mp_parties[['mp_pseudo_id', 'MMS_party_acronym']] \
        .rename(columns={'MMS_party_acronym': 'party'})

    # select parties to show
    _parties_to_show = mp_parties[~mp_parties[f'{survey.upper()}_party_acronym'].isna()]
    parties_to_show = _parties_to_show['MMS_party_acronym'].unique().tolist()

    d21_folder = os.path.join(f"exports/deliverableD21/ideological/{country}")
    output_folders = [emb_folder]

    for x, y in combinations(range(n_dims_to_viz), 2):
        visualize_ide(
            sources_coord_ide=ide_sources,
            targets_coord_ide=ide_targets,
            targets_parties=targets_parties,
            parties_to_show=parties_to_show,
            latent_dim_x=x,
            latent_dim_y=y,
            output_folders=output_folders,
            show=show,
            palette=palette,
            **idevizparams
        )
