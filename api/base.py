"""接口层基类：所有请求从这里出去。

这一层的存在意义（面试必答）：
- 用例层不该关心 URL 怎么拼、超时几秒、日志怎么打、断言长什么样。
- 一处改动（比如更换域名、加统一 header、加签名）只改这里，几十条用例不用动。
"""

import logging

import requests

log = logging.getLogger(__name__)


class BaseAPI:
    def __init__(self, session: requests.Session, base_url: str, timeout: int = 10):
        self.s = session
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def request(self, method: str, path: str, **kwargs) -> requests.Response:
        """统一发请求：补全 URL、设置超时、记录请求与响应日志。"""
        url = f"{self.base_url}{path}"
        kwargs.setdefault("timeout", self.timeout)

        log.info("--> %s %s | json=%s | params=%s", method, url, kwargs.get("json"), kwargs.get("params"))
        resp = self.s.request(method, url, **kwargs)
        log.info("<-- %s %s | %s", resp.status_code, resp.reason, resp.text[:300])
        return resp

    @staticmethod
    def expect(resp: requests.Response, code: int) -> requests.Response:
        """状态码断言。单独抽出来，是为了报错信息里能带响应体。"""
        assert resp.status_code == code, (
            f"期望状态码 {code}，实际 {resp.status_code}，响应体: {resp.text}"
        )
        return resp
