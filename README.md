# batch-minimal-example

## 1. Prepare job configuration

Modify the configuration in [`config.json`](./config.json):

- `remotePath` to point to a unique location (so that multiple runs can be done in parallel), for example: `gentropy-tmp/YOUR-UNIQUE-ID`
- `taskCount` to specify the total number of tasks (dataframe rows)
- Study loci in `taskEnvironments` (currently need to be specified manually)
- Inputs, outputs, parameters of the step

## 2. Copy code and submit Google Batch job

The first positional argument is job ID. (A job is a single submission which spawns a collection of tasks.) It has to be globally unique for all jobs, including ones submitted previously. Because of this, we append a timestamp, so the resulting job ID looks something like: `batch-example-20240410-115253`.

```bash
gcloud batch jobs submit \
    batch-example-$(date +%Y%m%d-%H%M%S) \
    --config=config.json \
    --project=open-targets-genetics-dev \
    --location=europe-west1
```

Note the unique job ID that has been assigned. You will need it for monitoring.

## 3. Monitor job progress

Job will shortly appear in the Google Batch dashboard (give it up to a minute): https://console.cloud.google.com/batch/jobs?referrer=search&project=open-targets-genetics-dev

Logs for each individual task will appear under `gs://${REMOTE_PATH}/logs`.

## 4. Log resource usage

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

Then SSH to it:

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

Substitute the unique job ID you got from step 3.

It will monitor instance memory usage and output it to screen and into a log file every few minutes. Once there are no instances remaining, it will exit automatically.
