
from flask import Flask, request, jsonify
from flask_restful import Resource, Api
import mysql.connector
from credentials import creds
from classes import PlantCareType, PlantInventory, PlantHistory, PlantSpecies
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import json

app = Flask(__name__)
api = Api(app)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True

CONN_STR = f"mysql://{creds['user']}:{creds['password']}@{creds['host']}/{creds['database']}"


class Inventory(Resource):
    def get(self):
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
    def get(self):
        engine = create_engine(CONN_STR, echo=True)

        Session = sessionmaker()
        Session.configure(bind=engine)
        session = Session()


        query = session.query(PlantHistory).\
            join(PlantInventory).\
            join(PlantSpecies).\
            join(PlantCareType).\
            filter(PlantInventory.site_user_id==1).all()


        my_list = []
        for row in query:
            x = row.to_json()
            my_list.append(x)

            x = json.dumps(my_list)

        return x

api.add_resource(Inventory, '/Inventory')
api.add_resource(Care, '/Care')

if __name__ == '__main__':
    app.run(debug=True)