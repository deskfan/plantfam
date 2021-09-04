import datetime
import os
import uuid
from functools import wraps

import jwt
from flask import Flask, jsonify, make_response, request
from flask_restx import Api, Resource, fields
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from werkzeug.middleware.proxy_fix import ProxyFix
from werkzeug.security import check_password_hash, generate_password_hash

from classes import PlantCareType, PlantHistory, PlantInventory, PlantSpecies, Users

SECRET_KEY = os.environ["SECRET_KEY"]
CONN_STR = os.environ["DATABASE_URL"]
JWT_ALGORITHMS = [os.environ["JWT_ALGORITHM"]]


app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)
app.config["JSONIFY_PRETTYPRINT_REGULAR"] = True
api = Api(
    app,
    version="1.0",
    title="PlantFam API",
    description="Logging plant care events for plant inventory",
)

ns = api.namespace("plantfam", description="Plant care operations")

engine = create_engine(CONN_STR)  # , echo=True)
Session = sessionmaker()
Session.configure(bind=engine)
session = Session()
session.execute("SET search_path TO plantfam")

model_care = api.model(
    "CareTypes",
    {"care_type_id": fields.Integer, "sort": fields.Integer, "type": fields.String},
)

model_species = api.model(
    "Species",
    {"bot": fields.String, "com": fields.String, "species_id": fields.Integer},
)

model_inventory = api.model(
    "Inventory",
    {"inventory_id": fields.Integer, "species": fields.Nested(model_species)},
)

model_nested = api.model(
    "CareHistory",
    {
        "care": fields.Nested(model_care),
        "history_id": fields.Integer,
        "species": fields.Nested(model_inventory),
    },
)


user_fields = api.model("User", {"user_id": fields.Integer})


def db_transact(operation, record):
    try:
        if operation == "add":
            session.add(record)
        elif operation == "delete":
            session.delete(record)
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()


@ns.route("/register")
class Register(Resource):
    def post(self):
        data = request.get_json()
        hashed_password = generate_password_hash(data["password"], method="sha256")

        new_user = Users(
            public_id=str(uuid.uuid4()),
            username=data["username"],
            hashed_password=hashed_password,
            email=data["email"]
            #            admin=False,
        )
        db_transact("add", new_user)

        return jsonify({"message": "registered successfully"})


def token_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):

        token = None

        if "x-access-tokens" in request.headers:
            token = request.headers["x-access-tokens"]

        if not token:
            return jsonify({"message": "a valid token is missing"})

        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=JWT_ALGORITHMS)

            current_user = (
                session.query(Users)
                .filter(Users.public_id == data["public_id"])
                .first()
            )
        except:
            return jsonify({"message": "token is invalid"})

        kwargs["current_user"] = current_user
        return f(current_user, *args, **kwargs)

    return decorator


@ns.route("/login")
class Login(Resource):
    def get(self):
        auth = request.authorization
        if not auth or not auth.username or not auth.password:
            return make_response(
                "could not verify",
                401,
                {"WWW.Authentication": 'Basic realm: "login required"'},
            )

        else:
            user = session.query(Users).filter(Users.username == auth.username).first()
            if check_password_hash(user.hashed_password, auth.password):
                token = jwt.encode(
                    {
                        "public_id": user.public_id,
                        "exp": datetime.datetime.utcnow()
                        + datetime.timedelta(minutes=30),
                    },
                    SECRET_KEY,
                )
                print(token)
                return jsonify({"token": token})  # .decode('UTF-8')})
            else:
                return make_response(
                    "could not verify",
                    401,
                    {"WWW.Authentication": 'Basic realm: "login required"'},
                )


@ns.route("/CareTypes")
class CareTypes(Resource):
    @token_required
    @ns.marshal_with(model_care)
    @ns.doc("care_types")
    def get(self, *args, **kwargs):
        #        x = kwargs["current_user"].public_id
        query = session.query(PlantCareType)
        response = [row.to_json() for row in query]
        return response


@ns.route("/Species")
class Species(Resource):
    @token_required
    @ns.marshal_with(model_species)
    @ns.doc("species")
    def get(self, *args, **kwargs):
        query = session.query(PlantSpecies)
        response = [row.to_json() for row in query]
        return response


@ns.route("/UserHistory")
class UserHistory(Resource):
    @token_required
    @ns.marshal_with(model_nested)
    @ns.doc("user_history")
    def get(self, *args, **kwargs):
        user_id = kwargs["current_user"].site_user_id

        filters = [PlantInventory.site_user_id == user_id]

        query = (
            session.query(PlantHistory)
            .join(PlantInventory)
            .join(PlantSpecies)
            .join(PlantCareType)
            .filter(*filters)
        )

        response = [row.to_json() for row in query]

        return response

    @token_required
    @ns.doc("user_history_add")
    def post(self, *args, **kwargs):
        user_id = kwargs["current_user"].site_user_id
        data = request.get_json()
        print(data)
        new_history = PlantHistory(
            plant_inventory_id=data["inventory_id"],
            plant_care_type_id=data["care_type_id"],
        )
        db_transact("add", new_history)
        return jsonify({"message": "new plant care added"})


@ns.route("/UserInventory")
class UserInventory(Resource):
    @token_required
    @ns.marshal_with(model_inventory)
    @ns.doc("user_inventory")
    def get(self, *args, **kwargs):
        user_id = kwargs["current_user"].site_user_id
        filters = [PlantInventory.site_user_id == user_id]
        query = session.query(PlantInventory).join(PlantSpecies).filter(*filters)
        response = [row.to_json() for row in query]
        return response

    @token_required
    @ns.doc("user_inventory_add")
    def post(self, *args, **kwargs):
        user_id = kwargs["current_user"].site_user_id
        data = request.get_json()
        print(data)
        new_inventory = PlantInventory(
            plant_species_id=data["species_id"], site_user_id=user_id
        )

        db_transact("add", new_inventory)
        return jsonify({"message": "new inventory added"})


if __name__ == "__main__":
    # app.run(debug=True)
    app.run()
