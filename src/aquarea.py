import requests
from urllib.parse import urlparse, parse_qsl
from bs4 import BeautifulSoup
import os

username = os.getenv('CLOUD_USERNAME')
assert username, 'missing env var CLOUD_USERNAME'
password = os.getenv('CLOUD_PASSWORD')
assert password, 'missing env var CLOUD_PASSWORD'

_HEADERS = {
    "Cache-Control": "max-age=0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Encoding": "deflate, br",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:74.0) Gecko/20100101 Firefox/74.0",
}


def login(session: requests.Session) -> str:
    res = session.post(
        "https://aquarea-smart.panasonic.com/remote/v1/api/auth/login",
        headers=_HEADERS
        | {
            "Referer": "https://aquarea-smart.panasonic.com/",
            "Popup-Screen-Id": "1001",
            "Registration-Id": "",
        },
        timeout=60,
    )
    assert res.status_code == 200, res.text

    res_data = res.json()
    assert res_data["errorCode"] == 0

    authorize_url = res_data["authorizeUrl"]
    assert authorize_url

    res = session.get(authorize_url, headers=_HEADERS, allow_redirects=True, timeout=60)
    assert res.status_code == 200, res.text

    oauth2_params = dict(parse_qsl(urlparse(res.url).query))

    csrf_token = session.cookies.get("_csrf")

    res = session.post(
        "https://authglb.digital.panasonic.com/usernamepassword/login",
        json={
            "_csrf": csrf_token,
            "_intstate": "deprecated",
            "audience": oauth2_params["audience"],
            "client_id": oauth2_params["client"],
            "connection": "PanasonicID-Authentication",
            "lang": "en",
            "password": password,
            "redirect_uri": "https://aquarea-smart.panasonic.com/authorizationCallback?lang=en",
            "response_type": oauth2_params["response_type"],
            "scope": oauth2_params["scope"],
            "state": oauth2_params["state"],
            "tenant": "pdpauthglb-a1",
            "username": username,
        },
        headers=_HEADERS
        | {"Auth0-Client": "eyJuYW1lIjoiYXV0aDAuanMtdWxwIiwidmVyc2lvbiI6IjkuMjMuMiJ9"},
        timeout=60,
    )

    assert res.status_code == 200, res.text

    soup = BeautifulSoup(res.text, features="html.parser")

    callback_url = soup.find("form").get("action")
    params = {
        elem.get("name"): elem.get("value")
        for elem in soup.find_all("input")
        if elem.get("type") != "submit"
    }

    res = session.post(
        callback_url, json=params, allow_redirects=True, headers=_HEADERS, timeout=60
    )
    assert res.status_code == 200, res.text

    access_token = session.cookies.get("accessToken")
    assert access_token, res.text

    res = session.post(
        "https://aquarea-smart.panasonic.com/remote/contract",
        headers=_HEADERS,
        data={"Registration-ID": ""},
        timeout=60,
    )
    assert res.status_code == 200, res.text

    device_id = session.cookies.get("selectedDeviceId")
    assert device_id, res.text


def get_device_status(session: requests.Session):
    device_id = session.cookies.get("selectedDeviceId")

    res = session.get(
        f"https://aquarea-smart.panasonic.com/remote/v1/api/devices/{device_id}",
        params={"var.deviceDirect": "1"},
        headers=_HEADERS,
        timeout=60,
    )
    assert res.status_code == 200, res.text
    res_data = res.json()
    assert res_data["errorCode"] == 0
    assert res_data["accessToken"]

    status = res_data["status"][0]

    return status


def get_device_consumption(session: requests.Session, date: str):
    device_id = session.cookies.get("selectedDeviceId")
    res = session.get(
        f"https://aquarea-smart.panasonic.com/remote/v1/api/consumption/{device_id}",
        params={"date": date},
        headers=_HEADERS,
        timeout=60,
    )
    assert res.status_code == 200, res.text
    res_data = res.json()
    assert res_data["errorCode"] == 0
    assert res_data["accessToken"]

    assert res_data["dateData"][0]["startDate"] == date

    consumption = res_data["dateData"][0]["dataSets"]
    return consumption
