import json
from pprint import pformat


def format_get_request(f):
    def wrapper(self,
                request):
        try:
            data = request.content.read()
            response_data = f(self, data)
            request.setHeader('Content-Type', 'application/json')
            response_raw = json.dumps(response_data).encode("utf-8")
            return response_raw
        except ValueError:
            request.setResponseCode(400)
            return "Invalid JSON data"

    return wrapper


def format_post_request(f):
    def wrapper(self,
                request):
        try:
            data = request.content.read()
            json_data = json.loads(data.decode("utf-8"))
            response_data = f(self, json_data)
            request.setHeader('Content-Type', 'application/json')
            response_raw = json.dumps(response_data).encode("utf-8")
            return response_raw
        except ValueError:
            request.setResponseCode(400)
            return "Invalid JSON data"

    return wrapper


class ToDict:

    def __repr__(self):
        return pformat(self.__dict__)

    def to_dict(self):
        return self.__dict__
