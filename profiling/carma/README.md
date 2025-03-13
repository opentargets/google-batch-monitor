# Profiling CARMA

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
gs://ot_orchestration/profiling/carma_ukb_ppp/finemapping_manifests/10_sample.csv

# Input datasets
gs://ot_orchestration/profiling/carma_ukb_ppp/loci/1000_largest/
gs://ot_orchestration/profiling/carma_ukb_ppp/loci/1000_sample/
gs://ot_orchestration/profiling/carma_ukb_ppp/loci/100_largest/
gs://ot_orchestration/profiling/carma_ukb_ppp/loci/100_sample/
gs://ot_orchestration/profiling/carma_ukb_ppp/loci/10_largest/
gs://ot_orchestration/profiling/carma_ukb_ppp/loci/10_sample/
```
