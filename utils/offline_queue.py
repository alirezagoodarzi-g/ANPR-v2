import json
import os


class OfflineQueue:

    def __init__(
        self,
        file_path,
        max_size=1000
    ):

        self.file_path = file_path
        self.max_size = max_size

        os.makedirs(
            os.path.dirname(file_path),
            exist_ok=True
        )

        if not os.path.exists(file_path):

            with open(file_path, "w") as f:
                json.dump([], f)

    def load(self):

        with open(self.file_path, "r") as f:
            return json.load(f)

    def save(self, data):

        with open(self.file_path, "w") as f:
            json.dump(data, f, indent=4)

    def add(self, payload):

        queue = self.load()

        queue.append(payload)

        if len(queue) > self.max_size:

            queue = queue[-self.max_size:]

        self.save(queue)

    def remove_first(self):

        queue = self.load()

        if not queue:
            return None

        item = queue.pop(0)

        self.save(queue)

        return item

    def size(self):

        return len(self.load())