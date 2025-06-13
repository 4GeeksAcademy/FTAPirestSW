from flask_sqlalchemy import SQLAlchemy
from typing import List
from sqlalchemy import String, Boolean, Integer,ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

db = SQLAlchemy()

class Person(db.Model):
    __tablename__="persons"
    person_id:Mapped[int] = mapped_column(Integer,primary_key=True)
    nickname:Mapped[str]= mapped_column(String(50),unique=True,nullable=False)
    name:Mapped[str]= mapped_column(String(40),nullable=False)
    last_name:Mapped[str]=mapped_column(String(40),nullable=False)
    email:Mapped[str] = mapped_column(String(250),unique=True, nullable=False)
    favorites:Mapped[List["Favorite"]]=relationship("Favorite",
    back_populates="person"
)
    

    def serialize(self):
        return{
         'id':self.person_id,
         'nickname':self.nickname,
         'name':self.name,
         'last_name':self.last_name
        }
    
    def serialize_with_relations(self):
        data = self.serialize()
        data['favorites']=  [favorite.serialize_with_relations() for favorite in self.favorites]
        return data
        

class Favorite(db.Model):
    __tablename__="favorites"
    favorite_id:Mapped[int]=mapped_column(Integer,primary_key=True)
    person_id:Mapped[int]=mapped_column(ForeignKey('persons.person_id'),nullable=False)
    person:Mapped['Person']=relationship("Person",
        back_populates="favorites"
    )
    character_id:Mapped[int]=mapped_column(ForeignKey('characters.character_id'),nullable=True)
    characters:Mapped["Character"]=relationship(
        back_populates="favorites"
    )
    planet_id:Mapped[int]=mapped_column(ForeignKey('planets.planet_id'),nullable=True)
    planets:Mapped["Planet"]=relationship(
        back_populates="favorites"
    )
    vehicle_id:Mapped[int]=mapped_column(ForeignKey('vehicles.vehicle_id'),nullable=True)
    vehicles:Mapped["Vehicle"]=relationship(
        back_populates="favorites"
    )

    def serialize(self):
        return {
            "person":self.person_id,
            "character_id":self.character_id,
            "planet_id":self.planet_id,
            "vehicle_id":self.vehicle_id

        }
    
    def serialize_with_relations(self):
        data=self.serialize()
        data["person"]= self.person.serialize() if self.person else None
        data["character"]= self.characters.serialize() if self.characters else None
        data["vehicles"]= self.vehicles.serialize()if self.vehicles else None
        data["planets"]= self.planets.serialize()if self.planets else None
        return data
    


class Character(db.Model):
    __tablename__="characters"
    character_id:Mapped[int]=mapped_column(Integer,primary_key=True)
    character_name:Mapped[str]=mapped_column(String(250))
    birthday_character:Mapped[str]=mapped_column(String(250))
    favorites:Mapped[List["Favorite"]]=relationship(
        back_populates="characters"
    )
    def serialize(self):
        return{
            'id':self.character_id,
            'name':self.character_name,
            'birthday':self.birthday_character
        }
    
    def serialize_with_relations(self):
        data=self.serialize()
        data['favorites'] = [favorite.serialize for favorite in self.favorites]
        return data
    

class Planet(db.Model):
    __tablename__="planets"
    planet_id:Mapped[int]=mapped_column(Integer,primary_key=True)
    planet_name:Mapped[str]=mapped_column(String(250))
    planet_surface:Mapped[int]=mapped_column(Integer)
    favorites:Mapped[List["Favorite"]]=relationship(
        back_populates="planets"
    )
    def serialize(self):
        return{
            'id':self.planet_id,
            'name':self.planet_name,
            'surfice':self.planet_surface
        }
    
    def serialize_wit_relations(self):
        data=self.serialize()
        data['favorites'] = [favorite.serialize for favorite in self.favorites]
        return data
    
    
class Vehicle(db.Model):
    __tablename__="vehicles"
    vehicle_id:Mapped[int]=mapped_column(Integer,primary_key=True)
    vehicle_name:Mapped[str]=mapped_column(String(250))
    vehicle_model:Mapped[int]=mapped_column(String(250))
    favorites:Mapped[List["Favorite"]]=relationship(
        back_populates="vehicles"
    )
    def serialize(self):
        return{
            'id':self.vehicle_id,
            'name':self.vehicle_name,
            'model':self.vehicle_model
        }
    
    def serialize_wit_relations(self):
        data=self.serialize()
        data['favorites'] = [favorite.serialize for favorite in self.favorites]
        return data

