
from flask import Flask, request, jsonify
from flask_restful import Resource, Api
import mysql.connector
from credentials import creds

app = Flask(__name__)
api = Api(app)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True



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



api.add_resource(Inventory, '/Inventory')

if __name__ == '__main__':
    app.run(debug=True)