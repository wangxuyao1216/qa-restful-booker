from api.base import BaseAPI


class HealthAPI(BaseAPI):
    def ping(self):
        return self.request("GET", "/ping")
