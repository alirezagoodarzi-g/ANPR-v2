import time


class DuplicateCache:

    def __init__(self, timeout_seconds=10):
        self.timeout = timeout_seconds
        self.cache = {}

    def is_duplicate(self, plate_number: str):

        current_time = time.time()

        if plate_number in self.cache:

            elapsed = current_time - self.cache[plate_number]

            if elapsed < self.timeout:
                return True

        self.cache[plate_number] = current_time

        return False