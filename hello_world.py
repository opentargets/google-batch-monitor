import os
import sys

from gentropy.common.session import Session
from gentropy.susie_finemapper import SusieFineMapperStep
import hail as hl

batch_task_index = int(sys.argv[1])
print(f"This is worker for task # {batch_task_index}")

path_study_locus = "gs://genetics-portal-dev-analysis/yt4/toy_studdy_locus_alzheimer"
path_si = "gs://gwas_catalog_data/study_index"
path_out = "gs://gentropy-tmp/finemapping/v2_2024-04-23"

hail_home = os.path.dirname(hl.__file__)
session = Session(
    hail_home=hail_home,
    start_hail=True,
    extended_spark_conf={
        "spark.jars": "https://storage.googleapis.com/hadoop-lib/gcs/gcs-connector-hadoop3-latest.jar"
    },
)
# hl.init(sc=session.spark.sparkContext, log="/dev/null")

id_to_process = str(
    int(
        session.spark.read.parquet(path_study_locus)
        .toPandas()
        .loc[batch_task_index, "studyLocusId"]
    )
)

L = SusieFineMapperStep(
    session=session,
    study_locus_to_finemap=id_to_process,
    study_locus_collected_path=path_study_locus,
    study_index_path=path_si,
    output_path=path_out,
    locus_radius=100_000,
    locus_l=10,
)
