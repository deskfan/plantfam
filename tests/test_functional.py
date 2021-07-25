import json
import uuid
from datetime import datetime

import jwt
import requests
from werkzeug.security import generate_password_hash

from ..credentials import (
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
    url = "http://127.0.0.1:5000/plantfam/login"
    r = requests.get(url=url, auth=(TEST_USERNAME, TEST_PASSWORD))
    data = json.loads(r.text)
    token = data["token"]
    return token


def get_response(endpoint):
    token = get_token()
    header = {"x-access-tokens": token}
    url = f"http://127.0.0.1:5000/plantfam/{endpoint}"
    x = requests.get(url=url, headers=header)
    return x.text


def test_care_types():
    x = get_response("CareTypes")
    y = [type for type in x if type["care_type_id"] == 13]
    return y


def test_species(token):

    header = {"x-access-tokens": token}
    url = "http://127.0.0.1:5000/plantfam/Species"
    x = requests.get(url=url, headers=header)

    return x.text


def decode_token(token):

    decoded = jwt.decode(token, SECRET_KEY, algorithms=JWT_ALGORITHMS)
    print(decoded)
    ts = int(decoded["exp"])
    print(datetime.utcfromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S"))


# token = get_token()
# print(token)
# decode_token(token)

x = test_care_types()
print(x)
print("hello")
