from api.base import BaseAPI


class AuthAPI(BaseAPI):
    """POST /auth —— 用户名密码换 token。"""

    def login(self, username: str, password: str):
        return self.request(
            "POST", "/auth", json={"username": username, "password": password}
        )
