import os
from argparse import ArgumentParser

FOLDERS = {
    'raw': {
        2023: '/home/jimena/work/dev/some4demDB/dbs',
        2020: '/home/jimena/work/dev/some4demDB/dbs/2020',
    },
    'lut': '/home/jimena/work/dev/gap-populations/temp/lut',
    'identifiable': '/home/jimena/work/dev/gap-populations/temp/identifiable',
    'pseudoanonymized': '/home/jimena/work/dev/gap-populations/temp/pseudoanonymized',
}

def get_path(country, year, kind):
    if kind == 'raw':
        return os.path.join(FOLDERS['raw'][year], f'{country}.db')
    else:
        return os.path.join(FOLDERS[kind], f'{country}_{year}_{kind}.db')


COUNTRIES = {
    2020: [
        "austria",
        "belgium",
        "denmark",
        "finland",
        "greece",
        "iceland", # IDENTIFIABLE checkTablesSchema FAILS
        "latvia",
        "malta",
        "luxembourg",
        "norway",
        "newzealand",
        "poland",
        "slovenia",
        "sweden",
        # "switzerland", # RAW checkSameSizeTables FAILS # IDENTIFIABLE checkTablesSchema FAILS
    ],
    2023: [
        "austria",
        "belgium",
        "cyprus",
        "czechia",
        "denmark",
        "ecuador",
        "estonia",
        "finland", # IDENTIFIABLE checkTablesExistence FAILS because of gps2019 att table missing
        "france",
        "greece",
        "hungary",
        "iceland",  # IDENTIFIABLE checkTablesSchema FAILS
        "ireland",  # IDENTIFIABLE checkTablesSchema FAILS
        "latvia",
        "lithuania",
        "luxembourg",
        "malta",
        "netherlands",
        "newzealand",
        "norway",  # IDENTIFIABLE checkTablesSchema FAILS
        "peru",
        "poland",
        "portugal",
        "romania",
        "serbia",
        "slovakia",
        "slovenia",
        "sweden",
        "switzerland",   # IDENTIFIABLE checkTablesSchema FAILS
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
            command = f"./validate_country.sh {country} {year} {dbpath}"
            print(f"[RUNNING]: {command}")
            os.system(command)
