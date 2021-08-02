import json
import uuid
from datetime import datetime

import jwt
import requests
from werkzeug.security import generate_password_hash

try:
    from .testvars import (API_NAMESPACE, BASE_URL, JWT_ALGORITHMS,
                           PASSWORD_HASH_METHOD, SECRET_KEY, TEST_PASSWORD,
                           TEST_USERNAME)
except:
    from testvars import (API_NAMESPACE, BASE_URL, JWT_ALGORITHMS,
                          PASSWORD_HASH_METHOD, SECRET_KEY, TEST_PASSWORD,
                          TEST_USERNAME)

token_held = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJwdWJsaWNfaWQiOiJiYzhiMDE2OS02NzExLTRlOGMtODQwNi1lMGM1MTMzZDM0OGUiLCJleHAiOjE2Mjc3ODA1OTZ9.cpnGFq_ccJ-z5w9XDjRTlNruj5orQ6tS-oa6PrxoUgw"


def test_register_new_user():
    url = f"{BASE_URL}/{API_NAMESPACE}/register"
    data = json.dumps(
        {
            "username": "test_user_name",
            "password": "test_pword",
            "email": "moi@email.com",
        }
    )
    header = {"Content-Type": "application/json"}
    response = requests.post(url=url, headers=header, data=data)

    assert response.status_code == 200
    assert json.loads(response.text)["message"] == "registered successfully"


def get_token():
    url = f"{BASE_URL}/{API_NAMESPACE}/login"
    r = requests.get(url=url, auth=(TEST_USERNAME, TEST_PASSWORD))
    print("token", r.text)
    data = json.loads(r.text)

    token = data["token"]
    return token


def decode_token(token):
    decoded = jwt.decode(token, SECRET_KEY, algorithms=JWT_ALGORITHMS)
    print(decoded)
    ts = int(decoded["exp"])
    print(datetime.utcfromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S"))


def get_response(endpoint, data=None, method="get"):
    global token_held
    if token_held != "":
        token = token_held
    else:
        token = get_token()
    header = {"x-access-tokens": token, "Content-Type": "application/json"}
    url = f"{BASE_URL}/{API_NAMESPACE}/{endpoint}"

    response = make_request(url, method, header, data)
    if json.loads(response.text)["message"] == "token is invalid":
        print("bad token")
        token_held = get_token()
        header["x-access-tokens"] = token_held
        return make_request(url, method, header, data).text
    else:
        return response.text


def make_request(url, method, header, data):
    if method == "get":
        x = requests.get(url=url, headers=header, data=data)
    else:
        x = requests.post(url=url, headers=header, data=data)
    return x


def test_care_types():
    response = get_response("CareTypes")
    care_type_list = json.loads(response)
    care_type_item = [type for type in care_type_list if type["care_type_id"] == 13]
    test_case = care_type_item[0]
    assert len(care_type_list) >= 13
    assert test_case["sort"] == 13
    assert test_case["type"] == "Fertilizer Quarter"


def test_species():
    response = get_response("Species")
    species_list = json.loads(response)
    species_item = [type for type in species_list if type["species_id"] == 8]
    test_case = species_item[0]
    assert len(species_list) >= 25
    assert test_case["bot"] == "Peperomia prostrata"
    assert test_case["com"] == "String Of Turtles"


def test_history():
    response = get_response("UserHistory")
    history_list = json.loads(response)
    history_item = [care for care in history_list if care["history_id"] == 7]
    test_case = history_item[0]
    assert len(history_list) >= 25
    assert test_case["species"]["inventory_id"] == 1
    assert test_case["species"]["species"]["bot"] == "Alocasia Black Velvet"


def test_inventory():
    response = get_response("UserInventory")
    inventory_list = json.loads(response)
    #    print(inventory_list)
    inventory_item = [care for care in inventory_list if care["inventory_id"] == 31]
    test_case = inventory_item[0]
    assert len(inventory_list) >= 15
    assert test_case["species"]["bot"] == "Sansevieria Moonshine"


def test_new_inventory():
    url = f"{BASE_URL}/{API_NAMESPACE}/UserInventory"
    data = json.dumps(
        {
            "species_id": 1,
        }
    )
    response = get_response("UserInventory", data, "post")
    text = json.loads(response)
    print(text)
    assert text["message"] == "new inventory added"


def test_new_care():
    url = f"{BASE_URL}/{API_NAMESPACE}/UserHistory"
    data = json.dumps({"inventory_id": 1, "care_type_id": 11})
    response = get_response("UserHistory", data, "post")
    text = json.loads(response)
    print(text)
    assert text["message"] == "new plant care added"

