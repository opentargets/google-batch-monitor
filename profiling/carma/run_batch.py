"""Script for running google batch fine-mapping job.

This script invokes the `google-batch` job with the script `carma_finemapping.sh` that is mounted to the `/mnt/share/carma_finemapping.sh`
to the host VMs running in batch tasks. To sync the scrip to the google cloud storage (correct location ) - run `make send-carma-finemapping-script`

To run this script run
`uv sync --frozen`
`uv run profiling/carma/run_batch.py -m gs://ot_orchestration/profiling/carma_ukb_ppp/finemapping_manifests/100_sample.csv -s gs://ukb_ppp_eur_data/study_index`

To see the results inside the google cloud monitoring - see the dashboard prepared in
https://console.cloud.google.com/monitoring/dashboards/builder/e87aa472-e2ec-46d0-8218-fea6385f3bfc;filters=type:umlabel,key:benchmark,val:100-sample;startTime=2025-03-17T16:19:39.846Z;endTime=2025-03-17T16:42:49.120Z?hl=en&inv=1&invt=AbsSoQ&project=open-targets-genetics-dev
"""

from argparse import ArgumentParser
import pandas as pd

from google.cloud.batch_v1 import (
    Job,
    LifecyclePolicy,
    BatchServiceClient,
    Runnable,
    TaskSpec,
    ComputeResource,
    TaskGroup,
    AllocationPolicy,
    LogsPolicy,
    GCS,
    Volume,
    Environment,
)
import logging
import datetime

GENTROPY_VERSION = "v2.2.0-rc.6"
JOB_NAME = (
    f"carma-profiling-gentropy-{datetime.datetime.now().strftime('%Y-%m-%d-%H%M')}"
)
GCP_PROJECT_GENETICS = "open-targets-genetics-dev"
GCP_REGION = "europe-west1"
GCP_ZONE = "europe-west1-d"
IMAGE_URI = f"europe-west1-docker.pkg.dev/open-targets-genetics-dev/gentropy-app/gentropy:{GENTROPY_VERSION.removeprefix('v')}"

logging.basicConfig(level=logging.INFO)


def main(**kwargs) -> None:
    for k, v in kwargs.items():
        logging.info(f"Using {k}: {v}")
        print(JOB_NAME)
    FinemappinJob(
        GCP_PROJECT_GENETICS,
        GCP_REGION,
        JOB_NAME,
        kwargs["study_index_path"],
        kwargs["manifest_path"],
    )._job()


class FinemappinJob:
    def __init__(
        self,
        project_id: str,
        region: str,
        job_name: str,
        study_index_path: str,
        study_locus_manifest_path: str,
    ):
        self.project_id = project_id
        self.region = region
        self.job_name = job_name
        self.study_index_path = study_index_path
        self.study_locus_manifest_path = study_locus_manifest_path
        self.remote_script_path = (
            "gs://ot_orchestration/test/ukb_ppp_eur_data/carma_finemapping.sh"
        )
        self.local_script_path = "/mnt/share/carma_finemapping.sh"
        self.remote_name = "ot_orchestration/test/ukb_ppp_eur_data/"
        benchmark = (
            self.study_locus_manifest_path.split("/")[-1]
            .removesuffix(".csv")
            .replace("_", "-")
        )
        self.labels = {
            "tool": "batch-job-monitor",
            "environment": "development",
            "subteam": "genetics",
            "team": "open-targets",
            "benchmark": benchmark,
            "google-cloud-ops-agent-enabled": "yes",
        }
        self.job_name = job_name + "-" + benchmark

        self.client = BatchServiceClient()

    def prepare_job_envs(self) -> list[Environment]:
        manifest = pd.read_csv(self.study_locus_manifest_path)
        n_tasks = len(manifest)
        tasks = list(range(0, n_tasks))
        return [
            Environment(
                variables={
                    "LOCUS_INDEX": str(i),
                    "STUDY_INDEX_PATH": self.study_index_path,
                    "STUDY_LOCUS_MANIFEST_PATH": self.study_locus_manifest_path,
                }
            )
            for i in tasks
        ]

    def _job(self) -> Job:
        # Define what will be done as part of the job.
        task_group = TaskGroup(
            task_spec=TaskSpec(
                runnables=[
                    Runnable(
                        script=Runnable.Script(text=f"bash {self.local_script_path}")
                    )
                ],
                compute_resource=ComputeResource(
                    cpu_milli=2000,
                    memory_mib=16000,
                    boot_disk_mib=1000,
                ),
                max_run_duration="3600s",
                max_retry_count=0,
                lifecycle_policies=[
                    LifecyclePolicy(
                        action=LifecyclePolicy.Action.FAIL_TASK,
                        action_condition=LifecyclePolicy.ActionCondition(
                            exit_codes=[50005]
                        ),
                    )
                ],
                volumes=[
                    Volume(
                        gcs=GCS(remote_path=self.remote_name), mount_path="/mnt/share"
                    )
                ],
            ),
            # Run 30 machines at the time with 2 job at a time.
            parallelism=30,
            task_environments=self.prepare_job_envs(),
            task_count_per_node=1,
        )
        job = Job(
            name=self.job_name,
            priority=0,
            task_groups=[task_group],
            allocation_policy=AllocationPolicy(
                location=AllocationPolicy.LocationPolicy(
                    allowed_locations=["zones/europe-west1-d"]
                ),
                instances=[
                    AllocationPolicy.InstancePolicyOrTemplate(
                        policy=AllocationPolicy.InstancePolicy(
                            machine_type="n2-highmem-2",  # 8G memory 2 CPU
                            provisioning_model=AllocationPolicy.ProvisioningModel.SPOT,
                            boot_disk=AllocationPolicy.Disk(
                                snapshot="compute-engine-monitoring-snapshot",
                            ),
                        ),
                        install_ops_agent=True,
                    ),
                ],
                labels=self.labels,
                network=AllocationPolicy.NetworkPolicy(
                    network_interfaces=[
                        AllocationPolicy.NetworkInterface(
                            network="global/networks/default",
                            subnetwork=f"regions/{GCP_REGION}/subnetworks/default",
                        )
                    ]
                ),
            ),
            labels=self.labels,
            logs_policy=LogsPolicy(destination=LogsPolicy.Destination.CLOUD_LOGGING),
        )
        logging.info(job)

        return self.client.create_job(
            job=job,
            parent=f"projects/{self.project_id}/locations/{self.region}",
            job_id=self.job_name,
        )


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument(
        "-m", "--manifest-path", help="fine-mapping manifest path", required=True
    )
    parser.add_argument(
        "-s", "--study-index-path", help="studyIndex path", required=True
    )
    args = parser.parse_args()
    main(**vars(args))
