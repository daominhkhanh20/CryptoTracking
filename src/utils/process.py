import concurrent
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm
import time
import random
from src.processor.network import NetworkProcessor


def concurrent_process(func, list_params: list, num_workers: int = 2, **kwargs):
    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        futures = []
        for param in list_params:
            if isinstance(param, tuple) or isinstance(param, list):
                futures.append(
                    executor.submit(func, *param)
                )
            elif isinstance(param, dict):
                futures.append(
                    executor.submit(func, **param)
                )
            else:
                futures.append(
                    executor.submit(func, param)
                )
        results = []
        for future in tqdm(concurrent.futures.as_completed(futures), total=len(futures)):
            results.append(future.result())
            if kwargs.get('time_sleep', 0) > 0:
                time.sleep(random.uniform(0, kwargs.get('time_sleep', 0)))
        return results


def loop_request(network: NetworkProcessor, url: str, params: dict, header: dict, limit: int = 100):

    data = []
    params['start'] = 1
    while True:
        response = network.requests(url, params=params, headers=header)
        if len(response['data']) == 0:
            break
        if isinstance(response['data'], list):
            data.extend(response['data'])
        else: # dict type
            data.append(response['data'])

        params['start'] += limit
    return data


def iterative_process(func, list_params: list, **kwargs):
    for param in tqdm(list_params, total=len(list_params)):
        if isinstance(param, tuple) or isinstance(param, list):
            func(*param)
        elif isinstance(param, dict):
            func(**param)
        else:
            func(param)
        if kwargs.get('time_sleep', 0) > 0:
            time.sleep(kwargs.get('time_sleep'))
