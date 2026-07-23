from concurrent.futures import ThreadPoolExecutor
from functools import lru_cache
import os


@lru_cache(maxsize=1)
def get_inference_executor():
    workers = int(os.getenv("INFERENCE_WORKERS", "2"))
    return ThreadPoolExecutor(max_workers=max(1, workers), thread_name_prefix="hiresense-inference")
