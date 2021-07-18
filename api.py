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
    care_args = {'user_id': fields.Int(required=True),
                'species_id': fields.Int(required=False)}   
    @app.route("/Care")
    @use_args(care_args, location='query')    
    def get_history(args):

        filters =  [PlantInventory.site_user_id==args["user_id"]]

        #todo, find a better pattern for this optional field/filter
        try:
            filters.append(PlantInventory.plant_species_id==args["species_id"])
        except:
            pass

        query = session.query(PlantHistory).\
            join(PlantInventory).\
            join(PlantSpecies).\
            join(PlantCareType).\
            filter(*filters)

        response = jsonify([row.to_json() for row in query])

        return response

if __name__ == '__main__':
    app.run(debug=True)