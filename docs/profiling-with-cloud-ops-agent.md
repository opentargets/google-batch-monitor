# Profiling with cloud ops agent

To profile google cloud batch job one can use the implementation of the 

This profiling was done on gentropy 2.2.0 version running carma implementation in the SusieFineMapper step.

## Profiling runs

* The profiling of google batch job was performed on 6 runs in total. 
* Each run executes tasks that are defined in on of the manifests (described below).
* Each manifest generates between 10 to 1000 google batch tasks depending on it's size.

```
$gcloud storage ls 'gs://ot_orchestration/profiling/carma_ukb_ppp/*'

# Input manifests to the fine-mappin job
gs://ot_orchestration/profiling/carma_ukb_ppp/finemapping_manifests/1000_largest.csv
gs://ot_orchestration/profiling/carma_ukb_ppp/finemapping_manifests/1000_sample.csv
gs://ot_orchestration/profiling/carma_ukb_ppp/finemapping_manifests/100_largest.csv
gs://ot_orchestration/profiling/carma_ukb_ppp/finemapping_manifests/100_sample.csv
gs://ot_orchestration/profiling/carma_ukb_ppp/finemapping_manifests/10_largest.csv

# Input datasets
gs://ot_orchestration/profiling/carma_ukb_ppp/loci/1000_largest/
gs://ot_orchestration/profiling/carma_ukb_ppp/loci/1000_sample/
gs://ot_orchestration/profiling/carma_ukb_ppp/loci/100_largest/
gs://ot_orchestration/profiling/carma_ukb_ppp/loci/100_sample/
gs://ot_orchestration/profiling/carma_ukb_ppp/loci/10_largest/
gs://ot_orchestration/profiling/carma_ukb_ppp/loci/10_sample/
```

To run the profiling one need to submit the google batch job via the `run_batch.py` script.

To run the script

```
uv sync --frozen
uv run profiling/carma/run_batch.py -m $Input_manifest -s gs://ukb_ppp_eur_data/study_index
```

> [!TIP]
> To run the script one need to set up the application-default-credentials with
> ```
> gcloud auth login application-default-credentials
> ```
> This tep is required to read the manifest and extract the amount of environments needed to be build to start the google batch job. 

The command will create a google batch job with respect to the input manifest and track the metrics like:
    - cpu_usage
    - memory_consumption
via the [Google Cloud Ops Agent](https://cloud.google.com/stackdriver/docs/solutions/agents/ops-agent).


