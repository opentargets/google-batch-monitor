"""Script for running google batch fine-mapping job."""

from argparse import ArgumentParser
import pandas as pd

from google.cloud.batch_v1 import Job, LifecyclePolicy, BatchServiceClient, Runnable, TaskSpec, ComputeResource, TaskGroup, AllocationPolicy, LogsPolicy, CreateJobRequest, Environment
import logging
import datetime
GENTROPY_VERSION="v2.2.0-rc.6"
JOB_NAME = f"carma-profiling-gentropy-{datetime.datetime.now().strftime('%Y-%m-%d-%H%M')}"
GCP_PROJECT_GENETICS = "open-targets-genetics-dev"
GCP_REGION = "europe-west1"
GCP_ZONE = "europe-west1-d"
IMAGE_URI = f"europe-west1-docker.pkg.dev/open-targets-genetics-dev/gentropy-app/gentropy:{GENTROPY_VERSION.removeprefix('v')}"

logging.basicConfig(level=logging.INFO)

def main(**kwargs) -> None:
    for k,v in kwargs.items():
        logging.info(f"Using {k}: {v}")
        print(JOB_NAME)
    fm = FinemappinJob(GCP_PROJECT_GENETICS, GCP_REGION, JOB_NAME, kwargs["study_index_path"], kwargs["manifest_path"])._job()


class FinemappinJob():
    def __init__(self, project_id: str, region: str, job_name: str, study_index_path: str, study_locus_manifest_path: str,):
        self.project_id = project_id
        self.region = region
        self.job_name = job_name
        self.study_index_path = study_index_path
        self.study_locus_manifest_path = study_locus_manifest_path
        benchmark = self.study_locus_manifest_path.split("/")[-1].removesuffix(".csv").replace("_", "-")
        self.labels = {
            "tool": "batch-job-monitor",
            "environment": "development",
            "subteam": "genetics",
            "team": "open-targets",
            "benchmark": benchmark,
            "google-cloud-ops-agent-enabled": "yes"
        }
        self.job_name = job_name + "-" + benchmark

        self.client = BatchServiceClient()

      
                
    def prepare_job_envs(self) -> list[Environment]:
        manifest = pd.read_csv(self.study_locus_manifest_path)
        n_tasks = len(manifest)
        tasks = list(range(0, n_tasks))
        return [Environment(variables={"LOCUS_INDEX": str(i)}) for i in tasks][0:2]

    def _job(self) -> Job:
        # Define what will be done as part of the job.
        task_group = TaskGroup(
            task_spec=TaskSpec(
                runnables = [
                    Runnable(
                        container=Runnable.Container(
                            image_uri=IMAGE_URI, 
                            commands=self.carma_command, 
                            entrypoint="/bin/sh"
                        )
                    )
                ],
                compute_resource=ComputeResource(
                    cpu_milli = 4000,
                    memory_mib = 25000,
                    boot_disk_mib = 20000,
                ),
                max_run_duration='3600s',
                max_retry_count=0,
                lifecycle_policies = [LifecyclePolicy(
                    action=LifecyclePolicy.Action.FAIL_TASK,
                    action_condition=LifecyclePolicy.ActionCondition(
                        exit_codes=[50005]
                    ),
                )],
            ),
            # parallelism=1,
            task_environments=self.prepare_job_envs(),
            # task_count_per_node=2,
        )
        job = Job(
            name=self.job_name, 
            priority=0,
            task_groups = [task_group],
            allocation_policy=AllocationPolicy(
                location=AllocationPolicy.LocationPolicy(
                    allowed_locations=["zones/europe-west1-d"]
                ),
                instances=[
                    AllocationPolicy.InstancePolicyOrTemplate(
                        policy=AllocationPolicy.InstancePolicy(
                            machine_type="n2-highmem-4",
                            provisioning_model=AllocationPolicy.ProvisioningModel.SPOT,
                            boot_disk=AllocationPolicy.Disk(
                                snapshot="compute-engine-monitoring-snapshot",
                                # type_="pd-standard",
                            )

                        ),
                        install_ops_agent=True,
                    ),

                ],
                labels=self.labels,
                network=AllocationPolicy.NetworkPolicy(
                    network_interfaces=[AllocationPolicy.NetworkInterface(
                        network="global/networks/default",
                        subnetwork=f"regions/{GCP_REGION}/subnetworks/default",
                    )]
                )
            ),
            labels=self.labels,
            logs_policy=LogsPolicy(
                destination=LogsPolicy.Destination.CLOUD_LOGGING
            ),
        )
        logging.info(job)

        return self.client.create_job(
            job=job,  
            parent=f"projects/{self.project_id}/locations/{self.region}",
            job_id=self.job_name
        )


    @property
    def carma_command(self) -> list[str]:
        """Get the command line interface for CARMA in gentropy."""
        return [
            "-c",
            (
                "uv run gentropy "
                "step=susie_finemapping "
                f"step.study_index_path={self.study_index_path} "
                f"step.study_locus_manifest_path={self.study_locus_manifest_path} "
                "step.study_locus_index=$LOCUS_INDEX "
                "step.max_causal_snps=10 "
                "step.lead_pval_threshold=1e-5 "
                "step.purity_mean_r2_threshold=0.25 "
                "step.purity_min_r2_threshold=0.25 "
                "step.cs_lbf_thr=2 step.sum_pips=0.95 "
                "step.susie_est_tausq=False "
                "step.run_carma=True "
                "step.run_sumstat_imputation=False "
                "step.carma_time_limit=3600 "
                "step.imputed_r2_threshold=0.9 "
                "step.ld_score_threshold=5 "
                "step.carma_tau=0.04 "
                "step.ld_min_r2=0.8 "
                "+step.session.extended_spark_conf={spark.jars:https://storage.googleapis.com/hadoop-lib/gcs/gcs-connector-hadoop3-latest.jar} "
                "+step.session.extended_spark_conf={spark.dynamicAllocation.enabled:false} "
                "+step.session.extended_spark_conf={spark.driver.memory:30g} "
                "+step.session.extended_spark_conf={spark.kryoserializer.buffer.max:500m} "
                "+step.session.extended_spark_conf={spark.driver.maxResultSize:5g} "
                "step.session.write_mode=overwrite"
            ),
        ]
    

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("-m", "--manifest-path", help="fine-mapping manifest path", required=True)
    parser.add_argument("-s", "--study-index-path", help="studyIndex path", required=True)
    args = parser.parse_args()
    main(**vars(args))