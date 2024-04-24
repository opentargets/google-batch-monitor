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
    sudo apt -y update
    sudo apt install -y bc
    sudo apt install -y curl git gcc make libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev libffi-dev default-jdk
    curl https://pyenv.run | bash
fi
export PATH="$HOME/.pyenv/bin:$PATH"
eval "$(pyenv init --path)"
if ! [ -d /tmp/dependencies_installed ]; then
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
python3 ${MOUNT_ROOT}/code/hello_world.py ${BATCH_TASK_INDEX}
export RETURNCODE=$?

time3=$(date +%s.%N)
echo "!!! Returncode ${RETURNCODE} Index ${BATCH_TASK_INDEX} Overhead $(echo "$time2 - $time1" | bc) Execution $(echo "$time3 - $time2" | bc)"
exit ${RETURNCODE}
