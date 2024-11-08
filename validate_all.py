import os
from argparse import ArgumentParser

FOLDERS = {
    'raw': {
        2023: '/home/jimena/work/dev/some4demDB/dbs',
        2020: '/home/jimena/work/dev/some4demDB/dbs/2020',
    },
}

def get_path(country, year, kind):
    if kind == 'raw':
        return os.path.join(FOLDERS['raw'][year], f'{country}.db')
    else:
        return os.path.join(FOLDERS[kind], f'{country}_{year}_{kind}.db')


COUNTRIES = {
    2020: [
    ],
    2023: [
        "austria",
        "belgium",
        "cyprus",
        "denmark",
        "estonia",
        "finland",
        "france",
        "germany",
        "greece",
        "iceland",
        "ireland",
        "latvia",
        "lithuania",
        "luxembourg",
        "malta",
        "netherlands",
        "newzealand",
        "portugal",
        "romania",
        "serbia",
        "slovakia",
        "slovenia",
        "sweden",
        "uruguay",
    ],
}


if __name__ == "__main__":

    # parse arguments and set paths
    ap = ArgumentParser()
    ap.add_argument('--country', type=str, default="")
    ap.add_argument('--year', type=int, default=0)
    args = ap.parse_args()
    country = args.country
    year = args.year

    if year:
        countries = {2023: [], 2020: []}
        if country:
            countries[year] = [country]
        else:
            countries[year] = COUNTRIES[year]
    else:
        countries = COUNTRIES

    for year in [2020, 2023]:
        for country in countries[year]:
            dbpath = get_path(country, year, kind="raw")
            print(f"--------------- {country} {year} ---------------")
            print(dbpath)
            command = f"bash -e validate_country.sh {country} {year} {dbpath}"
            print(f"[RUNNING]: {command}")
            os.system(command)
