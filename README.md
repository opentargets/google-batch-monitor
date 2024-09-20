# Google Batch run monitoring & log extraction

# Run profiling

You can create a VM which will monitor the resource usage:

```bash
gcloud compute instances create batch-monitor \
    --project=open-targets-genetics-dev \
    --zone=europe-west1-b \
    --machine-type=n2d-highcpu-32 \
    --network-interface=network-tier=PREMIUM,stack-type=IPV4_ONLY,subnet=default \
    --maintenance-policy=MIGRATE \
    --provisioning-model=STANDARD \
    --service-account=234703259993-compute@developer.gserviceaccount.com \
    --scopes=https://www.googleapis.com/auth/cloud-platform \
    --create-disk=auto-delete=yes,boot=yes,device-name=tskir-monitor,image=projects/debian-cloud/global/images/debian-12-bookworm-v20240415,mode=rw,size=500,type=projects/open-targets-genetics-dev/zones/europe-west1-b/diskTypes/pd-balanced \
    --no-shielded-secure-boot \
    --shielded-vtpm \
    --shielded-integrity-monitoring \
    --labels=goog-ec-src=vm_add-gcloud \
    --reservation-affinity=any
```

Then SSH into it:

```bash
gcloud compute ssh batch-monitor --zone europe-west1-b
screen
sudo apt install bc datamash parallel dos2unix
```

Copy `monitor.sh`:

```bash
gcloud compute scp monitor.sh poll.sh batch-monitor:~ --zone europe-west1-b
```

Once the job has started running, run `monitor.sh`:

```bash
bash monitor.sh UNIQUE_JOB_ID
```

Substitute the unique job ID you got from when you submitted the job.

It will monitor instance memory usage and output it to screen and into a log file every few minutes. Once there are no instances remaining, it will exit automatically.

# Extract logs

```bash
# Set up Batch job ID. This was printed at the end of step 1.
export GOOGLE_BATCH_JOB_ID=...
# *Full* path to the manifest of the given Batch run.
export MANIFEST=...

# Create folder for logs output.
mkdir -p logs_${GOOGLE_BATCH_JOB_ID} logs_${GOOGLE_BATCH_JOB_ID}/exit_statuses logs_${GOOGLE_BATCH_JOB_ID}/failed_logs
cd logs_${GOOGLE_BATCH_JOB_ID}

# Link task indexes to loci.
gsutil cat $MANIFEST \
    | tail -n+2 \
    | cut -d',' -f1 \
    | cut -d'=' -f2 \
    | awk -v GOOGLE_BATCH_JOB_ID=$GOOGLE_BATCH_JOB_ID '{print GOOGLE_BATCH_JOB_ID "-group0-" NR - 1 "\t" $1}' \
    | sort -k1,1 \
    > task_to_locus

# Collect instance logs.
gcloud logging read \
    "resource.type=gce_instance AND labels.job_uid=$GOOGLE_BATCH_JOB_ID" \
    --project=open-targets-genetics-dev \
    --format=json \
    --freshness=30d \
    > instance_log

# Extract exit statuses.
jq -r \
    '.[] | "\(.timestamp)\t\(.textPayload)"' \
    instance_log \
    | grep "Task task.*exited with status" \
    | sort -k1,1 \
    | sed -e 's@Task task/@@' -e 's@/./0 runnable 0 exited with status @|@' \
    | tr '|' '\t' \
    | awk -F'\t' '{print $0 > "exit_statuses/" $2}'

# Identify tasks which have not completed.
comm -13 <(ls exit_statuses | sort) <(cut -f1 task_to_locus | sort) \
| parallel echo -e 'no_timestamp\\t{}\\tnot_completed' '>' exit_statuses/{}

# Identify failed tasks (this includes the not completed ones).
tail -q -n1 exit_statuses/* \
    | awk -F'\t' '$3 != 0' \
    > failed_tasks

# Make directory structure for exit codes.
cut -f3 failed_tasks | sort -u | parallel mkdir failed_logs/{}

# Fetch logs for failed tasks only.
function fetch_logs () {
    export TASK_ID=$1
    export RETURN_CODE=$2
    gcloud logging read \
        "resource.type=batch.googleapis.com/Job AND labels.task_id=${TASK_ID}" \
        --project=open-targets-genetics-dev \
        --format=json \
        --freshness=30d \
        | jq -r '.[] | "\(.timestamp)\t\(.labels.task_id)\t\(.textPayload)"' \
        | sort -k1,1 \
        > failed_logs/${RETURN_CODE}/${TASK_ID}
}
export -f fetch_logs
parallel --jobs 4 --colsep '\t' fetch_logs {2} {3} :::: failed_tasks

# Rename logs of failed loci.
find failed_logs -type f | parallel echo "{/},{}" | tr ',' '\t' | sort -k1,1 > /tmp/task_to_filename
join task_to_locus /tmp/task_to_filename | tr ' ' '\t' | cut -f2,3 > /tmp/locus_to_filename
parallel --colsep '\t' mv {2} {2//}/{1} :::: /tmp/locus_to_filename
```
