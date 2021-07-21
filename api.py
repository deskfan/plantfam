from flask import Flask
import webargs as wa
import webargs.flaskparser as wf

from werkzeug.middleware.proxy_fix import ProxyFix
from flask_restx import Api, Resource, fields
from credentials import creds
from classes import PlantCareType, PlantInventory, PlantHistory, PlantSpecies
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
api = Api(app, version='1.0', title='PlantFam API',
    description='Logging plant care events for plant inventory')

ns = api.namespace('plantfam', description='Plant care operations')

CONN_STR = f"mysql://{creds['user']}:{creds['password']}@{creds['host']}/{creds['database']}"
engine = create_engine(CONN_STR, echo=True)
Session = sessionmaker()
Session.configure(bind=engine)
session = Session()

model_care = api.model('CareTypes',{
                                'care_type_id' : fields.Integer,
                                'sort' : fields.Integer,
                                'type' : fields.String
                            })

model_species = api.model('Species',{
                                    'bot' : fields.String,
                                    'com' : fields.String,
                                    'species_id' : fields.Integer
                                })

model_history = api.model('History',{
                                'inventory_id' : fields.Integer,
                                'species': fields.Nested(model_species)
                                })

model_nested = api.model('CareHistory', {
                            'care' : fields.Nested(model_care),
                            'history_id' : fields.Integer,
                            'species' : fields.Nested(model_history)
                            }
                    )


user_fields = api.model('User', {'user_id': fields.Integer})


@ns.route('/CareTypes')
class CareTypes(Resource):
    @ns.marshal_with(model_care)
    @ns.doc('care_types')
    def get(self):
        query = session.query(PlantCareType)
        response = [row.to_json() for row in query]
        return response


@ns.route('/Care/<user_id>')
@ns.doc(params={'user_id':'A User ID'})
class Care(Resource):
#    care_args = {'user_id': wa.fields.Int(required=True)}
    @ns.doc('care_history')
    @ns.marshal_with(model_nested)
    def get(self,user_id):

        filters =  [PlantInventory.site_user_id==user_id]

        query = session.query(PlantHistory).\
            join(PlantInventory).\
            join(PlantSpecies).\
            join(PlantCareType).\
            filter(*filters)

        response = [row.to_json() for row in query]

        return response




if __name__ == '__main__':
    app.run(debug=True)