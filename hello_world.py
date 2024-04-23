import gentropy
import time
import sys

batch_task_index = sys.argv[1]
print(f"I am worker for task # {batch_task_index}")
time.sleep(30)
