#!/bin/bash

function gn() {
    if [[ "$2" = "ches2019" ]]
    then
        python pipeline.py \
            --country=$1 \
            --output=output \
            --survey=ches2019 \
            --attdims=lrgen,lrecon,eu_position,people_vs_elite,antielite_salience,corrupt_salience,sociallifestyle,galtan,immigrate_policy,environment,enviro_salience,nationalism
    fi

    if [[ "$2" = "gps2019" ]]
    then
        python pipeline.py \
            --country=$1 \
            --output=output \
            --survey=gps2019 \
            --attdims=V4_Scale,V6_Scale,V8_Scale,V9,V10,V12,V13,V14,V18,V19,V20,V21
    fi

    if [[ "$2" = "ches2023" ]]
    then
        python pipeline.py \
            --country=$1 \
            --output=output \
            --survey=ches2023 \
            --attdims=antielite_salience,galtan,eu_position,lrecon,refugees
    fi
}

function fn() {
    if [[ "$1" = "argentina" ]]
    then
        gn argentina gps2019
    fi

    if [[ "$1" = "australia" ]]
    then
        gn australia gps2019
    fi

    if [[ "$1" = "austria" ]]
    then
        gn austria gps2019
        gn austria ches2019
        gn austria ches2023
    fi

    if [[ "$1" = "belgium" ]]
    then
        gn belgium gps2019
        gn belgium ches2019
        gn belgium ches2023
    fi

    if [[ "$1" = "brazil" ]]
    then
        gn brazil gps2019
    fi

    if [[ "$1" = "canada" ]]
    then
        gn canada gps2019
    fi

    if [[ "$1" = "chile" ]]
    then
        gn chile gps2019
    fi

    if [[ "$1" = "colombia" ]]
    then
        gn colombia gps2019
    fi

    if [[ "$1" = "croatia" ]]
    then
        gn croatia gps2019
        gn croatia ches2019
        gn croatia ches2023
    fi

    if [[ "$1" = "cyprus" ]]
    then
        gn cyprus gps2019
        gn cyprus ches2019
    fi

    if [[ "$1" = "czechia" ]]
    then
        gn czechia gps2019
        gn czechia ches2019
        gn czechia ches2023
    fi

    if [[ "$1" = "denmark" ]]
    then
        gn denmark gps2019
        gn denmark ches2019
        gn denmark ches2023
    fi

    if [[ "$1" = "ecuador" ]]
    then
        gn ecuador gps2019
    fi

    if [[ "$1" = "estonia" ]]
    then
        gn estonia gps2019
        gn estonia ches2019
        gn estonia ches2023
    fi

    if [[ "$1" = "finland" ]]
    then
        gn finland gps2019
        gn finland ches2019
        gn finland ches2023
    fi

    if [[ "$1" = "france" ]]
    then
        gn france gps2019
        gn france ches2019
        gn france ches2023
    fi

    if [[ "$1" = "germany" ]]
    then
        gn germany gps2019
        gn germany ches2019
        gn germany ches2023
    fi

    if [[ "$1" = "greece" ]]
    then
        gn greece gps2019
        gn greece ches2019
        gn greece ches2023
    fi

    if [[ "$1" = "hungary" ]]
    then
        gn hungary gps2019
        gn hungary ches2019
        gn hungary ches2023
    fi

    if [[ "$1" = "iceland" ]]
    then
        gn iceland gps2019
        gn iceland ches2019
        gn iceland ches2023
    fi

    if [[ "$1" = "india" ]]
    then
        gn india gps2019
    fi

    if [[ "$1" = "ireland" ]]
    then
        gn ireland gps2019
        gn ireland ches2019
        gn ireland ches2023
    fi

    if [[ "$1" = "israel" ]]
    then
        python pipeline.py \
            --country=$1 \
            --output=wip \
            --config=configs/embeddings_israel.yaml \
            --survey=gps2019 \
            --attdims=V4_Scale
    fi

    if [[ "$1" = "italy" ]]
    then
        gn italy gps2019
        gn italy ches2019
        gn italy ches2023
    fi

    if [[ "$1" = "japan" ]]
    then
        gn japan gps2019
    fi

    if [[ "$1" = "latvia" ]]
    then
        gn latvia gps2019
        gn latvia ches2019
        gn latvia ches2023
    fi

    if [[ "$1" = "lithuania" ]]
    then
        gn lithuania gps2019
        gn lithuania ches2019
        gn lithuania ches2023
    fi

    if [[ "$1" = "luxembourg" ]]
    then
        gn luxembourg gps2019
        gn luxembourg ches2019
    fi

    if [[ "$1" = "malta" ]]
    then
        gn malta gps2019
        gn malta ches2019
        gn malta ches2023
    fi

    if [[ "$1" = "mexico" ]]
    then
        gn mexico gps2019
    fi

    if [[ "$1" = "netherlands" ]]
    then
        gn netherlands gps2019
        gn netherlands ches2019
        gn netherlands ches2023
    fi

    if [[ "$1" = "newzealand" ]]
    then
        gn newzealand gps2019
    fi

    if [[ "$1" = "nigeria" ]]
    then
        gn nigeria gps2019
    fi

    if [[ "$1" = "norway" ]]
    then
        gn norway gps2019
        gn norway ches2019
        gn norway ches2023
    fi

    if [[ "$1" = "peru" ]]
    then
        gn peru gps2019
    fi

    if [[ "$1" = "poland" ]]
    then
        gn poland gps2019
        gn poland ches2019
        gn poland ches2023
    fi

    if [[ "$1" = "portugal" ]]
    then
        gn portugal gps2019
        gn portugal ches2019
        gn portugal ches2023
    fi

    if [[ "$1" = "romania" ]]
    then
        gn romania gps2019
        gn romania ches2019
        gn romania ches2023
    fi

    if [[ "$1" = "serbia" ]]
    then
        gn serbia gps2019
    fi

    if [[ "$1" = "slovakia" ]]
    then
        gn slovakia gps2019
        gn slovakia ches2019
        gn slovakia ches2023
    fi

    if [[ "$1" = "slovenia" ]]
    then
        gn slovenia gps2019
        gn slovenia ches2019
        gn slovenia ches2023
    fi

    if [[ "$1" = "southafrica" ]]
    then
        gn southafrica gps2019
    fi

    if [[ "$1" = "spain" ]]
    then
        gn spain gps2019
        gn spain ches2019
        gn spain ches2023
    fi

    if [[ "$1" = "sweden" ]]
    then
        gn sweden gps2019
        gn sweden ches2019
        gn sweden ches2023
    fi

    if [[ "$1" = "switzerland" ]]
    then
        gn switzerland gps2019
        gn switzerland ches2019
        gn switzerland ches2023
    fi

    if [[ "$1" = "taiwan" ]]
    then
        gn taiwan gps2019
    fi

    if [[ "$1" = "turkey" ]]
    then
        gn turkey gps2019
        gn turkey ches2019
        gn turkey ches2023
    fi

    if [[ "$1" = "uk" ]]
    then
        gn uk gps2019
        gn uk ches2019
        gn uk ches2023
    fi

    if [[ "$1" = "ukraine" ]]
    then
        gn ukraine gps2019
    fi

    if [[ "$1" = "uruguay" ]]
    then
        gn uruguay gps2019
    fi

    if [[ "$1" = "us" ]]
    then
        gn us gps2019
    fi

    if [[ "$1" = "venezuela" ]]
    then
        gn venezuela gps2019
    fi
}

fn $1
