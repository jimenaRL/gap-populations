#!/bin/bash

function gn() {

    DBPATH=$1
    COUNTRY=$2
    SURVEY=$3
    YEAR=$4
    OUTPUT_FOLDER=$5

    echo "--------------------------------------------------"
    echo "[COUNTRY] ${COUNTRY}"
    echo "[YEAR] ${YEAR}"
    echo "[DBPATH] ${DBPATH}"
    echo "[OUTPUT] ${OUTPUT_FOLDER}"
    echo "[SURVEY] ${SURVEY}"
    echo "--------------------------------------------------"

    command="python /home/jimena/work/dev/gap-populations/pipeline.py  --dbpath=$DBPATH --country=$COUNTRY --year=$YEAR --output=$OUTPUT_FOLDER --validation"

    if [[ "$SURVEY" = "ches2019" ]]
    then
        command="${command} --survey=ches2019 --attdims=lrgen,lrecon,eu_position,people_vs_elite,antielite_salience,corrupt_salience,sociallifestyle,galtan,immigrate_policy,environment,enviro_salience,nationalism"
    fi

    if [[ "$SURVEY" = "gps2019" ]]
    then
        command="${command} --survey=gps2019 --attdims=V4_Scale,V6_Scale,V8_Scale,V9,V10,V12,V13,V14,V18,V19,V20,V21"
    fi

    if [[ "$SURVEY" = "ches2023" ]]
    then
        command="${command} --survey=ches2023 --attdims=antielite_salience,galtan,eu_position,lrecon,refugees"
    fi

    echo "--------------------------------------------------"
    echo "[RUNNING] ${command}"
    echo "--------------------------------------------------"
    eval "$command"

}

function fn() {

    COUNTRY=$1
    YEAR=$2
    DBPATH=$3
    OUTPUT_FOLDER=$4

    if [[ $COUNTRY = "argentina" ]]
    then
        gn $DBPATH $COUNTRY gps2019 $YEAR $OUTPUT_FOLDER
    fi

    if [[ $COUNTRY = "australia" ]]
    then
        gn $DBPATH $COUNTRY gps2019 $YEAR $OUTPUT_FOLDER
    fi

    if [[ $COUNTRY = "austria" ]]
    then
        gn $DBPATH $COUNTRY gps2019 $YEAR $OUTPUT_FOLDER
        gn $DBPATH $COUNTRY ches2019 $YEAR $OUTPUT_FOLDER
        gn $DBPATH $COUNTRY ches2023 $YEAR $OUTPUT_FOLDER
    fi

    if [[ $COUNTRY = "belgium" ]]
    then
        gn $DBPATH $COUNTRY gps2019 $YEAR $OUTPUT_FOLDER
        gn $DBPATH $COUNTRY ches2019 $YEAR $OUTPUT_FOLDER
        gn $DBPATH $COUNTRY ches2023 $YEAR $OUTPUT_FOLDER
    fi

    if [[ $COUNTRY = "brazil" ]]
    then
        gn $DBPATH $COUNTRY gps2019 $YEAR $OUTPUT_FOLDER
    fi

    if [[ $COUNTRY = "canada" ]]
    then
        gn $DBPATH $COUNTRY gps2019 $YEAR $OUTPUT_FOLDER
    fi

    if [[ $COUNTRY = "chile" ]]
    then
        gn $DBPATH $COUNTRY gps2019 $YEAR $OUTPUT_FOLDER
    fi

    if [[ $COUNTRY = "colombia" ]]
    then
        gn $DBPATH $COUNTRY gps2019 $YEAR $OUTPUT_FOLDER
    fi

    if [[ $COUNTRY = "croatia" ]]
    then
        gn $DBPATH $COUNTRY gps2019 $YEAR $OUTPUT_FOLDER
        gn $DBPATH $COUNTRY ches2019 $YEAR $OUTPUT_FOLDER
        gn $DBPATH $COUNTRY ches2023 $YEAR $OUTPUT_FOLDER
    fi

    if [[ $COUNTRY = "cyprus" ]]
    then
        gn $DBPATH $COUNTRY gps2019 $YEAR $OUTPUT_FOLDER
        gn $DBPATH $COUNTRY ches2019 $YEAR $OUTPUT_FOLDER
    fi

    if [[ $COUNTRY = "czechia" ]]
    then
        gn $DBPATH $COUNTRY gps2019 $YEAR $OUTPUT_FOLDER
        gn $DBPATH $COUNTRY ches2019 $YEAR $OUTPUT_FOLDER
        gn $DBPATH $COUNTRY ches2023 $YEAR $OUTPUT_FOLDER
    fi

    if [[ $COUNTRY = "denmark" ]]
    then
        gn $DBPATH $COUNTRY gps2019 $YEAR $OUTPUT_FOLDER
        gn $DBPATH $COUNTRY ches2019 $YEAR $OUTPUT_FOLDER
        gn $DBPATH $COUNTRY ches2023 $YEAR $OUTPUT_FOLDER
    fi

    if [[ $COUNTRY = "ecuador" ]]
    then
        gn $DBPATH $COUNTRY gps2019 $YEAR $OUTPUT_FOLDER
    fi

    if [[ $COUNTRY = "estonia" ]]
    then
        gn $DBPATH $COUNTRY gps2019 $YEAR $OUTPUT_FOLDER
        gn $DBPATH $COUNTRY ches2019 $YEAR $OUTPUT_FOLDER
        gn $DBPATH $COUNTRY ches2023 $YEAR $OUTPUT_FOLDER
    fi

    if [[ $COUNTRY = "finland" ]]
    then
        gn $DBPATH $COUNTRY gps2019 $YEAR $OUTPUT_FOLDER
        gn $DBPATH $COUNTRY ches2019 $YEAR $OUTPUT_FOLDER
        gn $DBPATH $COUNTRY ches2023 $YEAR $OUTPUT_FOLDER
    fi

    if [[ $COUNTRY = "france" ]]
    then
        gn $DBPATH $COUNTRY gps2019 $YEAR $OUTPUT_FOLDER
        gn $DBPATH $COUNTRY ches2019 $YEAR $OUTPUT_FOLDER
        gn $DBPATH $COUNTRY ches2023 $YEAR $OUTPUT_FOLDER
    fi

    if [[ $COUNTRY = "germany" ]]
    then
        gn $DBPATH $COUNTRY gps2019 $YEAR $OUTPUT_FOLDER
        gn $DBPATH $COUNTRY ches2019 $YEAR $OUTPUT_FOLDER
        gn $DBPATH $COUNTRY ches2023 $YEAR $OUTPUT_FOLDER
    fi

    if [[ $COUNTRY = "greece" ]]
    then
        gn $DBPATH $COUNTRY gps2019 $YEAR $OUTPUT_FOLDER
        gn $DBPATH $COUNTRY ches2019 $YEAR $OUTPUT_FOLDER
        gn $DBPATH $COUNTRY ches2023 $YEAR $OUTPUT_FOLDER
    fi

    if [[ $COUNTRY = "hungary" ]]
    then
        gn $DBPATH $COUNTRY gps2019 $YEAR $OUTPUT_FOLDER
        gn $DBPATH $COUNTRY ches2019 $YEAR $OUTPUT_FOLDER
        gn $DBPATH $COUNTRY ches2023 $YEAR $OUTPUT_FOLDER
    fi

    if [[ $COUNTRY = "iceland" ]]
    then
        gn $DBPATH $COUNTRY gps2019 $YEAR $OUTPUT_FOLDER
        gn $DBPATH $COUNTRY ches2019 $YEAR $OUTPUT_FOLDER
        gn $DBPATH $COUNTRY ches2023 $YEAR $OUTPUT_FOLDER
    fi

    if [[ $COUNTRY = "india" ]]
    then
        gn $DBPATH $COUNTRY gps2019 $YEAR $OUTPUT_FOLDER
    fi

    if [[ $COUNTRY = "ireland" ]]
    then
        gn $DBPATH $COUNTRY gps2019 $YEAR $OUTPUT_FOLDER
        gn $DBPATH $COUNTRY ches2019 $YEAR $OUTPUT_FOLDER
        gn $DBPATH $COUNTRY ches2023 $YEAR $OUTPUT_FOLDER
    fi

    if [[ $COUNTRY = "israel" ]]
    then
        python /home/jimena/work/dev/gap-populations/pipeline.py \
            --country=israel \
            --year=$YEAR \
            --dbpath=$DBPATH \
            --output=$OUTPUT_FOLDER \
            --config=/home/jimena/work/dev/gap-populations/configs/embeddings_israel.yaml \
            --survey=gps2019 \
            --attdims=V4_Scale,V6_Scale,V8_Scale,V9,V10,V12,V13,V14,V18,V19,V20,V21 \
            --validation
    fi

    if [[ $COUNTRY = "italy" ]]
    then
        gn $DBPATH $COUNTRY gps2019 $YEAR $OUTPUT_FOLDER
        gn $DBPATH $COUNTRY ches2019 $YEAR $OUTPUT_FOLDER
        gn $DBPATH $COUNTRY ches2023 $YEAR $OUTPUT_FOLDER
    fi

    if [[ $COUNTRY = "japan" ]]
    then
        gn $DBPATH $COUNTRY gps2019 $YEAR $OUTPUT_FOLDER
    fi

    if [[ $COUNTRY = "latvia" ]]
    then
        gn $DBPATH $COUNTRY gps2019 $YEAR $OUTPUT_FOLDER
        gn $DBPATH $COUNTRY ches2019 $YEAR $OUTPUT_FOLDER
        gn $DBPATH $COUNTRY ches2023 $YEAR $OUTPUT_FOLDER
    fi

    if [[ $COUNTRY = "lithuania" ]]
    then
        gn $DBPATH $COUNTRY gps2019 $YEAR $OUTPUT_FOLDER
        gn $DBPATH $COUNTRY ches2019 $YEAR $OUTPUT_FOLDER
        gn $DBPATH $COUNTRY ches2023 $YEAR $OUTPUT_FOLDER
    fi

    if [[ "$COUNTRY" = "luxembourg" ]]
    then
        gn $DBPATH $COUNTRY gps2019 $YEAR $OUTPUT_FOLDER
        gn $DBPATH $COUNTRY ches2019 $YEAR $OUTPUT_FOLDER
    fi

    if [[ $COUNTRY = "malta" ]]
    then
        gn $DBPATH $COUNTRY gps2019 $YEAR $OUTPUT_FOLDER
        gn $DBPATH $COUNTRY ches2019 $YEAR $OUTPUT_FOLDER
        gn $DBPATH $COUNTRY ches2023 $YEAR $OUTPUT_FOLDER
    fi

    if [[ $COUNTRY = "mexico" ]]
    then
        gn $DBPATH $COUNTRY gps2019 $YEAR $OUTPUT_FOLDER
    fi

    if [[ $COUNTRY = "netherlands" ]]
    then
        gn $DBPATH $COUNTRY gps2019 $YEAR $OUTPUT_FOLDER
        gn $DBPATH $COUNTRY ches2019 $YEAR $OUTPUT_FOLDER
        gn $DBPATH $COUNTRY ches2023 $YEAR $OUTPUT_FOLDER
    fi

    if [[ $COUNTRY = "newzealand" ]]
    then
        gn $DBPATH $COUNTRY gps2019 $YEAR $OUTPUT_FOLDER
    fi

    if [[ $COUNTRY = "nigeria" ]]
    then
        gn $DBPATH $COUNTRY gps2019 $YEAR $OUTPUT_FOLDER
    fi

    if [[ $COUNTRY = "norway" ]]
    then
        gn $DBPATH $COUNTRY gps2019 $YEAR $OUTPUT_FOLDER
        gn $DBPATH $COUNTRY ches2019 $YEAR $OUTPUT_FOLDER
        gn $DBPATH $COUNTRY ches2023 $YEAR $OUTPUT_FOLDER
    fi

    if [[ $COUNTRY = "peru" ]]
    then
        gn $DBPATH $COUNTRY gps2019 $YEAR $OUTPUT_FOLDER
    fi

    if [[ $COUNTRY = "poland" ]]
    then
        gn $DBPATH $COUNTRY gps2019 $YEAR $OUTPUT_FOLDER
        gn $DBPATH $COUNTRY ches2019 $YEAR $OUTPUT_FOLDER
        gn $DBPATH $COUNTRY ches2023 $YEAR $OUTPUT_FOLDER
    fi

    if [[ $COUNTRY = "portugal" ]]
    then
        gn $DBPATH $COUNTRY gps2019 $YEAR $OUTPUT_FOLDER
        gn $DBPATH $COUNTRY ches2019 $YEAR $OUTPUT_FOLDER
        gn $DBPATH $COUNTRY ches2023 $YEAR $OUTPUT_FOLDER
    fi

    if [[ $COUNTRY = "romania2020.db" || $COUNTRY = "romania" ]]
    then
        gn $DBPATH $COUNTRY gps2019 $YEAR $OUTPUT_FOLDER
        gn $DBPATH $COUNTRY ches2019 $YEAR $OUTPUT_FOLDER
        gn $DBPATH $COUNTRY ches2023 $YEAR $OUTPUT_FOLDER
    fi

    if [[ $COUNTRY = "serbia" ]]
    then
        gn $DBPATH $COUNTRY gps2019 $YEAR $OUTPUT_FOLDER
    fi

    if [[ $COUNTRY = "slovakia" ]]
    then
        gn $DBPATH $COUNTRY gps2019 $YEAR $OUTPUT_FOLDER
        gn $DBPATH $COUNTRY ches2019 $YEAR $OUTPUT_FOLDER
        gn $DBPATH $COUNTRY ches2023 $YEAR $OUTPUT_FOLDER
    fi

    if [[ $COUNTRY = "slovenia" ]]
    then
        gn $DBPATH $COUNTRY gps2019 $YEAR $OUTPUT_FOLDER
        gn $DBPATH $COUNTRY ches2019 $YEAR $OUTPUT_FOLDER
        gn $DBPATH $COUNTRY ches2023 $YEAR $OUTPUT_FOLDER
    fi

    if [[ $COUNTRY = "southafrica" ]]
    then
        gn $DBPATH $COUNTRY gps2019 $YEAR $OUTPUT_FOLDER
    fi

    if [[ $COUNTRY = "spain" ]]
    then
        gn $DBPATH $COUNTRY gps2019 $YEAR $OUTPUT_FOLDER
        gn $DBPATH $COUNTRY ches2019 $YEAR $OUTPUT_FOLDER
        gn $DBPATH $COUNTRY ches2023 $YEAR $OUTPUT_FOLDER
    fi

    if [[ $COUNTRY = "sweden" ]]
    then
        gn $DBPATH $COUNTRY gps2019 $YEAR $OUTPUT_FOLDER
        gn $DBPATH $COUNTRY ches2019 $YEAR $OUTPUT_FOLDER
        gn $DBPATH $COUNTRY ches2023 $YEAR $OUTPUT_FOLDER
    fi

    if [[ $COUNTRY = "switzerland" ]]
    then
        gn $DBPATH $COUNTRY gps2019 $YEAR $OUTPUT_FOLDER
        gn $DBPATH $COUNTRY ches2019 $YEAR $OUTPUT_FOLDER
        gn $DBPATH $COUNTRY ches2023 $YEAR $OUTPUT_FOLDER
    fi

    if [[ $COUNTRY = "taiwan" ]]
    then
        gn $DBPATH $COUNTRY gps2019 $YEAR $OUTPUT_FOLDER
    fi

    if [[ $COUNTRY = "turkey" ]]
    then
        gn $DBPATH $COUNTRY gps2019 $YEAR $OUTPUT_FOLDER
        gn $DBPATH $COUNTRY ches2019 $YEAR $OUTPUT_FOLDER
        gn $DBPATH $COUNTRY ches2023 $YEAR $OUTPUT_FOLDER
    fi

    if [[ $COUNTRY = "uk" ]]
    then
        gn $DBPATH $COUNTRY gps2019 $YEAR $OUTPUT_FOLDER
        gn $DBPATH $COUNTRY ches2019 $YEAR $OUTPUT_FOLDER
        gn $DBPATH $COUNTRY ches2023 $YEAR $OUTPUT_FOLDER
    fi

    if [[ $COUNTRY = "ukraine" ]]
    then
        gn $DBPATH $COUNTRY gps2019 $YEAR $OUTPUT_FOLDER
    fi

    if [[ $COUNTRY = "uruguay" ]]
    then
        gn $DBPATH $COUNTRY gps2019 $YEAR $OUTPUT_FOLDER
    fi

    if [[ $COUNTRY = "us" ]]
    then
        gn $DBPATH $COUNTRY gps2019 $YEAR $OUTPUT_FOLDER
    fi

    if [[ $COUNTRY = "venezuela" ]]
    then
        gn $DBPATH $COUNTRY gps2019 $YEAR $OUTPUT_FOLDER
    fi
}

fn $1 $2 $3 $4
