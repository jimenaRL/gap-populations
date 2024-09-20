#!/bin/bash

DB=$1
YEAR=$2
COUNTRY=$(echo ${DB} | cut -d "." -f 1 | cut -d "b" -f 1)

LOCAL=/home/jimena/work/dev/gap-populations/dbs/${YEAR}
LOCALANN=/home/jimena/work/dev/gap-populations

declare -a Tables=(
    mp_follower_graph_minin_25_minout_3
    mp_party
    party_mapping
    party_ches2019
    party_ches2023
    party_gps2019
    labels_keywords_minin_25_minout_3
    labels_llm_minin_25_minout_3
    m3_minin_25_minout_3
)

if [[ $DB == *bis ]] # * is used for pattern matching
then
  NEWDB=${COUNTRY}${YEAR}bis_pseudoanonymized
else
  NEWDB=${COUNTRY}${YEAR}_pseudoanonymized
fi

if [[ $DB == *bis ]] # * is used for pattern matching
then
  LUTDB=${COUNTRY}${YEAR}bis_lut
else
  LUTDB=${COUNTRY}${YEAR}_lut
fi

for table in ${Tables[@]}; do
            sqlite3 -batch ${LOCAL}/${DB}.db ".dump ${table}" | sqlite3 ${LOCALANN}/${NEWDB}.db
            Nout=$(sqlite3 -batch -noheader ${LOCALANN}/${NEWDB}.db "SELECT count(*) FROM ${table}")
done

sqlite3 ${LOCALANN}/${NEWDB}.db "ALTER TABLE 'labels_keywords_minin_25_minout_3' RENAME TO 'labels_keywords'"
sqlite3 ${LOCALANN}/${NEWDB}.db "ALTER TABLE 'labels_llm_minin_25_minout_3' RENAME TO 'labels_llm'"
sqlite3 ${LOCALANN}/${NEWDB}.db "ALTER TABLE 'm3_minin_25_minout_3' RENAME TO 'm3_demographics'"
sqlite3 ${LOCALANN}/${NEWDB}.db "ALTER TABLE 'mp_follower_graph_minin_25_minout_3' RENAME TO 'mp_follower_graph'"

echo "==== PSEUDOANONIMYSATION DONE AT ${LOCALANN}/${NEWDB}.db"
echo "==== Tables:"
eval "sqlite3 -batch ${LOCALANN}/${NEWDB}.db .tables"
echo "============================================="


sqlite3 -batch ${LOCAL}/${DB}.db ".dump ${lut}" | sqlite3 ${LOCALANN}/${LUTDB}.db

echo "==== LUT TABLE SAVED DONE AT ${LOCALANN}/${LUTDB}.db"
echo "==== Tables:"
eval "sqlite3 -batch ${LOCALANN}/${LUTDB}.db .tables"
echo "============================================="


sqlite3 -batch ${LOCAL}/${DB}.db "DROP TABLElut"

echo "==== IDENTIFIABLE TABLE SAVED DONE AT ${LOCAL}/${DB}.db"
echo "==== Tables:"
eval "sqlite3 -batch ${LOCALANN}/${LUTDB}.db .tables"
echo "============================================="


