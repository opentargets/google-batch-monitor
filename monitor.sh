export JOB_UUID="$1"
rm -rf ${JOB_UUID}
mkdir ${JOB_UUID}
cd ${JOB_UUID}

echo "timestamp,num_instances,mem_min,mem_median,mem_max"
echo "timestamp,num_instances,mem_min,mem_median,mem_max" >> monitor_log

while true; do

    # Timestamp.
    export TIMESTAMP=$(date +%Y%m%d-%H%M%S)

    # Poll instances.
    gcloud compute instances list \
        | grep ${JOB_UUID} \
        | grep RUNNING \
        | awk '{print $1 "," $2}' \
        | parallel -k --jobs 64 --colsep ',' 'timeout 20 bash ../poll.sh {1} {2} 2>/dev/null' \
        > data.$TIMESTAMP

    # Check number of instances.
    export NUM_INSTANCES=$(wc -l <data.$TIMESTAMP)
    if [ ${NUM_INSTANCES} == 0 ]; then
        exit
    fi

    # Extract just the memory statistics.
    export F=memory.$TIMESTAMP
    cut -d',' -f3 data.$TIMESTAMP | grep -v '^$' > $F

    # Write report.
    export REPORT="$TIMESTAMP,${NUM_INSTANCES},$(datamash min 1 <$F),$(datamash median 1 <$F),$(datamash max 1 <$F)"
    echo $REPORT
    echo $REPORT >> monitor_log
done
