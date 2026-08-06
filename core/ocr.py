class PlateOCR:

    def __init__(self, model):
        self.model = model

    def read_text(self, image):

        try:

            result = self.model.predict(image)

            texts = []

            for item in result:

                if "text" in item:
                    texts.append(item["text"][::-1])

            if not texts:
                return None

            return texts[0]

        except Exception:
            return None