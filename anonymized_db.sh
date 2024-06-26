#!/bin/bash

COUNTRY=$1

REMOTEDB=jroyolet@cca.in2p3.fr:/sps/humanum/user/jroyolet/dev/some4demDB/dbs
DB=/home/jimena/work/dev/some4demDB/dbs
ANNDB=/home/jimena/work/dev/gap-populations

rsync -e ssh -r -ogt  --human-readable --verbose --stats --progress ${REMOTEDB}/${COUNTRY}.db ${DB}/${COUNTRY}.db

declare -a Tables=(
    mp_follower_graph_minin_25_minout_3
    mp_party
    party_mapping
    party_ches2019
    party_ches2023
    party_gps2019
    labels_keywords_minin_25_minout_3
    labels_llm_minin_25_minout_3
)

for table in ${Tables[@]}; do
    sqlite3 ${DB}/${COUNTRY}.db ".dump ${table}" | sqlite3 ${ANNDB}/${COUNTRY}.db
done
