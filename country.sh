#!/bin/bash

COUNTRY=$1
SURVEY=$2


if [[ "${SURVEY}" = "ches2019" ]]
then
    python pipeline.py \
        --country=${COUNTRY} \
        --output=wip \
        --survey=ches2019 \
        --attdims=lrgen,lrecon,eu_position,people_vs_elite,antielite_salience,corrupt_salience,sociallifestyle,galtan,immigrate_policy,environment,enviro_salience,nationalism
fi

if [[ "${SURVEY}" = "gps2019" ]]
then
    python pipeline.py \
        --country=${COUNTRY} \
        --output=wip \
        --survey=gps2019 \
        --attdims=V4_Scale,V6_Scale,V8_Scale,V9,V10,V12,V13,V14,V18,V19,V20,V21
fi

if [[ "${SURVEY}" = "ches2023" ]]
then
    python pipeline.py \
        --country=${COUNTRY} \
        --output=wip \
        --survey=ches2023 \
        --attdims=antielite_salience,galtan,eu_position,lrecon,refugees
fi