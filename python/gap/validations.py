import os
import yaml
import json
import logging
import itertools
from tqdm import tqdm

import numpy as np
import pandas as pd

from scipy.special import expit
from sklearn.linear_model import LogisticRegression
from imblearn.under_sampling import RandomUnderSampler
from imblearn.pipeline import make_pipeline
from sklearn.model_selection import cross_validate

from sklearn.metrics import \
    precision_score, \
    recall_score, \
    f1_score, \
    roc_auc_score, \
    r2_score, \
    confusion_matrix

from scipy.stats import chi2_contingency

import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

import seaborn as sns

from gap.conf import \
    VALIDATIONCONFIG, \
    ATTDICT

# Font & Latex definitions
mpl.rcParams['mathtext.fontset'] = 'cm'
mpl.rcParams['mathtext.rm'] = 'serif'
# mpl.rcParams['text.latex.preamble']=[r"\usepackage{amsmath}"]
fs = 12
figsize = (7.5,  5)
# dpi = 150
plt.rc('text', usetex=True)
plt.rc('font', family='sans-serif', size=fs)

def make_validation(
    parties_mapping,
    llm_labels,
    att_sources,
    cv_seed,
    nb_splits,
    country,
    year,
    survey,
    attdim,
    plot,
    show,
    valfolder,
    logger):


    ################
    # Loading data #
    ################

    if not attdim in att_sources:
        logger.info(
            f"VALIDATION: skipping missing attitudinal dimension {attdim}.")
        return {}

    llm_data = llm_labels.merge(
        att_sources,
        left_on='pseudo_id',
        right_on='entity',
        how='inner') \
        .drop(columns=['pseudo_id'])

    strategy_data = {
        'llm': llm_data
    }

    records = []
    for strategy, lrdata in tqdm(
        itertools.product(strategy_data.keys(), VALIDATIONCONFIG)):

        if not attdim in lrdata[survey]:
            continue

        egroups = {
            1:  f"{lrdata['group1']}",
            2:  f"{lrdata['group2']}",
        }

        data = {
            1: strategy_data[strategy].query(f"{egroups[1]}=='1' & {egroups[2]}!='1'"),
            2: strategy_data[strategy].query(f"{egroups[2]}=='1' & {egroups[1]}!='1'")
        }

        logger.info(
            f"VALIDATION: there are {len(data[1])} users labeled {egroups[1]} in data.")
        logger.info(
            f"VALIDATION: there are {len(data[2])} users labeled {egroups[2]} in data.")
        if len(data[1]) == 0:
            continue
        if len(data[2]) == 0:
            continue

        label1 = egroups[1]
        label2 = egroups[2]

        mss = f"VALIDATION: Using labels `{label1}` and `{label2}` from strategy "
        mss += f"`{strategy}` for validating {attdim} {survey} dimension."
        logger.info(mss)

        attdata1 = data[1][attdim]
        attdata2 = data[2][attdim]

        l1 = len(attdata1)
        l2 = len(attdata2)

        X = np.hstack([
            attdata1.values,
            attdata2.values
        ]).reshape(-1, 1)

        y = np.hstack([
            np.zeros_like(attdata1.values),
            np.ones_like(attdata2.values)
        ]).ravel()

        # egalize samples
        model = make_pipeline(
            RandomUnderSampler(
                sampling_strategy='not minority',
                random_state=cv_seed,
                replacement=False
            ),
            LogisticRegression(
                penalty='l2',
                class_weight=None,
                solver='lbfgs',
                verbose=0,
                n_jobs=-1,
            )
        )

        if not len(X) > nb_splits:
            m = f"VALIDATION: Too low sample number of attitudinal "
            m += f"embeddings({len(X)}), ignoring {lrdata}."
            logger.info(m)
            continue

        unique, counts = np.unique(y, return_counts=True)

        if counts.min() == 1:
            m = f"VALIDATION: Ignoring {lrdata} because "
            m += "of one ot the classes has only one member "
            m += f"{dict(np.array([unique, counts], dtype=int).T)}."
            logger.info(m)
            continue

        if counts.min() < nb_splits:
            m = f"VALIDATION: Number of splits for {lrdata} in cross validate "
            m += f"was decreased from {nb_splits} to {counts.min()} because "
            m += "of too low number of members if one ot the classes "
            m += f"{dict(np.array([unique, counts], dtype=int).T)}."
            logger.info(m)
            nb_splits = counts.min()

        cv_results = cross_validate(
            model, X, y, cv=nb_splits, scoring=('precision', 'recall', 'f1', 'roc_auc'),
            return_train_score=True, return_estimator=True, n_jobs=-1)

        clf_models = [pipe[-1] for pipe in cv_results['estimator']]
        clf_intercept = np.mean([clf.intercept_ for clf in clf_models])
        clf_coef = np.mean([clf.coef_ for clf in clf_models])

        # Compute validation scores
        precision = np.mean([
            precision_score(y, lr.predict(X)) for lr in clf_models])
        recall = np.mean([
            recall_score(y, lr.predict(X)) for lr in clf_models])
        f1 = np.mean([
            f1_score(y, lr.predict(X)) for lr in clf_models])
        auc = np.mean([
            roc_auc_score(y, lr.predict(X)) for lr in clf_models])

        chi2_stat = []
        chi2_pval = []
        for lr in clf_models:
            try:
                chi2_results = chi2_contingency(confusion_matrix(y, lr.predict(X)))
            except:
                logger.info(
                    f"VALIDATION: Unnable to compute chi2_results.")
                continue
            chi2_stat.append(chi2_results[0])
            chi2_pval.append(chi2_results[1])
        chi2_stat = np.mean(chi2_stat)
        chi2_pval = np.mean(chi2_pval)


        record = {
            "strategy": strategy,
            "label1": label1,
            "label2": label2,
            "nb_samples_label1": l1,
            "nb_samples_label2": l2,
            "attitudinal_dimension": attdim,
            "attitudinal_dimension_name": ATTDICT[survey][attdim],
            "survey": survey,
            "precision": precision,
            "recall":recall,
            "f1": f1,
            "auc": auc,
            "chi2_stat": chi2_stat,
            "chi2_pval": chi2_pval,
            "train_precision_mean": cv_results['train_precision'].mean(),
            "train_recall_mean": cv_results['train_recall'].mean(),
            "train_f1_mean":  cv_results['train_f1'].mean(),
            "train_auc_mean":  cv_results['train_roc_auc'].mean(),
            "train_precision_std": cv_results['train_precision'].std(),
            "train_recall_std": cv_results['train_recall'].std(),
            "train_f1_std":  cv_results['train_f1'].std(),
            "train_auc_std":  cv_results['train_roc_auc'].std(),
            "test_precision_mean": cv_results['test_precision'].mean(),
            "test_recall_mean": cv_results['test_recall'].mean(),
            "test_f1_mean":  cv_results['test_f1'].mean(),
            "test_precision_std": cv_results['test_precision'].std(),
            "test_recall_std": cv_results['test_recall'].std(),
            "test_f1_std":  cv_results['test_f1'].std(),
            "country": country,
            "nb_splits": str(nb_splits),
            "train_precision_by_folds":  ' | '.join([f"{i:.3f}" for i in cv_results['train_precision'].tolist()]),
            "train_recall_by_folds": ' | '.join([f"{i:.3f}" for i in cv_results['train_recall'].tolist()]),
            "train_f1_by_folds": ' | '.join([f"{i:.3f}" for i in cv_results['train_f1'].tolist()]),
            "test_precision_by_folds": ' | '.join([f"{i:.3f}" for i in cv_results['test_precision'].tolist()]),
            "test_recall_by_folds": ' | '.join([f"{i:.3f}" for i in cv_results['test_recall'].tolist()]),
            "test_f1_by_folds": ' | '.join([f"{i:.3f}" for i in cv_results['test_f1'].tolist()]),
        }

        records.append(record)

        su = strategy.capitalize()
        os.makedirs(os.path.join(valfolder, 'json'), exist_ok=True)
        result_path = os.path.join(
            valfolder, 'json', f"strategy_{su}_{attdim}_{label1}_{label2}.json")

        with open(result_path, 'w') as file:
            json.dump(record, file)

        logger.info(
            f"VALIDATION: Logistic regression results saved at {result_path}.")

        # plot
        if plot:
            # Xplot = np.sort(X.flatten())
            # f = expit(Xplot * clf_coef + clf_intercept).ravel()

            Xplot = np.linspace(-1.8, 11.8, 1000, endpoint=True)
            f = expit(Xplot * clf_coef + clf_intercept).ravel()

            if clf_intercept < 0:
                above_threshold = f > 0.5
            else:
                above_threshold = f < 0.5

            X_threshold = Xplot[above_threshold][0]

            custom_legend=[
                # densities
                Line2D([0], [0], color='white', lw=1, alpha=1, label='Users'),
                Line2D([0], [0], color='blue', marker='o', mew=0, lw=0, alpha=0.5,
                    label=f'Labeled {label1} ({l1})'),
                Line2D([0], [0], color='red', marker='o', mew=0, lw=0, alpha=0.5,
                    label=f'Labeled {label2} ({l2})'),
                #densities
                Line2D([0], [0], color='white', lw=1, alpha=1, label='\nDensities'),
                Line2D([0], [0], color='blue', alpha=1, label=f'Labeled {label1}'),
                Line2D([0], [0], color='red', alpha=1, label=f'Labeled {label2}\n'),
                Line2D([0], [0], color='white', lw=1, alpha=1, label='\nLogistic regression'),
                Line2D([0], [0], color='k',  alpha=1, label='Model'),
                Line2D([0], [0], color='k',  linestyle=':', alpha=1,
                    label='Classification'),
                Line2D([0], [0], color='white', lw=1, alpha=1, label='cuttof'),
                # metrics
                Line2D([0], [0], color='white', lw=1, alpha=1, label='\nMetrics'),
                Line2D([0], [0], color='white', alpha=1, label=f'F1 = {f1:.3f}'),
                Line2D([0], [0], color='white', alpha=1, label=f'precision = {precision:.3f}'),
                Line2D([0], [0], color='white', alpha=1, label=f'recall = {recall:.3f}'),
                Line2D([0], [0], color='white', alpha=1, label=f'AUC = {auc:.3f}'),
                Line2D([0], [0], color='white', alpha=1, label=f'$\chi^{{{2}}}$ = {chi2_stat:.3f}'),
                Line2D([0], [0], color='white', alpha=1, label=f'p = {chi2_pval:.3f}'),
            ]


            fig = plt.figure(figsize=figsize)

            ax = fig.add_subplot(1,  1,  1)

            # left/blue
            kde_left = sns.kdeplot(data=attdata1.to_frame(), x=attdim, color='blue', alpha=0.05, ax=ax, common_norm=False, fill=True)
            # ax.plot(X[y==0], np.zeros(X[y==0].size)-0.05, 'o', color='blue', alpha=0.02, ms=5, mew=1)

            # right/red
            kde_right = sns.kdeplot(data=attdata2.to_frame(), x=attdim, color='red', alpha=0.05, ax=ax, common_norm=False,  fill=True)
            # ax.plot(X[y==1], np.ones(X[y==1].size),  'o', color='red',  alpha=0.02, ms=5, mew=1)

            # logistic
            ax.plot(Xplot, f, color='black', linewidth=1)
            ax.axvline(X_threshold, linestyle=':', color='k')
            ax.axhline(0.5, linestyle=':', color='k')
            # ax.text(-1.8, 0.42, r'y=$0.5$', color='gray', fontsize=fs-3)
            # ax.text(X_threshold+0.25, 0.04, r'x=$%.2f$' % (X_threshold), color='gray', fontsize=fs-3)

            # # positives & negatives
            # ax.text(X_threshold+0.3, 1.05, 'True pos.', color='r', fontsize=fs)
            # ax.text(X_threshold-2.5, 1.05, 'False neg.', color='r', fontsize=fs)
            # ax.text(X_threshold+0.35, -0.15, 'False pos.', color='b', fontsize=fs)
            # ax.text(X_threshold-2.5, -0.15, 'True neg.', color='b', fontsize=fs)

            # axis
            ax.plot([-2, 12], [0, 0], color="black", linewidth=1) # base line
            ax.set_xlim((-2, 12))
            # ax.set_ylim((-0.2, 1.2))
            s = ATTDICT[survey][attdim]
            ax.set_xlabel(f"$\delta_{{{s}}}$", fontsize=fs*2)
            ax.set_ylabel('')
            ax.legend(handles=custom_legend, loc='center left', fontsize=fs-1, bbox_to_anchor=(1, 0.5))
            # plt.locator_params(axis='x', nbins=5)
            ax.set_xticks([0, 2, 4, 6, 8, 10])
            # ax.set_yticks([0, 0.2, 0.4, 0.6, 0.8, 1])
            ax.tick_params(axis='x', labelsize=fs*2)
            ax.tick_params(axis='y', labelsize=fs*2)
            plt.locator_params(axis='y', nbins=6)


            # title
            title = f'{country.capitalize()} {year}'
            ax.set_title(title, loc='center', fontweight='normal', fontsize=fs*2)
            # fig.suptitle(
            #     t=title,
            #     x=0.5,
            #     y=0.9,
            #     fontsize=fs
            # )

            plt.tight_layout()

            #saving
            os.makedirs(os.path.join(valfolder, 'png'), exist_ok=True)
            os.makedirs(os.path.join(valfolder, 'pdf'), exist_ok=True)
            figname = f'lr_{country}_{strategy}_strategy_{attdim}'
            figname += f'_l1_{egroups[1]}_vs_l2_{egroups[2]}'
            path_png = os.path.join(valfolder, 'png', figname+'.png')
            plt.savefig(path_png, dpi=300)
            path_pdf = os.path.join(valfolder, 'pdf', figname+'.pdf')
            plt.savefig(path_pdf, dpi=300)

            logger.info(
                f"VALIDATION: Logistic regression plot saved at {path_png}.")

            if show:
                plt.show()

            plt.close()

            logger.info(f"VALIDATION: Figures saved at {valfolder}")


    return records
