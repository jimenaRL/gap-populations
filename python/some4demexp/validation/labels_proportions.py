import os
import yaml
import numpy as np
import pandas as pd
from argparse import ArgumentParser

import statsmodels.api as sm

import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

from some4demdb import SQLite

from some4demexp.inout import \
    set_output_folder, \
    set_output_folder_emb, \
    load_ide_embeddings, \
    set_output_folder_att, \
    load_att_embeddings, \
    get_ide_ndims

from some4demexp.conf import \
    LOGISTICREGRESSIONS, \
    ATTDICT

# Font & Latex definitions
mpl.rcParams['mathtext.fontset'] = 'cm'
mpl.rcParams['mathtext.rm'] = 'serif'
fs = 32
# dpi = 150
plt.rc('text', usetex=True)
plt.rc('font', family='sans-serif', size=fs)
KWARGS = {
    'bins':  np.linspace(0, 10, 11),
    'range': [0, 10]
}

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

parties_mapping = SQLITE.getPartiesMapping()
ideN = get_ide_ndims(parties_mapping, survey)


# (0) Get embeddings and descriptions
folder = set_output_folder(params, country, output)

ide_folder = set_output_folder_emb(
    params, country, survey, ideN, output)
ide_sources, _ = load_ide_embeddings(ide_folder)

att_folder = set_output_folder_att(params, survey, country, ideN, output)
att_sources, _ = load_att_embeddings(att_folder)

# get A estrategy labels
keywords_labels = SQLITE.getKeywordsLabels(entity='user')
keywords_data = keywords_labels.merge(
    att_sources,
    left_on='pseudo_id',
    right_on='entity',
    how='inner') \
    .drop(columns=['pseudo_id'])

# get C estrategy labels
llm_labels = SQLITE.getLLMLabels('user')
llm_data = llm_labels.merge(
    att_sources,
    left_on='pseudo_id',
    right_on='entity',
    how='inner') \
    .drop(columns=['pseudo_id'])

# get baseline
baselineData = att_sources.merge(
    keywords_labels[['pseudo_id']],
    left_on='entity',
    right_on='pseudo_id',
    how='inner') \
    .drop(columns=['pseudo_id', 'entity'])

estrategy_data = {
    'A': keywords_data,
    'C': llm_data
}

COLOR = ['red', 'green']
for estrategy in estrategy_data.keys():

    for lrdata in LOGISTICREGRESSIONS:


        egroups = {
            1:  f"{estrategy}_{lrdata['group1']}",
            2:  f"{estrategy}_{lrdata['group2']}",
        }

        # check that label is prsent for estrategi
        # for instance there is no 'climate denialist' for the A estrategy
        if not egroups[1] in estrategy_data[estrategy]:
            print(f"{egroups[1]} is missing from {estrategy} estrategy data.")
            continue
        if not egroups[2] in estrategy_data[estrategy]:
            print(f"{egroups[2]} is missing from {estrategy} estrategy data.")
            continue

        data = {
            1: estrategy_data[estrategy].query(f"{egroups[1]}=='1'"),
            2: estrategy_data[estrategy].query(f"{egroups[2]}=='1'")
        }

        for attdim in lrdata[survey]:

            baseline, _ = np.histogram(baselineData[attdim], **KWARGS)

            fig = plt.figure(figsize=(12, 6))
            ax = fig.add_subplot(1, 1, 1)
            legend_axes =[]
            for egroup, datum, color in zip(egroups, data, COLOR):

                attdata = data[egroup][attdim]

                hist, bin_edges = np.histogram(attdata, **KWARGS)
                p = hist / baseline
                p_lower, p_upper = sm.stats.proportion_confint(
                    hist, baseline, method='beta', alpha=0.05)

                half_step = np.mean(bin_edges[0:2])
                plot_x = (bin_edges+half_step)[:-1]
                a, = ax.plot(
                    plot_x,
                    100.0*p,
                    color=color,
                    label=f"{egroups[egroup].replace('_', ' ')} ({len(data[egroup])} samples)"
                )
                legend_axes.append(a)
                ax.fill_between(
                    plot_x,
                    100.0*p_lower,
                    100.0*p_upper,
                    color=color,
                    alpha=0.25
                )

            ax.set_xlim([0, 10])
            ax.set_ylim((0, 200.0 * np.nanmax(p)))
            # title = f"{egroups[1]} ({len(data[1])} samples) vs "
            # title += f"{egroups[2]} ({len(data[2])} samples)"
            # ax.set_title(title)
            ax.set_xlabel(f"{survey.upper()} {ATTDICT[survey][attdim]}", fontsize=fs)
            fmt = '%.02f%%'
            pticks = ticker.FormatStrFormatter(fmt)
            ax.yaxis.set_major_formatter(pticks)
            plt.legend(fontsize=fs)
            plt.tight_layout()
            if show:
                plt.show()

            # saving
            figname = f'{estrategy}_strategy_{attdim}_'
            figname += f'{egroups[1]}_vs_{egroups[2]}_'
            figname += 'users_labeled_stats_with_confidence.png'
            path = os.path.join(att_folder, figname)
            plt.savefig(path, dpi=dpi)
            print(f"Figure saved at file with name {figname}.")


