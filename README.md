# qa-restful-booker

基于 pytest + requests 的接口自动化测试框架，被测系统为开源靶场 [restful-booker](https://github.com/mwinteringham/restful-booker)。

## 技术栈

- Python 3.13 + pytest 9
- requests（HTTP 会话复用）
- PyYAML（测试数据外部化）
- jsonschema（响应结构契约校验）
- allure-pytest（测试报告）
- GitHub Actions（CI，提交即跑）

## 设计要点

- **三层分离**：`api/` 封装请求、`data/` 存测试数据、`tests/` 只写断言，`tests/` 内不出现任何 URL
- **数据驱动**：用例数据全部在 `data/booking.yaml`，新增一组数据无需改动 `.py`，用例数自动增加
- **用例可重复执行**：`created_ids` fixture 在用例结束时清理造出的数据，连续运行多次库内数据量不增长
- **fixture 分层**：`base_url` / `api` / `token` 为 session 级（一轮只初始化一次），业务数据相关 fixture 为 function 级（用例间互不污染）

## 目录结构

```
qa-restful-booker/
├── conftest.py              # 全局 fixture：base_url / api session / token
├── api/
│   ├── base.py              # 请求基类：URL 拼接、超时、日志、状态码断言
│   ├── auth_api.py          # POST /auth
│   ├── booking_api.py       # booking 资源 CRUD
│   └── payloads.py          # 请求体模板
├── data/                    # 测试数据（YAML）
├── schemas/                 # JSON Schema
├── tests/
│   ├── test_auth.py         # 鉴权用例
│   └── ...
├── pytest.ini
├── requirements.txt
└── .github/workflows/       # CI
```

分层原则：**用例层只写业务断言，URL 与数据不许出现在 tests/ 里。**

## 快速开始

### 1. 启动被测服务

```bash
git clone https://github.com/mwinteringham/restful-booker.git
cd restful-booker
docker compose up -d
curl -i http://localhost:3001/ping     # 期望 HTTP/1.1 201 Created
```

### 2. 安装依赖

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements.txt
```

### 3. 运行测试

```bash
pytest                          # 全量
pytest -m smoke                 # 只跑冒烟
pytest -m negative              # 只跑异常用例
BASE_URL=http://其他地址 pytest  # 换被测环境
```

### 4. 查看报告

```bash
pytest --alluredir=allure-results
allure serve allure-results
```

## 设计说明

**为什么分 api / tests 两层**
URL、请求头、超时、日志统一收在 `api/base.py`。换域名或加统一签名只改一处，几十条用例不用动。

**为什么 fixture 用 session 级**
`api` 复用 TCP 连接；`token` 整个会话只登录一次，避免每条用例都打 `/auth`。代价是 token 失效会影响后续用例，这类场景单独写函数级 fixture 覆盖。

**为什么断言要看真实响应，不按直觉写**
`/auth` 密码错误时返回的是 `200` + `{"reason": "Bad credentials"}`，而不是 `401`。用例按接口真实行为断言，否则测试会假绿。

## 用例清单

| 用例 | 覆盖点 | 类型 |
|---|---|---|
| test_auth.py::3 条 | 正确凭证取 token / 错误凭证 / token 格式 | 正向 + 异常 |
| test_create_booking（4 组参数化） | 标准数据、仅必填、中文长文本、零价格最短行程 | 正向 |
| test_get_booking_by_id | 单条查询字段与创建时一致 | 正向 |
| test_get_booking_list | 列表仅返回 bookingid，无明细 | 正向 |
| test_filter_by_firstname | 按姓名筛选命中 | 正向 |
| test_update_booking | PUT 全量替换 + 复查落库 | 正向 |
| test_delete_booking | DELETE 返回 201，删后 GET 404 | 正向 |

共 12 条，全部通过。运行：`pytest -v`

## 进度

- [x] 骨架搭建：目录分层、请求基类、三个 fixture
- [x] 鉴权用例（ping / 登录成功 / 登录失败）
- [x] booking CRUD 正向用例 + YAML 参数化
- [ ] 异常用例（缺字段、类型错误、越权、不存在 id）+ JSON Schema
- [ ] Allure 报告 + GitHub Actions
