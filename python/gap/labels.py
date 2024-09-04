import os
import json

import numpy as np
import pandas as pd

import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

from gap.conf import \
    VALIDATIONCONFIG, \
    ATTDICT
from gap.correlation_coefficient import \
    by_interval_Clopper_Pearson

# Font & Latex definitions
mpl.rcParams['mathtext.fontset'] = 'cm'
mpl.rcParams['mathtext.rm'] = 'serif'
fs = 32
dpi = 150
plt.rc('text', usetex=True)
plt.rc('font', family='sans-serif', size=fs)
KWARGS = {
    'bins':  np.linspace(0, 10, 11).astype(int),
    'range': [0, 10],
    'density': False
}


def labels_stats(SQLITE, INOUT, survey, country, attdim, logger, plot, show):

    statsfolder = os.path.join(INOUT.att_folder, 'stats')
    os.makedirs(os.path.join(statsfolder), exist_ok=True)

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

    # get A strategy labels
    keywords_labels = SQLITE.getKeywordsLabels()
    keywords_data = keywords_labels.merge(
        att,
        left_on='pseudo_id',
        right_on='entity',
        how='inner') \
        .drop(columns=['pseudo_id'])

    strategy_data = {
        'keywords': keywords_data,
        'llm': llm_data
    }

    # set baseline
    baselineData = att.merge(
        keywords_labels[['pseudo_id']],
        right_on='pseudo_id',
        left_on='entity')

    COLOR = ['red', 'green']
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

                baseline_embeddings = baselineData[attdim]
                baseline_count, _ = np.histogram(baseline_embeddings, **KWARGS)

                data_ = strategy_data[strategy]
                label = strategy_groups[strategy_group]
                pos_labels = data_[data_[label] == '1']
                pos_labels_embeddings = pos_labels[attdim]
                pos_labels_count, bin_edges = np.histogram(
                    pos_labels_embeddings, **KWARGS)
                rate = pos_labels_count / baseline_count

                # compute confidence interval for a binomial proportion
                # Clopper-Pearson
                cis_low, cis_upp = by_interval_Clopper_Pearson(
                    pos_labels_embeddings,
                    baseline_embeddings,
                    KWARGS['bins'])

                # scaling
                proportions = 100 * rate
                cis_low *= 100
                cis_upp *= 100

                half_step = np.mean(bin_edges[0:2])
                xaxis = (bin_edges+half_step)[:-1]

                total_perc = 100 * len(pos_labels) / len(baseline_embeddings)

                result = {
                    "xaxis": xaxis.tolist(),
                    "proportions": proportions.tolist(),
                    "cis_low": cis_low.tolist(),
                    "cis_upp": cis_upp.tolist()
                }

                result_name = f'{strategy}_strategy_{attdim}_'
                result_name += f'{strategy_groups[strategy_group]}_'
                result_name += 'labels_propostions_and_CP_ci'

                result_path = os.path.join(
                    strategyfolder, f"{result_name}.json")

                with open(result_path, 'w') as file:
                    json.dump(result, file)

                logger.info(f"Label statistics saved at {result_path}.")

                if plot:
                    country_name = country.split('2')[0].capitalize()
                    char_end_country_name = len(country_name)
                    year = country[char_end_country_name:]
                    title = f"{country_name} {year} collection"

                    figlabel = f"Labelled "
                    figlabel += f"{label.capitalize()} {strategy.upper()}, ("
                    figlabel += f"{len(pos_labels)}/{len(baseline_embeddings)}"
                    figlabel += f") {total_perc:0.2f}\%"

                    fig = plt.figure(figsize=(18, 9))
                    ax = fig.add_subplot(1, 1, 1)
                    legend_axes =[]

                    a, = ax.plot(
                        xaxis,
                        proportions,
                        color='k',
                        label=figlabel
                    )

                    plt.errorbar(
                        xaxis,
                        proportions,
                        yerr=[cis_low, cis_upp],
                        linewidth=2,
                        marker='s',
                        color="black")

                    legend_axes.append(a)
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
                    fmt = '%.02f%%'
                    pticks = ticker.FormatStrFormatter(fmt)
                    ax.yaxis.set_major_formatter(pticks)
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