import os

import numpy as np
import pandas as pd

import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

from gap.conf import \
    LOGISTICREGRESSIONS, \
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


def labels_stats(SQLITE, INOUT, survey, country, logger, show):

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
        # 'keywords': keywords_data,
        'llm': llm_data
    }

    # set baseline
    baselineData = att.merge(
        keywords_labels[['pseudo_id']],
        right_on='pseudo_id',
        left_on='entity')

    COLOR = ['red', 'green']
    for strategy in strategy_data.keys():

        for lrdata in LOGISTICREGRESSIONS:

            egroups = {
                1:  f"{lrdata['group1']}",
                2:  f"{lrdata['group2']}",
            }

            # check that label is present for strategy
            # for instance there is no 'climate denialist' for the A strategy
            if not egroups[1] in strategy_data[strategy]:
                logger.info(
                    f"WARNING: {egroups[1]} is missing from {strategy} strategy data.")
                continue
            if not egroups[2] in strategy_data[strategy]:
                logger.info(
                    f"WARNING: {egroups[2]} is missing from {strategy} strategy data.")
                continue

            for attdim in lrdata[survey]:

                for egroup in egroups:

                    baseline_embeddings = baselineData[attdim]
                    baseline_count, _ = np.histogram(baseline_embeddings, **KWARGS)

                    fig = plt.figure(figsize=(18, 9))
                    ax = fig.add_subplot(1, 1, 1)
                    legend_axes =[]

                    data_ = strategy_data[strategy]
                    label = egroups[egroup]
                    pos_labels = data_[data_[label] == '1']
                    pos_labels_embeddings = pos_labels[attdim]
                    pos_labels_count, bin_edges = np.histogram(
                        pos_labels_embeddings, **KWARGS)
                    p = pos_labels_count / baseline_count

                    # compute confidence interval for a binomial proportion
                    # Clopper-Pearson
                    cis_low, cis_upp = by_interval_Clopper_Pearson(
                        pos_labels_embeddings,
                        baseline_embeddings,
                        KWARGS['bins'])

                    half_step = np.mean(bin_edges[0:2])
                    plot_x = (bin_edges+half_step)[:-1]

                    figlabel = f"{label} {strategy} label ({len(pos_labels)}/{len(baseline_embeddings)}), "
                    figlabel += f"{len(pos_labels)/len(baseline_embeddings):0.2f}\%"
                    a, = ax.plot(
                        plot_x,
                        p,
                        'o-',
                        color='k',
                        label=figlabel
                    )
                    plt.errorbar(
                        plot_x,
                        p,
                        yerr=[cis_low, cis_upp],
                        fmt="o",
                        color="gray")

                    legend_axes.append(a)
                    ax.set_xlim([0, 10])
                    ax.set_ylim((-0.1, 1))
                    plt.xticks([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
                    title = f"{country}"
                    ax.set_title(title)
                    ax.set_xlabel(f"{survey.upper()} {ATTDICT[survey][attdim]}", fontsize=fs)
                    fmt = '%.02f%%'
                    pticks = ticker.FormatStrFormatter(fmt)
                    ax.yaxis.set_major_formatter(pticks)
                    plt.legend(fontsize=fs)

                    plt.gca().xaxis.grid(True)
                    plt.grid(axis='x', color='gray', linestyle='dashed', linewidth=.8)
                    plt.grid(axis='y', linewidth=0)
                    plt.tight_layout()
                    if show:
                        plt.show()

                    # saving

                    strategyfolder = os.path.join(statsfolder, strategy)
                    os.makedirs(os.path.join(strategyfolder), exist_ok=True)

                    figname = f'{strategy}_strategy_{attdim}_'
                    figname += f'{egroups[egroup]}_'
                    figname += 'labels_propostions_and_CP_ci.png'
                    path = os.path.join(strategyfolder, figname)
                    plt.savefig(path, dpi=dpi)
                    print(f"Figure saved at {path}.")