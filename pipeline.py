import os
import sys
import yaml
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
    plot_attitudinal_embedding
from gap.validations import make_validation

# parse arguments and set paths
ap = ArgumentParser()
ap.add_argument('--country', type=str, required=True)
ap.add_argument('--dbpath', type=str)
ap.add_argument('--survey', type=str, required=True, choices=['ches2023', 'ches2019', 'gps2019'])
ap.add_argument('--ndimsviz', type=int, default=3)
ap.add_argument('--attdims', type=str, required=False)
ap.add_argument('--config', type=str, default="configs/embeddings.yaml")
ap.add_argument('--output', type=str, required=False)
ap.add_argument('--ideological', action='store_true')
ap.add_argument('--novalidation', action='store_true')
ap.add_argument('--plot', action='store_true')
ap.add_argument('--show', action='store_true')
args = ap.parse_args()
country = args.country
dbpath = args.dbpath
output = args.output
config = args.config
survey = args.survey
ndimsviz = args.ndimsviz
attdims = args.attdims
ideological = args.ideological
novalidation = args.novalidation
plot = args.plot
show = args.show


if not dbpath:
    dbpath = f"{country}.db"

if not output:
    output = country

# 0. Get things setted
logger = logging.getLogger(__name__)

with open(config, "r", encoding='utf-8') as fh:
    params = yaml.load(fh, Loader=yaml.SafeLoader)

if plot or show:
    vizconfig = f"configs/vizconfigs/{country}.yaml"
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

# Set the number of dimension for the ideological embedding
availableSurveys = SQLITE.getAvailableSurveys()
nPartiesPerSurvey = [SQLITE.getNParties(s) for s in availableSurveys]
ideN = max(nPartiesPerSurvey) - 1

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
ATTDIMS = params['attitudinal_dimensions'][survey]
if not attdims:
    attdims = ATTDIMS
else:
    attdims = attdims.split(',')

# 1. Create and plot ideological embedding
if ideological:
    create_ideological_embedding(
        SQLITE,
        INOUT,
        NB_MIN_FOLLOWERS,
        MIN_OUTDEGREE,
        ideN,
        logger)

    if plot:
        plot_ideological_embedding(
            SQLITE,
            INOUT,
            country,
            survey,
            ndimsviz,
            vizparams,
            show,
            logger)

# 2. Create and plot attitudinal embedding
create_attitudinal_embedding(
    SQLITE,
    INOUT,
    ATTDIMS,
    survey,
    logger)

if plot:
    for attdimspair in  combinations(attdims, 2):
        plot_attitudinal_embedding(
            SQLITE,
            INOUT,
            list(attdimspair),
            country,
            survey,
            vizparams,
            show,
            logger)

# 3. Make validations
if not novalidation:
    records = []
    for attdim in attdims:
        record = make_validation(
            SQLITE=SQLITE,
            INOUT=INOUT,
            SEED=187,
            country=country,
            survey=survey,
            attdim=attdim,
            plot=plot,
            show=show,
            logger=logger)
        if record:
            records.append(record)

    if len(records) > 0:
        records = pd.DataFrame(records).sort_values(by='f1', ascending=False)
        filename = f"{country}_{survey}_logistic_regression_cross_validate_f1_score"
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
            "f1"]
        os.system(f"xan select {','.join(cols)} {dfpath} | xan view")
        # print(records[cols])
