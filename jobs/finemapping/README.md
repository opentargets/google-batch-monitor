# Testing cloud usage via googlecloudprofiler

This approach relies on looking if the [`googlecloudprofiler`](https://cloud.google.com/profiler/docs/selecting-profiles) can estimate the CPU and memory usage of local pyspark job submited to the VM machine.


## main.py

The script relies on the installation of `gentropy` and `loguru` packages - see `pyproject.toml` for all dependencies.
To run the profiling run:


