import os
import json

import numpy as np
import pandas as pd
import statsmodels.api as sm

import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib.ticker import PercentFormatter

from gap.conf import \
    VALIDATIONCONFIG, \
    ATTDICT

# Font & Latex definitions
mpl.rcParams['mathtext.fontset'] = 'cm'
mpl.rcParams['mathtext.rm'] = 'serif'
fs = 28
dpi = 150
plt.rc('text', usetex=True)
plt.rc('font', family='sans-serif', size=fs)
BINS_REPRESENTATION_PERC_TH = 0.1
KWARGS = {
    'bins':  np.linspace(0, 10, 11).astype(int),
    'range': [0, 10],
    'density': False
}
BACKGROUNDCOLOR = ['lightgrey', 'darkgrey']

def labels_stats(SQLITE, INOUT, survey, country, year, attdim, logger, plot, show):

    statsfolder = os.path.join(INOUT.att_folder, 'stats')
    os.makedirs(os.path.join(statsfolder), exist_ok=True)

    bin_edges = KWARGS['bins']
    half_step = np.mean(bin_edges[0:2])
    xaxis = (bin_edges+half_step)[:-1]

    att_sources, att_targets = INOUT.load_att_embeddings()

    att = pd.concat([att_sources, att_targets])

    # get C strategy labels
    llm_labels = SQLITE.getLLMLabels()
    llm_data = llm_labels.merge(
        att,
        left_on='pseudo_id',
        right_on='entity',
        how='inner') \
        .drop(columns=['pseudo_id'])

    # # get A strategy labels
    # keywords_labels = SQLITE.getKeywordsLabels()
    # keywords_data = keywords_labels.merge(
    #     att,
    #     left_on='pseudo_id',
    #     right_on='entity',
    #     how='inner') \
    #     .drop(columns=['pseudo_id'])

    strategy_data = {
        # 'keywords': keywords_data,
        'llm': llm_data
    }

    # set baseline for attitudinal dim
    baselineData = att.merge(
        llm_labels[['pseudo_id']],
        right_on='pseudo_id',
        left_on='entity')
    baseline_embeddings = baselineData[attdim]
    baseline_count, _ = np.histogram(baseline_embeddings, **KWARGS)

    # remove non representative bins with less than a given % of total embeddings
    bins_th = BINS_REPRESENTATION_PERC_TH
    total_proportion = 100 * baseline_count / len(baseline_embeddings)
    representative_bins = total_proportion > bins_th
    dropped_bins = KWARGS['bins'][1:][~representative_bins].tolist()
    if len(dropped_bins) > 0:
        m = f"WARNING: data from the "
        m += f"{'th, '.join(map(str, dropped_bins[:-1]))}th "
        m += f"and {dropped_bins[-1]}th bins was dropped due to"
        m += f" low total representative (less than {bins_th}%)."
        logger.info(m)

    repr_xaxis = xaxis[representative_bins]
    baseline_count = baseline_count[representative_bins]

    for strategy in strategy_data.keys():

        strategyfolder = os.path.join(statsfolder, strategy)
        os.makedirs(os.path.join(strategyfolder), exist_ok=True)

        for lrdata in VALIDATIONCONFIG:

            if not attdim in lrdata[survey]:
                continue

            strategy_groups = {
                1:  f"{lrdata['group1']}",
                2:  f"{lrdata['group2']}",
            }

            # check that label is present for strategy
            # for instance there is no 'climate denialist'
            # for the keywords strategy
            if not strategy_groups[1] in strategy_data[strategy]:
                m = f"WARNING: {strategy_groups[1]} "
                m += f"is missing from {strategy} strategy data."
                logger.info(m)
                continue
            if not strategy_groups[2] in strategy_data[strategy]:
                m = f"WARNING: {strategy_groups[2]} "
                m += f"is missing from {strategy} strategy data."
                logger.info(m)
                continue

            for strategy_group in strategy_groups:

                result_name = f'{strategy}_strategy_{attdim}_'
                result_name += f'{strategy_groups[strategy_group]}_'
                result_name += 'labels_propostions_and_CP_ci'

                data_ = strategy_data[strategy]
                label = strategy_groups[strategy_group]
                pos_labels = data_[data_[label] == '1']
                pos_labels_embeddings = pos_labels[attdim]
                pos_labels_count, _ = np.histogram(
                    pos_labels_embeddings, **KWARGS)

                # remove non representative bins with less than a given % of total embeddings
                pos_labels_count = pos_labels_count[representative_bins]
                rate = pos_labels_count / baseline_count

                # compute confidence interval for a binomial proportion
                # Clopper-Pearson
                cis_low, cis_upp = sm.stats.proportion_confint(
                    pos_labels_count,
                    baseline_count,
                    method='beta',
                    alpha=0.05)

                # scalinf
                proportions = 100 * rate
                cis_low *= 100
                cis_upp *= 100

                # plot data
                total_perc = 100 * len(pos_labels) / len(baseline_embeddings)

                if plot:
                    country_name = country.split('2')[0].capitalize()
                    title = f"{country_name} {year} collection"

                    figlabel = f"Labelled "
                    figlabel += f"{label.capitalize()} {strategy.upper()}, ("
                    figlabel += f"{len(pos_labels)}/{len(baseline_embeddings)}"
                    figlabel += f") {total_perc:0.2f}\%"

                    fig = plt.figure(figsize=(18, 9))
                    ax = fig.add_subplot(1, 1, 1)

                    plt.errorbar(
                        repr_xaxis,
                        proportions,
                        yerr=[cis_low, cis_upp],
                        fmt='s',
                        markersize=9,
                        capsize=0,
                        color="black",
                        label=figlabel)

                    # fill background
                    for i in range(len(bin_edges) - 1):
                        plt.axvspan(
                            xmin=bin_edges[i],
                            xmax=bin_edges[i+1],
                            facecolor=BACKGROUNDCOLOR[i%2],
                            alpha=.35
                        )

                    ax.set_xlim([0, 10])
                    ax.set_ylim((
                        0,
                        1.1 * (np.nanmax(proportions) + np.nanmax(cis_upp))
                    ))
                    plt.xticks([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
                    ax.set_title(title)
                    ax.set_xlabel(
                        f"{survey.upper()} {ATTDICT[survey][attdim]}",
                        fontsize=fs)
                    ax.set_ylabel("Users annotated percentage", fontsize=fs)
                    # fmt = '%.02f%%'
                    # pticks = ticker.FormatStrFormatter(fmt)
                    # ax.yaxis.set_major_formatter(pticks)
                    plt.gca().yaxis.set_major_formatter(PercentFormatter(
                        xmax=100, decimals=0))
                    plt.legend(fontsize=fs, loc='upper center')

                    plt.gca().xaxis.grid(True)
                    plt.grid(
                        axis='x',
                        color='gray',
                        linestyle='dashed',
                        linewidth=.8)
                    plt.grid(axis='y', linewidth=0)
                    plt.tight_layout()

                    # saving
                    path = os.path.join(strategyfolder, result_name+'.png')
                    plt.savefig(path, dpi=dpi)
                    print(f"Figure saved at {path}.")

                if show:
                    plt.show()

                plt.close('all')

                result = {
                    "xaxis": xaxis.tolist(),
                    "proportions": proportions.tolist(),
                    "cis_low": cis_low.tolist(),
                    "cis_upp": cis_upp.tolist()
                }

                result_path = os.path.join(
                    strategyfolder, f"{result_name}.json")

                with open(result_path, 'w') as file:
                    json.dump(result, file)

                logger.info(f"Label statistics saved at {result_path}.")

