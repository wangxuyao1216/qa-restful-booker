import pytest
from conftest import load_case, BASE_PAYLOAD

CREATE_CASES = load_case("create")


@pytest.mark.parametrize("case", CREATE_CASES, ids=[c["case"] for c in CREATE_CASES])
def test_create_booking(api, base_url, created_ids, case):
    r = api.post(f"{base_url}/booking", json=case["payload"])
    assert r.status_code == 200, r.text
    body = r.json()
    created_ids.append(body["bookingid"])
    assert isinstance(body["bookingid"], int)
    assert body["booking"]["firstname"] == case["payload"]["firstname"]
    assert body["booking"]["totalprice"] == case["payload"]["totalprice"]

@pytest.mark.smoke
def test_get_booking_by_id(api, base_url, booking_id):
    r = api.get(f"{base_url}/booking/{booking_id}")
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["firstname"] == BASE_PAYLOAD["firstname"]
    assert body["totalprice"] == BASE_PAYLOAD["totalprice"]
    assert body["bookingdates"]["checkin"] == BASE_PAYLOAD["bookingdates"]["checkin"]


@pytest.mark.smoke
def test_get_booking_list(api, base_url, booking_id):
    r = api.get(f"{base_url}/booking")
    assert r.status_code == 200, r.text
    data = r.json()
    assert isinstance(data, list) and len(data) > 0
    assert set(data[0].keys()) == {"bookingid"}          # 列表页不返回明细
    assert any(i["bookingid"] == booking_id for i in data)


def test_filter_by_firstname(api, base_url, booking_id):
    r = api.get(f"{base_url}/booking", params={"firstname": BASE_PAYLOAD["firstname"]})
    assert r.status_code == 200, r.text
    assert any(i["bookingid"] == booking_id for i in r.json())

def test_update_booking(api, base_url, booking_id, token):
    payload = {**BASE_PAYLOAD, "firstname": "Updated", "totalprice": 222}
    r = api.put(f"{base_url}/booking/{booking_id}", json=payload,
                headers={"Cookie": f"token={token}"})
    assert r.status_code == 200, r.text
    assert r.json()["firstname"] == "Updated"

    again = api.get(f"{base_url}/booking/{booking_id}")
    assert again.json()["firstname"] == "Updated"
    assert again.json()["totalprice"] == 222      # 真落库了，不只是回显

def test_delete_booking(api, base_url, token):
    r = api.post(f"{base_url}/booking", json={**BASE_PAYLOAD, "firstname": "Del"})
    bid = r.json()["bookingid"]
    d = api.delete(f"{base_url}/booking/{bid}", headers={"Cookie": f"token={token}"})
    assert d.status_code == 201, d.text           # 注意是 201，不是 204
    assert api.get(f"{base_url}/booking/{bid}").status_code == 404