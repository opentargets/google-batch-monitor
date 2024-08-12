export NAME="$1"
export ZONE="$2"
# Memory usage in %
MEMORY=$(
    gcloud compute ssh $NAME --zone $ZONE -- free 2>/dev/null \
    | grep "Mem:" \
    | tr -d '\r' \
    | awk '{print "scale=2; 100*(1-" $7 "/" $2 ")"}' \
    | dos2unix \
    | bc -l \
    | cut -d '.' -f1
)
# Uptime in minutes
UPTIME=$(
    gcloud compute ssh $NAME --zone $ZONE -- cat /proc/uptime 2>/dev/null | awk '{print $1}' | cut -d'.' -f1
)
# CPU usage
LOAD=$(
    gcloud compute ssh $NAME --zone $ZONE -- uptime 2>/dev/null | awk -F'load average: ' '{print $2}' | awk -F', ' '{print "scale=0; 100*"$2}' | bc -l | cut -d'.' -f1
)
# Restart, if needed
RESTART="-"
# if [ "$LOAD" -lt 10 ] && [ "$UPTIME" -gt 300 ]; then
#     RESTART="RESTART"
#     gcloud compute ssh $NAME --zone $ZONE -- sudo reboot 2>/dev/null
# fi
echo "$NAME,$ZONE,$MEMORY,$UPTIME,$LOAD,$RESTART"
