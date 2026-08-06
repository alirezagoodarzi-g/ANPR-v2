import time


class RetryWorker:

    def __init__(
        self,
        api_client,
        queue,
        logger,
        retry_interval=10
    ):

        self.api_client = api_client
        self.queue = queue
        self.logger = logger
        self.retry_interval = retry_interval

    def start(self):

        while True:

            try:

                queue_size = self.queue.size()

                if queue_size > 0:

                    self.logger.info(
                        f"Retry queue size: "
                        f"{queue_size}"
                    )

                    payload = self.queue.remove_first()

                    if payload:

                        self.api_client.send_plate(
                            payload
                        )

                        self.logger.info(
                            "Cached payload resent"
                        )

            except Exception as e:

                self.logger.error(
                    f"Retry worker error: {e}"
                )

            time.sleep(self.retry_interval)