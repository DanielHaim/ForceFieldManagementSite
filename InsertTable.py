from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os.path
if(os.path.isfile('sqlalchemy_table.db')):
  os.remove('sqlalchemy_table.db')
from sqlalchemy.event import listen
from CreationTable import * 
from sqlalchemy import inspect,update


instancesToDelete = []
errorMessages = {}

#@event.listens_for(ParamsClass, 'before_insert')
#def checkClass(mapper, connect, self):
#    parameterInstance = session.query(ParameterTable).get(self.idParameter) 
#    #dictionary
#    options = { 1:"One",2:"Two",3:"Three",4:"Four",5:"Five"}
#    if(parameterInstance.classOrType == "type"):
#        #raise ValueError ("Couldn't be of type \"type\"")
#        #d'apres ce qui est ecrit dans le warning de ce lien
#        #http://docs.sqlalchemy.org/en/improve_toc/orm/events.html
#        #on ne peut pas changer le state d'un objet dans le before
#        #insert event je le fait donc dans le before commit
#        #ce event me sert juste a reperer les erreurs
#        #cette event me sert aussi a remplir le champ "tableName"
#        errorMessages[self] = "incompatible type"
#        self.tableName = options[parameterInstance.numberOfAtoms]+"Type"
#        instancesToDelete.append(self)
#    if(parameterInstance.classOrType == "class"):
#        self.tableName = options[parameterInstance.numberOfAtoms]+"Class"

#@event.listens_for(ParamsType, 'before_insert')
#def checkType(mapper, connect, self):
#    parameterInstance = session.query(ParameterTable).get(self.idParameter) 
#    #dictionary
#    options = { 1:"One",2:"Two",3:"Three",4:"Four",5:"Five"}
#    if(parameterInstance.classOrType == "type"):
#        #raise ValueError ("Couldn't be of type \"type\"")
#        #d'apres ce qui est ecrit dans le warning de ce lien
#        #http://docs.sqlalchemy.org/en/improve_toc/orm/events.html
#        #on ne peut pas changer le state d'un objet dans le before
#        #insert event je le fait donc dans le before commit
#        #ce event me sert juste a reperer les erreurs
#        #cette event me sert aussi a remplir le champ "tableName"
#        self.tableName = options[parameterInstance.numberOfAtoms]+"Type"
#    if(parameterInstance.classOrType == "class"):
#        errorMessages[self] = "incompatible class"
#        self.tableName = options[parameterInstance.numberOfAtoms]+"Class"
#        instancesToDelete.append(self)
#
#listen(ParamsClass, 'before_insert', checkClass)
#listen(ParamsType, 'before_insert', checkType)

def incompatibleRow(objList,session):
    for instance in objList:
        className = instance.__class__.__name__
        x =session.query(eval(className)).get(inspect(instance).identity)
        session.delete(x)
        print(bcolors.OKBLUE + 'instance of Table \"' + className + '\" with primary key '+ str(inspect(instance).identity) +' have been deleted' + bcolors.ENDC)
        print(bcolors.OKBLUE + 'ValueError: ' + errorMessages[instance] + bcolors.ENDC +'\n')
    

#Pour mettre un peut de couleur au output
#http://stackoverflow.com/questions/22886353/printing-colors-in-python-terminal
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

    def disable(self):
        self.HEADER = ''
        self.OKBLUE = ''
        self.OKGREEN = ''
        self.WARNING = ''
        self.FAIL = ''
        self.ENDC = ''


engine = create_engine('sqlite:///sqlalchemy_table.db')

Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


@event.listens_for(session, 'before_commit')
def receive_before_commit(session):
    print('------------------ERROR MESSAGE------------------------\n')
    incompatibleRow(instancesToDelete,session)
    print('------------------------------------------------------\n')

#creation de ForceField
amberFF98 = ForceField('AMBER_FF98')
charmm19 = ForceField('CHARMM19')
charmm27 = ForceField('CHARMM27')
opls_aa = ForceField('OPLS-AA')
ameoba_water = ForceField('AMOEBA-WATER')
session.add(amberFF98)
session.add(charmm19)
session.add(charmm27)
session.add(opls_aa)
session.add(ameoba_water)

#creation de user  
daniel = User('Daniel','Haim','danielmo','danielmoisehaim@gmail.com',password='K2baLLet',social_network='facebook')
raph = User('Raphael','Attal','rattal','raphaelattal1991@gmail.com','secret_key_raph')
yoel = User('Yoel','Levy','levyoel','yoel_levy_1@hotmail.fr','secret_key_yoel')

#creation de l'instance many_to_many
#recap:
#daniel --> amberFF98 , charm19 , amoeba_water
#raph --> amberFF98 , charm 27 , amoeba_water
#yoel --> charm27 , opls_aa
daniel_ff1 = UserForceField()
daniel_ff1.ff_instance = amberFF98
daniel_ff1.user_instance = daniel
daniel_ff1.isAuthor = True
daniel_ff2 = UserForceField()
daniel_ff2.ff_instance = charmm19
daniel_ff2.user_instance = daniel
daniel_ff2.isAuthor = False
daniel_ff3 = UserForceField()
daniel_ff3.ff_instance = ameoba_water
daniel_ff3.user_instance = daniel
daniel_ff3.isAuthor = False
raph_ff1 = UserForceField()
raph_ff1.ff_instance = amberFF98
raph_ff1.user_instance = raph
raph_ff1.isAuthor = False
raph_ff2 = UserForceField()
raph_ff2.ff_instance = charmm27
raph_ff2.user_instance = raph
raph_ff2.isAuthor = True
raph_ff3 = UserForceField()
raph_ff3.ff_instance = ameoba_water
raph_ff3.user_instance = raph
raph_ff3.isAuthor = False
yoel_ff1 = UserForceField()
yoel_ff1.ff_instance = charmm27
yoel_ff1.user_instance = yoel
yoel_ff1.isAuthor = False
yoel_ff2 = UserForceField()
yoel_ff2.ff_instance = opls_aa
yoel_ff2.user_instance = yoel
yoel_ff2.isAuthor = True

#creation de Parameter
van_der_walls = ParameterTable('Van Der Waals','Parameter',1,'class')
bond_stretching = ParameterTable('Bond Stretching','Parameter',2,'class')
partial_charge = ParameterTable('Atomic Partial Charge','Parameter',1,'type')
angle_bending = ParameterTable('Angle Bending','Parameter',3,'class')
improperTorsion = ParameterTable('Improper Torsion','Parameter',4,'class')
urey_bradley = ParameterTable('Urey-Bradley','Parameter', 3, 'class')
urey_bradley.columnsName = "KB, Distance"
atomic_multipole = ParameterTable('Atomic Multipole','Parameter', 1, 'type')
atomic_multipole.columnsName = "Axis Types, Frame, Multipoles (M-D-Q)"
dipole_polarizability = ParameterTable('Dipole Polarizability','Parameter', 1, 'type')
dipole_polarizability.columnsName = " Alpha, Group Atom Types"
#9
Atomic_Partial_Charge_SF = ParameterTable('Atomic Partial Charge Scaling Factors','SF',None,None)
#10
Van_der_Waals_SF = ParameterTable('Van Der Waals Scaling Factors','SF',None,None)
#11
Atomic_Multipole_SF = ParameterTable('Atomic Multipole Scaling Factors','SF',None,None)
#12
direct_polarizability_SF = ParameterTable('Direct Polarizability Scaling Factors','SF',None,None)
#13
mutual_polarizability_SF = ParameterTable('Mutual Polarizability Scaling Factors','SF',None,None)
#14
polarizability_energy_SF = ParameterTable('Polarizability Energy Scaling Factors','SF',None,None)
#15
higher_order_stretching_C = ParameterTable('Higher Order Stretching Constants','Constant',None,None)
#16
higher_order_bending_C = ParameterTable('Higher Order Bending Constants','Constant',None,None)
#jeTest = ParameterTable(nameParameter='Je Test',classOrType='Test')
#session.add(jeTest) // le test du Enum marche !!
session.add(van_der_walls)
session.add(bond_stretching)
session.add(partial_charge)
session.add(angle_bending)
session.add(improperTorsion)
session.add(urey_bradley)
session.add(atomic_multipole)
session.add(dipole_polarizability)
session.add(Atomic_Partial_Charge_SF)
session.add(Van_der_Waals_SF)
session.add(Atomic_Multipole_SF)
session.add(direct_polarizability_SF)
session.add(mutual_polarizability_SF)
session.add(polarizability_energy_SF)
session.add(higher_order_stretching_C)
session.add(higher_order_bending_C)

#Ajout dans la ManyToMany ParametersOfForceField
ParametersOfForceFieldInstance1 = ParametersOfForceField()
ParametersOfForceFieldInstance1.forcefieldInstance =  session.query(ForceField).get(1)
ParametersOfForceFieldInstance1.parametersInstance = session.query(ParameterTable).get(1)
ParametersOfForceFieldInstance2 = ParametersOfForceField()
ParametersOfForceFieldInstance2.forcefieldInstance =  session.query(ForceField).get(1)
ParametersOfForceFieldInstance2.parametersInstance = session.query(ParameterTable).get(2)
ParametersOfForceFieldInstance3 = ParametersOfForceField()
ParametersOfForceFieldInstance3.forcefieldInstance =  session.query(ForceField).get(1)
ParametersOfForceFieldInstance3.parametersInstance = session.query(ParameterTable).get(3)
ParametersOfForceFieldInstance4 = ParametersOfForceField()
ParametersOfForceFieldInstance4.forcefieldInstance =  session.query(ForceField).get(1)
ParametersOfForceFieldInstance4.parametersInstance = session.query(ParameterTable).get(4)
ParametersOfForceFieldInstance5 = ParametersOfForceField()
ParametersOfForceFieldInstance5.forcefieldInstance =  session.query(ForceField).get(1)
ParametersOfForceFieldInstance5.parametersInstance = session.query(ParameterTable).get(5)
ParametersOfForceFieldInstance6 = ParametersOfForceField()
ParametersOfForceFieldInstance6.forcefieldInstance =  session.query(ForceField).get(2)
ParametersOfForceFieldInstance6.parametersInstance = session.query(ParameterTable).get(1)
ParametersOfForceFieldInstance7 = ParametersOfForceField()
ParametersOfForceFieldInstance7.forcefieldInstance =  session.query(ForceField).get(2)
ParametersOfForceFieldInstance7.parametersInstance = session.query(ParameterTable).get(3)
ParametersOfForceFieldInstance8 = ParametersOfForceField()
ParametersOfForceFieldInstance8.forcefieldInstance =  session.query(ForceField).get(3)
ParametersOfForceFieldInstance8.parametersInstance = session.query(ParameterTable).get(1)
ParametersOfForceFieldInstance9 = ParametersOfForceField()
ParametersOfForceFieldInstance9.forcefieldInstance =  session.query(ForceField).get(5)
ParametersOfForceFieldInstance9.parametersInstance = session.query(ParameterTable).get(1)
ParametersOfForceFieldInstance10 = ParametersOfForceField()
ParametersOfForceFieldInstance10.forcefieldInstance =  session.query(ForceField).get(5)
ParametersOfForceFieldInstance10.parametersInstance = session.query(ParameterTable).get(2)
ParametersOfForceFieldInstance11 = ParametersOfForceField()
ParametersOfForceFieldInstance11.forcefieldInstance =  session.query(ForceField).get(5)
ParametersOfForceFieldInstance11.parametersInstance = session.query(ParameterTable).get(4)
ParametersOfForceFieldInstance12 = ParametersOfForceField()
ParametersOfForceFieldInstance12.forcefieldInstance =  session.query(ForceField).get(5)
ParametersOfForceFieldInstance12.parametersInstance = session.query(ParameterTable).get(6)
ParametersOfForceFieldInstance13 = ParametersOfForceField()
ParametersOfForceFieldInstance13.forcefieldInstance =  session.query(ForceField).get(5)
ParametersOfForceFieldInstance13.parametersInstance = session.query(ParameterTable).get(7)
ParametersOfForceFieldInstance14 = ParametersOfForceField()
ParametersOfForceFieldInstance14.forcefieldInstance =  session.query(ForceField).get(5)
ParametersOfForceFieldInstance14.parametersInstance = session.query(ParameterTable).get(8)
ParametersOfForceFieldInstance15 = ParametersOfForceField()
ParametersOfForceFieldInstance15.forcefieldInstance =  session.query(ForceField).get(1)
ParametersOfForceFieldInstance15.parametersInstance = session.query(ParameterTable).get(9)
ParametersOfForceFieldInstance16 = ParametersOfForceField()
ParametersOfForceFieldInstance16.forcefieldInstance =  session.query(ForceField).get(2)
ParametersOfForceFieldInstance16.parametersInstance = session.query(ParameterTable).get(10)
ParametersOfForceFieldInstance17 = ParametersOfForceField()
ParametersOfForceFieldInstance17.forcefieldInstance =  session.query(ForceField).get(2)
ParametersOfForceFieldInstance17.parametersInstance = session.query(ParameterTable).get(9)
ParametersOfForceFieldInstance18 = ParametersOfForceField()
ParametersOfForceFieldInstance18.forcefieldInstance =  session.query(ForceField).get(5)
ParametersOfForceFieldInstance18.parametersInstance = session.query(ParameterTable).get(10)
ParametersOfForceFieldInstance19 = ParametersOfForceField()
ParametersOfForceFieldInstance19.forcefieldInstance =  session.query(ForceField).get(5)
ParametersOfForceFieldInstance19.parametersInstance = session.query(ParameterTable).get(11)
ParametersOfForceFieldInstance20 = ParametersOfForceField()
ParametersOfForceFieldInstance20.forcefieldInstance =  session.query(ForceField).get(5)
ParametersOfForceFieldInstance20.parametersInstance = session.query(ParameterTable).get(12)
ParametersOfForceFieldInstance21 = ParametersOfForceField()
ParametersOfForceFieldInstance21.forcefieldInstance =  session.query(ForceField).get(5)
ParametersOfForceFieldInstance21.parametersInstance = session.query(ParameterTable).get(13)
ParametersOfForceFieldInstance22 = ParametersOfForceField()
ParametersOfForceFieldInstance22.forcefieldInstance =  session.query(ForceField).get(5)
ParametersOfForceFieldInstance22.parametersInstance = session.query(ParameterTable).get(14)
ParametersOfForceFieldInstance23 = ParametersOfForceField()
ParametersOfForceFieldInstance23.forcefieldInstance =  session.query(ForceField).get(5)
ParametersOfForceFieldInstance23.parametersInstance = session.query(ParameterTable).get(15)
ParametersOfForceFieldInstance24 = ParametersOfForceField()
ParametersOfForceFieldInstance24.forcefieldInstance =  session.query(ForceField).get(5)
ParametersOfForceFieldInstance24.parametersInstance = session.query(ParameterTable).get(16)




#creation de ScalingFactor
Atomic_Partial_Charge_SF_1 = ScalingFactorTable(1,9,'1-2 Atoms',0.000)
Atomic_Partial_Charge_SF_2 = ScalingFactorTable(1,9,'1-3 Atoms',0.000)
Atomic_Partial_Charge_SF_3 = ScalingFactorTable(1,9,'1-4 Atoms',0.833)
Atomic_Partial_Charge_SF_4 = ScalingFactorTable(1,9,'1-5 Atoms',1.000)
Van_der_Waals_SF_1 = ScalingFactorTable(2,10,'1-2 Atoms',0.000)
Van_der_Waals_SF_2 = ScalingFactorTable(2,10,'1-3 Atoms',0.000)
Van_der_Waals_SF_3 = ScalingFactorTable(2,10,'1-4 Atoms',1.000)
Van_der_Waals_SF_4 = ScalingFactorTable(2,10,'1-5 Atoms',1.000)
Atomic_Partial_Charge_SF_5 = ScalingFactorTable(2,9,'1-2 Atoms',0.000)
Atomic_Partial_Charge_SF_6 = ScalingFactorTable(2,9,'1-3 Atoms',0.000)
Atomic_Partial_Charge_SF_7 = ScalingFactorTable(2,9,'1-4 Atoms',1.000)
Atomic_Partial_Charge_SF_8 = ScalingFactorTable(2,9,'1-5 Atoms',1.000)
Van_der_Waals_SF_5 = ScalingFactorTable(5,10,'1-2 Atoms',0.000)
Van_der_Waals_SF_6 = ScalingFactorTable(5,10,'1-3 Atoms',0.000)
Van_der_Waals_SF_7 = ScalingFactorTable(5,10,'1-4 Atoms',1.000)
Van_der_Waals_SF_8 = ScalingFactorTable(5,10,'1-5 Atoms',1.000)
Atomic_Multipole_SF_1 = ScalingFactorTable(5,11,'1-2 Atoms',0.000)
Atomic_Multipole_SF_2 = ScalingFactorTable(5,11,'1-3 Atoms',0.000)
Atomic_Multipole_SF_3 = ScalingFactorTable(5,11,'1-4 Atoms',1.000)
Atomic_Multipole_SF_4 = ScalingFactorTable(5,11,'1-5 Atoms',1.000)
direct_polarizability_SF_1 = ScalingFactorTable(5,12,'1-1 Groups',0.000)
direct_polarizability_SF_2 = ScalingFactorTable(5,12,'1-2 Groups',1.000)
direct_polarizability_SF_3 = ScalingFactorTable(5,12,'1-3 Groups',1.000)
direct_polarizability_SF_4 = ScalingFactorTable(5,12,'1-4 Groups',1.000)
mutual_polarizability_SF_1 = ScalingFactorTable(5,13,'1-1 Groups',1.000)
mutual_polarizability_SF_2 = ScalingFactorTable(5,13,'1-2 Groups',1.000)
mutual_polarizability_SF_3 = ScalingFactorTable(5,13,'1-3 Groups',1.000)
mutual_polarizability_SF_4 = ScalingFactorTable(5,13,'1-4 Groups',1.000)
polarizability_energy_SF_1 = ScalingFactorTable(5,14,'1-2 Atoms',0.000)
polarizability_energy_SF_2 = ScalingFactorTable(5,14,'1-3 Atoms',0.000)
polarizability_energy_SF_3 = ScalingFactorTable(5,14,'1-4 Atoms',1.000)
polarizability_energy_SF_4 = ScalingFactorTable(5,14,'1-5 Atoms',1.000)
session.add(Atomic_Partial_Charge_SF_1)
session.add(Atomic_Partial_Charge_SF_2)
session.add(Atomic_Partial_Charge_SF_3)
session.add(Atomic_Partial_Charge_SF_4)
session.add(Atomic_Partial_Charge_SF_5)
session.add(Atomic_Partial_Charge_SF_6)
session.add(Atomic_Partial_Charge_SF_7)
session.add(Atomic_Partial_Charge_SF_8)
session.add(Van_der_Waals_SF_1)
session.add(Van_der_Waals_SF_2)
session.add(Van_der_Waals_SF_3)
session.add(Van_der_Waals_SF_4)
session.add(Van_der_Waals_SF_5)
session.add(Van_der_Waals_SF_6)
session.add(Van_der_Waals_SF_7)
session.add(Van_der_Waals_SF_8)
session.add(Atomic_Multipole_SF_1)
session.add(Atomic_Multipole_SF_2)
session.add(Atomic_Multipole_SF_3)
session.add(Atomic_Multipole_SF_4)
session.add(direct_polarizability_SF_1)
session.add(direct_polarizability_SF_2)
session.add(direct_polarizability_SF_3)
session.add(direct_polarizability_SF_4)
session.add(mutual_polarizability_SF_1)
session.add(mutual_polarizability_SF_2)
session.add(mutual_polarizability_SF_3)
session.add(mutual_polarizability_SF_4)
session.add(polarizability_energy_SF_1)
session.add(polarizability_energy_SF_2)
session.add(polarizability_energy_SF_3)
session.add(polarizability_energy_SF_4)


#creation de constants
higher_order_stretching_C_1 = ConstantTable(5,15,'Cubic',3)
higher_order_stretching_C_2 = ConstantTable(5,15,'Quartic',4)
higher_order_bending_C_1 = ConstantTable(5,16,'Cubic',-0.014)
higher_order_bending_C_2 = ConstantTable(5,16,'Quartic',0.000056)
higher_order_bending_C_3 = ConstantTable(5,16,'Pentic',-0.0000007)
higher_order_bending_C_4 = ConstantTable(5,16,'Sextic',0.000000022)
session.add(higher_order_stretching_C_1)
session.add(higher_order_stretching_C_2)
session.add(higher_order_bending_C_1)
session.add(higher_order_bending_C_2)
session.add(higher_order_bending_C_3)
session.add(higher_order_bending_C_4)


#creation de classAtom
classAtomInstance1 = ClassAtom(14, 1,'N', 7, 14.010, 3)
classAtomInstance2 = ClassAtom(1, 1,'CT', 6, 12.010, 4)
classAtomInstance3 = ClassAtom(2, 1,'C', 6, 12.010, 3)
classAtomInstance4 = ClassAtom(29, 1, 'H', 1, 1.008, 1)
classAtomInstance5 = ClassAtom(4,1,'CM',6,12.010,3)
classAtomInstance6 = ClassAtom(3,1,'CA',6,12.010,3)
classAtomInstance7 = ClassAtom(22,1,'OH',8,16.000,2)
classAtomInstance8 = ClassAtom(1, 2,'H', 1, 1.008, 1)
classAtomInstance9 = ClassAtom(2, 2, 'HC', 1, 1.008, 1)
classAtomInstance10 = ClassAtom( 3, 2, 'HT', 1, 1.008, 1)
classAtomInstance11 = ClassAtom( 4, 2, 'C', 6, 12.011, 3)
classAtomInstance12 = ClassAtom( 1, 3, 'HA', 1, 1.008, 1)
classAtomInstance13 = ClassAtom(2, 3,'HP', 1, 1.008, 1)
classAtomInstance14 = ClassAtom(3 , 3,'H', 1, 1.008, 1)
classAtomInstance15 = ClassAtom(4, 3,'HB',1, 1.008, 1)
classAtomInstance16 = ClassAtom(1 , 5,'O', 8 ,15.995, 2)
classAtomInstance17 = ClassAtom(2, 5,'H',1, 1.008, 1)
session.add(classAtomInstance1)
session.add(classAtomInstance2)
session.add(classAtomInstance3)
session.add(classAtomInstance4)
session.add(classAtomInstance5)
session.add(classAtomInstance6)
session.add(classAtomInstance7)
session.add(classAtomInstance8)
session.add(classAtomInstance9)
session.add(classAtomInstance10)
session.add(classAtomInstance11)
session.add(classAtomInstance12)
session.add(classAtomInstance13)
session.add(classAtomInstance14)
session.add(classAtomInstance15)
session.add(classAtomInstance16)
session.add(classAtomInstance17)

#creation de AtomType
atomsTypeInstance1  = AtomsType(idAtomType = 1, idClassAtom = 14,idForceField = 1,  description = 'Glycine N'           )
atomsTypeInstance2  = AtomsType(idAtomType = 2, idClassAtom = 1, idForceField = 1,  description = 'Glycine CA'          )
atomsTypeInstance3  = AtomsType(idAtomType = 3, idClassAtom = 2, idForceField = 1,  description = 'Glycine C'           )
atomsTypeInstance4  = AtomsType(idAtomType = 4, idClassAtom = 29,idForceField = 1,  description = 'Glycine HN'          )
atomsTypeInstance5  = AtomsType(idAtomType = 1, idClassAtom = 1, idForceField = 2,  description = 'Amide CONHR Hydrogen')
atomsTypeInstance6  = AtomsType(idAtomType = 2, idClassAtom = 1, idForceField = 2,  description = 'Amide CONH2 Hydrogen')
atomsTypeInstance7  = AtomsType(idAtomType = 3, idClassAtom = 1, idForceField = 2,  description = 'HIP Imidazolium HN'  )
atomsTypeInstance8  = AtomsType(idAtomType = 4, idClassAtom = 1, idForceField = 2,  description = 'Hydroxyl Hydrogen'   )
atomsTypeInstance9  = AtomsType(idAtomType = 5, idClassAtom = 2, idForceField = 2,  description = 'LYS/ARG/N-Term H'    )
atomsTypeInstance10 = AtomsType(idAtomType = 6, idClassAtom = 3, idForceField = 2,  description = 'Modified TIP3P H'    )
atomsTypeInstance11 = AtomsType(idAtomType = 7, idClassAtom = 4, idForceField = 2,  description = 'Amide Carbon'        )
atomsTypeInstance12 = AtomsType(idAtomType = 1, idClassAtom = 1, idForceField = 3,  description = 'Nonpolar Hydrogen'   )
atomsTypeInstance13 = AtomsType(idAtomType = 2, idClassAtom = 2, idForceField = 3,  description = 'Aromatic Hydrogen'   )
atomsTypeInstance14 = AtomsType(idAtomType = 3, idClassAtom = 3, idForceField = 3,  description = 'Peptide Amide HN'    )
atomsTypeInstance15 = AtomsType(idAtomType = 4, idClassAtom = 4, idForceField = 3,  description = 'Peptide HCA'         )
atomsTypeInstance16 = AtomsType(idAtomType = 1, idClassAtom = 1, idForceField = 5,  description = 'AMOEBA Water O'      )
atomsTypeInstance17 = AtomsType(idAtomType = 2, idClassAtom = 2, idForceField = 5,  description = 'AMOEBA Water H'      )
session.add(atomsTypeInstance1)
session.add(atomsTypeInstance2)
session.add(atomsTypeInstance3)
session.add(atomsTypeInstance4)
session.add(atomsTypeInstance5)
session.add(atomsTypeInstance6)
session.add(atomsTypeInstance7)
session.add(atomsTypeInstance8)
session.add(atomsTypeInstance9)
session.add(atomsTypeInstance10)
session.add(atomsTypeInstance11)
session.add(atomsTypeInstance12)
session.add(atomsTypeInstance13)
session.add(atomsTypeInstance14)
session.add(atomsTypeInstance15)
session.add(atomsTypeInstance16)
session.add(atomsTypeInstance17)

#creation de ParamsClass
paramsClassInstance1 = ParamsClass(idParameter=1,idForceField=1)  #VDW
paramsClassInstance2 = ParamsClass(idParameter=2,idForceField=1)  #BS
paramsClassInstance3 = ParamsClass(idParameter=1,idForceField=1)  #VDW
paramsClassInstance4 = ParamsClass(idParameter=3,idForceField=2)  #Angle Bending
paramsClassInstance5 = ParamsClass(idParameter=4,idForceField=1)  #Angle Bending
paramsClassInstance6 = ParamsClass(idParameter=5,idForceField=1)  #Improper Torsion
paramsClassInstance7 = ParamsClass(idParameter=1,idForceField=2)  #VDW
paramsClassInstance8 = ParamsClass(idParameter=1,idForceField=3)  #VDW
paramsClassInstance9 = ParamsClass(idParameter=2,idForceField=1)  #BS
paramsClassInstance10 = ParamsClass(idParameter=1,idForceField=5)  #VDW FOR AMOEBA-WATER 
paramsClassInstance11 = ParamsClass(idParameter=1,idForceField=5)  #VDW FOR AMOEBA-WATER 
paramsClassInstance12 = ParamsClass(idParameter=2,idForceField=5)  #BS FOR AMOEBA-WATER 
paramsClassInstance13 = ParamsClass(idParameter=4,idForceField=5)  #ANGLE BENDING FOR AMOEBA-WATER 
paramsClassInstance14 = ParamsClass(idParameter=6,idForceField=5)  #Urey-Bradley  FOR AMOEBA-WATER 
session.add(paramsClassInstance1)
session.add(paramsClassInstance2)
session.add(paramsClassInstance3)
session.add(paramsClassInstance4)
session.add(paramsClassInstance5)
session.add(paramsClassInstance6)
session.add(paramsClassInstance7)
session.add(paramsClassInstance8)
session.add(paramsClassInstance9)
session.add(paramsClassInstance10)
session.add(paramsClassInstance11)
session.add(paramsClassInstance12)
session.add(paramsClassInstance13)
session.add(paramsClassInstance14)

#,tableName = "OneClass")  
#,tableName = "TwoClass")  
#,tableName = "OneClass")  
#,tableName = "OneType")   
#,tableName = "ThreeClass")
#,tableName = "FourClass") 
#,tableName = "OneClass")  
#,tableName = "OneClass")  
#,tableName = "TwoClass")  

#creation de oneClass //premiere ligne de VDW
#pour le FF AMBER_FF98
OneClassInstance1 = ValueClass(idParam=1,key = "Radius",value=1.908)
OneClassInstance2 = ValueClass(idParam=1,key = "Epsilon",value=0.109)
OneClassInstance3 = ValueClass(idParam=1,key = "Reduction",value=0.000)
session.add(OneClassInstance1)
session.add(OneClassInstance2)
session.add(OneClassInstance3)

#creation de ClassAtom_ParamsClass (ManyToMany)
ClassAtom_ParamsClassInstance1 = ClassAtom_ParamsClass()
#on lie le class_atom idclassAtom=1 et forcefield=1 avec l'instance ManyToMany
ClassAtom_ParamsClassInstance1.classAtomsInstance =  session.query(ClassAtom).get((1,1))
#on lie le paramClass avec idParam=1 avec l'instance ManyToMany
ClassAtom_ParamsClassInstance1.paramsClassInstance = session.query(ParamsClass).get(1)


#creation de OneClass again //deuxieme ligne de VDW
#pour FF AMBER_FF98
OneClassInstance4 = ValueClass(idParam=3,key = "Radius",value=1.908)
OneClassInstance5 = ValueClass(idParam=3,key = "Epsilon",value=0.086)
OneClassInstance6 = ValueClass(idParam=3,key = "Reduction",value=0.000)
session.add(OneClassInstance4)
session.add(OneClassInstance5)
session.add(OneClassInstance6)

#Ajout dans la ManyToMany
ClassAtom_ParamsClassInstance2 = ClassAtom_ParamsClass()
ClassAtom_ParamsClassInstance2.classAtomsInstance =  session.query(ClassAtom).get((2,1))
ClassAtom_ParamsClassInstance2.paramsClassInstance = session.query(ParamsClass).get(3)

#creation de OneClass //premiere ligne de VDW
#pour le FF CHARM19
OneClassInstance7 = ValueClass(idParam=7,key = "Radius",value=0.800)
OneClassInstance8 = ValueClass(idParam=7,key = "Epsilon",value=0.050)
OneClassInstance9 = ValueClass(idParam=7,key = "Reduction",value=0.000)
session.add(OneClassInstance7)
session.add(OneClassInstance8)
session.add(OneClassInstance9)

#Ajout dans la ManyToMany
ClassAtom_ParamsClassInstance3 = ClassAtom_ParamsClass()
ClassAtom_ParamsClassInstance3.classAtomsInstance =  session.query(ClassAtom).get((1,2))
ClassAtom_ParamsClassInstance3.paramsClassInstance = session.query(ParamsClass).get(7)


#creation de OneClass //premiere ligne de VDW
#pour le FF CHARM27
OneClassInstance10 = ValueClass(idParam=8,key = "Radius",value=0.800)
OneClassInstance11 = ValueClass(idParam=8,key = "Epsilon",value=0.050)
OneClassInstance12 = ValueClass(idParam=8,key = "Reduction",value=0.000)
session.add(OneClassInstance10)
session.add(OneClassInstance11)
session.add(OneClassInstance12)

#Ajout dans la ManyToMany
ClassAtom_ParamsClassInstance4 = ClassAtom_ParamsClass()
ClassAtom_ParamsClassInstance4.classAtomsInstance =  session.query(ClassAtom).get((1,3))
ClassAtom_ParamsClassInstance4.paramsClassInstance = session.query(ParamsClass).get(8)


#creation de oneClass // premiere ligne de VDW pour  AMOEBA-WATER
OneClassInstance13 = ValueClass(idParam=10,key = "Radius",value=3.405)
OneClassInstance14 = ValueClass(idParam=10,key = "Epsilon",value=0.110)
OneClassInstance15 = ValueClass(idParam=10,key = "Reduction",value=0.000)
session.add(OneClassInstance13)
session.add(OneClassInstance14)
session.add(OneClassInstance15)

#Ajout dans la ManyToMany
ClassAtom_ParamsClassInstance5 = ClassAtom_ParamsClass()
#on lie le class_atom idclassAtom=1 et forcefield=1 avec l'instance ManyToMany
ClassAtom_ParamsClassInstance5.classAtomsInstance =  session.query(ClassAtom).get((1,5))
#on lie le paramClass avec idParam=1 avec l'instance ManyToMany
ClassAtom_ParamsClassInstance5.paramsClassInstance = session.query(ParamsClass).get(10)


#creation de oneClass // deuxieme ligne de VDW pour  AMOEBA-WATER
OneClassInstance16 = ValueClass(idParam=11,key = "Radius",value=2.655)
OneClassInstance17 = ValueClass(idParam=11,key = "Epsilon",value=0.013)
OneClassInstance18 = ValueClass(idParam=11,key = "Reduction",value=0.910)
session.add(OneClassInstance16)
session.add(OneClassInstance17)
session.add(OneClassInstance18)

#Ajout dans la ManyToMany
ClassAtom_ParamsClassInstance5 = ClassAtom_ParamsClass()
#on lie le class_atom idclassAtom=1 et forcefield=1 avec l'instance ManyToMany
ClassAtom_ParamsClassInstance5.classAtomsInstance =  session.query(ClassAtom).get((2,5))
#on lie le paramClass avec idParam=1 avec l'instance ManyToMany
ClassAtom_ParamsClassInstance5.paramsClassInstance = session.query(ParamsClass).get(11)


#creation de twoClass //deuxieme ligne de BS
#ForceField AMBER_FF98
twoClassInstance1 = ValueClass(idParam=2,key = "KS",value=317.000)
twoClassInstance2 = ValueClass(idParam=2,key = "Length",value=1.5220)
session.add(twoClassInstance1)
session.add(twoClassInstance2)

#Ajout dans la ManyToMany
ClassAtom_ParamsClassInstance5 = ClassAtom_ParamsClass(description="1-2")
ClassAtom_ParamsClassInstance5.classAtomsInstance =  session.query(ClassAtom).get((1,1))
ClassAtom_ParamsClassInstance5.paramsClassInstance = session.query(ParamsClass).get(2)
ClassAtom_ParamsClassInstance6 = ClassAtom_ParamsClass(description="1-2")
ClassAtom_ParamsClassInstance6.classAtomsInstance =  session.query(ClassAtom).get((2,1))
ClassAtom_ParamsClassInstance6.paramsClassInstance = session.query(ParamsClass).get(2)

#creation de twoClass //premiere ligne de BS
#ForceField AMBER_FF98
twoClassInstance3 = ValueClass(idParam=9,key = "KS",value=317.000)
twoClassInstance4 = ValueClass(idParam=9,key = "Length",value=1.5220)
session.add(twoClassInstance3)
session.add(twoClassInstance4)

#Ajout dans la ManyToMany
ClassAtom_ParamsClassInstance7 = ClassAtom_ParamsClass(description="1-1")
ClassAtom_ParamsClassInstance7.classAtomsInstance =  session.query(ClassAtom).get((1,1))
ClassAtom_ParamsClassInstance7.paramsClassInstance = session.query(ParamsClass).get(9)


#creation de twoClass //premiere ligne de BS
#ForceField AMOEBA-WATER
twoClassInstance5 = ValueClass(idParam=12,key = "KS",value=529.600)
twoClassInstance6 = ValueClass(idParam=12,key = "Length",value=0.9572)
session.add(twoClassInstance5)
session.add(twoClassInstance6)

#Ajout dans la ManyToMany
ClassAtom_ParamsClassInstance8 = ClassAtom_ParamsClass(description="1-2")
ClassAtom_ParamsClassInstance8.classAtomsInstance =  session.query(ClassAtom).get((1,5))
ClassAtom_ParamsClassInstance8.paramsClassInstance = session.query(ParamsClass).get(12)
ClassAtom_ParamsClassInstance9 = ClassAtom_ParamsClass(description="1-2")
ClassAtom_ParamsClassInstance9.classAtomsInstance =  session.query(ClassAtom).get((2,5))
ClassAtom_ParamsClassInstance9.paramsClassInstance = session.query(ParamsClass).get(12)


#creation de ThreeClass //Angle Bending du AMBER_FF98
#1ere ligne
threeClassInstance1 = ValueClass(idParam=5,key='KB',value=40.000)
threeClassInstance2 = ValueClass(idParam=5,key='Value1(R-X-R)',value=109.500)
session.add(threeClassInstance1)
session.add(threeClassInstance2)

#Ajout dans la ManyToMany
ClassAtom_ParamsClassInstance8 = ClassAtom_ParamsClass(description="1-1-1")
ClassAtom_ParamsClassInstance8.classAtomsInstance =  session.query(ClassAtom).get((1,1))
ClassAtom_ParamsClassInstance8.paramsClassInstance = session.query(ParamsClass).get(5)


#creation de ThreeClass //Angle Bending du AMOEBA-WATER
#1ere ligne
threeClassInstance3 = ValueClass(idParam=13,key='KB',value=34.050)
threeClassInstance4 = ValueClass(idParam=13,key='Value1(R-X-R)',value=108.500)
session.add(threeClassInstance3)
session.add(threeClassInstance4)

#Ajout dans la ManyToMany
ClassAtom_ParamsClassInstance9 = ClassAtom_ParamsClass(description="2-1-2")
ClassAtom_ParamsClassInstance9.classAtomsInstance =  session.query(ClassAtom).get((1,5))
ClassAtom_ParamsClassInstance9.paramsClassInstance = session.query(ParamsClass).get(13)
ClassAtom_ParamsClassInstance10 = ClassAtom_ParamsClass(description="2-1-2")
ClassAtom_ParamsClassInstance10.classAtomsInstance =  session.query(ClassAtom).get((2,5))
ClassAtom_ParamsClassInstance10.paramsClassInstance = session.query(ParamsClass).get(13)


#creation de ThreeClass //Urey-Bradley du AMOEBA-WATER
#1ere ligne
threeClassInstance5 = ValueClass(idParam=14,key='KB',value=38.250)
threeClassInstance6 = ValueClass(idParam=14,key='Distance',value=1.5537)
session.add(threeClassInstance5)
session.add(threeClassInstance6)

#Ajout dans la ManyToMany
ClassAtom_ParamsClassInstance11 = ClassAtom_ParamsClass(description="2-1-2")
ClassAtom_ParamsClassInstance11.classAtomsInstance =  session.query(ClassAtom).get((1,5))
ClassAtom_ParamsClassInstance11.paramsClassInstance = session.query(ParamsClass).get(14)
ClassAtom_ParamsClassInstance12 = ClassAtom_ParamsClass(description="2-1-2")
ClassAtom_ParamsClassInstance12.classAtomsInstance =  session.query(ClassAtom).get((2,5))
ClassAtom_ParamsClassInstance12.paramsClassInstance = session.query(ParamsClass).get(14)


#creation de FourClass //Improper Torsion du Amber_ff98
#premiere ligne
fourClassInstance1 = ValueClass(idParam=6,key='KTI',value=1.100)
fourClassInstance2 = ValueClass(idParam=6,key='Value1',value=180.0)
fourClassInstance3 = ValueClass(idParam=6,key='Value2',value=2)
session.add(fourClassInstance1)
session.add(fourClassInstance2)
session.add(fourClassInstance3)


#Ajout dans la ManyToMany
ClassAtom_ParamsClassInstance9 = ClassAtom_ParamsClass(description="3-3-2-22")
ClassAtom_ParamsClassInstance9.classAtomsInstance =  session.query(ClassAtom).get((3,1))
ClassAtom_ParamsClassInstance9.paramsClassInstance = session.query(ParamsClass).get(6)
ClassAtom_ParamsClassInstance10 = ClassAtom_ParamsClass(description="3-3-2-22")
ClassAtom_ParamsClassInstance10.classAtomsInstance =  session.query(ClassAtom).get((2,1))
ClassAtom_ParamsClassInstance10.paramsClassInstance = session.query(ParamsClass).get(6)
ClassAtom_ParamsClassInstance11 = ClassAtom_ParamsClass(description="3-3-2-22")
ClassAtom_ParamsClassInstance11.classAtomsInstance =  session.query(ClassAtom).get((22,1))
ClassAtom_ParamsClassInstance11.paramsClassInstance = session.query(ParamsClass).get(6)

#creation de paramType
paramTypeInstance1 = ParamsType(idParameter=3,idForceField=1)
paramTypeInstance2 = ParamsType(idParameter=3,idForceField=2)
paramTypeInstance3 = ParamsType(idParameter=3,idForceField=1)
paramTypeInstance4 = ParamsType(idParameter=3,idForceField=2)
paramTypeInstance5 = ParamsType(idParameter=7,idForceField=5)
paramTypeInstance6 = ParamsType(idParameter=7,idForceField=5)
paramTypeInstance7 = ParamsType(idParameter=8,idForceField=5)
paramTypeInstance8 = ParamsType(idParameter=8,idForceField=5)
session.add(paramTypeInstance1)
session.add(paramTypeInstance2)
session.add(paramTypeInstance3)
session.add(paramTypeInstance4)
session.add(paramTypeInstance5)
session.add(paramTypeInstance6)
session.add(paramTypeInstance7)
session.add(paramTypeInstance8)
#,tableName = "OneType"
#,tableName = "OneType"
#,tableName = "OneType"
#,tableName = "OneType"

#creation de OneType //Partial charge du Amber_ff98
#premiere ligne
oneTypeInstance1 = ValueType('Partial Chg', 1, -0.416)
session.add(oneTypeInstance1)
#deuxieme ligne
oneTypeInstance3 = ValueType('Partial Chg', 3, -0.025)
session.add(oneTypeInstance3)

#creation de OneType //Partial charge du Charm19
#premiere ligne
oneTypeInstance2 = ValueType('Partial Chg', 2, 0.250)
session.add(oneTypeInstance2)
#deuxieme ligne
oneTypeInstance4 = ValueType('Partial Chg', 4, 0.300)
session.add(oneTypeInstance4)


#creation de OneType //Atomic Multipole du AMOEBA-WATER
#premiere ligne
oneTypeInstance5 = ValueType('Axis Types', 5, 22)
oneTypeInstance6 = ValueType('Frame', 5, -0.51966)
oneTypeInstance7 = ValueType('Multipoles (M-D-Q)', 5, 0.14279)
session.add(oneTypeInstance5)
session.add(oneTypeInstance6)
session.add(oneTypeInstance7)
#deuxieme ligne
oneTypeInstance8 =  ValueType('Axis Types', 6, 12)
oneTypeInstance9 =  ValueType('Frame', 6, 0.25983)
oneTypeInstance10 = ValueType('Multipoles (M-D-Q)', 6, -0.05818)
session.add(oneTypeInstance8)
session.add(oneTypeInstance9)
session.add(oneTypeInstance10)

#creation de OneType //Dipole Polarizability du AMOEBA-WATER
#premiere ligne
oneTypeInstance11 = ValueType('Alpha', 7, 0.837)
oneTypeInstance12 = ValueType('Group Atom Types', 7, 2)
session.add(oneTypeInstance11)
session.add(oneTypeInstance12)
#deuxieme ligne
oneTypeInstance13 = ValueType('Alpha', 8, 0.496)
oneTypeInstance14 = ValueType('Group Atom Types', 8, 1)
session.add(oneTypeInstance13)
session.add(oneTypeInstance14)


#liaison avec many to many AtomsType_ParamType
#le OneTypeInstance1 est lier avec le ParamsTypeInstance1
#le OneTypeInstance1 fait partie du ForceField AMBER_FF98
#et est relier avec le idAtomType=1 de ce ForceField donc

#paramTypeInstance1 est lier:
#idForceField = 1 =>[AMBER_FF98]  
#idAtomType = 1 => [Type = 1]
#paramTypeInstance1.atomsTypeParents.append(session.query(AtomsType).get((1,1)))
AtomsType_ParamTypeInstance1 = AtomsType_ParamsType()
AtomsType_ParamTypeInstance1.atomsTypeInstance = session.query(AtomsType).get((1,1))
AtomsType_ParamTypeInstance1.paramsTypeInstance = paramTypeInstance1 #session.query(ParamsType).get(1)
#paramTypeInstance3 est lier:
#idForceField = 1 =>[AMBER_FF98]  
#idAtomType = 2 => [Type = 2]
#paramTypeInstance3.atomsTypeParents.append(session.query(AtomsType).get((2,1)))
AtomsType_ParamTypeInstance2 = AtomsType_ParamsType()
AtomsType_ParamTypeInstance2.atomsTypeInstance = session.query(AtomsType).get((2,1))
AtomsType_ParamTypeInstance2.paramsTypeInstance = paramTypeInstance3 #session.query(ParamsType).get(3)
#paramTypeInstance2 est lier:
#idForceField = 2 =>[CHARM19]  
#idAtomType = 1 => [Type = 1]
#paramTypeInstance2.atomsTypeParents.append(session.query(AtomsType).get((1,2)))
AtomsType_ParamTypeInstance3 = AtomsType_ParamsType()
AtomsType_ParamTypeInstance3.atomsTypeInstance = session.query(AtomsType).get((1,2))
AtomsType_ParamTypeInstance3.paramsTypeInstance = paramTypeInstance2 #session.query(ParamsType).get(2)

#paramTypeInstance4 est lier:
#idForceField = 2 =>[CHARM19]  
#idAtomType = 2 => [Type = 2]
#paramTypeInstance4.atomsTypeParents.append(session.query(AtomsType).get((2,2)))
AtomsType_ParamTypeInstance4 = AtomsType_ParamsType()
AtomsType_ParamTypeInstance4.atomsTypeInstance = session.query(AtomsType).get((2,2))
AtomsType_ParamTypeInstance4.paramsTypeInstance = paramTypeInstance4 #session.query(ParamsType).get(4)


#paramTypeInstance5 est lier:
#idForceField = 5 =>[AMOEBA-WATER]  
#idAtomType = 1 et 2 => [Type = 1, 2]
#paramTypeInstance4.atomsTypeParents.append(session.query(AtomsType).get((2,2)))
AtomsType_ParamTypeInstance5 = AtomsType_ParamsType()
AtomsType_ParamTypeInstance5.atomsTypeInstance = session.query(AtomsType).get((1,5))
AtomsType_ParamTypeInstance5.paramsTypeInstance = paramTypeInstance5 #session.query(ParamsType).get(5)
AtomsType_ParamTypeInstance6 = AtomsType_ParamsType()
AtomsType_ParamTypeInstance6.atomsTypeInstance = session.query(AtomsType).get((2,5))
AtomsType_ParamTypeInstance6.paramsTypeInstance = paramTypeInstance6 #session.query(ParamsType).get(6)


#paramTypeInstance7 et 8 est lier:
#idForceField = 5 =>[AMOEBA-WATER]  
#idAtomType = 1 et 2 => [Type = 1, 2]
#paramTypeInstance4.atomsTypeParents.append(session.query(AtomsType).get((2,2)))
AtomsType_ParamTypeInstance7 = AtomsType_ParamsType()
AtomsType_ParamTypeInstance7.atomsTypeInstance = session.query(AtomsType).get((1,5))
AtomsType_ParamTypeInstance7.paramsTypeInstance = paramTypeInstance7 #session.query(ParamsType).get(7)
AtomsType_ParamTypeInstance8 = AtomsType_ParamsType()
AtomsType_ParamTypeInstance8.atomsTypeInstance = session.query(AtomsType).get((2,5))
AtomsType_ParamTypeInstance8.paramsTypeInstance = paramTypeInstance8 #session.query(ParamsType).get(8)


session.commit()


print(bcolors.FAIL + '       ForceFieldTable' + bcolors.ENDC+'\n')
print('idForceField  nameForceField \n')
for instance in session.query(ForceField):
     print('{:^12}    {}'.format(instance.idForceField,instance.nameForceField))

print('----------------------------------------------------')
print(bcolors.FAIL +'                 ParameterTable' + bcolors.ENDC+'\n')
print('{:^11}  {:<40} {:^13}  {} \n'.format('idParameter','nameParameter','numberOfAtoms','classOrType'))
for instance in session.query(ParameterTable):
     print('{:^11}  {:<40} {:^13}  {}'.format(instance.idParameter,instance.nameParameter,str(instance.numberOfAtoms),str(instance.classOrType)))

print('----------------------------------------------------')
print(bcolors.FAIL +'           ScalingFactorTable ' + bcolors.ENDC+'\n')
print('{:<40}  {:^11} {:<12} {}\n'.format('nameScalingFactor','idForceField','idParameter','Description','Value'))
for instance in session.query(ScalingFactorTable):
     print('{:<40}  {:^11} {:<12} {}'.format(session.query(ParameterTable).get(instance.idParameter).nameParameter,instance.idForceField,instance.idParameter,instance.key,instance.value))    
  
print('----------------------------------------------------')
print(bcolors.FAIL +'          ConstantTable ' + bcolors.ENDC+'\n')
print('{:<40} {:^10} {:^20} {:<10} {:<13}\n'.format('nameConstant','idForceField','idParameter','key','value'))
for instance in session.query(ConstantTable):
    print('{:<40} {:^10} {:^20} {:<13} {:<13}'.format(session.query(ParameterTable).get(instance.idParameter).nameParameter,instance.idForceField,instance.idParameter, instance.key, instance.value))
  
print('----------------------------------------------------')
print(bcolors.FAIL +'                       classAtomTable ' + bcolors.ENDC+'\n')
print('idClassAtom  idForceField  symbol  atomicNumber  atomicWeight  valence\n')
for instance in session.query(ClassAtom):
     print('{:^12}{:^14}  {:<8}{:^13}    {:<9}{:^9}'.format(instance.idClassAtom,instance.idForceField,instance.symbol,instance.atomicNumber,instance.atomicWeight,instance.valence))

print('----------------------------------------------------')
print(bcolors.FAIL +'          AtomTypeTable ' + bcolors.ENDC+'\n')
print('{0} {1} {2} {3}\n'.format('idClassAtom','idForceField','idAtomType','Description'))
for instance in session.query(AtomsType):
     print('{:^11}{:^14}{:^11}{} '.format(instance.idClassAtom,instance.idForceField,instance.idAtomType,instance.description))

print('----------------------------------------------------')
print(bcolors.FAIL +'          ParamsClassTable ' + bcolors.ENDC+'\n')
print('idParam  idParameter idForceField tableName  nameParameter\n')
for instance in session.query(ParamsClass):
    print('{:^7} {:^13} {:^12} {:<10} {}'.format(instance.idParam,instance.idParameter,instance.idForceField, session.query(ParameterTable).get(instance.idParameter).numberOfAtoms,session.query(ParameterTable).get(instance.idParameter).nameParameter))

print('----------------------------------------------------')
print(bcolors.FAIL +'          ClassAtom_ParamsClass Table ' + bcolors.ENDC+'\n')
print('{} {} {} {}\n'.format('idClassAtom','idForceField','idParam','description'))
for instance in session.query(ClassAtom_ParamsClass):
  print('{:^11} {:^11} {:^7} {}'.format(instance.idClassAtom,instance.idForceField,instance.idParam,instance.description))

print('----------------------------------------------------')
print(bcolors.FAIL +'       OneClassTable ' + bcolors.ENDC+'\n')
print('idParam    Key         Value\n')
for instance in session.query(ValueClass):
    idParameter = session.query(ParamsClass).get(instance.idParam).idParameter
    if(session.query(ParameterTable).get(idParameter).numberOfAtoms == 1):
        print('{:^8}   {:<12}{}'.format(instance.idParam,instance.key,instance.value))

print('----------------------------------------------------')
print(bcolors.FAIL +'          TwoClassTable ' + bcolors.ENDC+'\n')
print('idParam    Key         Value\n')
for instance in session.query(ValueClass):
    idParameter = session.query(ParamsClass).get(instance.idParam).idParameter
    if(session.query(ParameterTable).get(idParameter).numberOfAtoms == 2):
        print('{:^8}   {:<12}{}'.format(instance.idParam,instance.key,instance.value))

print('----------------------------------------------------')
print(bcolors.FAIL +'          ThreeClassTable ' + bcolors.ENDC+'\n')
print('idParam        Key              Value\n')
for instance in session.query(ValueClass):
    idParameter = session.query(ParamsClass).get(instance.idParam).idParameter
    if(session.query(ParameterTable).get(idParameter).numberOfAtoms == 3):
        print('{:^8}   {:<12}{}'.format(instance.idParam,instance.key,instance.value))

print('----------------------------------------------------')
print(bcolors.FAIL +'          FourClassTable ' + bcolors.ENDC+'\n')
print('idParam    Key         Value\n')
for instance in session.query(ValueClass):
    idParameter = session.query(ParamsClass).get(instance.idParam).idParameter
    if(session.query(ParameterTable).get(idParameter).numberOfAtoms == 4):
        print('{:^8}   {:<12}{}'.format(instance.idParam,instance.key,instance.value))

print('----------------------------------------------------')
print(bcolors.FAIL +'          ParamType Table' + bcolors.ENDC+'\n')
print('idParam  idParameter idForceField  tableName  nameParameter\n')
for instance in session.query(ParamsType):
    print('{:^7} {:^13} {:^13} {:<10} {}'.format(instance.idParam,instance.idParameter,instance.idForceField,session.query(ParameterTable).get(instance.idParameter).numberOfAtoms,session.query(ParameterTable).get(instance.idParameter).nameParameter))

print('----------------------------------------------------')
print(bcolors.FAIL +'          OneTypeTable' + bcolors.ENDC+'\n')
print('idParam    Key           Value\n')
for instance in session.query(ValueType):
    idParameter = session.query(ParamsType).get(instance.idParam).idParameter
    if(session.query(ParameterTable).get(idParameter).numberOfAtoms == 1):
        print('{:^8}   {:<12}{}'.format(instance.idParam,instance.key,instance.value))

#Affichage de tous les SF qui appartiennent au AMBER_FF98
#utilisation du one to many entre ScalingFactorTable et Forcefield 
x = session.query(ForceField).get(1).childrenScalingFactor
print('----------------------------------------------------')
print(bcolors.FAIL +'     ScalingFactor belong to AMBER_FF98' + bcolors.ENDC+'\n')
print('idForceField  idParameter  Description  Value\n')
for instance in x:
  print('{:^13}  {:^11} {:<12} {}'.format(instance.idForceField,instance.idParameter,instance.key,instance.value))

#Apres les changement cette requette ne peut plus se faire
#Affichage de tous les SF qui sont lier a AtomicPartialCharge
#utilisation du one to many entre ScalingFactor et ParameterTable
#x = session.query(ParameterTable).get(3).childrenScalingFactor
#print('----------------------------------------------------')
#print(bcolors.FAIL +'   ScalingFactor of AtomicPartialCharge\'s Parameter' + bcolors.ENDC+'\n')
#print('idForceField  idParameter  Description  Value\n')
#for instance in x:
#  print('{:^13}  {:^11} {:<12} {}'.format(instance.idForceField,instance.idParameter,instance.key,instance.value))

#Affichage de tous le AtomType qui sont lier au ClassAtom 1 du ForceField 2
#utilisation du one to many entre AtomType et ClassAtom 
print('----------------------------------------------------')
print(bcolors.FAIL +'   Atoms Type of CHARMM27 belong to ClassAtom number 1' + bcolors.ENDC+'\n')
print('{0} {1} {2}\n'.format('ClassAtom','ForceField','Description'))
x = session.query(ClassAtom).get((1,2)).atoms_typeChildren
for instance in x:
  print('{0:^9}{1:^12}{2} '.format(instance.idClassAtom,instance.idForceField,instance.description))



print('----------------------------------------------------')
print(bcolors.FAIL +'   Many To Many between AtomsType/ParamsType ' + bcolors.ENDC+'\n')
print(bcolors.FAIL +'   ParamType belong to ForceField Amber_ff98 ' + bcolors.ENDC+'\n')
#Affichage de la Table many to many entre AtomType et ParamType
x = session.query(ParamsType).filter(ParamsType.atomsTypeParents.any(idForceField=1)).all()
for instance in x:
   print(instance.idParam,instance.idParameter,session.query(ParameterTable).get(instance.idParameter).nameParameter)

print('----------------------------------------------------')
print(bcolors.FAIL +'   Many To Many between AtomsType/ParamsType' + bcolors.ENDC+'\n')
print(bcolors.FAIL +'  ParamType bound to idAtomType = 1' + bcolors.ENDC+'\n')
#Affichage de la Table many to many entre AtomType et ParamType
x = session.query(ParamsType).filter(ParamsType.atomsTypeParents.any(idAtomType=1)).all()
for instance in x:
   print(instance.idParam,instance.idParameter,session.query(ParameterTable).get(instance.idParameter).nameParameter)

print('----------------------------------------------------')
print(bcolors.FAIL +'   Many To Many between AtomsType/ParamsType' + bcolors.ENDC+'\n')
print(bcolors.FAIL +'ParamType belong to AMBER_FF98 and bound to idAtomType = 1' + bcolors.ENDC+'\n')
#Affichage de la Table many to many entre AtomType et ParamType
x = session.query(ParamsType).filter(ParamsType.atomsTypeParents.any(idForceField=1,idAtomType=1)).all()
for instance in x:
   print(instance.idParam,instance.idParameter,session.query(ParameterTable).get(instance.idParameter).nameParameter)




print('----------------------------------------------------')
print(bcolors.FAIL +'   Many to Many between ClassAtom/ParamsClass' + bcolors.ENDC+'\n')
print(bcolors.FAIL +' idParam bound to idClassAtom=1 && idForceField=1' + bcolors.ENDC+'\n')
x = session.query(ClassAtom).get((1,1)).paramsClassChildren
for instance in x:
  print('{} '.format(instance.idParam),end="")
print('\n')


print('----------------------------------------------------')
print(bcolors.FAIL +'   Many to Many between ClassAtom/ParamsClass' + bcolors.ENDC+'\n')
print(bcolors.FAIL +'   idClassAtom belong to idParam 6' + bcolors.ENDC+'\n')
x = session.query(ParamsClass).get(6).classAtomsParents
for instance in x:
  print('{} '.format(instance.idClassAtom),end="")
print('\n')


print('----------------------------------------------------')
print(bcolors.FAIL +'   idParam belong to Forcefield amberFF98'+ bcolors.ENDC+'\n')
x = session.query(ForceField).get(1).childrenParamClass
for instance1 in x:
  paramInstance =  session.query(ParamsClass).get(instance1.idParam)
  parameterInstance = session.query(ParameterTable).get(paramInstance.idParameter)
  #je verifie si le idParam est bien de type class
  if(parameterInstance.classOrType == "class"):
    print('idParam:            {}'.format(instance1.idParam))
    xx = session.query(ParameterTable).get(instance1.idParameter).nameParameter
    xx = xx + ":"
    print('{:<20}'.format(xx),end="")
    valueParams = session.query(ValueClass).filter(ValueClass.idParam == paramInstance.idParam)
    for instance3 in valueParams:
      print('{} = {}, '.format(instance3.key,instance3.value),end="")
    y = session.query(ParamsClass).get(instance1.idParam).classAtomsParents
    description = session.query(ClassAtom_ParamsClass).filter(ClassAtom_ParamsClass.idParam == instance1.idParam).first().description
    print('')
    for instance2 in y:
      x = session.query(ClassAtom).get((instance2.idClassAtom,1))
      print('ClassAtoms:         {:<3} {:<3} {} {} {}'.format(x.idClassAtom,x.symbol,x.atomicNumber,x.atomicWeight,x.valence)) 
    if(description != None):
      print('Description:        ' + description)
  print('')

#pour afficher tous les parametre d'un forcefield ici 
#le forcfield numero 1
print('\n----------------------------------------------------')
print(bcolors.FAIL +'Display all Parameter(without SF/C) of AMBER_FF98'+ bcolors.ENDC+'\n')
listOfParams = session.query(ForceField).get(1).childrenParamClass
listOfParameter = [x.idParameter for x in listOfParams]
listOfParameter = list(set(listOfParameter))
for number in listOfParameter:
    print (session.query(ParameterTable).get(number).nameParameter)

print('')

#Pour afficher la many to many entre forcefield et parametreTable
print('----------------------------------------------------')
print(bcolors.FAIL +'   Many To Many between ForceField/ParameterTable' + bcolors.ENDC+'\n')
#print(bcolors.FAIL +'Parameter belong to AMOEBA-WATER' + bcolors.ENDC+'\n')
#Affichage de la Table many to many entre AtomType et ParamType
#x = session.query(ParameterTable).filter(ParameterTable.associatedForcefield.any(idForceField=5)).all()
print('{:<14} {}\n'.format('ForceField','Parameter'))
for instance in session.query(ParametersOfForceField):
   print('{:<14} {}'.format(session.query(ForceField).get(instance.idForceField).nameForceField,session.query(ParameterTable).get(instance.idParameter).nameParameter))


#Pour afficher la many to many entre forcefield et parametreTable
print('----------------------------------------------------')
print(bcolors.FAIL +'   Many To Many between ForceField/ParameterTable' + bcolors.ENDC+'\n')
print(bcolors.FAIL +'Parameter belong to AMOEBA-WATER' + bcolors.ENDC+'\n')
x = session.query(ForceField).get(5).childrenParameter
# x c'est une liste d'objet de parametersOfForceField
print('{:<14} {}\n'.format('ForceField','Parameter'))
for instance in x:
   print('{:<14} {}'.format(session.query(ForceField).get(instance.idForceField).nameForceField,session.query(ParameterTable).get(instance.idParameter).nameParameter))

#pour afficher les SF de AMOEBA-WATER
print('\n----------------------------------------------------')
print(bcolors.FAIL +'scaling Factor belong to AMOEBA-WATER' + bcolors.ENDC+'\n')
print('{:<14} {}\n'.format('ForceField','ScalingFactor'))
# x c'est une liste d'objet de la table de ParameterTable
x = session.query(ForceField).get(5).childrenParameter
for instance in x:
    parameterInstance = session.query(ParameterTable).get(instance.idParameter)
    if(parameterInstance.parameterType == 'SF'):
        print('{:<14} {}'.format(session.query(ForceField).get(5).nameForceField,parameterInstance.nameParameter))


#pour afficher les constants de AMOEBA-WATER
print('\n----------------------------------------------------')
print(bcolors.FAIL +'constant belong to AMOEBA-WATER' + bcolors.ENDC+'\n')
print('{:<14} {}\n'.format('ForceField','constantName'))
# x c'est une liste d'objet de la table de ParameterTable
x = session.query(ForceField).get(5).childrenParameter
for instance in x:
    parameterInstance = session.query(ParameterTable).get(instance.idParameter)
    if(parameterInstance.parameterType == 'Constant'):
        print('{:<14} {}'.format(session.query(ForceField).get(5).nameForceField,parameterInstance.nameParameter))

#pour afficher les Users et leurs FF
print('\n----------------------------------------------------')
print(bcolors.FAIL +'\tUser and their FF' + bcolors.ENDC+'\n')
users = session.query(User).all()
for user_instance in users:
    print(user_instance.firstname,user_instance.lastname,end="")
    print(' --> ',end="")
    for ff_list in user_instance.forcefield_list:
        print(session.query(ForceField).get(ff_list.idForceField).nameForceField,end="")
        print("(" + str(ff_list.isAuthor) +")", end="")
        print(" ",end="")
    print(' ')
print(" ")

user = session.query(User).get(1)
session.query(User).filter(User.user_id==1).update({'username':'danielmo'})

users = session.query(User).all()
for user_instance in users:
    print(user_instance.username)




#pour afficher toutes les valeur d'une table 
#pour un parametre et forcefield donnee
#ici j'ai pris AMBER_FF98 et VDW

#http://stackoverflow.com/questions/23654652/how-to-retrieve-data-from-tables-with-relationships-many-to-many-sqlalchemy
