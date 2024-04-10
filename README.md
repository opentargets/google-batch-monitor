# batch-minimal-example

## 1. Prepare job configuration
The configuration is in JSON format and in this case it has been prepared in advance in [`config.json`](./config.json). It specifies, in order:
* Which script to run on the machine
* Which computing resources are required to run the job (note that it uses a weird "milli-CPU" unit, so if you want one CPU per task, you specify 1000)
* In which Storage bucket the code is stored, and where to mount it on each worker machine
* Maximum retry count for task and maximum duration in seconds
* How many tasks are there going to be in total (in this example, 10; in real life example, this would be for example the number of rows in a table that we are iterating over)
* How many tasks to run concurrently, in this example 4, but it can be as high as 1,000 or 2,000 as needed.
* Machine worker type
* Provisioning model and logging policy

## 2. Copy all code to the staging Storage bucket
This is the bucket where Batch will read the code from.
```bash
gsutil cp \
    runner.sh requirements.txt hello_world.py \
    gs://gentropy-tmp/batch-example/code
```

## 3. Submit job to Google Batch
The first positional argument is job ID. (A job is a single submission which spawns a collection of tasks.) It has to be globally unique for all jobs, including ones submitted previously. Because of this, we append timestamp, so the resulting job ID looks something like: `batch-example-20240410-115253`.
```bash
gcloud batch jobs submit \
    batch-example-$(date +%Y%m%d-%H%M%S) \
    --config=config.json \
    --project=open-targets-genetics-dev \
    --location=europe-west1
```

## 4. Monitor job progress
Job will shortly appear in the Google Batch dashboard (give it 15-30 seconds): https://console.cloud.google.com/batch/jobs?referrer=search&project=open-targets-genetics-dev

Logs for each individual task will appear under `gs://gentropy-tmp/batch-example/logs`.
