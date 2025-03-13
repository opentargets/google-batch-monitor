import time
from loguru import logger
from importlib.metadata import version
import sys
import googlecloudprofiler

logger.remove(0)
logger.add(sys.stdout, format="{time} | {level} | {file}:{function}:{line} |  SusieFinemapper with CARMA profiling | {message}")
gentropy_version = version("gentropy")

def timeit(func):
    def wrapper():
        logger.info(f"Starting susie finemapper step from gentropy {gentropy_version}")
        start = time.perf_counter()
        logger.info(f"Starting at {start}...")
        func()
        end = time.perf_counter()
        logger.info(f"Ending at {end}")
        logger.info(f"Susie finemapper elapsed for {end - start:.2f} seconds")
    return wrapper

@timeit
def main():
    try:
        googlecloudprofiler.start(
            service="gentropy-susie-fine-mapper-profiler",
            service_version=gentropy_version,
            project_id="open-targets-genetics-dev",
            verbose=3,
        )
    except (ValueError, NotImplementedError) as exc:
        print(exc)  # Handle errors here
    from gentropy.common.session import Session
    session = Session(
        spark_uri = "local[*]",
        extended_spark_conf={"spark.jars": "https://storage.googleapis.com/hadoop-lib/gcs/gcs-connector-hadoop3-latest.jar"}
    )
    study_index = session.spark.read.parquet("gs://ukb_ppp_eur_data/credible_set_clean/20250129")
    # Perform some dummy operations that will result in usage of multiple cores to ensure the cloud profiler captures all core usages
    study_index.groupBy("studyId").count().show()

if __name__ == "__main__":
    main()
