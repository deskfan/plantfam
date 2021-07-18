from flask import Flask, request, jsonify
from flask_restful import Resource, Api, abort
from webargs import fields, validate
from webargs.flaskparser import use_kwargs, parser, use_args
import mysql.connector
from credentials import creds
from classes import PlantCareType, PlantInventory, PlantHistory, PlantSpecies
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import json

app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
app.config["DEBUG"] = True

CONN_STR = f"mysql://{creds['user']}:{creds['password']}@{creds['host']}/{creds['database']}"

engine = create_engine(CONN_STR, echo=True)
Session = sessionmaker()
Session.configure(bind=engine)
session = Session()

class Inventory(Resource):

    def get_inventory():
        if self.get_approved_ip(request.remote_addr):
            connection = mysql.connector.connect(user = creds['user'],
                                                password = creds['password'],
                                                host = creds['host'],
                                                database = creds['database'])
            cursor = connection.cursor()
            result = cursor.callproc('sp_ViewInventory',[])

            for result in cursor.stored_results():
                return result.fetchall()
            
            cursor.close()
            connection.close()
        else:
            return {'Error': 'IP Address Not Authorized'}
        
    def get_approved_ip(self,ip):
        print(ip)
        if ip in ['76.11.95.2','156.57.147.217','156.57.135.220','127.0.0.1']:
            return True
        else:
            return False


class Care(Resource):
#    care_args = {'user_id': fields.Int(required=True)}   
#    @use_args(care_args)    
    @app.route("/Care")
    def get_history():

        query = session.query(PlantHistory).\
            join(PlantInventory).\
            join(PlantSpecies).\
            join(PlantCareType).\
            filter(PlantInventory.site_user_id==1).all()
#            filter(PlantInventory.site_user_id==args["user_id"]).all()

        x = jsonify([row.to_json() for row in query])

        return x

#app.add_resource(Inventory, '/Inventory')
#api.add_resource(Care, '/Care')

# This error handler is necessary for usage with Flask-RESTful
#@parser.error_handler
#def handle_request_parsing_error(err, req, schema, *, error_status_code, error_headers):
#    """webargs error handler that uses Flask-RESTful's abort function to return
#    a JSON error response to the client.
#    """
#    abort(error_status_code, errors=err.messages)

if __name__ == '__main__':
    app.run(debug=True)