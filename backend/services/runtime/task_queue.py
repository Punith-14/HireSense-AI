import importlib
import os

from backend.celery import celery_app
from services.runtime.task_executor import get_inference_executor


@celery_app.task(bind=True)
def execute_callable(self, dotted_path, args, kwargs):
    module_name, func_name = dotted_path.rsplit(".", 1)
    module = importlib.import_module(module_name)
    func = getattr(module, func_name)
    return func(*args, **kwargs)


def submit_background(func, *args, **kwargs):
    if os.getenv("CELERY_ENABLED", "False").lower() == "true":
        dotted_path = f"{func.__module__}.{func.__name__}"
        return execute_callable.delay(dotted_path, args, kwargs)
    executor = get_inference_executor()
    return executor.submit(func, *args, **kwargs)
