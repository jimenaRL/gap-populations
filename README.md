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

To compute embeddings for a given *country* on a specific survey and validation on specific attitudinal dimensions run

```
python pipeline.py --country=country --dbpath=country.db --ideological --attitudinal --validation --survey=survey --attdims=attdim1,attdim2,attdim3 
```

To options `--plot` and `--show` will additionally create and show images for the embeddings and for the validations. Plase notice that this require latex to be installed in your machine to correctly display images annotations.

For instances, the commands

```
python pipeline.py --country=uruguay --dbpath=uruguay2023.db --ideological --survey=gps2019 --plot
```

```
python pipeline.py --country=uruguay --dbpath=uruguay2023.db --attitudinal --survey=gps2019 --attdims=V4_Scale,V8_Scale  --plot
```
```
python pipeline.py --country=uruguay --dbpath=uruguay2023.db --validation --survey=gps2019 --attdims=V4_Scale  --plot
```


To compute embeddings for a given *country* on all available surveys and validations on all attitudinal dimensions run

```
source gap.sh country
```
