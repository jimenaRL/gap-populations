# Global Attitudinally Positioned Populations for Multidimensional Polarization Studies

## Installation

1. Clone or download this repository and cd to the folder `gap-populations`
2. Pip install the python packages from  the [requirements file](https://github.com/jimenaRL/gap-populations/tree/main/python/requirements.txt) 
3. Add the path of the [python](https://github.com/jimenaRL/gap-populations/tree/main/python) folder to the PYTHONPATH terminal variable : `export PYTHONPATH=$PYTHONPATH:$(pwd)/python` 
5. Copy the sqlite file (.db extension) of a given *country* to the `gap-populations` folder

## Run

To compute embeddings for a given *country* on all available surveys and validations on all attitudinal dimensions run


`        python pipeline.py --country=*country* --survey=ches2019 --attdims=lrgen

To compute embeddings for a given *country* on all available surveys and validations on all attitudinal dimensions run

`source gap.sh country`
