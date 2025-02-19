import os
import sys
import yaml
import pathlib
import logging
from itertools import combinations
from argparse import ArgumentParser

import pandas as pd

from gap.sqlite import SQLite
from gap.inout import InOut
from gap.embeddings import \
    create_ideological_embedding, \
    create_attitudinal_embedding
from gap.visualizations import \
    plot_ideological_embedding, \
    plot_attitudinal_embedding, \
    plot_1d_attitudinal_distributions
from gap.validations import make_validation
from gap.labels import labels_stats


SURVEYS = ['ches2023', 'ches2019', 'ches2020', 'gps2019']
PARENTFOLDER = pathlib.Path(__file__).parent.resolve()
CONFIGDEFAULTPATH = os.path.join(PARENTFOLDER, "configs/embeddings_pseudonymized_alldata.yaml")
VIZCONFIGDEFAULTPATH = os.path.join(PARENTFOLDER, "configs/vizconfigs/template.yaml")
# parse arguments and set paths
ap = ArgumentParser()
ap.add_argument('--country', type=str, required=True)
ap.add_argument('--year', type=str, required=True)
ap.add_argument('--dbpath', type=str, required=True, help="Path to the dataset")
ap.add_argument('--survey', type=str, required=False, default=None, choices=SURVEYS)
ap.add_argument('--ndimsviz', type=int, default=2)
ap.add_argument('--ideN', type=int, default=20)
ap.add_argument('--attdims', type=str, required=False)
ap.add_argument('--att_missing_values_strategy', type=str, required=False, choices=['drop_dims', 'drop_parties'])
ap.add_argument('--config', type=str, required=False, default=CONFIGDEFAULTPATH)
ap.add_argument('--vizconfig', type=str, default=VIZCONFIGDEFAULTPATH)
ap.add_argument('--output', type=str, required=False)
ap.add_argument('--ideological', action='store_true')
ap.add_argument('--attitudinal', action='store_true')
ap.add_argument('--validation', action='store_true')
ap.add_argument('--distributions', action='store_true')
ap.add_argument('--bivariate', action='store_true')
ap.add_argument('--no_recomputation', action='store_true')
ap.add_argument('--nbsplits_validation', type=int, default=10)
ap.add_argument('--seed_validation', type=int, default=42)
ap.add_argument('--labels', action='store_true')
ap.add_argument('--plot', action='store_true')
ap.add_argument('--show', action='store_true')
args = ap.parse_args()
country = args.country
year = args.year
dbpath = args.dbpath
output = args.output
config = args.config
vizconfig = args.vizconfig
survey = args.survey
ideN = args.ideN
ndimsviz = args.ndimsviz
attdims = args.attdims
att_missing_values_strategy = args.att_missing_values_strategy
ideological = args.ideological
attitudinal = args.attitudinal
labels = args.labels
validation = args.validation
distributions = args.distributions
bivariate = args.bivariate
no_recomputation = args.no_recomputation
seed = args.seed_validation
nb_splits = args.nbsplits_validation
plot = args.plot
show = args.show


if not (ideological or attitudinal or validation or labels or distributions or bivariate):
    e = "Please add at least one of the following actions as argument to run "
    e += "the script:\n--ideological\n--attitudinal\n--validation\n--labels."
    ap.error(e)

if (attitudinal or validation) and not survey:
    e = f"Please specify one fo the surveys in {SURVEYS} for computing "
    e += f"attitudinal embeddings."
    ap.error(e)

if not output:
    output = os.path.join(PARENTFOLDER, f"{country}_{year}")

# 0. Get things setted
logger = logging.getLogger(__name__)

with open(config, "r", encoding='utf-8') as fh:
    params = yaml.load(fh, Loader=yaml.SafeLoader)

if plot or show:
    with open(vizconfig, "r", encoding='utf-8') as fh:
        vizparams = yaml.load(fh, Loader=yaml.SafeLoader)

NB_MIN_FOLLOWERS = params['sources_min_followers']
MIN_OUTDEGREE = params['sources_min_outdegree']

SQLITE = SQLite(
    db_path=dbpath,
    tables=params['tables'],
    sources_min_followers=NB_MIN_FOLLOWERS,
    sources_min_outdegree=MIN_OUTDEGREE,
    logger=logger,
    country=country)

INOUT = InOut(
    params=params,
    country=country,
    n_latent_dimensions=ideN,
    survey=survey,
    output=output,
    logger=logger
)

logfile = os.path.join(INOUT.basepath, f'{country}.log')
logging.basicConfig(
    level=logging.INFO,
    format=f"%(asctime)s [%(levelname)s] {country.upper()} %(message)s",
    handlers=[
        logging.FileHandler(logfile, 'w', 'utf-8'),
        logging.StreamHandler(sys.stdout)],
)

# Get attitudinal dimension to plot and validate if not specified
if survey:
    ATTDIMS = params['attitudinal_dimensions'][survey]
    if not attdims:
        attdims = ATTDIMS
    else:
        attdims = attdims.split(',')


# 1. Create and plot ideological embedding
if ideological:
    if not no_recomputation:
        create_ideological_embedding(
            SQLITE,
            INOUT,
            NB_MIN_FOLLOWERS,
            MIN_OUTDEGREE,
            ideN,
            logger)

    if bivariate and plot:
        plot_ideological_embedding(
            SQLITE,
            INOUT,
            country,
            ndimsviz,
            vizparams,
            show,
            logger)

# 2. Create and plot attitudinal embedding
if attitudinal:

    # Set the number of dimension for the mapping to the attitudinal space
    # 1. Get the number of unique survey parties corresponding with an available
    # EPO party after follower>Mps graph preprocessing
    survey_party_acronym = f"{survey.upper()}_party_acronym"
    query = f"""
        SELECT COUNT(DISTINCT(p.{survey_party_acronym}))
        FROM mp_follower_graph_minin_25_minout_3 g
        LEFT JOIN mp_annotation USING(mp_pseudo_id)
        LEFT JOIN party_mapping p USING(EPO_party_acronym)
        WHERE p.{survey_party_acronym} is NOT NULL"""
    res = SQLITE.retrieve(query)
    numberEPOPartiesWithMPsinPPGraph = res[0][0]
    N_survey = numberEPOPartiesWithMPsinPPGraph - 1

    if not no_recomputation:
        create_attitudinal_embedding(
            SQLITE,
            INOUT,
            ATTDIMS,
            survey,
            N_survey,
            logger,
            att_missing_values_strategy)

    if distributions and plot:
        plot_1d_attitudinal_distributions(
            SQLITE,
            INOUT,
            country,
            survey,
            show)

    if bivariate and plot:
        for attdimspair in  combinations(attdims, 2):
            plot_attitudinal_embedding(
                SQLITE,
                INOUT,
                list(attdimspair),
                country,
                survey,
                vizparams,
                show,
                logger,
                att_missing_values_strategy)

# 3. Make validations
if validation:
    records = []
    for attdim in attdims:
        record = make_validation(
            SQLITE=SQLITE,
            INOUT=INOUT,
            cv_seed=seed,
            nb_splits=nb_splits,
            country=country,
            survey=survey,
            attdim=attdim,
            plot=plot,
            show=show,
            logger=logger)

        if record:
            records.extend(record)

    if len(records) > 0:
        records = pd.DataFrame(records).sort_values(by='f1', ascending=False)
        filename = f"{country}_{year}_{survey}_logistic_regression_cross_validate_f1_score"
        valfolder = os.path.join(INOUT.att_folder, 'validations')
        dfpath = os.path.join(valfolder, filename+'.csv')
        records.to_csv(dfpath, index=False)

        cols = [
            "country",
            "strategy",
            "label1",
            "nb_samples_label1",
            "label2",
            "nb_samples_label2",
            "attitudinal_dimension",
            "survey",
            "f1",
            # "recall",
            # "precision",
            "auc",
            # "chi2_stat",
            "chi2_pval",
            ]
        rcols = [
            "country",
            "strategy",
            "l1",
            "#l1",
            "l2",
            "#l2",
            "att_dim",
            "survey",
            "f1",
            # "recall",
            # "precision",
            "auc",
            # "chi2_stat",
            "chi2_pval",
            ]
        os.system(f"xan select {','.join(cols)} {dfpath} | xan rename {','.join(rcols)} | xan view -I")
        # print(records[cols])
        logger.info(f"VALIDATION: scores saved at {dfpath}")

# 4. Compute labels statistics
if labels:
    for attdim in attdims:
        labels_stats(
            SQLITE, INOUT, survey, country, attdim, logger, plot, show)