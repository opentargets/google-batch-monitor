# batch-minimal-example

## 1. Prepare job configuration

The configuration is in JSON format and in this case it has been prepared in advance in [`config.json`](./config.json). It specifies, in order:

- Which script to run on the machine
- Which computing resources are required to run the job (note that it uses a weird "milli-CPU" unit, so if you want one CPU per task, you specify 1000)
- In which Storage bucket the code is stored, and where to mount it on each worker machine
- Maximum retry count for task and maximum duration in seconds
- How many tasks are there going to be in total (in this example, 10; in real life example, this would be for example the number of rows in a table that we are iterating over)
- How many tasks to run concurrently, in this example 4, but it can be as high as 1,000 or 2,000 as needed.
- Machine worker type
- Provisioning model and logging policy

## 2. Copy code and submit Google Batch job

The first positional argument is job ID. (A job is a single submission which spawns a collection of tasks.) It has to be globally unique for all jobs, including ones submitted previously. Because of this, we append timestamp, so the resulting job ID looks something like: `batch-example-20240410-115253`.

```bash
gsutil cp \
    runner.sh requirements.txt run_finemapping.py \
    gs://gentropy-tmp/batch-example/code && \
gcloud batch jobs submit \
    batch-example-$(date +%Y%m%d-%H%M%S) \
    --config=config.json \
    --project=open-targets-genetics-dev \
    --location=europe-west1
```

## 3. Monitor job progress

Job will shortly appear in the Google Batch dashboard (give it up to a minute): https://console.cloud.google.com/batch/jobs?referrer=search&project=open-targets-genetics-dev

Logs for each individual task will appear under `gs://gentropy-tmp/batch-example/logs`.

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
sudo apt install bc datamash parallel
```

Copy `monitor.sh`:

```bash
gcloud compute scp monitor.sh batch-monitor:~ --zone europe-west1-b
```

Once the job has started running, run `monitor.sh`:

```bash
bash monitor.sh
```

It will monitor instance memory usage and output it to screen and into a log file every few minutes. Once there are no instances remaining, it will exit automatically.
