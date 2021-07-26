import json
import uuid
from datetime import datetime

import jwt
import requests
from werkzeug.security import generate_password_hash

from .testvars import (
    API_NAMESPACE,
    BASE_URL,
    JWT_ALGORITHMS,
    PASSWORD_HASH_METHOD,
    SECRET_KEY,
    TEST_PASSWORD,
    TEST_USERNAME,
)


def user_setup(password):
    public_id = str(uuid.uuid4())
    hashed_password = generate_password_hash(password, method=PASSWORD_HASH_METHOD)
    return (public_id, hashed_password)


def get_token():
    url = f"{BASE_URL}/{API_NAMESPACE}/login"
    r = requests.get(url=url, auth=(TEST_USERNAME, TEST_PASSWORD))
    data = json.loads(r.text)
    token = data["token"]
    return token


def get_response(endpoint):
    token = get_token()
    header = {"x-access-tokens": token}
    url = f"{BASE_URL}/{API_NAMESPACE}/{endpoint}"
    x = requests.get(url=url, headers=header)
    return x.text


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


def decode_token(token):

    decoded = jwt.decode(token, SECRET_KEY, algorithms=JWT_ALGORITHMS)
    print(decoded)
    ts = int(decoded["exp"])
    print(datetime.utcfromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S"))
