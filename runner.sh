set -x
time1=$(date +%s.%N)
# Mount point for the relevant Google Cloud bucket.
export MOUNT_ROOT=/mnt/share
# Create directory for logs, if necessary.
export LOG_DIR=${MOUNT_ROOT}/logs/${BATCH_ID}
mkdir -p ${LOG_DIR}
# Redirect all subsequent logs.
# The $BATCH_TASK_INDEX variable is set by Google Batch.
exec &> ${LOG_DIR}/${BATCH_TASK_INDEX}.log
# Establish dependency installation lock.
while ! mkdir /tmp/install.lock 2>/dev/null; do
    sleep 0.5
done
export HOME=/tmp/home
mkdir -p $HOME
if ! [ -d /tmp/dependencies_installed ]; then
    sudo fallocate -l 32G /swapfile && sudo chmod 600 /swapfile && sudo mkswap /swapfile && sudo swapon /swapfile && echo '/swapfile   none    swap    sw    0   0' | sudo tee -a /etc/fstab > /dev/null
    sudo apt -y update
    sudo apt install -y bc
    sudo apt install -y curl git gcc make libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev libffi-dev default-jdk
    curl https://pyenv.run | bash
fi
export PATH="$HOME/.pyenv/bin:$PATH"
eval "$(pyenv init --path)"
if ! (grep 3.10.11 <(pyenv versions)); then
    pyenv install 3.10.11
fi
pyenv global 3.10.11
if ! [ -d /tmp/dependencies_installed ]; then
    python3 -m ensurepip
    python3 -m pip install --upgrade pip setuptools
    python3 -m pip install git+https://github.com/opentargets/gentropy@dev
fi
# Mark dependency installation complete
mkdir -p /tmp/dependencies_installed
# Release dependency installation lock.
rmdir /tmp/install.lock

time2=$(date +%s.%N)
python3 ${MOUNT_ROOT}/code/run_finemapping.py ${BATCH_TASK_INDEX} 2>&1 | tee /tmp/python.${BATCH_TASK_INDEX}.log
export RETURNCODE=${PIPESTATUS[0]}

time3=$(date +%s.%N)
echo "!!! Returncode ${RETURNCODE} Index ${BATCH_TASK_INDEX} Overhead $(echo "$time2 - $time1" | bc) Execution $(echo "$time3 - $time2" | bc)"

if [ ${RETURNCODE} == 0 ]; then
    echo "All good, exit as 0"
    exit 0
fi

if (grep "requests.exceptions.ConnectionError" /tmp/python.${BATCH_TASK_INDEX}.log &>/dev/null); then
    echo "Sporadic error, exit as 37 and retry"
    exit 37
fi

if (grep "ERROR SparkContext: Error initializing SparkContext" /tmp/python.${BATCH_TASK_INDEX}.log &>/dev/null); then
    echo "Sporadic error, exit as 37 and retry"
    exit 37
fi

echo "Unexpected error, exit as 73, so that the task is NOT restarted"
exit 73
