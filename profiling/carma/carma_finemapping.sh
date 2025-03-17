#!/bin/bash
# This script runs the fine-mapping step of the CARMA pipeline using the gentropy tool.
# The script assumes that the following environment variables are set:
# - STUDY_INDEX_PATH: The path to the study index file.
# - STUDY_LOCUS_MANIFEST_PATH: The path to the study locus manifest file.
# - LOCUS_INDEX: The index of the locus to be fine-mapped.
# The script assumes that there is gcloud installed.
# The script installs the following tools:
# - curl
# - unzip
# - zip
# - git
# - uv (including python3)
# - sdkman (including JAVA)

export HOME=$PWD
export DIR="gentropy"


function prepare_gentropy {
    mkdir -p gentropy
	git clone https://github.com/opentargets/gentropy.git gentropy
    (cd gentropy && git checkout v2.2.0 && uv sync --frozen)
}


function install_libs {
    sudo apt install unzip zip git curl -y
}


function install_java {
    curl -s "https://get.sdkman.io" | bash
    source "$HOME/.sdkman/bin/sdkman-init.sh"
    sdk install java 11.0.26-amzn -y && sdk default java 11.0.26-amzn
}

function install_uv {
    curl -LsSf https://astral.sh/uv/install.sh | sh
}



function run_carma {
    . $HOME/.local/bin/env
    source "$HOME/.sdkman/bin/sdkman-init.sh"
    export JAVA_HOME=$(sdk home java 11.0.26-amzn)
    cd gentropy
    uv run gentropy \
        step=susie_finemapping \
        step.study_index_path=${STUDY_INDEX_PATH} \
        step.study_locus_manifest_path=${STUDY_LOCUS_MANIFEST_PATH} \
        step.study_locus_index=$LOCUS_INDEX \
        step.max_causal_snps=10 \
        step.lead_pval_threshold=1e-5 \
        step.purity_mean_r2_threshold=0.25 \
        step.purity_min_r2_threshold=0.25 \
        step.cs_lbf_thr=2 step.sum_pips=0.95 \
        step.susie_est_tausq=False \
        step.run_carma=True \
        step.run_sumstat_imputation=False \
        step.carma_time_limit=3600 \
        step.imputed_r2_threshold=0.9 \
        step.ld_score_threshold=5 \
        step.carma_tau=0.04 \
        step.ld_min_r2=0.8 \
        +step.session.extended_spark_conf="{spark.jars:https://storage.googleapis.com/hadoop-lib/gcs/gcs-connector-hadoop3-latest.jar}" \
        +step.session.extended_spark_conf="{spark.dynamicAllocation.enabled:false}" \
        +step.session.extended_spark_conf="{spark.driver.memory:15g}" \
        +step.session.extended_spark_conf="{spark.kryoserializer.buffer.max:500m}" \
        +step.session.extended_spark_conf="{spark.driver.maxResultSize:2g}" \
        step.session.write_mode=overwrite
}


function main() {
    if [ ! -d "${DIR}" ]; then
        echo $DIR
        # In case the directory does not exist we are in the fresh VM and need to install the tools
        install_libs
        install_java
        install_uv
        prepare_gentropy
    fi
    run_carma
}


main
