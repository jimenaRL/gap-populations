import os
from glob import glob
from argparse import ArgumentParser

import pandas as pd

# parse arguments and set paths
ap = ArgumentParser()
ap.add_argument('--country', type=str, required=False, default="")
ap.add_argument('--year', type=str, required=False, default="")
args = ap.parse_args()
country = args.country
year = args.year

if country and year:
    base = f"{country}_{year}"
    ouputpath = f'validations_{base}.xlsx'
else:
    base = "*"
    ouputpath = 'validations.xlsx'

basepath = os.path.join(
    "./",
    base,
    f"min_followers_25_min_outdegree_3/*/*/validations",
    f"*_*_logistic_regression_cross_validate_f1_score.csv"
)

paths = glob(basepath)
mssg = '\n'+'\t\n'.join(paths)
# print(f"Adding paths at {mssg}")
df = pd.concat([pd.read_csv(path) for path in paths])
df = df.round(2)

df = df[['strategy', 'label1', 'label2', 'nb_samples_label1',
       'nb_samples_label2', 'attitudinal_dimension',
       'attitudinal_dimension_name', 'survey', 'precision', 'recall', 'f1',
       'train_precision_by_folds', 'train_recall_by_folds', 'train_f1_by_folds',
      'country', 'path']]

df = df.rename(columns={
    'nb_samples_label1': 'nb_label1',
    'nb_samples_label2': 'nb_label2',
    'attitudinal_dimension': 'dim',
    'attitudinal_dimension_name': 'dim_name',
    })


df = df[~df.path.isna()]
df = df.assign(year=df.path.apply(lambda p: '2020' if '2020' in p else '2023'))
df = df.assign(country=df.country+'_'+df.year)

del df["path"]

with pd.ExcelWriter(ouputpath) as writer:
    for c in sorted(set(df.country.tolist())):
        df[df.country == c].to_excel(writer, sheet_name=c, index=False)
