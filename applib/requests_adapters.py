from requests.adapters import HTTPAdapter


class TimeoutHTTPAdapter(HTTPAdapter):
    def __init__(self, *args, force=False, **kwargs):
        self.force = force
        if "timeout" in kwargs:
            self.timeout = kwargs["timeout"]
            del kwargs["timeout"]
        super().__init__(*args, **kwargs)

    def send(self, request, **kwargs):
        timeout = kwargs.get("timeout")
        if hasattr(self, 'timeout') and (timeout is None or self.force):
            kwargs["timeout"] = self.timeout

        return super().send(request, **kwargs)
