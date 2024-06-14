import os
import yaml
from argparse import ArgumentParser

import numpy as np
import pandas as pd
from scipy import stats

import seaborn as sns
import matplotlib.pyplot as plt

from some4demdb import SQLite
from some4demexp.inout import \
    get_ide_ndims, \
    set_output_folder, \
    set_output_folder_att, \
    load_att_embeddings, \
    save_issues_benckmarks, \
    set_output_folder_emb, \
    load_ide_embeddings

from some4demexp.conf import \
    ATTDICT

from some4demexp.correlation_coefficient import smallSamplesSpearmanr

# parse arguments and set paths
ap = ArgumentParser()
ap.add_argument('--config', type=str, required=True)
ap.add_argument('--country', type=str, required=True)
ap.add_argument('--survey', type=str, required=True)
ap.add_argument('--output', type=str, required=True)
ap.add_argument('--show',  action='store_true', required=False)

args = ap.parse_args()
config = args.config
country = args.country
survey = args.survey
output = args.output
show = args.show

with open(config, "r", encoding='utf-8') as fh:
    params = yaml.load(fh, Loader=yaml.SafeLoader)

with open(params['params_db'], "r", encoding='utf-8') as fh:
    params_db = yaml.load(fh, Loader=yaml.SafeLoader)

SQLITE = SQLite(
    params['sqlite_db'].format(country=country),
    params_db['output']['tables'],
    country)

ATTDIMS = params['attitudinal_dimensions'][survey]
parties_mapping = SQLITE.getPartiesMapping()
ideN = get_ide_ndims(parties_mapping, survey)
IDEDIMS = range(ideN)

IDEDIMSNAMES = [fr'$\delta_{j+1}$' for j in IDEDIMS]
ATTDIMSNAMES = [ATTDICT[survey][i] for i in ATTDIMS]
SURVEYCOL = f'{survey.upper()}_party_acronym'

cmap_s = sns.diverging_palette(145, 300, s=60, as_cmap=True)

SMALL_SAMPLES_METHODS = [
    ("Pearson", stats.pearsonr, "vlag"),
    ("Spearman", smallSamplesSpearmanr, cmap_s),
]

LARGE_SAMPLES_METHODS = [
    ("Pearson",  stats.pearsonr, "vlag"),
    ("Spearman", stats.spearmanr, cmap_s),
]


def compute_correlation_matrices(
    ide_data, att_data, info, methods, pvalue_display_th=0.05):


    for method, correlation_fn, cmap in methods:

        print(f"----------------- {method} -----------------")
        print(f"----------------- {info} -----------------")

        fig = plt.figure(figsize=(16, 8))
        ax = fig.add_subplot(1,  1,  1)

        # init r-values matrices
        correlations = np.empty((len(ATTDIMS), ideN), float)
        # init p-values matrices
        pvalues = np.empty((len(ATTDIMS), ideN), float)
        annotations = np.empty((len(ATTDIMS), ideN), object)

        for i, attdim in enumerate(ATTDIMS):
            for j in IDEDIMS:
                statistic, pvalue = correlation_fn(
                    ide_data[f'latent_dimension_{j}'],
                    att_data[attdim]
                )
                correlations[i, j] = statistic
                pvalues[i, j] = pvalue
                if pvalue <= pvalue_display_th:
                    annotations[i, j] = f'{statistic:.2f} (p={pvalue:.3f})'
                else:
                    annotations[i, j] = f'{statistic:.2f}'

        correlations = pd.DataFrame(
            correlations,
            index=ATTDIMSNAMES,
            columns=IDEDIMSNAMES
        ) \
        .rename_axis(
            index="Attitudinal",
            columns='Ideological'
        )

        pvalues = pd.DataFrame(
            pvalues,
            index=ATTDIMSNAMES,
            columns=IDEDIMSNAMES
        ) \
        .rename_axis(
            index="Attitudinal",
            columns='Ideological'
        )

        rfigpath = os.path.join(
            att_folder,
            f"party_corr_{method}_{country}_{survey}_r.csv")
        correlations.to_csv(rfigpath, index=True)
        print(f"Correlation matrix (r-values) saved at {rfigpath}.")

        pfigpath = os.path.join(
            att_folder,
            f"party_corr_{method}_{country}_{survey}_p.csv")
        pvalues.to_csv(pfigpath, index=True)
        print(f"Correlation matrix (p-values) saved at {pfigpath}.")

        annotations = pd.DataFrame(
            annotations,
            index=ATTDIMSNAMES,
            columns=IDEDIMSNAMES,
            dtype=str,
        ) \
        .rename_axis(
            index="Attitudinal",
            columns='Ideological'
        )

        print(annotations)

        # sns.heatmap(correlations, ax=ax, annot=annotations, fmt="", cmap=cmap)
        # ax.set(xlabel="", ylabel="")
        # ax.xaxis.tick_top()
        # _title = f"{method} Coeficient Correlation Matrix \n"
        # _title += f"{country.capitalize()} N={ideN}  M={len(ATTDIMS)}\n"
        # _title += info
        # _title += f"\np-values less than {pvalue_display_th} displayed"
        # plt.title(_title)
        # plt.tight_layout()

        # figpath = os.path.join(
        #     att_folder,
        #     f"{info}_{method}_ide_vs_att_dims_correlation_matrix.png")
        # plt.savefig(figpath)
        # print(f"Correlation Matrix figure saved at {figpath}.")

    if show:
        plt.show()


# (0) Get embeddings and parties assignations
folder = set_output_folder(params, country, output)

ide_folder = set_output_folder_emb(
    params, country, survey, ideN, output)
ide_sources, ide_targets = load_ide_embeddings(ide_folder)

att_folder = set_output_folder_att(params, survey, country, ideN, output)
att_sources, att_targets = load_att_embeddings(att_folder)

targets_parties = SQLITE.getMpParties(['MMS', survey])

ide_targets = ide_targets.merge(
        targets_parties,
        left_on="entity",
        right_on="mp_pseudo_id",
        how="inner"
    ) \
    .drop(columns="mp_pseudo_id")



# (1) Compute correlation matrix IDE vs CHES for parties

parties_coord_att = SQLITE.getPartiesAttitudes(survey, ATTDIMS) \
    .drop(columns='MMS_party_acronym') \
    .drop_duplicates()

parties_with_atts = parties_coord_att[SURVEYCOL].unique().tolist()

estimated_groups_coord_ide = ide_targets[ide_targets[SURVEYCOL].isin(parties_with_atts)] \
    .drop(columns=['entity', 'MMS_party_acronym']) \
    .groupby(SURVEYCOL) \
    .mean() \
    .reset_index()

compute_correlation_matrices(
    estimated_groups_coord_ide.sort_values(by=SURVEYCOL),
    parties_coord_att.sort_values(by=SURVEYCOL),
    "PARTIES",
    SMALL_SAMPLES_METHODS)


# # (2) Compute correlation matrix IDE vs CHES for sources

# data =  ide_sources.merge(att_sources,  on='entity',  how='inner')
# compute_correlation_matrices(
#     data,
#     data,
#     "SOURCES",
#     LARGE_SAMPLES_METHODS)

