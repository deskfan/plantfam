from flask import Flask
from flask_restx import Api, Resource, fields

from credentials import creds
from classes import PlantCareType, PlantInventory, PlantHistory, PlantSpecies
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
api = Api(app)

CONN_STR = f"mysql://{creds['user']}:{creds['password']}@{creds['host']}/{creds['database']}"
engine = create_engine(CONN_STR, echo=True)
Session = sessionmaker()
Session.configure(bind=engine)
session = Session()

model_care = api.model('CareTwo',{
                                'care_type_id' : fields.Integer,
                                'sort' : fields.Integer,
                                'type' : fields.String
                            })

model_species = api.model('SpeciesTwo',{
                                    'bot' : fields.String,
                                    'com' : fields.String,
                                    'species_id' : fields.Integer
                                })

model_history = api.model('HistoryTwo',{
                                'inventory_id' : fields.Integer,
                                'species': fields.Nested(model_species)
                                })

model_nested = api.model('Care', {
                            'care' : fields.Nested(model_care),
                            'history_id' : fields.Integer,
                            'species' : fields.Nested(model_history)
                            }
                    )


care_fields = {'care_type_id': fields.Integer}
#care_fields['sort'] = fields.Integer
care_fields['type'] = fields.String


@api.route('/CareTypes')
class CareTypes(Resource):
    @api.marshal_with(care_fields)
    def get(self):
        query = session.query(PlantCareType)
        response = [row.to_json() for row in query]
        return response


@api.route('/Care')
class Care(Resource):
    @api.marshal_with(model_nested)
    def get(self):

#        filters =  [PlantInventory.site_user_id==args["user_id"]]
        filters =  [PlantInventory.site_user_id==1]

        query = session.query(PlantHistory).\
            join(PlantInventory).\
            join(PlantSpecies).\
            join(PlantCareType).\
            filter(*filters)

        response = [row.to_json() for row in query]

        return response




if __name__ == '__main__':
    app.run(debug=True)