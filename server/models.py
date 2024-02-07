from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import validates
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin

convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

metadata = MetaData(naming_convention=convention)

db = SQLAlchemy(metadata=metadata)


class Activity(db.Model, SerializerMixin):
    __tablename__ = 'activities'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    difficulty = db.Column(db.Integer)

    #By creating a db.relionship, it allows the dev to not create a physical foreign key to 
    #relate one model to another. So, when instantiating a new class, instead of inputting the 
    #foreign key, the user will simply add the model object straight in.

    #back_populates vs backref...
    #back ref automatically relates the relating model, so you wouldn't have to reciprocally 
    #create a db.relationip... for the other side
    #However, even to me, I will be confused and hard to keep track of what is actually being 
    #related. So, it is generally recommended to use back_populates!

    signups = db.relationship('Signup', back_populates='activity', cascade='all, delete-orphan')
    #back_populates is relating to the current table
    #campers = db.relationship('Camper', secondary="signups", back_populates='activities')
    #use association proxies instead!

    campers = association_proxy('signups', 'camper', 
                                creator=lambda camper_obj: Signup(camper_id=camper_obj))
    
    # Add serialization rules
    # serialization rules are to set recursion limits
    serialize_rules = ('-signups.activity', '-signups.camper') 
    serialize_only = ('id', 'name', 'difficulty')

    
    def __repr__(self):
        return f'<Activity {self.id}: {self.name}>'


class Camper(db.Model, SerializerMixin):
    __tablename__ = 'campers'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    age = db.Column(db.Integer)


    # Add relationship
    signups = db.relationship("Signup", back_populates="camper", cascade='all, delete-orphan')
    activities = db.relationship("Activity", secondary="signups", back_populates="campers")

    activities = association_proxy('signups', 'activity',
                                   creator=lambda activity_obj: Signup(activity_id=activity_obj))
    # Add serialization rules
    serialize_rules = ('-signups.camper', '-signups.activity')
    serialize_only = ('id', 'name', 'age', 'signups')

    # Add validation
    @validates('age')
    def validates_age(self, key, age):
        if not 8 <= age <= 18:
            raise ValueError("Age must be in between 8 and 18")
        return age
    
    @validates('name')
    def validate_name(self, key, name):
        if not name:
            raise ValueError("Name cannot be omitted")
        return name
    
    
    def __repr__(self):
        return f'<Camper {self.id}: {self.name}>'


class Signup(db.Model, SerializerMixin):
    __tablename__ = 'signups'

    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.Integer)

    activity_id = db.Column(db.Integer, db.ForeignKey("activities.id"))
    camper_id = db.Column(db.Integer, db.ForeignKey("campers.id"))

    # Add relationships
    activity = db.relationship('Activity', back_populates='signups')
    camper = db.relationship('Camper', back_populates='signups')
    # Add serialization rules
    serialize_rules = ('-activity.signups','-camper.signups')

    #serialize_only = ('id', 'time', 'activity_id', 'camper_id')
    
    # Add validation
    @validates('time')
    def validates_time(self, key, time):
        if not 0 <= time <= 23:
            raise ValueError("Time must be in between 0 and 23.")
        return time

    def __repr__(self):
        return f'<Signup {self.id}>'


# add any models you may need.
