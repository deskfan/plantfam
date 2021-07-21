from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql.sqltypes import Date


Base = declarative_base()

class PlantSpecies(Base):
    __tablename__ = 'plant_species'
    plant_species_id = Column(Integer, primary_key=True)
    plant_botanical_name = Column(String)
    plant_common_name = Column(String)

    def __repr__(self):
        return "<Plant(id='%s', botanical='%s', common='%s')>" % (
                            self.plant_species_id, self.plant_botanical_name, self.plant_common_name)

    def to_json(self):
        return {'species_id':self.plant_species_id, 'bot':self.plant_botanical_name,'com':self.plant_common_name}


class PlantCareType(Base):
    __tablename__ = 'plant_care_types'
    plant_care_type_id = Column(Integer, primary_key=True)
    plant_care_type = Column(String)
    sort_order = Column(Integer)

    def __repr__(self):
        return "<Care(id='%s', type='%s', sort='%s')>" % (
                            self.plant_care_type_id, self.plant_care_type, self.sort_order)

    def to_json(self):
        return {'care_type_id':self.plant_care_type_id, 'type':self.plant_care_type,'sort':self.sort_order}


class PlantInventory(Base):
    __tablename__ = 'plant_inventory'
    plant_inventory_id = Column(Integer, primary_key=True)
    site_user_id = Column(Integer)
    plant_species_id = Column(Integer, ForeignKey('plant_species.plant_species_id'))
    species = relationship("PlantSpecies")

    def to_json(self):
        return {'inventory_id':self.plant_inventory_id, 'species':self.species.to_json()}



class PlantHistory(Base):
    __tablename__ = 'plant_history'
    plant_history_id = Column(Integer, primary_key=True)
    notes = Column(String)
    plant_inventory_id = Column(Integer, ForeignKey('plant_inventory.plant_inventory_id'))
    plant_care_type_id = Column(Integer, ForeignKey('plant_care_types.plant_care_type_id'))
    plant_care_time = Column(Date)
    inventory = relationship("PlantInventory")
    care = relationship("PlantCareType")


    def __repr__(self):
        return "<History(id='%s', species_id='%s', species='%s')>" % (
                            self.plant_history_id, self.care, self.inventory.species)

    def to_json(self):
        return {'history_id':self.plant_history_id,'species':self.inventory.to_json(),'care': self.care.to_json()}
