import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String, Table ,Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.schema import ForeignKeyConstraint
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy import event 


Base = declarative_base()

@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


#AtomsType_ParamsType = Table('AtomsType_ParamsType',Base.metadata,
#                              Column('idForceField',Integer),
#                              Column('idAtomType',Integer),
#                              Column('idParams',Integer,ForeignKey('ParamsType.idParam')),
#                              ForeignKeyConstraint(
#                                        ['idForceField','idAtomType'],['AtomsType.idForceField','AtomsType.idAtomType'],
#                                        ))

class ForceField(Base):
    __tablename__ = 'ForceField'
    idForceField = Column(Integer, primary_key=True)
    nameForceField = Column(String(250), nullable=False)
    childrenClassAtom = relationship("ClassAtom", backref="force_field", cascade='delete,all')
    childrenScallingFactor = relationship("ScallingFactorTable", backref="ForceField", cascade='delete,all')   
    childrenParamClass = relationship("ParamsClass",backref="ForceFieldParent", cascade='delete,all' )
    childrenParamsType = relationship("ParamsType",backref="ForceFieldParent", cascade='delete,all')
    def __init__(self, nameForceField):
        self.nameForceField = nameForceField

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
    def __init__(self, idClassAtom, idForceField, symbol ,atomicNumber, atomicWeight, valence ):
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

class ParameterTable(Base):
    __tablename__ = 'ParameterTable'
    idParameter = Column(Integer, primary_key=True)
    nameParameter = Column(String(250), nullable=False)
    numberOfAtoms = Column(Integer)
    classOrType = Column(Enum('class','type',name='class_or_type'), nullable=False)
    columnsName = Column(String(250),nullable=True)
    childrenParamsClass = relationship("ParamsClass", backref="ParameterTable", cascade='delete,all')
    childrenScallingFactor = relationship("ScallingFactorTable", backref="ParameterTable", cascade='delete,all')
    childrenParamsType = relationship("ParamsType", backref="ParamsType", cascade='delete,all')    
    def __init__(self, nameParameter, numberOfAtoms ,classOrType,columnsName):
        self.nameParameter = nameParameter
        self.classOrType = classOrType
        self.numberOfAtoms = numberOfAtoms
        self.columnsName = columnsName
      

class ScallingFactorTable(Base):
    __tablename__ = 'ScallingFactorTable'
    idForceField = Column(Integer, ForeignKey('ForceField.idForceField'), primary_key=True)
    idParameter = Column(Integer, ForeignKey('ParameterTable.idParameter'), primary_key=True)
    description = Column(String(250),primary_key=True, nullable=False)
    value = Column(Integer, nullable=False)
    def __init__(self, idForceField, idParameter, description, value):
        self.idForceField = idForceField
        self.idParameter = idParameter
        self.description = description
        self.value = value

class ParamsClass(Base):
    __tablename__ = 'ParamsClass'
    idParam = Column(Integer, primary_key=True)
    idParameter = Column(Integer,ForeignKey(ParameterTable.idParameter))
    idForceField = Column(Integer,ForeignKey(ForceField.idForceField))
    tableName = Column(String(50))
    classAtomsParents = relationship("ClassAtom_ParamsClass",backref='paramsClassInstance', cascade='delete,all')
    oneClassChildren = relationship("OneClass",backref='paramsClassParent', cascade='delete,all')
    twoClassChildren = relationship("TwoClass",backref='paramsClassParent', cascade='delete,all')
    threeClassChildren = relationship("ThreeClass",backref='paramsClassParent', cascade='delete,all')
    fourClassChildren = relationship("FourClass",backref='paramsClassParent', cascade='delete,all')
    def __init__(self,idParameter , idForceField):
        self.idParameter = idParameter
        self.idForceField = idForceField
        
    
class OneClass(Base):
    __tablename__ = 'OneClass'
    key = Column(String(250), primary_key=True)
    idParam = Column(Integer, ForeignKey(ParamsClass.idParam), primary_key=True)
    value = Column(Integer)
    def __init__(self, key, idParam, value):
        self.key = key
        self.idParam = idParam 
        self.value = value 

class TwoClass(Base):
    __tablename__ = 'TwoClass'
    key = Column(String(250), primary_key=True)
    idParam = Column(Integer, ForeignKey('ParamsClass.idParam'), primary_key=True)
    value = Column(Integer)
    def __init__(self, key, idParam, value):
        self.key = key
        self.idParam = idParam 
        self.value = value 

class ThreeClass(Base):
    __tablename__ = 'ThreeClass'
    key = Column(String(250), primary_key=True)
    idParam = Column(Integer, ForeignKey('ParamsClass.idParam'), primary_key=True)
    value = Column(Integer)
    def __init__(self, key, idParam, value):
        self.key = key
        self.idParam = idParam 
        self.value = value 

class FourClass(Base):
    __tablename__ = 'FourClass'
    key = Column(String(250), primary_key=True)
    idParam = Column(Integer, ForeignKey('ParamsClass.idParam'), primary_key=True)
    value = Column(Integer)
    def __init__(self, key, idParam, value):
        self.key = key
        self.idParam = idParam 
        self.value = value 

class ParamsType(Base):
    __tablename__ = 'ParamsType'
    idParam = Column(Integer, primary_key=True)
    idParameter = Column(Integer, ForeignKey(ParameterTable.idParameter))
    idForceField = Column(Integer,ForeignKey(ForceField.idForceField))
    tableName = Column(String(50))
    atomsTypeParents = relationship('AtomsType_ParamsType', backref = 'paramsTypeInstance', cascade='delete,all')
    oneTypeClass = relationship('OneType',backref='paramTypeParent', cascade='delete,all') 
    def __init__(self,idParameter , idForceField):
        self.idParameter = idParameter
        self.idForceField = idForceField
        #parameterInstance = session.query(ParameterTable).get(idParameter) 
        #options = { 1:"One",2:"Two",3:"Three",4:"Four",5:"Five"}
        #if(parameterInstance.classOrType == "class"):
        #    raise ValueError ("Couldn't be of type \"class\"")
        #if(parameterInstance.classOrType == "type"):
        #    tableName = optionsClass[parameterInstance.numberOfAtoms]+"Type"

class OneType(Base):
    __tablename__ = 'OneType'
    key = Column(String(250), primary_key=True)
    idParam = Column(Integer, ForeignKey('ParamsType.idParam'), primary_key=True)
    value = Column(Integer)
    def __init__(self, key, idParam, value):
        self.key = key
        self.idParam = idParam 
        self.value = value 
    
#engine = create_engine('sqlite:///sqlalchemy_table.db')
#Base.metadata.create_all(engine) 