import time
import numpy as np

def my_decorator(function):
    times = []   # an array to store times
    def wrapper(*args, **kwargs):
        start = time.time()
        result = function(*args, **kwargs)  # call the decorated function
        end = time.time()
        times.append(end - start)
        return result
    
    def get_stats():
        print(np.round(sorted(times), 3))
        return f'Mean: {np.round(np.mean(times), 3)}, std: {np.round(np.std(times), 3)}, min: {np.round(np.min(times), 3)}, max: {np.round(np.max(times), 3)}, median: {np.round(np.median(times), 3)}'

    wrapper.get_stats = get_stats   # set an attribute to a wrapper
    return wrapper

@my_decorator
def my_function():
    A = np.random.rand(1000, 1000)
    B = np.random.rand(1000, 1000)
    C = np.dot(A, B)
    return C

for i in range(10):
    my_function()

print(my_function.get_stats())