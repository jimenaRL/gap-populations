import os
from glob import glob
import pandas as pd

country = "finland"

basepath = os.path.join(
    f"wip/*",
    f"min_followers_25_min_outdegree_3/*/*/validations",
    f"*_*_logistic_regression_cross_validate_f1_score.csv"
)

paths = glob(basepath)
df = pd.concat([pd.read_csv(path) for path in paths])
df = df.round(2)

df = df[['strategy', 'label1', 'label2', 'nb_samples_label1',
       'nb_samples_label2', 'attitudinal_dimension',
       'attitudinal_dimension_name', 'survey', 'precision', 'recall', 'f1',
       'country']]

df = df.rename(columns={
    'nb_samples_label1': 'nb_label1',
    'nb_samples_label2': 'nb_label2',
    'attitudinal_dimension': 'dim',
    'attitudinal_dimension_name': 'dim_name',
    })

with pd.ExcelWriter('output.xlsx') as writer:
    for c in sorted(set(df.country.tolist()))
        df[df.country == c].to_excel(writer, sheet_name=c, index=False)
