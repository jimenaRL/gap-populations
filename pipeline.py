import sys
import yaml
import logging
from argparse import ArgumentParser

from gap.sqlite import SQLite
from gap.embeddings import \
    create_ideological_embedding, \
    create_attitudinal_embedding
from gap.visualizations import \
    plot_ideological_embedding, \
    plot_attitudinal_embedding
from gap.logistic_regression import make_validations
from gap.inout import \
    get_ide_ndims, \
    set_output_folder, \
    set_output_folder_emb, \
    set_output_folder_att

# parse arguments and set paths
ap = ArgumentParser()
ap.add_argument('--config', type=str, required=True)
ap.add_argument('--country', type=str, required=True)
ap.add_argument('--surveys', type=str, required=True)
ap.add_argument('--output', type=str, required=True)
ap.add_argument('--show', type=str, default=True)
args = ap.parse_args()
config = args.config
output = args.output
surveys = args.surveys.split(',')
country = args.country
show = args.show

# 0. Get things setted
logfile = f'{country}.log'
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.DEBUG,
    format=f"%(asctime)s [%(levelname)s] {country.upper()} %(message)s",
    handlers=[
        logging.FileHandler(logfile, 'w', 'utf-8'),
        logging.StreamHandler(sys.stdout)],
)

with open(config, "r", encoding='utf-8') as fh:
    params = yaml.load(fh, Loader=yaml.SafeLoader)

vizconfig = f"configs/vizconfigs/{country}.yaml"
with open(vizconfig, "r", encoding='utf-8') as fh:
    vizparams = yaml.load(fh, Loader=yaml.SafeLoader)

NB_MIN_FOLLOWERS = params['sources_min_followers']
MIN_OUTDEGREE = params['sources_min_outdegree']

SQLITE = SQLite(
    db_path=params['sqlite'].format(country=country),
    tables=params['tables'],
    sources_min_followers=NB_MIN_FOLLOWERS,
    sources_min_outdegree=MIN_OUTDEGREE,
    logger=logger,
    country=country)

# 0. Get ideological embedding space dimension and folder paths
ideN = max([
    get_ide_ndims(SQLITE.getPartiesMapping([survey]), survey)
    for survey in surveys])
folder = set_output_folder(
    params, country, output, logger)
emb_folder = set_output_folder_emb(
    params, country, ideN, output, logger)

# 1. Create and plot ideological embedding
create_ideological_embedding(
    SQLITE,
    NB_MIN_FOLLOWERS,
    MIN_OUTDEGREE,
    ideN,
    folder,
    emb_folder,
    logger)

n_dims_to_viz=3
for survey in surveys:

    plot_ideological_embedding(
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
        logger)

# 2. Create and plot attitudinal embedding

for survey in surveys:

    ATTDIMS = params['attitudinal_dimensions'][survey]
    att_folder = set_output_folder_att(
        params, survey, country, ideN, output, logger)

    create_attitudinal_embedding(
        SQLITE,
        NB_MIN_FOLLOWERS,
        MIN_OUTDEGREE,
        ATTDIMS,
        ideN,
        survey,
        folder,
        emb_folder,
        att_folder,
        logger)

    plot_attitudinal_embedding(
        SQLITE,
        NB_MIN_FOLLOWERS,
        MIN_OUTDEGREE,
        ATTDIMS,
        country,
        ideN,
        survey,
        folder,
        emb_folder,
        att_folder,
        vizparams,
        show,
        logger)

# 3. Make validations

make_validations(
    SQLITE,
    187,
    country,
    survey,
    att_folder,
    True,
    True,
    logger)

# 3. Show stats