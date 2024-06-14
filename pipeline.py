import sys
import yaml
import logging
from argparse import ArgumentParser

from some4demdb import SQLite
from some4demexp.ideological_embedding import create_ideological_embedding
from some4demexp.attitudinal_embedding import create_attitudinal_embedding
from some4demexp.inout import \
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
args = ap.parse_args()
config = args.config
output = args.output
surveys = args.surveys.split(',')
country = args.country

# 0. Get things setted
logfile = f'logs/{country}.log'
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

with open(params['params_db'], "r", encoding='utf-8') as fh:
    params_db = yaml.load(fh, Loader=yaml.SafeLoader)

SQLITE = SQLite(
    db_path=params['sqlite'].format(country=country),
    tables=params_db['output']['tables'],
    pp_params=params_db['preprocess'],
    logger=logger,
    country=country)

NB_MIN_FOLLOWERS = params['sources_min_followers']
MIN_OUTDEGREE = params['sources_min_outdegree']


# get ideological embedding space dimension
ideN = max([
    get_ide_ndims(SQLITE.getPartiesMapping([survey]), survey)
    for survey in surveys])
folder = set_output_folder(
    params, country, output, logger)
emb_folder = set_output_folder_emb(
    params, country, ideN, output, logger)

# # 1. Create ideological embedding
create_ideological_embedding(
    SQLITE,
    NB_MIN_FOLLOWERS,
    MIN_OUTDEGREE,
    ideN,
    folder,
    emb_folder,
    logger)

# 2. Create create_attitudinal embedding

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

