from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os.path
if(os.path.isfile('sqlalchemy_table.db')):
  os.remove('sqlalchemy_table.db')
from sqlalchemy.event import listen
from CreationTable import * 
from sqlalchemy import inspect

instancesToDelete = []
errorMessages = {}

@event.listens_for(ParamsClass, 'before_insert')
def checkClass(mapper, connect, self):
    parameterInstance = session.query(ParameterTable).get(self.idParameter) 
    #dictionary
    options = { 1:"One",2:"Two",3:"Three",4:"Four",5:"Five"}
    if(parameterInstance.classOrType == "type"):
        #raise ValueError ("Couldn't be of type \"type\"")
        #d'apres ce qui est ecrit dans le warning de ce lien
        #http://docs.sqlalchemy.org/en/improve_toc/orm/events.html
        #on ne peut pas changer le state d'un objet dans le before
        #insert event je le fait donc dans le before commit
        #ce event me sert juste a reperer les erreurs
        #cette event me sert aussi a remplir le champ "tableName"
        errorMessages[self] = "incompatible type"
        self.tableName = options[parameterInstance.numberOfAtoms]+"Type"
        instancesToDelete.append(self)
    if(parameterInstance.classOrType == "class"):
        self.tableName = options[parameterInstance.numberOfAtoms]+"Class"

@event.listens_for(ParamsType, 'before_insert')
def checkType(mapper, connect, self):
    parameterInstance = session.query(ParameterTable).get(self.idParameter) 
    #dictionary
    options = { 1:"One",2:"Two",3:"Three",4:"Four",5:"Five"}
    if(parameterInstance.classOrType == "type"):
        #raise ValueError ("Couldn't be of type \"type\"")
        #d'apres ce qui est ecrit dans le warning de ce lien
        #http://docs.sqlalchemy.org/en/improve_toc/orm/events.html
        #on ne peut pas changer le state d'un objet dans le before
        #insert event je le fait donc dans le before commit
        #ce event me sert juste a reperer les erreurs
        #cette event me sert aussi a remplir le champ "tableName"
        self.tableName = options[parameterInstance.numberOfAtoms]+"Type"
    if(parameterInstance.classOrType == "class"):
        errorMessages[self] = "incompatible class"
        self.tableName = options[parameterInstance.numberOfAtoms]+"Class"
        instancesToDelete.append(self)

listen(ParamsClass, 'before_insert', checkClass)
listen(ParamsType, 'before_insert', checkType)

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
session.add(amberFF98)
session.add(charmm19)
session.add(charmm27)
session.add(opls_aa)

#creation de Parameter
van_der_walls = ParameterTable('Van Der Waals',1,'class')
bond_stretching = ParameterTable('Bond Stretching',2,'class')
partial_charge = ParameterTable('Atomic Partial Charge',1,'type')
angle_bending = ParameterTable('Angle Bending',3,'class')
improperTorsion = ParameterTable('Improper Torsion',4,'class')
#jeTest = ParameterTable(nameParameter='Je Test',classOrType='Test')
#session.add(jeTest) // le test du Enum marche !!
session.add(van_der_walls)
session.add(bond_stretching)
session.add(partial_charge)
session.add(angle_bending)
session.add(improperTorsion)

#creation de ScalingFactor
Atomic_Partial_Charge_SF_1 = ScalingFactorTable(1,'Atomic Partial Charge Scalings Factors','1-2 Atoms',0.000,3)
Atomic_Partial_Charge_SF_2 = ScalingFactorTable(1,'Atomic Partial Charge Scalings Factors','1-3 Atoms',0.000,3)
Atomic_Partial_Charge_SF_3 = ScalingFactorTable(1,'Atomic Partial Charge Scalings Factors','1-4 Atoms',0.833,3)
Atomic_Partial_Charge_SF_4 = ScalingFactorTable(1,'Atomic Partial Charge Scalings Factors','1-5 Atoms',1.000,3)
Van_der_Waals_SF_1 = ScalingFactorTable(2,'Van Der Waals Scalings Factors','1-2 Atoms',0.000,1)
Van_der_Waals_SF_2 = ScalingFactorTable(2,'Van Der Waals Scalings Factors','1-3 Atoms',0.000,1)
Van_der_Waals_SF_3 = ScalingFactorTable(2,'Van Der Waals Scalings Factors','1-4 Atoms',1.000,1)
Van_der_Waals_SF_4 = ScalingFactorTable(2,'Van Der Waals Scalings Factors','1-5 Atoms',1.000,1)
Atomic_Partial_Charge_SF_5 = ScalingFactorTable(2,'Atomic Partial Charge Scalings Factors','1-2 Atoms',0.000,3)
Atomic_Partial_Charge_SF_6 = ScalingFactorTable(2,'Atomic Partial Charge Scalings Factors','1-3 Atoms',0.000,3)
Atomic_Partial_Charge_SF_7 = ScalingFactorTable(2,'Atomic Partial Charge Scalings Factors','1-4 Atoms',1.000,3)
Atomic_Partial_Charge_SF_8 = ScalingFactorTable(2,'Atomic Partial Charge Scalings Factors','1-5 Atoms',1.000,3)
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
session.add(paramsClassInstance1)
session.add(paramsClassInstance2)
session.add(paramsClassInstance3)
session.add(paramsClassInstance4)
session.add(paramsClassInstance5)
session.add(paramsClassInstance6)
session.add(paramsClassInstance7)
session.add(paramsClassInstance8)
session.add(paramsClassInstance9)

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
OneClassInstance1 = OneClass(idParam=1,key = "Radius",value=1.908)
OneClassInstance2 = OneClass(idParam=1,key = "Epsilon",value=0.109)
OneClassInstance3 = OneClass(idParam=1,key = "Reduction",value=0.000)
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
OneClassInstance4 = OneClass(idParam=3,key = "Radius",value=1.908)
OneClassInstance5 = OneClass(idParam=3,key = "Epsilon",value=0.086)
OneClassInstance6 = OneClass(idParam=3,key = "Reduction",value=0.000)
session.add(OneClassInstance4)
session.add(OneClassInstance5)
session.add(OneClassInstance6)

#Ajout dans la ManyToMany
ClassAtom_ParamsClassInstance2 = ClassAtom_ParamsClass()
ClassAtom_ParamsClassInstance2.classAtomsInstance =  session.query(ClassAtom).get((2,1))
ClassAtom_ParamsClassInstance2.paramsClassInstance = session.query(ParamsClass).get(3)

#creation de OneClass //premiere ligne de VDW
#pour le FF CHARM19
OneClassInstance7 = OneClass(idParam=7,key = "Radius",value=0.800)
OneClassInstance8 = OneClass(idParam=7,key = "Epsilon",value=0.050)
OneClassInstance9 = OneClass(idParam=7,key = "Reduction",value=0.000)
session.add(OneClassInstance7)
session.add(OneClassInstance8)
session.add(OneClassInstance9)

#Ajout dans la ManyToMany
ClassAtom_ParamsClassInstance3 = ClassAtom_ParamsClass()
ClassAtom_ParamsClassInstance3.classAtomsInstance =  session.query(ClassAtom).get((1,2))
ClassAtom_ParamsClassInstance3.paramsClassInstance = session.query(ParamsClass).get(7)


#creation de OneClass //premiere ligne de VDW
#pour le FF CHARM27
OneClassInstance10 = OneClass(idParam=8,key = "Radius",value=0.800)
OneClassInstance11 = OneClass(idParam=8,key = "Epsilon",value=0.050)
OneClassInstance12 = OneClass(idParam=8,key = "Reduction",value=0.000)
session.add(OneClassInstance10)
session.add(OneClassInstance11)
session.add(OneClassInstance12)

#Ajout dans la ManyToMany
ClassAtom_ParamsClassInstance4 = ClassAtom_ParamsClass()
ClassAtom_ParamsClassInstance4.classAtomsInstance =  session.query(ClassAtom).get((1,3))
ClassAtom_ParamsClassInstance4.paramsClassInstance = session.query(ParamsClass).get(8)



#creation de twoClass //deuxieme ligne de BS
#ForceField AMBER_FF98
twoClassInstance1 = TwoClass(idParam=2,key = "KS",value=317.000)
twoClassInstance2 = TwoClass(idParam=2,key = "Length",value=1.5220)
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
twoClassInstance3 = TwoClass(idParam=9,key = "KS",value=317.000)
twoClassInstance4 = TwoClass(idParam=9,key = "Length",value=1.5220)
session.add(twoClassInstance3)
session.add(twoClassInstance4)

#Ajout dans la ManyToMany
ClassAtom_ParamsClassInstance7 = ClassAtom_ParamsClass(description="1-1")
ClassAtom_ParamsClassInstance7.classAtomsInstance =  session.query(ClassAtom).get((1,1))
ClassAtom_ParamsClassInstance7.paramsClassInstance = session.query(ParamsClass).get(9)


#creation de ThreeClass //Angle Bending du AMBER_FF98
#1ere ligne
threeClassInstance1 = ThreeClass(idParam=5,key='KB',value=40.000)
threeClassInstance2 = ThreeClass(idParam=5,key='Value1(R-X-R)',value=109.500)
session.add(threeClassInstance1)
session.add(threeClassInstance2)

#Ajout dans la ManyToMany
ClassAtom_ParamsClassInstance8 = ClassAtom_ParamsClass(description="1-1-1")
ClassAtom_ParamsClassInstance8.classAtomsInstance =  session.query(ClassAtom).get((1,1))
ClassAtom_ParamsClassInstance8.paramsClassInstance = session.query(ParamsClass).get(5)


#creation de FourClass //Improper Torsion du Amber_ff98
#premiere ligne
fourClassInstance1 = FourClass(idParam=6,key='KTI',value=1.100)
fourClassInstance2 = FourClass(idParam=6,key='Value1',value=180.0)
fourClassInstance3 = FourClass(idParam=6,key='Value2',value=2)
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
session.add(paramTypeInstance1)
session.add(paramTypeInstance2)
session.add(paramTypeInstance3)
session.add(paramTypeInstance4)
#,tableName = "OneType"
#,tableName = "OneType"
#,tableName = "OneType"
#,tableName = "OneType"

#creation de OneType //Partial charge du Amber_ff98
#premiere ligne
oneTypeInstance1 = OneType('Partial Chg', 1, -0.416)
session.add(oneTypeInstance1)
#deuxieme ligne
oneTypeInstance3 = OneType('Partial Chg', 3, -0.025)
session.add(oneTypeInstance3)

#creation de OneType //Partial charge du Charm19
#premiere ligne
oneTypeInstance2 = OneType('Partial Chg', 2, 0.250)
session.add(oneTypeInstance2)
#deuxieme ligne
oneTypeInstance4 = OneType('Partial Chg', 4, 0.300)
session.add(oneTypeInstance4)

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


session.commit()




print(bcolors.FAIL + '       ForceFieldTable' + bcolors.ENDC+'\n')
print('idForceField  nameForceField \n')
for instance in session.query(ForceField):
     print('{:^12}    {}'.format(instance.idForceField,instance.nameForceField))

print('----------------------------------------------------')
print(bcolors.FAIL +'                 ParameterTable' + bcolors.ENDC+'\n')
print('idParameter  nameParameter            numberOfAtoms  classOrType\n')
for instance in session.query(ParameterTable):
     print('{:^11}  {:<25} {:^13}  {}'.format(instance.idParameter,instance.nameParameter,instance.numberOfAtoms,instance.classOrType))

print('----------------------------------------------------')
print(bcolors.FAIL +'           ScalingFactorTable ' + bcolors.ENDC+'\n')
print('idForceField  idParameter  Description  Value     nameScalingsFactor\n')
for instance in session.query(ScalingFactorTable):
     print('{:^13}  {:^11} {:<12} {}      {}'.format(instance.idForceField,instance.idParameter,instance.key,instance.value,instance.nameScalingFactor))
     
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
    print('{:^7} {:^13} {:^12} {:<10} {}'.format(instance.idParam,instance.idParameter,instance.idForceField, instance.tableName,session.query(ParameterTable).get(instance.idParameter).nameParameter))

print('----------------------------------------------------')
print(bcolors.FAIL +'          ClassAtom_ParamsClass Table ' + bcolors.ENDC+'\n')
print('{} {} {} {}\n'.format('idClassAtom','idForceField','idParam','description'))
for instance in session.query(ClassAtom_ParamsClass):
  print('{:^11} {:^11} {:^7} {}'.format(instance.idClassAtom,instance.idForceField,instance.idParam,instance.description))

print('----------------------------------------------------')
print(bcolors.FAIL +'       OneClassTable ' + bcolors.ENDC+'\n')
print('idParam    Key         Value\n')
for instance in session.query(OneClass):
    print('{:^8}   {:<12}{}'.format(instance.idParam,instance.key,instance.value))

print('----------------------------------------------------')
print(bcolors.FAIL +'          TwoClassTable ' + bcolors.ENDC+'\n')
print('idParam    Key         Value\n')
for instance in session.query(TwoClass):
    print('{:^8}   {:<12}{}'.format(instance.idParam,instance.key,instance.value))

print('----------------------------------------------------')
print(bcolors.FAIL +'          ThreeClassTable ' + bcolors.ENDC+'\n')
print('idParam        Key              Value\n')
for instance in session.query(ThreeClass):
    print('{:^8}       {:<17}{}'.format(instance.idParam,instance.key,instance.value))

print('----------------------------------------------------')
print(bcolors.FAIL +'          FourClassTable ' + bcolors.ENDC+'\n')
print('idParam    Key         Value\n')
for instance in session.query(FourClass):
    print('{:^8}   {:<12}{}'.format(instance.idParam,instance.key,instance.value))

print('----------------------------------------------------')
print(bcolors.FAIL +'          ParamType Table' + bcolors.ENDC+'\n')
print('idParam  idParameter idForceField  tableName  nameParameter\n')
for instance in session.query(ParamsType):
    print('{:^7} {:^13} {:^13} {:<10} {}'.format(instance.idParam,instance.idParameter,instance.idForceField,instance.tableName,session.query(ParameterTable).get(instance.idParameter).nameParameter))

print('----------------------------------------------------')
print(bcolors.FAIL +'          OneTypeTable' + bcolors.ENDC+'\n')
print('idParam    Key           Value\n')
for instance in session.query(OneType):
    print('{:^8}   {:<12}  {}'.format(instance.idParam,instance.key,instance.value))

#Affichage de tous les SF qui appartiennent au AMBER_FF98
#utilisation du one to many entre ScalingFactorTable et Forcefield 
x = session.query(ForceField).get(1).childrenScalingFactor
print('----------------------------------------------------')
print(bcolors.FAIL +'     ScalingFactor belong to AMBER_FF98' + bcolors.ENDC+'\n')
print('idForceField  idParameter  Description  Value\n')
for instance in x:
  print('{:^13}  {:^11} {:<12} {}'.format(instance.idForceField,instance.idParameter,instance.key,instance.value))

#Affichage de tous les SF qui sont lier a AtomicPartialCharge
#utilisation du one to many entre ScalingFactor et ParameterTable
x = session.query(ParameterTable).get(3).childrenScalingFactor
print('----------------------------------------------------')
print(bcolors.FAIL +'   ScalingFactor of AtomicPartialCharge\'s Parameter' + bcolors.ENDC+'\n')
print('idForceField  idParameter  Description  Value\n')
for instance in x:
  print('{:^13}  {:^11} {:<12} {}'.format(instance.idForceField,instance.idParameter,instance.key,instance.value))

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
print(bcolors.FAIL +'  One Class where idParam = 1' + bcolors.ENDC+'\n')
x = session.query(OneClass).filter(OneClass.idParam == 1).all()
for instance in x:
  print(instance.idParam,instance.key,instance.value)

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
    valueParams = session.query(eval(paramInstance.tableName)).filter(eval(paramInstance.tableName).idParam == paramInstance.idParam)
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
print('')
listOfParams = session.query(ForceField).get(1).childrenParamClass
listOfParameter = [x.idParameter for x in listOfParams]
listOfParameter = list(set(listOfParameter))
for number in listOfParameter:
    print (session.query(ParameterTable).get(number).nameParameter)

print('')
#pour afficher toutes les valeur d'une table 
#pour un parametre et forcefield donnee
#ici j'ai pris AMBER_FF98 et VDW

#http://stackoverflow.com/questions/23654652/how-to-retrieve-data-from-tables-with-relationships-many-to-many-sqlalchemy


#pour suprimer le fichier pour pouvoir
#reexecuter plusieurs fois
#os.remove('sqlalchemy_table.db')
