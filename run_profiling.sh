#!/usr/bin/env bash


echo "Running google cloud profiler"
APP="gentropy-susie-fine-mapper-profiling"
GCP_PROJECT_ID="open-targets-genetics-dev"
GCP_ZONE="europe-west1-b"
MACHINE_TYPE="n1-standard-4"


gcloud compute instances create ${USER}-${APP} \
    --project=${GCP_PROJECT_ID} \
    --zone=${GCP_ZONE} \
    --machine-type=${MACHINE_TYPE} \
    

