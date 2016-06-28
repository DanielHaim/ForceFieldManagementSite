import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String, Table ,Enum ,DateTime,Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship,sessionmaker
from sqlalchemy.schema import ForeignKeyConstraint
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy import event
from time import gmtime, strftime
import datetime


Base = declarative_base()

@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

class User(Base):
    __tablename__ = 'User'
    user_id = Column(Integer,primary_key=True,autoincrement=True)
    firstname = Column(String(64),nullable=False)
    lastname = Column(String(64),nullable=False)
    username = Column(String(64),nullable=False,unique=True)
    email = Column(String(120),nullable=True,unique=True)
    password = Column(String(256),nullable=True)
    user_role = Column(Enum('visitor','owner'),nullable=False,default="visitor")
    user_registered_on = Column(DateTime,nullable=False)
    password_registered_on = Column(DateTime,nullable=True)
    confirmed = Column(Boolean,nullable=False,default=False)
    confirmed_on = Column(DateTime,nullable=True)
    last_login_at = Column(DateTime,nullable=True)
    active = Column(Boolean,nullable=False,default=False)
    social_network = Column(Enum('facebook','google'),nullable=True)
    forcefield_list = relationship('UserForceField',backref='user_instance',cascade='delete,all') 
    def __init__(self,firstname,lastname,username,email=None,password=None,social_network=None):
        self.firstname = firstname
        self.lastname = lastname
        self.username = username
        if email:
            self.email = email
        self.user_registered_on = datetime.datetime.now()
        if password:
            self.password = password
            self.password_registered_on = datetime.datetime.now()
        if social_network:
            self.social_network = social_network
            self.confirmed = True
            self.confirmed_on = datetime.datetime.now()


    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        try:
            return unicode(self.user_id)  # python 2
        except NameError:
            return str(self.user_id)  # python 3

    def __repr__(self):
        return 'User: %s %s' % (self.firstName,self.lastName)

    def getTime(self ,date):
        return date.strftime("%d/%m/%Y at %H:%M:%S")

    def is_confirmed(self):
        self.confirmed = True
        self.confirmed_on = datetime.datetime.now()



class ForceField(Base):
    __tablename__ = 'ForceField'
    idForceField = Column(Integer, primary_key=True)
    nameForceField = Column(String(250), nullable=False)
    childrenClassAtom = relationship("ClassAtom", backref="force_field", cascade='delete,all')
    childrenScalingFactor = relationship("ScalingFactorTable", backref="ForceField", cascade='delete,all')
    childrenConstant = relationship("ConstantTable", backref="ForceField", cascade='delete,all') 
    childrenParamClass = relationship("ParamsClass",backref="ForceFieldParent", cascade='delete,all' )
    childrenParamsType = relationship("ParamsType",backref="ForceFieldParent", cascade='delete,all')
    childrenParameter = relationship('ParametersOfForceField',backref='forcefieldInstance',cascade='delete,all')
    owners = relationship('UserForceField',backref='ff_instance',cascade='delete,all')
    def __init__(self, nameForceField):
        self.nameForceField = nameForceField

class UserForceField(Base):
    __tablename__ = 'UserForceField'
    idUser = Column(Integer,ForeignKey('User.user_id'),primary_key=True)
    idForceField = Column(Integer,ForeignKey('ForceField.idForceField'),primary_key=True)
    isAuthor = Column(Boolean,nullable=False)

class ParameterTable(Base):
    __tablename__ = 'ParameterTable'
    idParameter = Column(Integer, primary_key=True)
    nameParameter = Column(String(250), nullable=False)
    numberOfAtoms = Column(Integer,nullable=True)
    columnsName = Column(String(250),nullable=True)
    classOrType = Column(Enum('class','type',name='class_or_type'), nullable=True)
    parameterType = Column(Enum('Parameter','SF','Constant'),nullable=False)
    childrenParamsClass = relationship("ParamsClass", backref="ParameterTable", cascade='delete,all')
    childrenScalingFactor = relationship("ScalingFactorTable", backref="ParameterTable", cascade='delete,all')
    childrenConstant = relationship("ConstantTable", backref="ParameterTable", cascade='delete,all')
    childrenParamsType = relationship("ParamsType", backref="ParamsType", cascade='delete,all')    
    associatedForcefield = relationship("ParametersOfForceField",backref='parametersInstance',cascade='delete,all')
    def __init__(self, nameParameter,parameterType,numberOfAtoms=None,classOrType=None):
        self.nameParameter = nameParameter
        self.classOrType = classOrType
        self.numberOfAtoms = numberOfAtoms
        self.parameterType = parameterType


class ParametersOfForceField(Base):
    __tablename__ = 'ParametersOfForceField'
    idForceField = Column(Integer,ForeignKey('ForceField.idForceField'),primary_key = True)
    idParameter = Column(Integer,ForeignKey('ParameterTable.idParameter'),primary_key = True)
    columnsName = Column(String(250), nullable=True)

class ClassAtom(Base):
    __tablename__= 'ClassAtom'
    idClassAtom = Column(Integer, primary_key=True, autoincrement=False)
    idForceField = Column(Integer, ForeignKey('ForceField.idForceField'), primary_key=True)
    symbol = Column(String(250))
    atomicNumber = Column(Integer)
    atomicWeight = Column(Integer)
    valence = Column(Integer)
    paramsClassChildren = relationship("ClassAtom_ParamsClass",backref="classAtomsInstance", cascade='delete,all')
    atoms_typeChildren = relationship("AtomsType",backref='class_atomParent', cascade='delete,all')
    def __init__(self, idClassAtom, idForceField, symbol ,atomicNumber, atomicWeight, valence):
        self.idClassAtom = idClassAtom
        self.idForceField = idForceField
        self.symbol = symbol
        self.atomicNumber = atomicNumber
        self.atomicWeight = atomicWeight
        self.valence = valence

class ClassAtom_ParamsClass(Base): 
    __tablename__ = 'ClassAtom_ParamsClass'
    idClassAtom = Column(Integer,primary_key=True)
    idForceField = Column(Integer,primary_key=True)
    idParam =  Column(Integer,ForeignKey('ParamsClass.idParam'),primary_key=True)
    description = Column(String(50),nullable=True)
    ForeignKeyConstraint(
        [idClassAtom,idForceField],[ClassAtom.idClassAtom,ClassAtom.idForceField],
                        )
 
class AtomsType(Base):
   __tablename__ = 'AtomsType'
   idAtomType = Column(Integer,primary_key=True,autoincrement=False)
   idForceField = Column(Integer,primary_key=True)
   idClassAtom = Column(Integer)
   description = Column(String(250))
   paramsTypeChildren = relationship("AtomsType_ParamsType",backref="atomsTypeInstance", cascade='delete,all')
   ForeignKeyConstraint(
           [idClassAtom,idForceField], [ClassAtom.idClassAtom,ClassAtom.idForceField]
           )
   def __init__(self,idAtomType, idClassAtom, idForceField , description):
       self.idAtomType = idAtomType
       self.idClassAtom = idClassAtom
       self.idForceField = idForceField
       self.description = description

class AtomsType_ParamsType(Base):     
    __tablename__ = 'AtomsType_ParamsType'
    idForceField = Column(Integer,primary_key=True)
    idAtomType = Column(Integer,primary_key=True)
    idParam = Column(Integer,ForeignKey('ParamsType.idParam'),primary_key=True)
    description = Column(String(50),nullable=True)
    ForeignKeyConstraint(
        [idForceField,idAtomType],[AtomsType.idForceField,AtomsType.idAtomType],
                        )
      

class ScalingFactorTable(Base):
    __tablename__ = 'ScalingFactorTable'
    idForceField = Column(Integer, ForeignKey('ForceField.idForceField'),primary_key=True)
    idParameter = Column(Integer, ForeignKey('ParameterTable.idParameter'),primary_key=True)
    key = Column(String(250),primary_key=True, nullable=False)
    value = Column(Integer, nullable=False)
    def __init__(self,idForceField,idParameter,key,value):
        self.idForceField = idForceField
        self.idParameter = idParameter
        self.key = key
        self.value = value
        
        
class ConstantTable(Base):
    __tablename__ = 'ConstantTable'
    idForceField = Column(Integer, ForeignKey('ForceField.idForceField'), primary_key=True)
    idParameter = Column(Integer, ForeignKey('ParameterTable.idParameter'),primary_key=True)
    key = Column(String(250),primary_key=True, nullable=False)
    value = Column(Integer, nullable=False)
    def __init__(self,idForceField,idParameter,key,value):
        self.idForceField = idForceField
        self.idParameter = idParameter
        self.key = key
        self.value = value

class ParamsClass(Base):
    __tablename__ = 'ParamsClass'
    idParam = Column(Integer, primary_key=True)
    idParameter = Column(Integer,ForeignKey(ParameterTable.idParameter))
    idForceField = Column(Integer,ForeignKey(ForceField.idForceField))
    classAtomsParents = relationship("ClassAtom_ParamsClass",backref='paramsClassInstance', cascade='delete,all')
    valueClassChildren = relationship("ValueClass",backref='paramsClassParent', cascade='delete,all')
    def __init__(self,idParameter , idForceField):
        self.idParameter = idParameter
        self.idForceField = idForceField
         
 

class ParamsType(Base):
    __tablename__ = 'ParamsType'
    idParam = Column(Integer, primary_key=True)
    idParameter = Column(Integer, ForeignKey(ParameterTable.idParameter))
    idForceField = Column(Integer,ForeignKey(ForceField.idForceField))
    atomsTypeParents = relationship('AtomsType_ParamsType', backref = 'paramsTypeInstance', cascade='delete,all')
    valueTypeClass = relationship('ValueType',backref='paramTypeParent', cascade='delete,all') 
    def __init__(self,idParameter , idForceField):
        self.idParameter = idParameter
        self.idForceField = idForceField

class ValueClass(Base):
    __tablename__ = 'ValueClass'
    key = Column(String(250), primary_key=True)
    idParam = Column(Integer, ForeignKey(ParamsClass.idParam), primary_key=True)
    value = Column(Integer)
    def __init__(self, key, idParam, value):
        self.key = key
        self.idParam = idParam
        self.value = value 


class ValueType(Base):
    __tablename__ = 'ValueType'
    key = Column(String(250), primary_key=True)
    idParam = Column(Integer, ForeignKey('ParamsType.idParam'), primary_key=True)
    value = Column(Integer)
    def __init__(self, key, idParam, value):
        self.key = key
        self.idParam = idParam 
        self.value = value 
    
engine = create_engine('sqlite:///sqlalchemy_table.db')
Base.metadata.create_all(engine)
