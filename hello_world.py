import os
import sys

from gentropy.common.session import Session
from gentropy.susie_finemapper import SusieFineMapperStep
import hail as hl

batch_task_index = int(sys.argv[1])
print(f"This is worker for task # {batch_task_index}")

path_study_locus = "gs://genetics-portal-dev-analysis/yt4/ukbb_ppp_no_mhc_small"
path_study_index = "gs://gentropy-tmp/finemapping/ukbb_study_index_corrected2_2024-04-23"
path_out = "gs://gentropy-tmp/finemapping/v3_2024-04-23_5k"

hail_home = os.path.dirname(hl.__file__)
session = Session(
    hail_home=hail_home,
    start_hail=True,
    extended_spark_conf={
        "spark.jars": "https://storage.googleapis.com/hadoop-lib/gcs/gcs-connector-hadoop3-latest.jar"
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

SusieFineMapperStep(
    session=session,
    study_locus_to_finemap=id_to_process,
    study_locus_collected_path=path_study_locus,
    study_index_path=path_study_index,
    output_path=path_out,
    locus_radius=100_000,
    max_causal_snps=10,
)
