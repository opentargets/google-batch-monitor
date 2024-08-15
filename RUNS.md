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
export OUTPUT=gs://gentropy-tmp/gwas_finemapping_test/1_carma_32gb
# Where to store the manifest for processing.
export MANIFEST_PREFIX=gs://gentropy-tmp/finemapping-manifest/gwas_finemapping_test/1_carma_32gb
# Finemapping parameters.
export FINEMAPPING_PARAMS="step.max_causal_snps=10 step.primary_signal_pval_threshold=1 step.secondary_signal_pval_threshold=1 step.purity_mean_r2_threshold=0 step.purity_min_r2_threshold=0 step.cs_lbf_thr=2 step.sum_pips=0.99 step.susie_est_tausq=False step.run_carma=True step.run_sumstat_imputation=False step.carma_time_limit=600 step.imputed_r2_threshold=0.9 step.ld_score_threshold=5"
# Computing parameters.
export PARALLELISM=500
export VM_TYPE=n2-highmem-4
export CPU_MILLI=4000
export MEMORY_MIB=25000
# If set more than 0, then only the first N loci will be processed. Useful for debugging.
export FIRST_N_LOCI=500
```

Run details:
* 2024-08-12
* finemapping-202408-68109d57-8594-4f0b0
* gs://gentropy-tmp/finemapping-manifest/gwas_finemapping_test/1_carma_32gb/batch_chunk_aa
* 32 GB per task + 1 task per VM

## 2024-07-19: GWAS Catalog, 500 loci, test (2) with CARMA + imputation

```bash
# Input and output parameters.
export STUDY_INDEX=gs://genetics_etl_python_playground/releases/24.06/study_index/gwas_catalog
export COLLECTED_LOCI=gs://genetics-portal-dev-analysis/dc16/output/gwas_cat_clumped_collected.parquet
export OUTPUT=gs://gentropy-tmp/gwas_finemapping_test/2_imputation
# Where to store the manifest for processing.
export MANIFEST_PREFIX=gs://gentropy-tmp/finemapping-manifest/gwas_finemapping_test/2_imputation
# Finemapping parameters.
export FINEMAPPING_PARAMS="step.max_causal_snps=10 step.primary_signal_pval_threshold=1 step.secondary_signal_pval_threshold=1 step.purity_mean_r2_threshold=0 step.purity_min_r2_threshold=0 step.cs_lbf_thr=2 step.sum_pips=0.99 step.susie_est_tausq=False step.run_carma=True step.run_sumstat_imputation=True step.carma_time_limit=600 step.imputed_r2_threshold=0.9 step.ld_score_threshold=5"
# Computing parameters.
export PARALLELISM=500
export VM_TYPE=n2-highmem-4
export CPU_MILLI=4000
export MEMORY_MIB=25000
# If set more than 0, then only the first N loci will be processed. Useful for debugging.
export FIRST_N_LOCI=500
```

Run details:
* 2024-08-15
* finemapping-202408-ac309602-4a5e-41ab0
* gs://gentropy-tmp/finemapping-manifest/gwas_finemapping_test/2_imputation/batch_chunk_aa
* 32 GB per task + 1 task per VM

## 2024-07-19: GWAS Catalog, 500 loci, test (3) with CARMA + imputation + susie_est_tausq

```bash
# Input and output parameters.
export STUDY_INDEX=gs://genetics_etl_python_playground/releases/24.06/study_index/gwas_catalog
export COLLECTED_LOCI=gs://genetics-portal-dev-analysis/dc16/output/gwas_cat_clumped_collected.parquet
export OUTPUT=gs://gentropy-tmp/gwas_finemapping_test/3_susie_est_tausq
# Where to store the manifest for processing.
export MANIFEST_PREFIX=gs://gentropy-tmp/finemapping-manifest/gwas_finemapping_test/3_susie_est_tausq
# Finemapping parameters.
export FINEMAPPING_PARAMS="step.max_causal_snps=10 step.primary_signal_pval_threshold=1 step.secondary_signal_pval_threshold=1 step.purity_mean_r2_threshold=0 step.purity_min_r2_threshold=0 step.cs_lbf_thr=2 step.sum_pips=0.99 step.susie_est_tausq=True step.run_carma=True step.run_sumstat_imputation=True step.carma_time_limit=600 step.imputed_r2_threshold=0.9 step.ld_score_threshold=5"
# Computing parameters.
export PARALLELISM=500
export VM_TYPE=n2-highmem-4
export CPU_MILLI=4000
export MEMORY_MIB=25000
# If set more than 0, then only the first N loci will be processed. Useful for debugging.
export FIRST_N_LOCI=500
```

Run details:
* 2024-08-15
* finemapping-202408-2ffb3350-bc30-443b0
* gs://gentropy-tmp/finemapping-manifest/gwas_finemapping_test/3_susie_est_tausq/batch_chunk_aa
* 32 GB per task + 1 task per VM
