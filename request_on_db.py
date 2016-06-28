from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import *
from CreationTable import * 
from migrate.changeset.constraint import ForeignKeyConstraint
from sqlalchemy.ext.declarative import declarative_base


engine = create_engine('sqlite:///sqlalchemy_table.db')
Base = declarative_base()
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


#class SixClass(Base):
#    __tablename__ = 'SixClass'
#    key = Column(String(250), primary_key=True)
#    idParam = Column(Integer,ForeignKey(ParamsClass.idParam),primary_key=True)
#    value = Column(Integer)
#    def __init__(self, key, idParam, value):
#        self.key = key
#        self.idParam = idParam 
#        self.value = value 

#sixInstance = SixClass.__table__('Daniel',2,26)
##session.add(sixInstance)
#session.commit()
def is_author(user_id,forcefieldName):
    user = session.query(User).filter(User.user_id == user_id).first()
    forcefield_id = session.query(ForceField).filter(ForceField.nameForceField == forcefieldName).first().idForceField
    idForcefieldList = (instance.idForceField for instance in user.forcefield_list)
    return forcefield_id in idForcefieldList

#Base.metadata.create_all(engine)

print(session.query(func.count(User.user_id)).scalar())
print()

user = session.query(User).get(2)
#user.social_network = None
user.is_confirmed()
session.add(user)
session.commit()

users = session.query(User).all()
#
for user in users:
	print(is_author(user.user_id,'AMBER_FF98'))
	print(user.user_id)
	print(user.firstname)
	print(user.lastname)
	print(user.username)
	if user.email:
		print(user.email)
	print(user.user_role)
	print(user.password)
	print(user.confirmed)
	if user.social_network:
		print(user.social_network)
	if user.confirmed_on:
		print(user.getTime(user.confirmed_on))
	print(user.getTime(user.user_registered_on))
	print()

#ff = session.query(ForceField).all()
#for x in ff:
#	print(x.nameForceField)


#amoeba_water = session.query(ForceField).get(5)
#print(amoeba_water.idForceField,amoeba_water.nameForceField)
#session.delete(amoeba_water)

#session.commit()
#pour afficher les Users et leurs FF
print('\n----------------------------------------------------')
users = session.query(User).all()
for user_instance in users:
    print(user_instance.firstname,user_instance.lastname,end="")
    print(' --> ',end="")
    for ff_list in user_instance.forcefield_list:
        print(session.query(ForceField).get(ff_list.idForceField).nameForceField,end="")
        print(" ",end="")
    print(' ')
print(" ")
#table = 'User'
#column = 'username'
#Table = eval(table)
#Column = getattr(Table,column)
#pipi = Column.property.columns[0].type
#
#if "INTEGER" in str(pipi):
#	print('int')
#if "VARCHAR" in str(pipi):
#	print('string')

#user = session.query(User).get(4)
#session.delete(user)
#session.commit()
#popo = SixClass.key.property.columns[0].type
#print("popo")
#print(popo)
#print(session.query(func.count(User.user_id)).scalar())

#print(Base.metadata.tables['SixClass'])

#print(SixClass.__table__._columns.get('idParam'))

#toto = session.query(Base.metadata.tables['SixClass'])
#print(dir(toto))

#print(ParamsClass.__table__.columns.get('idParam'))

#ha = session.query(SixClass).all()

#for x in ha:
#	print(ha.key,ha.idParam,ha.value)

#cons = ForeignKeyConstraint([SixClass.__table__._columns.get('idParam')], [ParamsClass.__table__.columns.get('idParam')])
# Create the constraint
#cons.create()
