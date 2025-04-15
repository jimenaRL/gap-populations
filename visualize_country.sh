#!/bin/bash

function gn() {

    DBPATH=$1
    COUNTRY=$2
    SURVEY=$3
    YEAR=$4
    OUTPUT_FOLDER=$5
    ATT_STRATEGY=$6
    IDEOLOGICAL=$7
    LABELS=$8

    echo "--------------------------------------------------"
    echo "[COUNTRY] ${COUNTRY}"
    echo "[YEAR] ${YEAR}"
    echo "[DBPATH] ${DBPATH}"
    echo "[OUTPUT] ${OUTPUT_FOLDER}"
    echo "[SURVEY] ${SURVEY}"
    echo "[ATT_STRATEGY] ${ATT_STRATEGY}"
    if [ ! -z "$IDEOLOGICAL" ]
        then
            echo "[IDEOLOGICAL] ${IDEOLOGICAL}"
    fi
    if [ ! -z "$LABELS" ]
        then
            echo "[LABELS] ${LABELS}"
    fi
    echo "--------------------------------------------------"

    command="python /home/jimena/work/dev/gap-populations/pipeline.py"
    command="${command} --dbpath=$DBPATH --country=$COUNTRY --year=$YEAR"
    command="${command} --output=$OUTPUT_FOLDER --plot"
    command="${command} --att_missing_values_strategy=$ATT_STRATEGY"
    # command="${command} --show"

    if [[ "$IDEOLOGICAL" = "ideological" ]]; then
        command="${command} --ideological --bivariate --distributions --ndimsviz=2"
    else
        command="${command} --validation"
        if [[ "$SURVEY" = "ches2019" ]]
        then
            command="${command} --attitudinal --bivariate --distributions --survey=ches2019 --attdims=lrgen,lrecon,eu_position,people_vs_elite,antielite_salience,corrupt_salience,sociallifestyle,galtan,immigrate_policy,environment,enviro_salience,nationalism"
        fi

        if [[ "$SURVEY" = "gps2019" ]]
        then
            command="${command} --attitudinal --bivariate --distributions --survey=gps2019 --attdims=V4_Scale,V6_Scale,V8_Scale,V9,V10,V12,V13,V14,V18,V19,V20,V21"
        fi

        if [[ "$SURVEY" = "ches2023" ]]
        then
            command="${command} --attitudinal --bivariate --distributions --survey=ches2023 --attdims=antielite_salience,galtan,eu_position,lrecon,refugees"
        fi
        if [[ "$SURVEY" = "ches2020" ]]
        then
            command="${command} --attitudinal --bivariate --distributions --survey=ches2020 --attdims=lrgen,lrecon,people_vs_elite,antielite_salience,corrupt_salience,sociallifestyle,galtan,immigrate_policy,environment,enviro_salience"
        fi
        if [[ "$LABELS" = "labels" ]]; then
            command="${command} --labels"
        fi
    fi

    echo "--------------------------------------------------"
    echo "[RUNNING] ${command}"
    echo "--------------------------------------------------"
    # eval "$command"
    echo "$command"

}



function fn() {

    COUNTRY=$1
    YEAR=$2
    DBPATH=$3
    OUTPUT_FOLDER=$4

    if [[ $COUNTRY = "argentina" ]]
    then
        gn $DBPATH $COUNTRY "" $YEAR $OUTPUT_FOLDER drop_parties ideological ""
        gn $DBPATH $COUNTRY gps2019 $YEAR $OUTPUT_FOLDER drop_parties "" labels
        gn $DBPATH $COUNTRY ches2020 $YEAR $OUTPUT_FOLDER drop_parties "" labels
    fi

    if [[ $COUNTRY = "australia" ]]
    then
        gn $DBPATH $COUNTRY "" $YEAR $OUTPUT_FOLDER drop_parties ideological ""
        gn $DBPATH $COUNTRY gps2019 $YEAR $OUTPUT_FOLDER drop_parties "" labels
    fi

    if [[ $COUNTRY = "austria" || $COUNTRY = "austriabis" ]]
    then
        gn $DBPATH $COUNTRY "" $YEAR $OUTPUT_FOLDER drop_parties ideological ""
        gn $DBPATH $COUNTRY gps2019 $YEAR $OUTPUT_FOLDER drop_parties "" labels
        gn $DBPATH $COUNTRY ches2019 $YEAR $OUTPUT_FOLDER drop_parties "" labels
        gn $DBPATH $COUNTRY ches2023 $YEAR $OUTPUT_FOLDER drop_parties "" labels
    fi

    if [[ $COUNTRY = "belgium" ]]
    then
        gn $DBPATH $COUNTRY "" $YEAR $OUTPUT_FOLDER drop_parties ideological ""
        gn $DBPATH $COUNTRY gps2019 $YEAR $OUTPUT_FOLDER drop_parties "" labels
        gn $DBPATH $COUNTRY ches2019 $YEAR $OUTPUT_FOLDER drop_parties "" labels
        gn $DBPATH $COUNTRY ches2023 $YEAR $OUTPUT_FOLDER drop_parties "" labels
    fi

    if [[ $COUNTRY = "brazil" ]]
    then
        gn $DBPATH $COUNTRY "" $YEAR $OUTPUT_FOLDER drop_parties ideological ""
        gn $DBPATH $COUNTRY gps2019 $YEAR $OUTPUT_FOLDER drop_parties "" labels
        gn $DBPATH $COUNTRY ches2020 $YEAR $OUTPUT_FOLDER drop_parties "" labels
    fi

    if [[ $COUNTRY = "canada" ]]
    then
        gn $DBPATH $COUNTRY "" $YEAR $OUTPUT_FOLDER drop_parties ideological ""
        gn $DBPATH $COUNTRY gps2019 $YEAR $OUTPUT_FOLDER drop_parties "" labels
    fi

    if [[ $COUNTRY = "chile" ]]
    then
        gn $DBPATH $COUNTRY "" $YEAR $OUTPUT_FOLDER drop_parties ideological ""
        gn $DBPATH $COUNTRY gps2019 $YEAR $OUTPUT_FOLDER drop_parties "" labels
        gn $DBPATH $COUNTRY ches2020 $YEAR $OUTPUT_FOLDER drop_parties "" labels
    fi

    if [[ $COUNTRY = "colombia" ]]
    then
        gn $DBPATH $COUNTRY "" $YEAR $OUTPUT_FOLDER drop_parties ideological ""
        gn $DBPATH $COUNTRY gps2019 $YEAR $OUTPUT_FOLDER drop_parties "" labels
        gn $DBPATH $COUNTRY ches2020 $YEAR $OUTPUT_FOLDER drop_parties "" labels
    fi

    if [[ $COUNTRY = "croatia" ]]
    then
        gn $DBPATH $COUNTRY "" $YEAR $OUTPUT_FOLDER drop_parties ideological ""
        gn $DBPATH $COUNTRY gps2019 $YEAR $OUTPUT_FOLDER drop_parties "" labels
        gn $DBPATH $COUNTRY ches2019 $YEAR $OUTPUT_FOLDER drop_parties "" labels
        gn $DBPATH $COUNTRY ches2023 $YEAR $OUTPUT_FOLDER drop_parties "" labels
    fi

    if [[ $COUNTRY = "cyprus" ]]
    then
        gn $DBPATH $COUNTRY "" $YEAR $OUTPUT_FOLDER drop_parties ideological ""
        gn $DBPATH $COUNTRY gps2019 $YEAR $OUTPUT_FOLDER drop_parties "" labels
        gn $DBPATH $COUNTRY ches2019 $YEAR $OUTPUT_FOLDER drop_parties "" labels
    fi

    if [[ $COUNTRY = "czechia" ]]
    then
        gn $DBPATH $COUNTRY "" $YEAR $OUTPUT_FOLDER drop_parties ideological ""
        gn $DBPATH $COUNTRY gps2019 $YEAR $OUTPUT_FOLDER drop_parties "" labels
        gn $DBPATH $COUNTRY ches2019 $YEAR $OUTPUT_FOLDER drop_parties "" labels
        gn $DBPATH $COUNTRY ches2023 $YEAR $OUTPUT_FOLDER drop_parties "" labels
    fi

    if [[ $COUNTRY = "denmark" ]]
    then
        gn $DBPATH $COUNTRY "" $YEAR $OUTPUT_FOLDER drop_parties ideological ""
        gn $DBPATH $COUNTRY gps2019 $YEAR $OUTPUT_FOLDER drop_parties "" labels
        gn $DBPATH $COUNTRY ches2019 $YEAR $OUTPUT_FOLDER drop_parties "" labels
        gn $DBPATH $COUNTRY ches2023 $YEAR $OUTPUT_FOLDER drop_parties "" labels
    fi

    if [[ $COUNTRY = "ecuador" ]]
    then
        gn $DBPATH $COUNTRY "" $YEAR $OUTPUT_FOLDER drop_parties ideological ""
        gn $DBPATH $COUNTRY gps2019 $YEAR $OUTPUT_FOLDER drop_parties "" labels
        gn $DBPATH $COUNTRY ches2020 $YEAR $OUTPUT_FOLDER drop_parties "" labels
    fi

    if [[ $COUNTRY = "estonia" ]]
    then
        gn $DBPATH $COUNTRY "" $YEAR $OUTPUT_FOLDER drop_parties ideological ""
        gn $DBPATH $COUNTRY gps2019 $YEAR $OUTPUT_FOLDER drop_parties "" labels
        gn $DBPATH $COUNTRY ches2019 $YEAR $OUTPUT_FOLDER drop_parties "" labels
        gn $DBPATH $COUNTRY ches2023 $YEAR $OUTPUT_FOLDER drop_parties "" labels
    fi

    if [[ $COUNTRY = "finland" ]]
    then
        gn $DBPATH $COUNTRY "" $YEAR $OUTPUT_FOLDER drop_parties ideological ""
        gn $DBPATH $COUNTRY gps2019 $YEAR $OUTPUT_FOLDER drop_parties "" labels
        gn $DBPATH $COUNTRY ches2019 $YEAR $OUTPUT_FOLDER drop_parties "" labels
        gn $DBPATH $COUNTRY ches2023 $YEAR $OUTPUT_FOLDER drop_parties "" labels
    fi

    if [[ $COUNTRY = "france" || $COUNTRY = "francebis" ]]
    then
        gn $DBPATH $COUNTRY "" $YEAR $OUTPUT_FOLDER drop_parties ideological ""
        gn $DBPATH $COUNTRY gps2019 $YEAR $OUTPUT_FOLDER drop_parties "" labels
        gn $DBPATH $COUNTRY ches2019 $YEAR $OUTPUT_FOLDER drop_parties "" labels
        gn $DBPATH $COUNTRY ches2023 $YEAR $OUTPUT_FOLDER drop_parties "" labels
    fi

    if [[ $COUNTRY = "germany" || $COUNTRY = "germanybis" ]]
    then
        gn $DBPATH $COUNTRY "" $YEAR $OUTPUT_FOLDER drop_parties ideological ""
        gn $DBPATH $COUNTRY gps2019 $YEAR $OUTPUT_FOLDER drop_parties "" labels
        gn $DBPATH $COUNTRY ches2019 $YEAR $OUTPUT_FOLDER drop_parties "" labels
        gn $DBPATH $COUNTRY ches2023 $YEAR $OUTPUT_FOLDER drop_parties "" labels
    fi

    if [[ $COUNTRY = "greece" ]]
    then
        gn $DBPATH $COUNTRY "" $YEAR $OUTPUT_FOLDER drop_parties ideological ""
        gn $DBPATH $COUNTRY gps2019 $YEAR $OUTPUT_FOLDER drop_parties "" labels
        gn $DBPATH $COUNTRY ches2019 $YEAR $OUTPUT_FOLDER drop_parties "" labels
        gn $DBPATH $COUNTRY ches2023 $YEAR $OUTPUT_FOLDER drop_parties "" labels
    fi

    if [[ $COUNTRY = "hungary" ]]
    then
        gn $DBPATH $COUNTRY "" $YEAR $OUTPUT_FOLDER drop_parties ideological ""
        gn $DBPATH $COUNTRY gps2019 $YEAR $OUTPUT_FOLDER drop_parties "" labels
        gn $DBPATH $COUNTRY ches2019 $YEAR $OUTPUT_FOLDER drop_parties "" labels
        gn $DBPATH $COUNTRY ches2023 $YEAR $OUTPUT_FOLDER drop_parties "" labels
    fi

    if [[ $COUNTRY = "iceland" ]]
    then
        gn $DBPATH $COUNTRY "" $YEAR $OUTPUT_FOLDER drop_parties ideological ""
        gn $DBPATH $COUNTRY gps2019 $YEAR $OUTPUT_FOLDER drop_parties "" labels
        gn $DBPATH $COUNTRY ches2019 $YEAR $OUTPUT_FOLDER drop_parties "" labels
        gn $DBPATH $COUNTRY ches2023 $YEAR $OUTPUT_FOLDER drop_parties "" labels
    fi

    if [[ $COUNTRY = "india" ]]
    then
        gn $DBPATH $COUNTRY "" $YEAR $OUTPUT_FOLDER drop_parties ideological ""
        gn $DBPATH $COUNTRY gps2019 $YEAR $OUTPUT_FOLDER drop_parties "" labels
    fi

    if [[ $COUNTRY = "ireland" ]]
    then
        gn $DBPATH $COUNTRY "" $YEAR $OUTPUT_FOLDER drop_parties ideological ""
        gn $DBPATH $COUNTRY gps2019 $YEAR $OUTPUT_FOLDER drop_parties "" labels
        gn $DBPATH $COUNTRY ches2019 $YEAR $OUTPUT_FOLDER drop_parties "" labels
        gn $DBPATH $COUNTRY ches2023 $YEAR $OUTPUT_FOLDER drop_parties "" labels
    fi

    if [[ $COUNTRY = "israel" ]]
    then
        python /home/jimena/work/dev/gap-populations/pipeline.py \
            --country=$COUNTRY \
            --year=$YEAR \
            --dbpath=$DBPATH \
            --output=$OUTPUT_FOLDER \
            --config=/home/jimena/work/dev/gap-populations/configs/embeddings_pseudonymized_alldata_$COUNTRY.yaml \
            --survey=gps2019 \
            --attdims=V4_Scale,V6_Scale,V8_Scale,V9,V10,V12,V13,V14,V18,V19,V20,V21 \
            --validation
    fi

    if [[ $COUNTRY = "italy" || $COUNTRY = "italybis" ]]
    then
        gn $DBPATH $COUNTRY "" $YEAR $OUTPUT_FOLDER drop_parties ideological ""
        gn $DBPATH $COUNTRY gps2019 $YEAR $OUTPUT_FOLDER drop_parties "" labels
        gn $DBPATH $COUNTRY ches2019 $YEAR $OUTPUT_FOLDER drop_parties "" labels
        gn $DBPATH $COUNTRY ches2023 $YEAR $OUTPUT_FOLDER drop_parties "" labels
    fi

    if [[ $COUNTRY = "japan" ]]
    then
        python /home/jimena/work/dev/gap-populations/pipeline.py \
            --country=$COUNTRY \
            --year=$YEAR \
            --dbpath=$DBPATH \
            --output=$OUTPUT_FOLDER \
            --config=/home/jimena/work/dev/gap-populations/configs/embeddings_pseudonymized_alldata_$COUNTRY.yaml \
            --survey=gps2019 \
            --attdims=V4_Scale,V6_Scale,V8_Scale,V9,V10,V12,V13,V14,V18,V19,V20,V21 \
            --validation
    fi

    if [[ $COUNTRY = "latvia" ]]
    then
        gn $DBPATH $COUNTRY "" $YEAR $OUTPUT_FOLDER drop_parties ideological ""
        gn $DBPATH $COUNTRY gps2019 $YEAR $OUTPUT_FOLDER drop_parties "" labels
        gn $DBPATH $COUNTRY ches2019 $YEAR $OUTPUT_FOLDER drop_parties "" labels
        gn $DBPATH $COUNTRY ches2023 $YEAR $OUTPUT_FOLDER drop_parties "" labels
    fi

    if [[ $COUNTRY = "lithuania" ]]
    then
        gn $DBPATH $COUNTRY "" $YEAR $OUTPUT_FOLDER drop_parties ideological ""
        gn $DBPATH $COUNTRY gps2019 $YEAR $OUTPUT_FOLDER drop_parties "" labels
        gn $DBPATH $COUNTRY ches2019 $YEAR $OUTPUT_FOLDER drop_parties "" labels
        gn $DBPATH $COUNTRY ches2023 $YEAR $OUTPUT_FOLDER drop_parties "" labels
    fi

    if [[ "$COUNTRY" = "luxembourg" ]]
    then
        gn $DBPATH $COUNTRY "" $YEAR $OUTPUT_FOLDER drop_parties ideological ""
        gn $DBPATH $COUNTRY gps2019 $YEAR $OUTPUT_FOLDER drop_parties "" labels
        gn $DBPATH $COUNTRY ches2019 $YEAR $OUTPUT_FOLDER drop_parties "" labels
    fi

    if [[ $COUNTRY = "malta" ]]
    then
        gn $DBPATH $COUNTRY "" $YEAR $OUTPUT_FOLDER drop_parties ideological ""
        gn $DBPATH $COUNTRY gps2019 $YEAR $OUTPUT_FOLDER drop_parties "" labels
        gn $DBPATH $COUNTRY ches2019 $YEAR $OUTPUT_FOLDER drop_parties "" labels
        gn $DBPATH $COUNTRY ches2023 $YEAR $OUTPUT_FOLDER drop_parties "" labels
    fi

    if [[ $COUNTRY = "mexico" ]]
    then
        gn $DBPATH $COUNTRY "" $YEAR $OUTPUT_FOLDER drop_parties ideological ""
        gn $DBPATH $COUNTRY gps2019 $YEAR $OUTPUT_FOLDER drop_parties "" labels
        gn $DBPATH $COUNTRY ches2020 $YEAR $OUTPUT_FOLDER drop_parties "" labels
    fi

    if [[ $COUNTRY = "netherlands" ]]
    then
        gn $DBPATH $COUNTRY "" $YEAR $OUTPUT_FOLDER drop_parties ideological ""
        gn $DBPATH $COUNTRY gps2019 $YEAR $OUTPUT_FOLDER drop_parties "" labels
        gn $DBPATH $COUNTRY ches2019 $YEAR $OUTPUT_FOLDER drop_parties "" labels
        gn $DBPATH $COUNTRY ches2023 $YEAR $OUTPUT_FOLDER drop_parties "" labels
    fi

    if [[ $COUNTRY = "newzealand" ]]
    then
        gn $DBPATH $COUNTRY "" $YEAR $OUTPUT_FOLDER drop_parties ideological ""
        gn $DBPATH $COUNTRY gps2019 $YEAR $OUTPUT_FOLDER drop_parties "" labels
    fi

    if [[ $COUNTRY = "nigeria" ]]
    then
        gn $DBPATH $COUNTRY "" $YEAR $OUTPUT_FOLDER drop_parties ideological ""
        gn $DBPATH $COUNTRY gps2019 $YEAR $OUTPUT_FOLDER drop_parties "" labels
    fi

    if [[ $COUNTRY = "norway" ]]
    then
        gn $DBPATH $COUNTRY "" $YEAR $OUTPUT_FOLDER drop_parties ideological ""
        gn $DBPATH $COUNTRY gps2019 $YEAR $OUTPUT_FOLDER drop_parties "" labels
        gn $DBPATH $COUNTRY ches2019 $YEAR $OUTPUT_FOLDER drop_parties "" labels
        gn $DBPATH $COUNTRY ches2023 $YEAR $OUTPUT_FOLDER drop_parties "" labels
    fi

    if [[ $COUNTRY = "peru" ]]
    then
        gn $DBPATH $COUNTRY "" $YEAR $OUTPUT_FOLDER drop_parties ideological ""
        gn $DBPATH $COUNTRY gps2019 $YEAR $OUTPUT_FOLDER drop_parties "" labels
        gn $DBPATH $COUNTRY ches2020 $YEAR $OUTPUT_FOLDER drop_parties "" labels
    fi

    if [[ $COUNTRY = "poland" ]]
    then
        gn $DBPATH $COUNTRY "" $YEAR $OUTPUT_FOLDER drop_parties ideological ""
        gn $DBPATH $COUNTRY gps2019 $YEAR $OUTPUT_FOLDER drop_parties "" labels
        gn $DBPATH $COUNTRY ches2019 $YEAR $OUTPUT_FOLDER drop_parties "" labels
        gn $DBPATH $COUNTRY ches2023 $YEAR $OUTPUT_FOLDER drop_parties "" labels
    fi

    if [[ $COUNTRY = "portugal" ]]
    then
        gn $DBPATH $COUNTRY "" $YEAR $OUTPUT_FOLDER drop_parties ideological ""
        gn $DBPATH $COUNTRY gps2019 $YEAR $OUTPUT_FOLDER drop_parties "" labels
        gn $DBPATH $COUNTRY ches2019 $YEAR $OUTPUT_FOLDER drop_parties "" labels
        gn $DBPATH $COUNTRY ches2023 $YEAR $OUTPUT_FOLDER drop_parties "" labels
    fi

    if [[ $COUNTRY = "romania2020.db" || $COUNTRY = "romania" ]]
    then
        gn $DBPATH $COUNTRY "" $YEAR $OUTPUT_FOLDER drop_parties ideological ""
        gn $DBPATH $COUNTRY gps2019 $YEAR $OUTPUT_FOLDER drop_parties "" labels
        gn $DBPATH $COUNTRY ches2019 $YEAR $OUTPUT_FOLDER drop_parties "" labels
        gn $DBPATH $COUNTRY ches2023 $YEAR $OUTPUT_FOLDER drop_parties "" labels
    fi

    if [[ $COUNTRY = "serbia" ]]
    then
        gn $DBPATH $COUNTRY "" $YEAR $OUTPUT_FOLDER drop_parties ideological ""
        gn $DBPATH $COUNTRY gps2019 $YEAR $OUTPUT_FOLDER drop_parties "" labels
    fi

    if [[ $COUNTRY = "slovakia" ]]
    then
        gn $DBPATH $COUNTRY "" $YEAR $OUTPUT_FOLDER drop_parties ideological ""
        gn $DBPATH $COUNTRY gps2019 $YEAR $OUTPUT_FOLDER drop_parties "" labels
        gn $DBPATH $COUNTRY ches2019 $YEAR $OUTPUT_FOLDER drop_parties "" labels
        gn $DBPATH $COUNTRY ches2023 $YEAR $OUTPUT_FOLDER drop_parties "" labels
    fi

    if [[ $COUNTRY = "slovenia" ]]
    then
        gn $DBPATH $COUNTRY "" $YEAR $OUTPUT_FOLDER drop_parties ideological ""
        gn $DBPATH $COUNTRY gps2019 $YEAR $OUTPUT_FOLDER drop_parties "" labels
        gn $DBPATH $COUNTRY ches2019 $YEAR $OUTPUT_FOLDER drop_parties "" labels drop_dims "" labels
        gn $DBPATH $COUNTRY ches2023 $YEAR $OUTPUT_FOLDER drop_parties "" labels drop_dims "" labels
    fi

    if [[ $COUNTRY = "southafrica" ]]
    then
        gn $DBPATH $COUNTRY "" $YEAR $OUTPUT_FOLDER drop_parties ideological ""
        gn $DBPATH $COUNTRY gps2019 $YEAR $OUTPUT_FOLDER drop_parties "" labels
    fi

    if [[ $COUNTRY = "spain" ]]
    then
        gn $DBPATH $COUNTRY "" $YEAR $OUTPUT_FOLDER drop_parties ideological ""
        gn $DBPATH $COUNTRY gps2019 $YEAR $OUTPUT_FOLDER drop_parties "" labels
        gn $DBPATH $COUNTRY ches2019 $YEAR $OUTPUT_FOLDER drop_parties "" labels
        gn $DBPATH $COUNTRY ches2023 $YEAR $OUTPUT_FOLDER drop_parties "" labels
    fi

    if [[ $COUNTRY = "sweden" ]]
    then
        gn $DBPATH $COUNTRY "" $YEAR $OUTPUT_FOLDER drop_parties ideological ""
        gn $DBPATH $COUNTRY gps2019 $YEAR $OUTPUT_FOLDER drop_parties "" labels
        gn $DBPATH $COUNTRY ches2019 $YEAR $OUTPUT_FOLDER drop_parties "" labels
        gn $DBPATH $COUNTRY ches2023 $YEAR $OUTPUT_FOLDER drop_parties "" labels
    fi

    if [[ $COUNTRY = "switzerland" ]]
    then
        gn $DBPATH $COUNTRY "" $YEAR $OUTPUT_FOLDER drop_parties ideological ""
        gn $DBPATH $COUNTRY gps2019 $YEAR $OUTPUT_FOLDER drop_parties "" labels
        gn $DBPATH $COUNTRY ches2019 $YEAR $OUTPUT_FOLDER drop_parties "" labels
        gn $DBPATH $COUNTRY ches2023 $YEAR $OUTPUT_FOLDER drop_parties "" labels
    fi

    if [[ $COUNTRY = "taiwan" ]]
    then
        gn $DBPATH $COUNTRY "" $YEAR $OUTPUT_FOLDER drop_parties ideological ""
        gn $DBPATH $COUNTRY gps2019 $YEAR $OUTPUT_FOLDER drop_parties "" labels
    fi

    if [[ $COUNTRY = "turkey" ]]
    then
        gn $DBPATH $COUNTRY "" $YEAR $OUTPUT_FOLDER drop_parties ideological ""
        gn $DBPATH $COUNTRY gps2019 $YEAR $OUTPUT_FOLDER drop_parties "" labels
        gn $DBPATH $COUNTRY ches2019 $YEAR $OUTPUT_FOLDER drop_parties "" labels
        gn $DBPATH $COUNTRY ches2023 $YEAR $OUTPUT_FOLDER drop_parties "" labels
    fi

    if [[ $COUNTRY = "uk" || $COUNTRY = "ukbis" ]]
    then
        gn $DBPATH $COUNTRY "" $YEAR $OUTPUT_FOLDER drop_parties ideological ""
        gn $DBPATH $COUNTRY gps2019 $YEAR $OUTPUT_FOLDER drop_parties "" labels
        gn $DBPATH $COUNTRY ches2019 $YEAR $OUTPUT_FOLDER drop_parties "" labels
        gn $DBPATH $COUNTRY ches2023 $YEAR $OUTPUT_FOLDER drop_parties "" labels
    fi

    if [[ $COUNTRY = "ukraine" ]]
    then
        gn $DBPATH $COUNTRY "" $YEAR $OUTPUT_FOLDER drop_parties ideological ""
        gn $DBPATH $COUNTRY gps2019 $YEAR $OUTPUT_FOLDER drop_parties "" labels
    fi

    if [[ $COUNTRY = "uruguay" ]]
    then
        gn $DBPATH $COUNTRY "" $YEAR $OUTPUT_FOLDER drop_parties ideological ""
        gn $DBPATH $COUNTRY gps2019 $YEAR $OUTPUT_FOLDER drop_parties "" labels
        gn $DBPATH $COUNTRY ches2020 $YEAR $OUTPUT_FOLDER drop_parties "" labels
    fi

    if [[ $COUNTRY = "us" || $COUNTRY = "usbis" ]]
    then
        gn $DBPATH $COUNTRY "" $YEAR $OUTPUT_FOLDER drop_parties ideological ""
        gn $DBPATH $COUNTRY gps2019 $YEAR $OUTPUT_FOLDER drop_parties "" labels
    fi

    if [[ $COUNTRY = "venezuela" ]]
    then
        gn $DBPATH $COUNTRY gps2019 $YEAR $OUTPUT_FOLDER drop_parties "" labels
        gn $DBPATH $COUNTRY "" $YEAR $OUTPUT_FOLDER drop_parties ideological ""
        gn $DBPATH $COUNTRY ches2020 $YEAR $OUTPUT_FOLDER drop_parties "" labels
    fi
}


COUNTRY=$1
YEAR=$2
DBPATH=$3
OUTPUT_FOLDER=$4

fn $COUNTRY $YEAR $DBPATH $OUTPUT_FOLDER
