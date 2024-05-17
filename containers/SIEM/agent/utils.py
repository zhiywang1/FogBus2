import json


def check_post_data(f):
    def wrapper(self,
                request):
        try:
            data = request.content.read()
            json_data = json.loads(data)
            response_data = f(self, json_data)
            request.setHeader('Content-Type', 'application/json')
            response_raw = json.dumps(response_data).encode("utf-8")
            return response_raw
        except ValueError:
            request.setResponseCode(400)
            return "Invalid JSON data"

    return wrapper
