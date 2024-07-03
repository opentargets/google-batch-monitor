import os
import sys

from gentropy.common.session import Session
from gentropy.susie_finemapper import SusieFineMapperStep
import hail as hl

batch_task_index = int(sys.argv[1])
print(f"This is worker for task # {batch_task_index}")

path_study_locus = (
    "gs://gentropy-tmp/tskir/ukb_ppp_eur_data_collected_patched_2024_07_03"
)
path_study_index = "gs://ukb_ppp_eur_data/study_index"
path_out = "gs://gentropy-tmp/test_finemapped_out"
logs_out = "gs://gentropy-tmp/test_finemapped_logs"

hail_home = os.path.dirname(hl.__file__)
session = Session(
    hail_home=hail_home,
    start_hail=True,
    extended_spark_conf={
        "spark.jars": "https://storage.googleapis.com/hadoop-lib/gcs/gcs-connector-hadoop3-latest.jar",
        "spark.dynamicAllocation.enabled": "false",
        "spark.driver.memory": "30g",
        "spark.kryoserializer.buffer.max": "500m",
        "spark.driver.maxResultSize": "5g",
    },
)

id_to_process = str(
    int(
        session.spark.read.parquet(path_study_locus)
        .select("studyLocusId")
        .toPandas()
        .loc[batch_task_index, "studyLocusId"]
    )
)

# Remove the path in case it already exists (re-run due to VM preemption, for example).
os.system(f"gsutil -m rm -r {path_out}/{id_to_process}")

SusieFineMapperStep(
    session=session,
    study_locus_to_finemap=id_to_process,
    study_locus_collected_path=path_study_locus,
    study_index_path=path_study_index,
    output_path=path_out,
    # locus_radius=1_500_000,
    max_causal_snps=10,
    primary_signal_pval_threshold=1,
    secondary_signal_pval_threshold=1,
    purity_mean_r2_threshold=0,
    purity_min_r2_threshold=0,
    cs_lbf_thr=2,
    sum_pips=0.99,
    # logging=True,
    susie_est_tausq=False,
    run_carma=False,
    run_sumstat_imputation=False,
    carma_time_limit=600,
    imputed_r2_threshold=0.9,
    ld_score_threshold=5,
    output_path_log=logs_out,
)
