#!/bin/bash

function gn() {

    dbpath=$1
    survey=$2
    ideological=$3

    country=$(echo ${dbpath} | cut -d "." -f 1)

    command="python pipeline.py --config=configs/embeddings.yaml --dbpath=$dbpath --country=$country --validation --attitudinal --labels"

    if [[ "$survey" = "ches2019" ]]
    then
        command="${command} --survey=ches2019 --attdims=lrgen,lrecon,eu_position,people_vs_elite,antielite_salience,corrupt_salience,sociallifestyle,galtan,immigrate_policy,environment,enviro_salience,nationalism"
    fi

    if [[ "$survey" = "gps2019" ]]
    then
        command="${command} --survey=gps2019 --attdims=V4_Scale,V6_Scale,V8_Scale,V9,V10,V12,V13,V14,V18,V19,V20,V21"
    fi

    if [[ "$survey" = "ches2023" ]]
    then
        command="${command} --survey=ches2023 --attdims=antielite_salience,galtan,eu_position,lrecon,refugees"
    fi

    if [[ "$ideological" = "ideological" ]]
    then
        command="${command} --ideological"
    fi

    echo "--------------------------------------------------"
    echo "[RUNNING] ${command}"
    echo "--------------------------------------------------"
    eval "$command"

}

function fn() {

    dbpath=$1
    country=$(echo ${dbpath} | cut -d "." -f 1 | cut -d "2" -f 1 )

    echo "--------------------------------------------------"
    echo "[COUNTRY] ${country}"
    echo "--------------------------------------------------"

    if [[ $country = "argentina" ]]
    then
        gn $dbpath gps2019 ideological
    fi

    if [[ $country = "australia" ]]
    then
        gn $dbpath gps2019 ideological
    fi

    if [[ $country = "austria" ]]
    then
        gn $dbpath gps2019 ideological
        gn $dbpath ches2019
        gn $dbpath ches2023
    fi

    if [[ $country = "belgium" ]]
    then
        gn $dbpath gps2019 ideological
        gn $dbpath ches2019
        gn $dbpath ches2023
    fi

    if [[ $country = "brazil" ]]
    then
        gn $dbpath gps2019 ideological
    fi

    if [[ $country = "canada" ]]
    then
        gn $dbpath gps2019 ideological
    fi

    if [[ $country = "chile" ]]
    then
        gn $dbpath gps2019 ideological
    fi

    if [[ $country = "colombia" ]]
    then
        gn $dbpath gps2019 ideological
    fi

    if [[ $country = "croatia" ]]
    then
        gn $dbpath gps2019 ideological
        gn $dbpath ches2019
        gn $dbpath ches2023
    fi

    if [[ $country = "cyprus" ]]
    then
        gn $dbpath gps2019 ideological
        gn $dbpath ches2019
    fi

    if [[ $country = "czechia" ]]
    then
        gn $dbpath gps2019 ideological
        gn $dbpath ches2019
        gn $dbpath ches2023
    fi

    if [[ $country = "denmark" ]]
    then
        gn $dbpath gps2019 ideological
        gn $dbpath ches2019
        gn $dbpath ches2023
    fi

    if [[ $country = "ecuador" ]]
    then
        gn $dbpath gps2019 ideological
    fi

    if [[ $country = "estonia" ]]
    then
        gn $dbpath gps2019 ideological
        gn $dbpath ches2019
        gn $dbpath ches2023
    fi

    if [[ $country = "finland" ]]
    then
        gn $dbpath gps2019 ideological
        gn $dbpath ches2019
        gn $dbpath ches2023
    fi

    if [[ $country = "france" ]]
    then
        gn $dbpath gps2019 ideological
        gn $dbpath ches2019
        gn $dbpath ches2023
    fi

    if [[ $country = "germany" ]]
    then
        gn $dbpath gps2019 ideological
        gn $dbpath ches2019
        gn $dbpath ches2023
    fi

    if [[ $country = "greece" ]]
    then
        gn $dbpath gps2019 ideological
        gn $dbpath ches2019
        gn $dbpath ches2023
    fi

    if [[ $country = "hungary" ]]
    then
        gn $dbpath gps2019 ideological
        gn $dbpath ches2019
        gn $dbpath ches2023
    fi

    if [[ $country = "iceland" ]]
    then
        gn $dbpath gps2019 ideological
        gn $dbpath ches2019
        gn $dbpath ches2023
    fi

    if [[ $country = "india" ]]
    then
        gn $dbpath gps2019
    fi

    if [[ $country = "ireland" ]]
    then
        gn $dbpath gps2019 ideological
        gn $dbpath ches2019
        gn $dbpath ches2023
    fi

    if [[ $country = "israel" ]]
    then
        python pipeline.py \
            --country=israel \
            --dbpath=$dbpath \
            --config=configs/embeddings_israel.yaml \
            --survey=gps2019 \
            --attdims=V4_Scale \
            --ideological
    fi

    if [[ $country = "italy" ]]
    then
        gn $dbpath gps2019 ideological
        gn $dbpath ches2019
        gn $dbpath ches2023
    fi

    if [[ $country = "japan" ]]
    then
        gn $dbpath gps2019 ideological
    fi

    if [[ $country = "latvia" ]]
    then
        gn $dbpath gps2019 ideological
        gn $dbpath ches2019
        gn $dbpath ches2023
    fi

    if [[ $country = "lithuania" ]]
    then
        gn $dbpath gps2019 ideological
        gn $dbpath ches2019
        gn $dbpath ches2023
    fi

    if [[ "$country" = "luxembourg" ]]
    then
        gn $dbpath gps2019 ideological
        gn $dbpath ches2019
    fi

    if [[ $country = "malta" ]]
    then
        gn $dbpath gps2019 ideological
        gn $dbpath ches2019
        gn $dbpath ches2023
    fi

    if [[ $country = "mexico" ]]
    then
        gn $dbpath gps2019 ideological
    fi

    if [[ $country = "netherlands" ]]
    then
        gn $dbpath gps2019 ideological
        gn $dbpath ches2019
        gn $dbpath ches2023
    fi

    if [[ $country = "newzealand" ]]
    then
        gn $dbpath gps2019 ideological
    fi

    if [[ $country = "nigeria" ]]
    then
        gn $dbpath gps2019 ideological
    fi

    if [[ $country = "norway" ]]
    then
        gn $dbpath gps2019 ideological
        gn $dbpath ches2019
        gn $dbpath ches2023
    fi

    if [[ $country = "peru" ]]
    then
        gn $dbpath gps2019 ideological
    fi

    if [[ $country = "poland" ]]
    then
        gn $dbpath gps2019 ideological
        gn $dbpath ches2019
        gn $dbpath ches2023
    fi

    if [[ $country = "portugal" ]]
    then
        gn $dbpath gps2019 ideological
        gn $dbpath ches2019
        gn $dbpath ches2023
    fi

    if [[ $country = "romania2020.db" || $country = "romania" ]]
    then
        gn $dbpath gps2019 ideological
        gn $dbpath ches2019
        gn $dbpath ches2023
    fi

    if [[ $country = "serbia" ]]
    then
        gn $dbpath gps2019 ideological
    fi

    if [[ $country = "slovakia" ]]
    then
        gn $dbpath gps2019 ideological
        gn $dbpath ches2019
        gn $dbpath ches2023
    fi

    if [[ $country = "slovenia" ]]
    then
        gn $dbpath gps2019 ideological
        gn $dbpath ches2019
        gn $dbpath ches2023
    fi

    if [[ $country = "southafrica" ]]
    then
        gn $dbpath gps2019 ideological
    fi

    if [[ $country = "spain" ]]
    then
        gn $dbpath gps2019 ideological
        gn $dbpath ches2019
        gn $dbpath ches2023
    fi

    if [[ $country = "sweden" ]]
    then
        gn $dbpath gps2019 ideological
        gn $dbpath ches2019
        gn $dbpath ches2023
    fi

    if [[ $country = "switzerland" ]]
    then
        gn $dbpath gps2019 ideological
        gn $dbpath ches2019
        gn $dbpath ches2023
    fi

    if [[ $country = "taiwan" ]]
    then
        gn $dbpath gps2019 ideological
    fi

    if [[ $country = "turkey" ]]
    then
        gn $dbpath gps2019 ideological
        gn $dbpath ches2019
        gn $dbpath ches2023
    fi

    if [[ $country = "uk" ]]
    then
        gn $dbpath gps2019 ideological
        gn $dbpath ches2019
        gn $dbpath ches2023
    fi

    if [[ $country = "ukraine" ]]
    then
        gn $dbpath gps2019 ideological
    fi

    if [[ $country = "uruguay" ]]
    then
        gn $dbpath gps2019 ideological
    fi

    if [[ $country = "us" ]]
    then
        gn $dbpath gps2019 ideological
    fi

    if [[ $country = "venezuela" ]]
    then
        gn $dbpath gps2019 ideological
    fi
}

fn $1
