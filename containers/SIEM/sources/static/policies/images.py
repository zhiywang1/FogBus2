class ImagesPolicy:
    def __init__(self):
        self.valid_images = set(self.get_valid_images())

    @staticmethod
    def get_valid_images():
        with open('valid_images.list', 'r') as f:
            return [line.strip() for line in f.readlines()]

    def apply(self,
              data):
        got_images = set(data['data'])
        not_valid = got_images.difference(self.valid_images)
        if len(not_valid):
            body = '\r\n'.join(not_valid)
            return '[WARNING] Unrecognized image', body
        return None, None
