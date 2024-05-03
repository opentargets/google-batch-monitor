rm -f instances.* memory.* monitor_log
echo "timestamp,num_instances,mem_min,mem_median,mem_max"
echo "timestamp,num_instances,mem_min,mem_median,mem_max" >> monitor_log

while true; do
    # Timestamp.
    export TIMESTAMP=$(date +%Y%m%d-%H%M%S)
    export F=memory.$TIMESTAMP
    # Get instances.
    gcloud compute instances list \
        | grep batch-example \
        | grep RUNNING \
        | awk '{print $1 "," $2}' \
        > instances.$TIMESTAMP
    export NUM_INSTANCES=$(wc -l <instances.$TIMESTAMP)
    if [ ${NUM_INSTANCES} == 0 ]; then
        exit
    fi
    # Poll instances.
    cat instances.$TIMESTAMP \
        | parallel --jobs 64 --colsep ',' 'timeout 15 gcloud compute ssh {1} --zone {2} -- free 2>/dev/null' \
        | grep Mem: \
        | awk '{print "100 *" $3 "/" $2}' \
        | bc \
        > $F
    # Write report.
    export REPORT="$TIMESTAMP,${NUM_INSTANCES},$(datamash min 1 <$F),$(datamash median 1 <$F),$(datamash max 1 <$F)"
    echo $REPORT
    echo $REPORT >> monitor_log
done
