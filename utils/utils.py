import inspect


def get_current_function_name():
    stack = inspect.stack()
    caller_frame = stack[1]
    return caller_frame.frame.f_code.co_name


def get_base_url_by_job_name(json_data, job_name):
    for item in json_data:
        if item['job_name'] == job_name:
            return item['base_url']
    return None
