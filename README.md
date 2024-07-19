# Submitting a finemapping run

## 1. Configure parameters

Input and output data paths:

```bash
# Input and output parameters.
export STUDY_INDEX=gs://ukb_ppp_eur_data/study_index
export COLLECTED_LOCI=gs://genetics-portal-dev-analysis/dc16/output/ukb_ppp/clean_loci.parquet
export OUTPUT=gs://ukb_ppp_eur_data/finemapped_20240719
# Where to store the manifest for processing.
export MANIFEST_PREFIX=gs://gentropy-tmp/finemapping-manifest/ukb_ppp_20240719
# Finemapping parameters.
export FINEMAPPING_PARAMS="step.max_causal_snps=10 step.primary_signal_pval_threshold=1 step.secondary_signal_pval_threshold=1 step.purity_mean_r2_threshold=0 step.purity_min_r2_threshold=0 step.cs_lbf_thr=2 step.sum_pips=0.99 step.susie_est_tausq=False step.run_carma=False step.run_sumstat_imputation=False step.carma_time_limit=600 step.imputed_r2_threshold=0.9 step.ld_score_threshold=5"
# If set more than 0, then only the first N loci will be processed. Useful for debugging.
export FIRST_N_LOCI=0
```

Also, if you need to modify the finemapping run parameters, modify directly inside `config.json`.

## 2. Prepare inputs and submit Google Batch job

The first positional argument is job ID. (A job is a single submission which spawns a collection of tasks.) It has to be globally unique for all jobs, including ones submitted previously. Because of this, we append a timestamp, so the resulting job ID looks something like: `batch-example-20240410-115253`.

```bash
# 1. List collected loci.
gsutil ls ${COLLECTED_LOCI} | grep studyLocusId | rev | cut -d'/' -f2 | rev > /tmp/collected_loci

# 2. If needed: get the first N loci.
if [ ${FIRST_N_LOCI} -gt 0 ]; then
    head -n ${FIRST_N_LOCI} /tmp/collected_loci > /tmp/loci_to_process
else
    cat /tmp/collected_loci > /tmp/loci_to_process
fi

# 3. Prepare input and output paths.
awk \
    -v COLLECTED_LOCI=${COLLECTED_LOCI} \
    -v OUTPUT=${OUTPUT} \
    '{print COLLECTED_LOCI "/" $1 "," OUTPUT "/" $1}' \
    /tmp/loci_to_process \
    > /tmp/loci_input_output

# 4. Split the manifest into at most 100,000 long chunks.
rm /tmp/batch_chunk_*
split -l 100000 /tmp/loci_input_output /tmp/batch_chunk_

# 5. Operating on each chunk now.
for CHUNK in /tmp/batch_chunk_*; do
    # 5a. Add header and upload.
    export CHUNK
    MANIFEST_LOCATION=${MANIFEST_PREFIX}/$(basename $CHUNK)
    (echo "study_locus_input,study_locus_output"; cat $CHUNK) | gsutil cp - ${MANIFEST_LOCATION}
    # 5b. Create config.
    NUM_OF_TASKS=$(wc -l <$CHUNK)
    cat config.json \
    | sed -e "s@VALUE_STUDY_INDEX@${STUDY_INDEX}@g" \
    | sed -e "s@VALUE_MANIFEST@${MANIFEST_LOCATION}@g" \
    | sed -e "s@VALUE_TASK_COUNT@${NUM_OF_TASKS}@g" \
    | sed -e "s@VALUE_FINEMAPPING_PARAMS@${FINEMAPPING_PARAMS}@g" \
    > $CHUNK.json
    # 5c. Submit for processing.
    gcloud batch jobs submit \
        batch-example-$(date +%Y%m%d-%H%M%S) \
        --config=${CHUNK}.json \
        --project=open-targets-genetics-dev \
        --location=europe-west1
    sleep 2
done
```

Note the unique job ID(s) that has been assigned. You will need it for monitoring.

Job will shortly appear in the Google Batch dashboard (give it up to a minute): https://console.cloud.google.com/batch/jobs?referrer=search&project=open-targets-genetics-dev

# Profiling

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
