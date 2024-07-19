# List of finemapping runs & parameters

## 2024-07-19: Standard UKB PPP finemapping
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