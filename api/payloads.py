"""POST /booking 的请求体模板。

真实项目里这类数据要从 YAML 读（第 2 周会迁到 data/booking.yaml），
这里先给一个函数，是为了让第 1 周的用例能跑起来，同时不把字典散落在用例里。
"""

BOOKING_PAYLOAD = {
    "firstname": "Jim",
    "lastname": "Brown",
    "totalprice": 111,
    "depositpaid": True,
    "bookingdates": {"checkin": "2027-01-01", "checkout": "2027-01-05"},
    "additionalneeds": "Breakfast",
}


def booking_payload(**overrides) -> dict:
    """返回一份默认请求体，可用关键字参数覆盖任意字段。"""
    data = {
        **BOOKING_PAYLOAD,
        "bookingdates": dict(BOOKING_PAYLOAD["bookingdates"]),
    }
    data.update(overrides)
    return data
