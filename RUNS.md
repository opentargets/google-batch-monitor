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
# Computing parameters.
export PARALLELISM=4000
export VM_TYPE=n2-standard-4
export CPU_MILLI=2000
export MEMORY_MIB=12500
# If set more than 0, then only the first N loci will be processed. Useful for debugging.
export FIRST_N_LOCI=0
```

Run ID batch-example-2024-9984b186-ec63-42680. Observation: very smooth run, all successful.

## 2024-07-19: GWAS Catalog, 500 loci, test (1) with CARMA

```bash
# Input and output parameters.
export STUDY_INDEX=gs://genetics_etl_python_playground/releases/24.06/study_index/gwas_catalog
export COLLECTED_LOCI=gs://genetics-portal-dev-analysis/dc16/output/gwas_cat_clumped_collected.parquet
export OUTPUT=gs://gentropy-tmp/gwas_finemapping_test/1_carma
# Where to store the manifest for processing.
export MANIFEST_PREFIX=gs://gentropy-tmp/finemapping-manifest/gwas_finemapping_test/1_carma
# Finemapping parameters.
export FINEMAPPING_PARAMS="step.max_causal_snps=10 step.primary_signal_pval_threshold=1 step.secondary_signal_pval_threshold=1 step.purity_mean_r2_threshold=0 step.purity_min_r2_threshold=0 step.cs_lbf_thr=2 step.sum_pips=0.99 step.susie_est_tausq=False step.run_carma=True step.run_sumstat_imputation=False step.carma_time_limit=6000 step.imputed_r2_threshold=0.9 step.ld_score_threshold=5"
# Computing parameters.
export PARALLELISM=125
export VM_TYPE=n2-standard-4
export CPU_MILLI=2000
export MEMORY_MIB=12500
# If set more than 0, then only the first N loci will be processed. Useful for debugging.
export FIRST_N_LOCI=500
```

/// Run ID finemapping-202407-11b0bd61-444e-47ff0 (original).

Run ID finemapping-202408-2cda4e59-cde6-4e1c0 (re-run 2024-08-04).

## 2024-07-19: GWAS Catalog, 500 loci, test (2) with CARMA + imputation

```bash
# Input and output parameters.
export STUDY_INDEX=gs://genetics_etl_python_playground/releases/24.06/study_index/gwas_catalog
export COLLECTED_LOCI=gs://genetics-portal-dev-analysis/dc16/output/gwas_cat_clumped_collected.parquet
export OUTPUT=gs://gentropy-tmp/gwas_finemapping_test/2_imputation
# Where to store the manifest for processing.
export MANIFEST_PREFIX=gs://gentropy-tmp/finemapping-manifest/gwas_finemapping_test/2_imputation
# Finemapping parameters.
export FINEMAPPING_PARAMS="step.max_causal_snps=10 step.primary_signal_pval_threshold=1 step.secondary_signal_pval_threshold=1 step.purity_mean_r2_threshold=0 step.purity_min_r2_threshold=0 step.cs_lbf_thr=2 step.sum_pips=0.99 step.susie_est_tausq=False step.run_carma=True step.run_sumstat_imputation=True step.carma_time_limit=6000 step.imputed_r2_threshold=0.9 step.ld_score_threshold=5"
# Computing parameters.
export PARALLELISM=125
export VM_TYPE=n2-standard-4
export CPU_MILLI=2000
export MEMORY_MIB=12500
# If set more than 0, then only the first N loci will be processed. Useful for debugging.
export FIRST_N_LOCI=500
```

/// Run ID finemapping-202407-30750a18-f830-47720 (original).

## 2024-07-19: GWAS Catalog, 500 loci, test (3) with CARMA + imputation + susie_est_tausq

```bash
# Input and output parameters.
export STUDY_INDEX=gs://genetics_etl_python_playground/releases/24.06/study_index/gwas_catalog
export COLLECTED_LOCI=gs://genetics-portal-dev-analysis/dc16/output/gwas_cat_clumped_collected.parquet
export OUTPUT=gs://gentropy-tmp/gwas_finemapping_test/3_susie_est_tausq
# Where to store the manifest for processing.
export MANIFEST_PREFIX=gs://gentropy-tmp/finemapping-manifest/gwas_finemapping_test/3_susie_est_tausq
# Finemapping parameters.
export FINEMAPPING_PARAMS="step.max_causal_snps=10 step.primary_signal_pval_threshold=1 step.secondary_signal_pval_threshold=1 step.purity_mean_r2_threshold=0 step.purity_min_r2_threshold=0 step.cs_lbf_thr=2 step.sum_pips=0.99 step.susie_est_tausq=True step.run_carma=True step.run_sumstat_imputation=True step.carma_time_limit=6000 step.imputed_r2_threshold=0.9 step.ld_score_threshold=5"
# Computing parameters.
export PARALLELISM=125
export VM_TYPE=n2-standard-4
export CPU_MILLI=2000
export MEMORY_MIB=12500
# If set more than 0, then only the first N loci will be processed. Useful for debugging.
export FIRST_N_LOCI=500
```

/// Run ID finemapping-202407-1a3d6a4c-9250-4a700 (original).

