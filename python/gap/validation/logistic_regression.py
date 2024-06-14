import os
import yaml
import json
import itertools
from tqdm import tqdm
from argparse import ArgumentParser

import numpy as np
import pandas as pd

from scipy.special import expit
from sklearn.linear_model import LogisticRegression
from imblearn.under_sampling import RandomUnderSampler
from imblearn.pipeline import make_pipeline
from sklearn.model_selection import cross_validate

import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.lines import Line2D
from matplotlib.patches import FancyArrowPatch
from mpl_toolkits.mplot3d import proj3d
import matplotlib.ticker as mtick
import matplotlib.patheffects as PathEffects

import seaborn as sns
import matplotlib.pyplot as plt

from some4demdb import SQLite

from corg import \
    BenchmarkDimension

from some4demexp.inout import \
    set_output_folder,  \
    set_output_folder_att,  \
    load_att_embeddings,  \
    get_ide_ndims

from some4demexp.conf import \
    LOGISTICREGRESSIONS, \
    ATTDICT

# Font & Latex definitions
mpl.rcParams['mathtext.fontset'] = 'cm'
mpl.rcParams['mathtext.rm'] = 'serif'
# mpl.rcParams['text.latex.preamble']=[r"\usepackage{amsmath}"]
fs = 12
# dpi = 150
plt.rc('text', usetex=True)
plt.rc('font', family='sans-serif', size=fs)


# parse arguments and set paths
ap = ArgumentParser()
ap.add_argument('--config', type=str, required=True)
ap.add_argument('--country', type=str, required=True)
ap.add_argument('--survey', type=str, required=True)
ap.add_argument('--output', type=str, required=True)
ap.add_argument('--plot',  action='store_true', required=False)
ap.add_argument('--show',  action='store_true', required=False)

args = ap.parse_args()
config = args.config
country = args.country
survey = args.survey
output = args.output
plot = args.plot
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

SEED = 187

# (0) Get embeddings and descriptions
folder = set_output_folder(params, country, output)

att_folder = set_output_folder_att(params, survey, country, ideN, output)
att_sources, _ = load_att_embeddings(att_folder)

lrfolder = os.path.join(att_folder, 'logistic_regression')

################
# Loading data #
################

# get A strategy labels
keywords_labels = SQLITE.getKeywordsLabels(entity='user')
keywords_data = keywords_labels.merge(
    att_sources,
    left_on='pseudo_id',
    right_on='entity',
    how='inner') \
    .drop(columns=['pseudo_id'])

# get C strategy labels
llm_labels = SQLITE.getLLMLabels('user')
llm_data = llm_labels.merge(
    att_sources,
    left_on='pseudo_id',
    right_on='entity',
    how='inner') \
    .drop(columns=['pseudo_id'])

strategy_data = {
    'A': keywords_data,
    'C': llm_data
}


records = []

for strategy, lrdata in tqdm(
    itertools.product(strategy_data.keys(), LOGISTICREGRESSIONS)):

    #  FOR DEBUGGING
    # if not (lrdata['group1'] == 'right' and lrdata['group2'] == 'left'):
    # if not (lrdata['group1'] == 'liberal' and lrdata['group2'] == 'conservative'):
    # if not (lrdata['group1'] == 'eurosceptic' and lrdata['group2'] == 'pro_european'):
    #     continue

    egroups = {
        1:  f"{strategy}_{lrdata['group1']}",
        2:  f"{strategy}_{lrdata['group2']}",
    }

    # check that label is present for estrategy
    # for instance there is no 'climate denialist' for the A strategy
    if not egroups[1] in strategy_data[strategy]:
        print(f"{egroups[1]} is missing from {strategy} strategy data.")
        continue
    if not egroups[2] in strategy_data[strategy]:
        print(f"{egroups[2]} is missing from {strategy} strategy data.")
        continue

    data = {
        1: strategy_data[strategy].query(f"{egroups[1]}=='1' & {egroups[2]}!='1'"),
        2: strategy_data[strategy].query(f"{egroups[2]}=='1' & {egroups[1]}!='1'")
    }

    if len(data[1]) == 0:
        print(f"{country}: there is no users labeled {egroups[1]} in data.")
        continue
    if len(data[2]) == 0:
        print(f"{country}: there is no users labeled {egroups[2]} in data.")
        continue

    for attdim in lrdata[survey]:

        label1 = egroups[1]
        label2 = egroups[2]

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
            RandomUnderSampler(random_state=SEED),
            LogisticRegression(penalty='l2', C=1e5, class_weight='balanced')
        )

        nb_splits = 10
        if not len(X) > nb_splits:
            print(f"Too low sample number ({len(X)}), ignoring {lrdata}.")
            continue

        cv_results = cross_validate(
            model, X, y, cv=nb_splits, scoring=('precision', 'recall', 'f1'),
            return_train_score=True, return_estimator=True, n_jobs=-1)

        clf_models = [pipe[-1] for pipe in cv_results['estimator']]
        clf_intercept = np.mean([clf.intercept_ for clf in clf_models])
        clf_coef = np.mean([clf.coef_ for clf in clf_models])

        precision = cv_results['train_precision'].mean()
        recall = cv_results['train_recall'].mean()
        f1 = cv_results['train_f1'].mean()

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
            "f1":  f1,
            "train_precision_mean": cv_results['train_precision'].mean(),
            "train_recall_mean": cv_results['train_recall'].mean(),
            "train_f1_mean":  cv_results['train_f1'].mean(),
            "train_precision_std": cv_results['train_precision'].std(),
            "train_recall_std": cv_results['train_recall'].std(),
            "train_f1_std":  cv_results['train_f1'].std(),
            "test_precision_mean": cv_results['test_precision'].mean(),
            "test_recall_mean": cv_results['test_recall'].mean(),
            "test_f1_mean":  cv_results['test_f1'].mean(),
            "test_precision_std": cv_results['test_precision'].std(),
            "test_recall_std": cv_results['test_recall'].std(),
            "test_f1_std":  cv_results['test_f1'].std(),
            "country": country
            }

        su = strategy.upper()
        os.makedirs(os.path.join(lrfolder, 'json'), exist_ok=True)
        result_path = os.path.join(
            lrfolder, 'json', f"strategy{su}_{attdim}_{label1}_{label2}.json")
        result_path_exp = os.path.join(
            f"exports/deliverableD21/validations/{country}",
            f"strategy{su}_{attdim}_{label1}_{label2}.json")
        with open(result_path, 'w') as file:
            json.dump(record, file)
        with open(result_path_exp, 'w') as file:
            json.dump(record, file)

        # add results data
        # print(record)
        records.append(record)

        # plot
        if plot:
            Xplot = np.sort(X.flatten())
            f = expit(Xplot * clf_coef + clf_intercept).ravel()

            if clf_intercept < 0:
                above_threshold = f > 0.5
            else:
                above_threshold = f < 0.5

            X_threshold = Xplot[above_threshold][0]

            custom_legend=[
                #densities
                Line2D([0], [0], color='white', lw=1, alpha=1, label='Users:'),
                Line2D([0], [0], color='blue', marker='o', mew=0, lw=0, alpha=0.5,
                    label=f'Labeled {label1} ({l1})'),
                Line2D([0], [0], color='red', marker='o', mew=0, lw=0, alpha=0.5,
                    label=f'Labeled {label2} ({l2})'),
                #densities
                Line2D([0], [0], color='white', lw=1, alpha=1, label='\nDensities:'),
                Line2D([0], [0], color='blue', alpha=1, label=f'Labeled {label1}'),
                Line2D([0], [0], color='red', alpha=1, label=f'Labeled {label2}\n'),
                Line2D([0], [0], color='white', lw=1, alpha=1, label='\nLogistic Reg.:'),
                Line2D([0], [0], color='k',  alpha=1, label='Model'),
                Line2D([0], [0], color='k',  linestyle=':', alpha=1,
                    label='Classification'),
                Line2D([0], [0], color='white', lw=1, alpha=1, label='cuttof'),
            ]

            fig = plt.figure(figsize=(5,  3.3))
            ax = fig.add_subplot(1,  1,  1)

            # left/blue
            sns.kdeplot(data=attdata1.to_frame(), x=attdim, color='blue', ax=ax, common_norm=False)
            ax.plot(X[y==0], np.zeros(X[y==0].size), 'o', color='blue', alpha=0.02, ms=5, mew=1)

            # right/red
            sns.kdeplot(data=attdata2.to_frame(), x=attdim, color='red', ax=ax, common_norm=False)
            ax.plot(X[y==1], np.ones(X[y==1].size),  'o', color='red',  alpha=0.02, ms=5, mew=1)

            # logistic
            ax.plot(Xplot, f, color='k')
            ax.axvline(X_threshold, linestyle=':', color='k')
            ax.axhline(0.5, linestyle=':', color='k')
            ax.text(-2.3, 0.42, r'$0.5$', color='gray', fontsize=10)
            ax.text(X_threshold+0.25, -0.18, r'$%.2f$' % (X_threshold), color='gray', fontsize=10)

            # positives & negatives
            ax.text(X_threshold+0.2, 1.1, 'True pos.', color='r', fontsize=9)
            ax.text(X_threshold-3.15, 1.1, 'False neg.', color='r', fontsize=9)
            ax.text(X_threshold+0.2, -0.1, 'False pos.', color='b', fontsize=9)
            ax.text(X_threshold-3.05, -0.1, 'True neg.', color='b', fontsize=9)

            # axis
            ax.set_xlim((-2.5, 15))
            ax.set_ylim((-0.2, 1.2))
            s = ATTDICT[survey][attdim].replace(' ', '-')
            ax.set_xlabel(f"$\delta_{{{s}}}$", fontsize=13)
            ax.set_ylabel('')
            ax.legend(handles=custom_legend, loc='center left', fontsize=8.7, bbox_to_anchor=(1, 0.5))
            ax.set_xticks([0, 2.5, 5, 7.5, 10])
            ax.set_yticks([0, 0.2, 0.4, 0.6, 0.8, 1])
            title = f
            fig.suptitle(
                t=f'{country.capitalize()}: precision=%.3f,  recall=%.3f,  F1=%.3f ' % (precision, recall, f1),
                x=0.5,
                y=0.94
            )
            plt.tight_layout()

            #saving
            figname = f'lr_{country}_{strategy}_strategy_{attdim}_'
            figname += f'{egroups[1]}_vs_{egroups[2]}'
            path_png = os.path.join(lrfolder, 'png', figname+'.png')
            plt.savefig(path_png, dpi=300)
            path_pdf = os.path.join(att_folder, 'logistic_regression', 'pdf', figname+'.pdf')
            plt.savefig(path_pdf, dpi=300)

            path_pdf_exp = os.path.join(
                f"exports/deliverableD21/validations/{country}",
                f"strategy{su}_{attdim}_{label1}_{label2}.pdf")
            plt.savefig(path_pdf_exp, dpi=300)

            if show:
                plt.show()

            plt.close()

print(f"Figures saved at {lrfolder}")

records = pd.DataFrame(records).sort_values(by='f1', ascending=False)

filename = f"{country}_{survey}_logistic_regression_cross_validate_f1_score"
dfpath = os.path.join(lrfolder, filename+'.csv')
records.to_csv(dfpath, index=False)
print(f"Logistic regression results (image and csv) saved at {lrfolder}")

if show:
    plt.show()
