# Run profiling
One of the difficult things to guess when doing a Google Batch run is how much RAM to allocate to each task. This is complicated by the fact that Google Cloud Monitoring doesn't provide facilities to monitor RAM usage (only CPU usage, which isn't as important).

The protocol described here creates a monitoring VM which continuously polls all VMs used by a given Google Batch run to create a summary of RAM usage across all VMs at a given time.

It also counts how many VMs are being used at any given time, which makes it possible to create accurate estimations as to how much the run cost was.

The protocol currently has to be manually triggered, but if it proves useful, in the future it could be automated and even incorporated into Google Batch DAGs for automated data collection and reporting.

### 1. Create a VM which will monitor the resource usage
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

### 2. SSH into it
```bash
gcloud compute ssh batch-monitor --zone europe-west1-b
screen
sudo apt install bc datamash parallel dos2unix
```

### 3. Copy the scripts
```bash
gcloud compute scp monitor.sh poll.sh batch-monitor:~ --zone europe-west1-b
```

### 4. Once the job has started running, run monitoring
```bash
bash monitor.sh UNIQUE_JOB_ID
```

Substitute the unique job ID you got from when you submitted the job.

It will monitor instance memory usage and output it to screen and into a log file every few minutes. Once there are no instances remaining, it will exit automatically.

### 5. Create run report
(To be added later)