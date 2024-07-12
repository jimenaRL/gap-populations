# Global Attitudinally Positioned Populations for Multidimensional Polarization Studies

## Installation

1. Clone or download this repository and cd to the `gap-populations` folder:
```
git clone https://github.com/jimenaRL/gap-populations && cd gap-populations
```
2. Pip install the python packages from  the [requirements file](https://github.com/jimenaRL/gap-populations/tree/main/python/requirements.txt):
```
pip install -r python/requirements.txt
```
4. Add the path of the [python](https://github.com/jimenaRL/gap-populations/tree/main/python) folder to the PYTHONPATH terminal variable:
```
export PYTHONPATH=$PYTHONPATH:$(pwd)/python
```

## Run

Copy the sqlite file of a given *country* to the `gap-populations` folder:

```
cp /path/to/the/db/folder/country.db ./country.db
```

To compute embeddings for a given *country* on a specific survey and validation on specific attitudinal dimension run

```
python pipeline.py --country=country --dbpath=country.db --survey=ches2019 --attdims=lrgen
```

To compute embeddings for a given *country* on all available surveys and validations on all attitudinal dimensions run

```
source gap.sh country
```
