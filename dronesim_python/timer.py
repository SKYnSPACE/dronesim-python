import time

class Timer:
    def __init__(self):
        self.start_time = time.perf_counter();
        
    def elapsed_time(self):
        return time.perf_counter() - self.start_time;

# This creates a global Timer instance that can be imported and used anywhere. (Singleton pattern)
timer = Timer();