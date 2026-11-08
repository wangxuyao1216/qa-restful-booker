from api.base import BaseAPI


class BookingAPI(BaseAPI):
    """booking 资源的五个接口。

    改和删需要 Cookie: token=xxx，这是 restful-booker 的设计，
    所以 update/delete 显式接收 token 参数，不在类内部偷偷维护状态。
    """

    def list(self, **params):
        return self.request("GET", "/booking", params=params or None)

    def get(self, booking_id: int):
        return self.request("GET", f"/booking/{booking_id}")

    def create(self, payload: dict):
        return self.request("POST", "/booking", json=payload)

    def update(self, booking_id: int, payload: dict, token: str):
        return self.request(
            "PUT",
            f"/booking/{booking_id}",
            json=payload,
            headers={"Cookie": f"token={token}"},
        )

    def delete(self, booking_id: int, token: str):
        return self.request(
            "DELETE",
            f"/booking/{booking_id}",
            headers={"Cookie": f"token={token}"},
        )
