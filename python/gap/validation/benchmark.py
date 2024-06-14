import yaml
import numpy as np
import pandas as pd
from argparse import ArgumentParser

from some4demexp.inout import \
    set_output_folder, \
    set_output_folder_att, \
    load_att_embeddings, \
    load_issues, \
    save_issues_benckmarks, \
    set_output_folder_emb, \
    load_ide_embeddings, \
    get_ide_ndims

from corg import \
    BenchmarkDimension, \
    DiscoverDimension

from some4demdb import SQLite

from some4demexp.conf import \
    LOGISTICREGRESSIONS, \
    ATTDICT


# parse arguments and set paths
# parse arguments and set paths
ap = ArgumentParser()
ap.add_argument('--config', type=str, required=True)
ap.add_argument('--country', type=str, required=True)
ap.add_argument('--survey', type=str, required=True)
ap.add_argument('--output', type=str, required=True)

args = ap.parse_args()
config = args.config
country = args.country
survey = args.survey
output = args.output

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

estrategy_data = {
    'A': keywords_data,
    'C': llm_data
}

benchmark_records = []
discover_records = []


for estrategy in estrategy_data.keys():

    for lrdata in LOGISTICREGRESSIONS:

        egroups = {
            1:  f"{estrategy}_{lrdata['group1']}",
            2:  f"{estrategy}_{lrdata['group2']}",
        }

        # check that label is present for estrategy
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

        if len(data[1]) == 0:
            print(f"{country}: there is no users labeled {egroups[1]} in data.")
            continue
        if len(data[2]) == 0:
            print(f"{country}: there is no users labeled {egroups[2]} in data.")
            continue

        for attdim in lrdata[survey]:

            label1 = egroups[1]
            label2 = egroups[2]

            attdata1 = data[1][['entity', attdim]].assign(label=0)
            attdata2 = data[2][['entity', attdim]].assign(label=1)

            # egalize sample
            SEED = 666
            n = min(len(attdata1), len(attdata2))
            _data = pd.concat([
                attdata1.sample(n=n, random_state=SEED),
                attdata2.sample(n=n, random_state=SEED)
            ])
            print(f"Left-Right data downsampled to {n} samples of each categorie.")

            # (1) Measure accuracy of estimated positions
            Y = _data[['entity', 'label']]

            # (1.1) Benchmark attitudinal dimension
            mb = BenchmarkDimension(
                compute_train_error=True,
                undersample_data=False,
                random_state=SEED
            )
            Xb = _data[['entity', attdim]]
            mssg = f"Fitting regresion on {len(data)} samples for  "
            mssg += f"attitudinal dimension {attdim}... "
            print(mssg)
            mb.fit(Xb, Y)

            benchmark_records.append({
                'embedding': 'attitudinal',
                'dimension': attdim,
                'issue': f"{label1}_vs_{label2}",
                'beta0': mb.beta0_,
                'beta1': mb.beta1_,
                'precision_train_': mb.precision_train_,
                'recall_train_': mb.recall_train_,
                'f1_score_train_': mb.f1_score_train_,
            })

            # for idedim in IDEDIMS:
            #     mb = BenchmarkDimension(
            #         compute_train_error=True,
            #         undersample_data=False,
            #         random_state=666
            #     )
            #     Xb = labeled_data[['entity', f'latent_dimension_{idedim}']]
            #     print(f"Fitting regresion for ide benchmark {idedim}... ")
            #     mb.fit(Xb, Y)

            #     benchmark_records.append({
            #         'embedding': 'ideological',
            #         'dimension': idedim,
            #         'issue': issue,
            #         'beta0': mb.beta0_,
            #         'beta1': mb.beta1_,
            #         'precision_train_': mb.precision_train_,
            #         'recall_train_': mb.recall_train_,
            #         'f1_score_train_': mb.f1_score_train_,
            #     })

            # # (1.2) Discover Dimension

            # # # ideological embedding
            # # md = DiscoverDimension()
            # # Xd = data[['entity']+[f'latent_dimension_{idedim}' for idedim in IDEDIMS]]
            # # md.fit(Xd, Y)

            # # discover_records.append({
            # #     'embedding': 'ideological',
            # #     'issue': issue,
            # #     'model_decision_boundary_': md.model_decision_boundary_,
            # #     'beta1': md.decision_hyperplane_unit_normal,
            # #     'precision_train_': md.precision_train_,
            # #     'recall_train_': md.recall_train_,
            # #     'f1_score_train_': md.f1_score_train_,
            # # })

            # # attitudinal embedding
            # md = DiscoverDimension()
            # Xd = data[['entity']+ATTDIMS]
            # md.fit(Xd, Y)

            # discover_records.append({
            #     'embedding': 'attitudinal',
            #     'issue': issue,
            #     'model_decision_boundary_': md.model_decision_boundary_,
            #     'beta1': md.decision_hyperplane_unit_normal,
            #     'precision_train_': md.precision_train_,
            #     'recall_train_': md.recall_train_,
            #     'f1_score_train_': md.f1_score_train_,
            # })

benchmark = pd.DataFrame \
    .from_records(benchmark_records) \
    .drop_duplicates() \
    .sort_values(by=['embedding', 'issue', 'dimension'])

# print(benchmark)
save_issues_benckmarks(
    att_folder,
    benchmark)

# discover_records = pd.DataFrame.from_records(discover_records)
# print(discover_records)
