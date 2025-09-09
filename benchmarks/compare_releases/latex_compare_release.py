import os
from glob import glob
import pandas as pd
from string import Template
from argparse import ArgumentParser

ap = ArgumentParser(prog="Make openia async requests.")
ap.add_argument('--country', required=True, type=str)
ap.add_argument('--year', required=True, type=int, choices=[2023, 2023, 2025])

args = ap.parse_args()
country = args.country
year = args.year

r1 = "20250416"
r2 = "next"
alias = {
    "r1": "free",
    "r2": "guided"
}
validation_patterns = {
    "r1": "/mnt/hdd2/epodata/production/v0/validations/${country}_${year}_${survey}_logistic_regression_cross_validate_f1_score_*.csv",
    "r2": "/mnt/hdd1/jimena/epodata/stage/next/validations/${country}_${year}_${survey}_logistic_regression_cross_validate_f1_score.csv"
}

s1 = alias["r1"]
s2 = alias["r2"]
outfile = f"benchmark_{country}_{year}_{s1}_vs_{s2}.txt"

# validation_pattern = "/mnt/hdd2/epodata/stage/${release}/validations/${country}_${year}_${survey}_logistic_regression_cross_validate_f1_score.csv"
# validation_pattern = Template(validation_pattern).safe_substitute(country=country, year=year)

section = "\section{${country}}"

subsection = "\subsection{${country} ${year} ${survey}}"

cols = [
    "country",
    "label1",
    "nb_samples_label1",
    "label2",
    "nb_samples_label2",
    "attitudinal_dimension",
    "survey",
    "f1",
    "auc"
]

renamed_cols = [
    "country",
    "l1",
    "# l1",
    "l2",
    "# l2",
    "att_dim",
    "survey",
    "f1",
    "auc"
]

def latexFormat(df, highlight_max=False):
    if not highlight_max:
        return df.to_latex(
            float_format="%.3f",
            escape=True,
            index=False,
            formatters={
                "l1": lambda s: s.replace("_", " "),
                "l2": lambda s: s.replace("_", " "),
                "att_dim": lambda s: s.replace("_", " "),
                "strategy": lambda s: s.replace("_", " "),
                },
            )
    else:
        df = df.reset_index().drop(columns=["index"])
        return df.style.hide(axis=0).highlight_max(
            axis=0,
            subset=["f1", "auc"],
            props='bfseries: ;') \
            .to_latex() \
            .replace("_", " ")


def dim2Latex(df, att_dim):
    # return latexFormat(df[df.att_dim == att_dim], highlight_max=False) \
    #     .split("\\\n\\bottomrule\n\\end{tabular}\n")[0] \
    #     .split("\midrule")[1]+"\\"
    return " " + latexFormat(df[df.att_dim == att_dim], highlight_max=True) \
        .split("\\\\\n\\end{tabular}\n")[0]\
        .split("strategy \\\\\n")[1] + "\\\\"


def frame2Latex(df):
    head = latexFormat(df).split("\midrule")[0]
    tail = "\\bottomrule\n\\end{tabular}\n"
    body = '\midrule' + '\n\midrule '.join([dim2Latex(df, att_dim) for att_dim in df.att_dim.unique()])
    return ' '.join([head, body, tail])

def getLatexTables(country, year, metric):
    tables = {}
    for survey in surveys:
        df = pd.read_csv(resultPath(country, year, survey))
        df = df.drop(columns=["country", "survey"], axis=1)
        df = df.rename(columns={
            "l1": "label A", 
            "l2": "label B",
            "nb_l1": "\# label A",
            "nb_l2": "\# label B",
        })
        df = df[["att_dim", "label A", "\# label A", "label B", "\# label B", "release", "f1", "auc"]]
        tables[survey] = frame2Latex(df)
    return df, tables


if __name__ == "__main__":


    validations_paths = {
        k: glob(Template(v).substitute(survey='*')) for k,v in  validation_patterns.items()
    }


    surveys = [p.split(f"{country}_{year}_")[1].split('_')[0] for p in validations_paths]


    latex = Template(section).safe_substitute(country=country.capitalize())
    latex += "\n\n"
    for survey in surveys:
        df1 = pd.read_csv(Template(validation_pattern).substitute(release=r1, survey=survey))[cols] \
            .rename(columns={k:v for k,v in zip(cols, renamed_cols)}) \
            .assign(strategy=alias["r1"])
        df2 = pd.read_csv(Template(validation_pattern).substitute(release=r2, survey=survey))[cols] \
            .rename(columns={k:v for k,v in zip(cols, renamed_cols)}) \
            .assign(strategy=alias["r2"])

        df = pd.concat([df2, df1]) \
            .sort_values(["att_dim", "l2", "l1"]) \
            .drop(columns=["country", "survey"])

        latex += Template(subsection).safe_substitute(
            country=country.capitalize(),
            year=year,
            survey=survey)
        latex += "\n\n"
        latex += frame2Latex(df)


    with open(outfile, 'w') as f:
        f.write(latex)

    print(f"Latex code save at {outfile}")
