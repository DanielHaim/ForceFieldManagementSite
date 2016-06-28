from flask.json import JSONEncoder
from json import loads
from flask import session,g
from app import db
from .models import *
import sys


#class to get object back form dict
class obj(object):
    def __init__(self, d):
        for a, b in d.items():
            if isinstance(b, (list, tuple)):
               setattr(self, a, [obj(x) if isinstance(x, dict) else x for x in b])
            else:
               setattr(self, a, obj(b) if isinstance(b, dict) else b)



def objDecoder(obj):
    if '__type__' in obj and obj['__type__'] == 'constantScalingFactorData':
        return ConstantScalingFactorData(obj['idParameter'],obj['keyValue'],obj['key'],obj['headerUpdate'],obj['oldValue'],obj['value'])
    if '__type__' in obj and obj['__type__'] == 'AtomClassDefinition':
        return AtomClassDefinition(obj['idClassAtom'],obj['symbol'],obj['atomicNumber'],obj['atomicWeight'],obj['valence'],obj['idAtomType'],obj['description'],
                 True if obj['existClass']=="true" else False, obj['headerUpdate'], obj['oldValue'], obj['table'],obj['newExistClass'],obj['actualValue'])
    if  '__type__' in obj and obj['__type__'] == 'parameterClassOrType':
        return parameterClassOrType(obj['typeOrClass'],obj['idParameter'],obj['tableName'],obj['descriptionForClass'],obj['keyValue'],obj['idParam'],
                 obj['headerUpdate'],obj['oldValue'],obj['key'],obj['value'])
    if  '__type__' in obj and obj['__type__'] == 'UndoRedoObject':
        return UndoRedoObject(obj['operation'],obj['nameForceField'],obj['nameParameter'],obj['atomClassDefinitionList'],obj['constantScalingFactorDataList'],
            obj['parameterClassOrTypeList'],True if obj['exist']=="true" else False,obj['typeParam'],obj['oldValue'],obj['numberAtoms'] if obj['numberAtoms'] else None,
            obj['classOrType'] if obj['classOrType'] else None,obj['nameColumns'] if obj['nameColumns'] else None,obj['listParameterNameFF'],obj['listUserOfForceField'],obj['ownerFF'])
    return obj


class CustomJSONEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ConstantScalingFactorData):
            result =  {"__type__":"constantScalingFactorData",
                       "idParameter":obj.idParameter,
                       "keyValue":obj.keyValue,
                       "key":obj.key,
                       "headerUpdate":obj.headerUpdate,
                       "oldValue":obj.oldValue,
                       "value":obj.value}
            return result
        if isinstance(obj,AtomClassDefinition):
            result = {"__type__":"AtomClassDefinition",
                      "idClassAtom":obj.idClassAtom,
                      "symbol":obj.symbol,
                      "atomicNumber":obj.atomicNumber,
                      "atomicWeight":obj.atomicWeight,
                      "valence":obj.valence,
                      "idAtomType":obj.idAtomType,
                      "description":obj.description,
                      "existClass":'true' if obj.existClass else 'false',
                      "headerUpdate":obj.headerUpdate,
                      "oldValue":obj.oldValue,
                      "table":obj.table,
                      "newExistClass":obj.newExistClass,
                      "actualValue":obj.actualValue}
            return result
        if isinstance(obj,parameterClassOrType):
            result = {"__type__":"parameterClassOrType",
                      "typeOrClass":obj.typeOrClass,
                      "idParameter":obj.idParameter,
                      "tableName":obj.tableName,
                      "descriptionForClass":obj.descriptionForClass,
                      "keyValue":obj.keyValue,
                      "idParam":obj.idParam,
                      "headerUpdate":obj.headerUpdate,
                      "oldValue":obj.oldValue,
                      "key":obj.key,
                      "value":obj.value}
            return result
        if isinstance(obj,UndoRedoObject):
            result = {"__type__":"UndoRedoObject",
                      "operation":obj.operation,
                      "nameForceField":obj.nameForceField,
                      "nameParameter":obj.nameParameter,
                      "atomClassDefinitionList":obj.atomClassDefinitionList,
                      "constantScalingFactorDataList":obj.constantScalingFactorDataList,
                      "parameterClassOrTypeList":obj.parameterClassOrTypeList,
                      "listParameterNameFF":obj.listParameterNameFF,
                      "listUserOfForceField":obj.listUserOfForceField,
                      "exist":"true" if obj.exist else "false",
                      "typeParam":obj.typeParam,
                      "numberAtoms":obj.numberAtoms  if obj.numberAtoms else "",
                      "classOrType":obj.classOrType if obj.classOrType else "",
                      "nameColumns":obj.nameColumns if obj.nameColumns else "",
                      "oldValue":obj.oldValue,
                      "ownerFF":obj.ownerFF}
            return result
        else:
            JSONEncoder.default(self, obj)


class UndoRedoObject:

    operation = ''
    nameForceField = ''
    nameParameter = ''
    constantScalingFactorDataList = []
    atomClassDefinitionList = []
    parameterClassOrTypeList = []
    exist = False
    typeParam = ''
    numberAtoms = None
    classOrType = None
    nameColumns = None
    oldValue = ''
    ownerFF = '' 
    listParameterNameFF = []
    listUserOfForceField = []


    def __init__(self, operation,nameForceField,nameParameter="",atomClassDefinitionList=[],
        constantScalingFactorDataList=[],parameterClassOrTypeList=[],exist=False,typeParam="",oldValue="",
        numberAtoms=None,classOrType=None,nameColumns=None,listParameterNameFF=[],listUserOfForceField=[],ownerFF=''):
        self.operation = operation # l'operation qui a ete operer add/delete/update
        self.nameForceField = nameForceField
        self.nameParameter = nameParameter
        #There is an object of AtomClassDefinition/constantSF/parameterClassOrType
        self.atomClassDefinitionList = atomClassDefinitionList[:] #copy the list of AtomClassDefinition object
        self.constantScalingFactorDataList = constantScalingFactorDataList[:] #copy the list of constantScalingFactorData object
        self.parameterClassOrTypeList = parameterClassOrTypeList[:]
        self.exist = exist
        self.typeParam=typeParam
        self.numberAtoms=numberAtoms
        self.classOrType=classOrType
        self.nameColumns=nameColumns
        self.oldValue = oldValue
        self.listParameterNameFF = listParameterNameFF[:]
        self.listUserOfForceField = listUserOfForceField[:]



class ConstantScalingFactorData:
    def __init__(self,idParameter=-1,keyValue={},key="",headerUpdate="", oldValue="",value=""):
        self.idParameter = idParameter
        self.keyValue = keyValue.copy() #Make copy ofDictionary of key/value that represent all the key value of this constant
        self.key = key
        self.headerUpdate = headerUpdate
        self.oldValue = oldValue
        self.value = value


class AtomClassDefinition:
    def __init__(self, idClassAtom=-1,symbol="",atomicNumber=-1,atomicWeight=-1,valence=-1,idAtomType=-1,description="",
                 existClass=False, headerUpdate="", oldValue="", table="",newExistClass="",actualValue=""):
        self.idClassAtom = idClassAtom
        self.symbol = symbol
        self.atomicNumber = atomicNumber
        self.atomicWeight = atomicWeight
        self.valence = valence
        self.idAtomType = idAtomType
        self.description = description
        self.existClass = existClass #FOr the add row operation, he help me to know if the class was new class or not
        self.headerUpdate = headerUpdate
        self.oldValue = oldValue
        self.table = table
        self.newExistClass = newExistClass
        self.actualValue = actualValue



class parameterClassOrType:
    def __init__(self, typeOrClass="",idParameter=-1,tableName="",descriptionForClass="",keyValue={},idParam=-1,
                 headerUpdate="",oldValue="",key="",value=""):
        self.typeOrClass = typeOrClass
        self.idParameter = idParameter
        self.tableName = tableName
        self.descriptionForClass = descriptionForClass
        self.keyValue = keyValue
        self.idParam = idParam
        self.headerUpdate = headerUpdate
        self.oldValue = oldValue
        self.key = key
        self.value = value

#in jqxTool the attribute is 'disabled':false ==> 'enable':true
#and 'disable':true ==> 'enable':false
def sessionData(operation=None,nameForceField=None,nameParameter=None):
    sessionStr = '{"undo":' 
    if session['undo']:
        sessionStr += "false" 
    else: 
        sessionStr += "true"
    sessionStr += ',"redo":'
    if session['redo']:
        sessionStr += "false" 
    else:
        sessionStr += "true"
    sessionStr += ',"save":'
    if session['save']:
        sessionStr += "false" 
    else:
        sessionStr +=  "true"
    sessionStr +=',"operation":'
    if(operation):
        sessionStr += '"' + operation + '"'
    else:
        sessionStr += "null"
    sessionStr +=',"nameForceField":'
    if(nameForceField):
        sessionStr += '"' + nameForceField + '"'
    else:
        sessionStr += "null"
    sessionStr +=',"nameParameter":'
    if(nameParameter):
        sessionStr += '"' + nameParameter + '"'
    else:
        sessionStr += "null"
    sessionStr += '}'
    
    return sessionStr

def flashIndex(msg,typeMsg,sessionStr=None):
    result = '{"msg":"'+ msg + '",'
    result += '"type":"' + typeMsg + '"'
    if(sessionStr): 
        result += ',"session":' + sessionStr
    result +=  '}' 
    return result

def recoverAtomDefinition(atomClassDefinitionList,forceFieldId):
    listAlreadyExist = []
    if(len(atomClassDefinitionList) > 0 and isinstance(atomClassDefinitionList[0],dict)):
        atomClassDefinitionList = str(atomClassDefinitionList).replace("'", '"')
        atomClassDefinitionList = loads(atomClassDefinitionList,object_hook=objDecoder)

    for instance in atomClassDefinitionList:
        if instance.idClassAtom not in listAlreadyExist:
            newClassAtom = ClassAtom(instance.idClassAtom,forceFieldId,instance.symbol,instance.atomicNumber,
                                 instance.atomicWeight,instance.valence)
            db.session.add(newClassAtom)
            listAlreadyExist.append(instance.idClassAtom)
        newAtom = AtomsType(instance.idAtomType,instance.idClassAtom,forceFieldId,instance.description)
        db.session.add(newAtom)
    db.session.commit()

def recoverParameterNameFF(listParameterNameFF,forceFieldId):
    for parameterName in listParameterNameFF:
        param_instance = db.session.query(ParameterTable).filter(ParameterTable.nameParameter == parameterName).scalar()
        ff_instance = db.session.query(ForceField).get(forceFieldId)
        ParametersOfForceFieldInstance = ParametersOfForceField()
        ParametersOfForceFieldInstance.forcefieldInstance = ff_instance
        ParametersOfForceFieldInstance.parametersInstance = param_instance
        db.session.flush()
    db.session.commit()   

def recoverUserOfFF(ownerName,listUserOfForceField,forceFieldId):
    for userName in listUserOfForceField:
        userId = db.session.query(User.user_id).filter(User.username == userName).scalar()
        ff_instance = db.session.query(ForceField).get(forceFieldId)
        param_instance = db.session.query(User).get(userId)
        if(ownerName == userName):
            isAuthor = True
        else:
            isAuthor = False
        UserForceFieldInstance = UserForceField()
        UserForceFieldInstance.ff_instance = ff_instance
        UserForceFieldInstance.user_instance = param_instance
        UserForceFieldInstance.isAuthor = isAuthor
        db.session.flush()
    db.session.commit()       
        
def recoverScalingFactorConstant(constantScalingFactorDataList, forceFieldId):
    if(isinstance(constantScalingFactorDataList[0],dict)):
        constantScalingFactorDataList = str(constantScalingFactorDataList).replace("'", '"')
        constantScalingFactorDataList = loads(constantScalingFactorDataList,object_hook=objDecoder)


    for instance in constantScalingFactorDataList:
        parameterInstance = db.session.query(ParameterTable).filter(ParameterTable.idParameter == instance.idParameter).scalar()
        listKey = list(instance.keyValue.keys())
        listKey.sort(key=lambda x:x[0])
        if parameterInstance.parameterType=='SF':
            for key in listKey:
                newScaling = ScalingFactorTable(forceFieldId,instance.idParameter,key.split('_')[1],instance.keyValue[key])
                db.session.add(newScaling)
        else:
            for key in listKey:
                newConstant = ConstantTable(forceFieldId,instance.idParameter,key.split('_')[1],instance.keyValue[key])
                db.session.add(newConstant)
    db.session.commit()

                
def recoverParameter(parameterClassOrTypeList,forceFieldId):
    if(isinstance(parameterClassOrTypeList[0],dict)):
        parameterClassOrTypeList = str(parameterClassOrTypeList).replace("'", '"')
        parameterClassOrTypeList = loads(parameterClassOrTypeList,object_hook=objDecoder)

    size=0
    newParam = -1

    for instance in parameterClassOrTypeList:
        if(isinstance(instance.descriptionForClass, str)):
            listClassAtom = instance.descriptionForClass.split('-')
            listClassAtom = list(set(listClassAtom))
        else:
            listClassAtom = [instance.descriptionForClass]

        if instance.typeOrClass == 'class':
            newParam = ParamsClass(instance.idParameter,forceFieldId)
            db.session.add(newParam)
            db.session.commit()

            listKey = list(instance.keyValue.keys())
            listKey.sort(key=lambda x:x[0])
            for key in listKey:
                newSon = (ValueClass(key.split('_')[1],newParam.idParam,instance.keyValue[key]))
                db.session.add(newSon)
                db.session.flush()
            

            for classAtom in listClassAtom:
                classAtom = int(classAtom) if isinstance(classAtom,str) else classAtom
                classAtom_instance = db.session.query(ClassAtom).get((classAtom,forceFieldId))
                newClassAtomParams = ClassAtom_ParamsClass(description=instance.descriptionForClass)
                newClassAtomParams.classAtomsInstance = classAtom_instance
                newClassAtomParams.paramsClassInstance = newParam
                db.session.commit()
                        
        else: # If the value parameter is type
            newParam = ParamsType(instance.idParameter,forceFieldId)
            db.session.add(newParam)
            db.session.commit()

            listKey = list(instance.keyValue.keys())
            listKey.sort(key=lambda x:x[0])
            for key in listKey:
                newSon = (ValueType(key.split('_')[1],newParam.idParam,instance.keyValue[key]))
                db.session.add(newSon)
            
            for typeAtom in listClassAtom:
                typeAtom = int(typeAtom) if isinstance(typeAtom,str) else typeAtom
                newAtomTypeParams = AtomsType_ParamsType(description=instance.descriptionForClass)
                newAtomTypeParams.atomsTypeInstance =  db.session.query(AtomsType).get((typeAtom,forceFieldId))
                newAtomTypeParams.paramsTypeInstance = newParam 
        
        #dans le remove value parameter ce code est execute
        countOperation = session['countOperation']          
        if (session['listOfOperation'][countOperation])['operation'] == "deleteValueParameter":
            (((session['listOfOperation'][countOperation+1])['parameterClassOrTypeList'])[size])['idParam'] = newParam.idParam
        size+=1
        db.session.commit()


def deleteOneLineValue(undoRedoObject):
    undoRedoObject = loads(str(undoRedoObject).replace("'",'"'),object_hook=objDecoder)
    idForceField = db.session.query(ForceField.idForceField).filter(ForceField.nameForceField == undoRedoObject.nameForceField).scalar()
    if undoRedoObject.nameParameter == "Atom Definition":
        #because there is only one instance in the list 
        objectAtom = undoRedoObject.atomClassDefinitionList[0]
        if objectAtom.existClass == False:
            instanceToDelete = db.session.query(ClassAtom).filter(ClassAtom.idClassAtom == objectAtom.idClassAtom,
                                                               ClassAtom.idForceField == idForceField).scalar()
        else:
            instanceToDelete = db.session.query(AtomsType).filter(AtomsType.idAtomType == objectAtom.idAtomType,
                                                               AtomsType.idForceField == idForceField).scalar()    
    else:
        instanceParameter = db.session.query(ParameterTable).filter(ParameterTable.nameParameter == undoRedoObject.nameParameter).scalar()
        if instanceParameter.parameterType == 'SF':
            objectScaling = undoRedoObject.constantScalingFactorDataList[0]
            instanceToDelete = db.session.query(ScalingFactorTable).filter(ScalingFactorTable.idParameter == objectScaling.idParameter,
                               ScalingFactorTable.idForceField == idForceField, ScalingFactorTable.key== objectScaling.key).scalar()
        elif instanceParameter.parameterType == 'Constant':
            objectConstant = undoRedoObject.constantScalingFactorDataList[0]
            instanceToDelete = db.session.query(ConstantTable).filter(ConstantTable.idParameter == objectConstant.idParameter, 
                               ConstantTable.idForceField == idForceField, ConstantTable.key== objectConstant.key).scalar()
        else:
            objectParameter = undoRedoObject.parameterClassOrTypeList[0]
            if objectParameter.typeOrClass == "class":
                instanceToDelete = db.session.query(ParamsClass).filter(ParamsClass.idParam == objectParameter.idParam).scalar()
            else:
                instanceToDelete = db.session.query(ParamsType).filter(ParamsType.idParam == objectParameter.idParam).scalar()
    db.session.delete(instanceToDelete)
    db.session.commit()


def addOneLineValue(undoRedoObject):
    undoRedoObject = loads(str(undoRedoObject).replace("'",'"'),object_hook=objDecoder)
    idForceField = db.session.query(ForceField.idForceField).filter(ForceField.nameForceField == undoRedoObject.nameForceField).scalar()
    if undoRedoObject.nameParameter == "Atom Definition":
        for objectAtom in undoRedoObject.atomClassDefinitionList:
            if objectAtom.existClass == False:
                instanceClass = ClassAtom(objectAtom.idClassAtom,idForceField,objectAtom.symbol,objectAtom.atomicNumber,
                                          objectAtom.atomicWeight,objectAtom.valence)
                db.session.add(instanceClass)
                db.session.flush()
            
            instanceType = AtomsType(objectAtom.idAtomType,objectAtom.idClassAtom,idForceField,objectAtom.description)
            db.session.add(instanceType)
            db.session.flush()
        recoverParameter(undoRedoObject.parameterClassOrTypeList,idForceField)                                                   
    else:
        instanceParameter = db.session.query(ParameterTable).filter(ParameterTable.nameParameter == undoRedoObject.nameParameter).scalar()
        if (instanceParameter.parameterType == 'SF') or (instanceParameter.parameterType == 'Constant'):
            recoverScalingFactorConstant(undoRedoObject.constantScalingFactorDataList, idForceField)
        else:
            recoverParameter(undoRedoObject.parameterClassOrTypeList,idForceField)
    db.session.flush()  
    db.session.commit()

def deleteClassAtom(undoRedoObject):
    undoRedoObject = loads(str(undoRedoObject).replace("'",'"'),object_hook=objDecoder)
    idForceField = db.session.query(ForceField.idForceField).filter(ForceField.nameForceField == undoRedoObject.nameForceField).scalar()
    idClassAtom = undoRedoObject.atomClassDefinitionList[0].idClassAtom
    atomClassToDelete = db.session.query(ClassAtom).get((idClassAtom,idForceField))
    db.session.delete(atomClassToDelete)
    db.session.commit()

def addClassAtomRedo(undoRedoObject):
    undoRedoObject = loads(str(undoRedoObject).replace("'",'"'),object_hook=objDecoder)
    idForceField = db.session.query(ForceField.idForceField).filter(ForceField.nameForceField == undoRedoObject.nameForceField).scalar()
    instance = undoRedoObject.atomClassDefinitionList[0]
    #create new instance of ClassAtom
    atomClassInstance = ClassAtom(instance.idClassAtom,idForceField,instance.symbol,instance.atomicNumber,instance.atomicWeight,instance.valence)
    #add the new ClassAtom in the table
    db.session.add(atomClassInstance)
    db.session.flush()

def addAtomTypeRedo(undoRedoObject):
    undoRedoObject = loads(str(undoRedoObject).replace("'",'"'),object_hook=objDecoder)
    idForceField = db.session.query(ForceField.idForceField).filter(ForceField.nameForceField == undoRedoObject.nameForceField).scalar()
    instance = undoRedoObject.atomClassDefinitionList[0]
    #create new instance of AtomType
    newAtomType = AtomsType(instance.idAtomType,instance.idClassAtom,idForceField,instance.description)
    #add new instance in data base
    db.session.add(newAtomType)
    db.session.flush()

def deleteAtomType(undoRedoObject):
    undoRedoObject = loads(str(undoRedoObject).replace("'",'"'),object_hook=objDecoder)
    idForceField = db.session.query(ForceField.idForceField).filter(ForceField.nameForceField == undoRedoObject.nameForceField).scalar()
    idAtomType = undoRedoObject.atomClassDefinitionList[0].idAtomType
    atomTypeToDelete = db.session.query(AtomsType).get((idAtomType,idForceField))
    db.session.delete(atomTypeToDelete)
    db.session.commit()


def deleteAllparameterOfClassAtom(idForceField,classAtomInstance):
    resultDict = {}
    atomClassDefinitionList = []
    parameterList = []
    ClassAtom_ParamsClassList_help = []
    idParamList_help = []

    #i need to store it for undo/redo
    atomClassDefinitionList.append(AtomClassDefinition(idClassAtom=classAtomInstance.idClassAtom,
                                         symbol=classAtomInstance.symbol,
                                         atomicNumber=classAtomInstance.atomicNumber,
                                         atomicWeight=classAtomInstance.atomicWeight,
                                         valence=classAtomInstance.valence,
                                         headerUpdate='idClassAtom',
                                         existClass=False))

    resultDict['atomClassDefinitionList'] = atomClassDefinitionList
    #i save all instance of parameter that will be remove
    #after the remove of classAtom to delete , in order to 
    #keep data for undo/redo

    ClassAtom_ParamsClassList = db.session.query(ClassAtom_ParamsClass).filter(ClassAtom_ParamsClass.idClassAtom == classAtomInstance.idClassAtom,ClassAtom_ParamsClass.idForceField == idForceField).all()
    idParamList = [x.idParam for x in ClassAtom_ParamsClassList]
    idParamList_help = [x.idParam for x in ClassAtom_ParamsClassList]

    for x in ClassAtom_ParamsClassList:
        if x.idParam in idParamList_help:
            ClassAtom_ParamsClassList_help.append(x)
            idParamList_help.remove(x.idParam)

    for instance in ClassAtom_ParamsClassList_help:
        keyValue = {}
        paramClassInstance = db.session.query(ParamsClass).get(instance.idParam)
        sonParam = db.session.query(ValueClass).filter(ValueClass.idParam == instance.idParam).all()
        count = 0
        for x in sonParam:
            keyValue[str(count)+'_'+x.key] = x.value
            count = count + 1
        parameterList.append(parameterClassOrType(typeOrClass="class",idParameter=paramClassInstance.idParameter,
                                                descriptionForClass=instance.description if instance.description else instance.idClassAtom,
                                                keyValue=keyValue,idParam=instance.idParam))

    resultDict['parameterClassOrTypeList'] = parameterList


    #I delete all parameter that was calculated by the deleted type/class
    for idParam in idParamList:
        db.session.delete(db.session.query(ParamsClass).get(idParam))
    

    #once i save it for undo , i delete it
    db.session.delete(classAtomInstance)
    db.session.commit()

    return resultDict


def updateAtomType(undoRedoObject,num):
    undoRedoObject = loads(str(undoRedoObject).replace("'",'"'),object_hook=objDecoder)
    idForceField = db.session.query(ForceField.idForceField).filter(ForceField.nameForceField == undoRedoObject.nameForceField).scalar()
    atomClassDefinitionList = undoRedoObject.atomClassDefinitionList
    atomClassToDelete = None

    temp = []
    
    #if the operation is undo
    if(num == 0):
        #if class atom was deleted and this is why the list's size = 3
        if(len(atomClassDefinitionList) == 3):
            temp.append(atomClassDefinitionList[0])
            temp.append(atomClassDefinitionList[1])
            atomClassDefinitionList = temp
        else:
            atomClassDefinitionList = [atomClassDefinitionList[0]]
    
    #if the operation is redo
    if(num == 1):
        #i need to delete the class atom , wich found in atomClassDefinitionList[0]
        if(len(atomClassDefinitionList) == 3):
            atomClassToDelete = atomClassDefinitionList[0]
            atomClassToDelete = db.session.query(ClassAtom).get((atomClassToDelete.idClassAtom,idForceField))
            atomClassDefinitionList = [atomClassDefinitionList[2]]
        else:
            atomClassDefinitionList = [atomClassDefinitionList[1]]




    for atomClassDefinition in atomClassDefinitionList:
        if(atomClassDefinition.headerUpdate == "idAtomType" and atomClassDefinition.oldValue == atomClassDefinition.actualValue):
            #so the update concern only the atom itself
            #and i need to restore the old atom type only
            instanceToUpdate = db.session.query(AtomsType).get((int(atomClassDefinition.actualValue),idForceField))
            instanceToUpdate.idClassAtom = int(atomClassDefinition.idClassAtom)
            instanceToUpdate.description = atomClassDefinition.description
            db.session.add(instanceToUpdate)
            db.session.commit()
        
        if(atomClassDefinition.headerUpdate == "idAtomType" and atomClassDefinition.oldValue != atomClassDefinition.actualValue):
            #i have to create the oldAtomType instance
            #so that there will not problem of foreign key
            #when i will change 
            oldAtomTypeInstance = AtomsType(atomClassDefinition.idAtomType,atomClassDefinition.idClassAtom,idForceField,atomClassDefinition.description)
            db.session.add(oldAtomTypeInstance)
            db.session.commit()
            #since the edit was on the idAtomType itself
            #i need to replace all actualIdAtomType by  
            #oldIdAtomType instance in AtomsType_ParamsType
            db.session.query(AtomsType_ParamsType).filter(AtomsType_ParamsType.idAtomType == int(atomClassDefinition.actualValue),\
                AtomsType_ParamsType.idForceField == idForceField).update({'idAtomType':atomClassDefinition.oldValue})
            db.session.commit()
            #i need to update all the description field that contains the old number
            listAtomsType_ParamsTypes = db.session.query(AtomsType_ParamsType).all()
            for instance in listAtomsType_ParamsTypes:
                if(instance.description):
                    listDescription = instance.description.split('-')
                    if(atomClassDefinition.actualValue in listDescription):
                        listDescription = [ atomClassDefinition.oldValue if x == atomClassDefinition.actualValue else x for x in listDescription ]
                    instance.description = '-'.join(listDescription)
                    db.session.add(instance)
                db.session.commit()

            #now i delete the newAtomType
            print(atomClassDefinition.actualValue)
            actualAtomTypeInstanceToDelete = db.session.query(AtomsType).get((int(atomClassDefinition.actualValue),idForceField))
            db.session.delete(actualAtomTypeInstanceToDelete)
            db.session.commit()
        
        if(atomClassDefinition.headerUpdate == "idClassAtom" and not atomClassDefinition.existClass):
            #add the class atom that was deleted and i need to create new one
            classAtomInstance = ClassAtom(atomClassDefinition.idClassAtom,idForceField,atomClassDefinition.symbol,atomClassDefinition.atomicNumber,atomClassDefinition.atomicWeight,atomClassDefinition.valence)
            db.session.add(classAtomInstance)
            db.session.flush()

            recoverParameter(undoRedoObject.parameterClassOrTypeList,idForceField)   

        if(atomClassDefinition.headerUpdate == "idClassAtom" and atomClassDefinition.existClass):
            #the class atom was no deleted but only changed so i need to restore it                            
            classAtomInstance = db.session.query(ClassAtom).get((int(atomClassDefinition.idClassAtom),idForceField))
            classAtomInstance.symbol = atomClassDefinition.symbol
            classAtomInstance.atomicNumber = atomClassDefinition.atomicNumber
            classAtomInstance.atomicWeight = atomClassDefinition.atomicWeight
            classAtomInstance.valence = atomClassDefinition.valence
            db.session.add(classAtomInstance)
            db.session.commit()
    
    
    if(atomClassToDelete):
        deleteAllparameterOfClassAtom(idForceField,atomClassToDelete)


def updateAtomClass(undoRedoObject,num):
    undoRedoObject = loads(str(undoRedoObject).replace("'",'"'),object_hook=objDecoder)
    idForceField = db.session.query(ForceField.idForceField).filter(ForceField.nameForceField == undoRedoObject.nameForceField).scalar()
    savedClassAtom = undoRedoObject.atomClassDefinitionList[num]
    actualIdClassAtom = int(savedClassAtom.actualValue)
    oldIdClassAtom = int(savedClassAtom.idClassAtom)
    
    if(savedClassAtom.oldValue == savedClassAtom.actualValue):
        #so the update concern only the atom itself
        #and i need to restore the old atom class only
        instanceToUpdate = db.session.query(ClassAtom).get((actualIdClassAtom,idForceField))
        instanceToUpdate.symbol = savedClassAtom.symbol
        instanceToUpdate.atomicNumber = savedClassAtom.atomicNumber
        instanceToUpdate.atomicWeight = savedClassAtom.atomicWeight
        instanceToUpdate.valence = savedClassAtom.valence
        db.session.add(instanceToUpdate)
        db.session.commit()
    
    if(savedClassAtom.oldValue != savedClassAtom.actualValue):
        #i have to create the oldClassAtom instance
        #so that there will not problem of foreign key
        #when i will change 
        oldClassAtomInstance = ClassAtom(savedClassAtom.idClassAtom,idForceField,savedClassAtom.symbol,savedClassAtom.atomicNumber,savedClassAtom.atomicWeight,savedClassAtom.valence)
        db.session.add(oldClassAtomInstance)
        db.session.commit()
        #i need to loop over the atomType Table and change all
        #instance with the newId by the oldId
        atomsTypeInstances = db.session.query(AtomsType).filter(AtomsType.idForceField == idForceField,AtomsType.idClassAtom == actualIdClassAtom).all()
        for instance in atomsTypeInstances:
            instance.idClassAtom = savedClassAtom.idClassAtom
            db.session.add(instance)
        db.session.commit()
        #since the edit was on the number atom itself
        #i need to replace all actualIdClassAtom by  
        #oldIdClassAtom instance in ClassAtomParam
        db.session.query(ClassAtom_ParamsClass).filter(ClassAtom_ParamsClass.idClassAtom == actualIdClassAtom,\
            ClassAtom_ParamsClass.idForceField == idForceField).update({'idClassAtom':oldIdClassAtom})
        db.session.commit()
        #i need to update all the description field that contains the old number
        listClassAtomParams = db.session.query(ClassAtom_ParamsClass).all()
        for instance in listClassAtomParams:
            if(instance.description):
                listDescription = instance.description.split('-')
                if(str(actualIdClassAtom) in listDescription):
                    listDescription = [ str(oldIdClassAtom) if x == str(actualIdClassAtom) else x for x in listDescription ]
                instance.description = '-'.join(listDescription)
                db.session.add(instance)
            db.session.commit()

        #now i delete the newClassAtom
        actualClassAtomInstanceToDelete = db.session.query(ClassAtom).get((actualIdClassAtom,idForceField))
        db.session.delete(actualClassAtomInstanceToDelete)
        db.session.commit()

def updateScalingFactor(undoRedoObject,num):
    undoRedoObject = loads(str(undoRedoObject).replace("'",'"'),object_hook=objDecoder)
    idForceField = db.session.query(ForceField.idForceField).filter(ForceField.nameForceField == undoRedoObject.nameForceField).scalar()
    idParameter = db.session.query(ParameterTable.idParameter).filter(ParameterTable.nameParameter == undoRedoObject.nameParameter).scalar()
    sf_instance = undoRedoObject.constantScalingFactorDataList[num]
    

    newSf = db.session.query(ScalingFactorTable).filter(ScalingFactorTable.idForceField == idForceField,
                                                            ScalingFactorTable.idParameter == idParameter,
                                                            ScalingFactorTable.key == sf_instance.value).first()
    
    newSf.key = sf_instance.keyValue['Configuration']
    newSf.value = sf_instance.keyValue['Value']
    db.session.add(newSf)
    db.session.commit()

def updateConstant(undoRedoObject,num):
    undoRedoObject = loads(str(undoRedoObject).replace("'",'"'),object_hook=objDecoder)
    idForceField = db.session.query(ForceField.idForceField).filter(ForceField.nameForceField == undoRedoObject.nameForceField).scalar()
    idParameter = db.session.query(ParameterTable.idParameter).filter(ParameterTable.nameParameter == undoRedoObject.nameParameter).scalar()
    constant_instance = undoRedoObject.constantScalingFactorDataList[num]
    

    newConsatnt = db.session.query(ConstantTable).filter(ConstantTable.idForceField == idForceField,
                                                            ConstantTable.idParameter == idParameter,
                                                            ConstantTable.key == constant_instance.value).first()
    
    newConsatnt.key = constant_instance.keyValue['Key']
    newConsatnt.value = constant_instance.keyValue['Value']
    db.session.add(newConsatnt)
    db.session.commit()

 
def editScalingFactor(ffName,parameterName,oldRowData,newRowData):
    ConstantScalingFactorDataList = []
    listChanged = []
    keyValue = {}

    #check if there was an change
    for x in oldRowData.keys():
        if(oldRowData[x] != newRowData[x]):
            listChanged.append(x)
    if(len(listChanged) == 0):
        return flashIndex("There is no change.",'error')

    #get the parameter instance
    parameterInstance = db.session.query(ParameterTable).filter(ParameterTable.nameParameter == parameterName).first()
    idParameter  = parameterInstance.idParameter
    
    #get the forceFieldInsatnce
    forceFIeldInstance = db.session.query(ForceField).filter(ForceField.nameForceField == ffName).first()
    idForceField = forceFIeldInstance.idForceField
    
    #get the scalingFactor Instance
    sf_instance = db.session.query(ScalingFactorTable).filter(ScalingFactorTable.idForceField == idForceField,\
                                                            ScalingFactorTable.idParameter == idParameter,\
                                                            ScalingFactorTable.key == oldRowData['Configuration']).first()


    if(oldRowData['Configuration'] != newRowData['Configuration']):
        #check if the configuration already exist
        isExist = db.session.query(ScalingFactorTable).filter(ScalingFactorTable.idForceField == idForceField,ScalingFactorTable.idParameter == idParameter,\
                ScalingFactorTable.key == newRowData['Configuration']).all()
        if(isExist):
            return flashIndex("The configuration "+ newRowData['Configuration'] +" is already existing,Please choose another one.",'error')
    


    keyValue['Configuration'] = oldRowData['Configuration']
    keyValue['Value'] = oldRowData['Value']
    #save the SF before the updated for Undo
    ConstantScalingFactorDataList.append(ConstantScalingFactorData(idParameter=idParameter,
                                            keyValue=keyValue,
                                            value= newRowData['Configuration']))

    
    keyValue = {}
    keyValue['Configuration'] = newRowData['Configuration']
    keyValue['Value'] = newRowData['Value']
    #save the SF before the updated for Redo
    ConstantScalingFactorDataList.append(ConstantScalingFactorData(idParameter=idParameter,
                                            keyValue=keyValue,
                                            value= oldRowData['Configuration']))


    #do the update here
    sf_instance.key = newRowData['Configuration']
    sf_instance.value = newRowData['Value']

    db.session.add(sf_instance)
    db.session.commit()

    #for undoRedoOperation
    instanceForUndoRedo = UndoRedoObject("editScalinFactor",ffName,nameParameter=parameterName,
                                                 constantScalingFactorDataList=ConstantScalingFactorDataList)
    
    if session['countOperation'] != (len(session['listOfOperation']) -1):
        for i in range((len(session['listOfOperation'])-1),session['countOperation'],-1):
            session['listOfOperation'].pop(i)
        session['redo'] = False
    session['listOfOperation'].append(instanceForUndoRedo)
    session['countOperation'] += 1
    session['undo'] = True
    session['save'] = True

    return flashIndex('The scaling factor was updated sucessfuly','success',sessionData(nameParameter=parameterName,nameForceField=ffName))

def editConstant(ffName,parameterName,oldRowData,newRowData):
    ConstantScalingFactorDataList = []
    listChanged = []
    keyValue = {}

    #check if there was an change
    for x in oldRowData.keys():
        if(oldRowData[x] != newRowData[x]):
            listChanged.append(x)
    if(len(listChanged) == 0):
        return flashIndex("There is no change.",'error')

    #get the parameter instance
    parameterInstance = db.session.query(ParameterTable).filter(ParameterTable.nameParameter == parameterName).first()
    idParameter  = parameterInstance.idParameter
    
    #get the forceFieldInsatnce
    forceFIeldInstance = db.session.query(ForceField).filter(ForceField.nameForceField == ffName).first()
    idForceField = forceFIeldInstance.idForceField
    
    #get the scalingFactor Instance
    constant_instance = db.session.query(ConstantTable).filter(ConstantTable.idForceField == idForceField,\
                                                            ConstantTable.idParameter == idParameter,\
                                                            ConstantTable.key == oldRowData['Key']).first()


    if(oldRowData['Key'] != newRowData['Key']):
        #check if the configuration already exist
        isExist = db.session.query(ConstantTable).filter(ConstantTable.idForceField == idForceField,ConstantTable.idParameter == idParameter,\
                ConstantTable.key == newRowData['Key']).all()
        if(isExist):
            return flashIndex("The Key "+ newRowData['Key'] +" is already existing,Please choose another one.",'error')
    


    keyValue['Key'] = oldRowData['Key']
    keyValue['Value'] = oldRowData['Value']
    #save the SF before the updated for Undo
    ConstantScalingFactorDataList.append(ConstantScalingFactorData(idParameter=idParameter,
                                            keyValue=keyValue,
                                            value= newRowData['Key']))

    
    keyValue = {}
    keyValue['Key'] = newRowData['Key']
    keyValue['Value'] = newRowData['Value']
    #save the SF before the updated for Redo
    ConstantScalingFactorDataList.append(ConstantScalingFactorData(idParameter=idParameter,
                                            keyValue=keyValue,
                                            value= oldRowData['Key']))


    #do the update here
    constant_instance.key = newRowData['Key']
    constant_instance.value = newRowData['Value']

    db.session.add(constant_instance)
    db.session.commit()

    #for undoRedoOperation
    instanceForUndoRedo = UndoRedoObject("editConstant",ffName,nameParameter=parameterName,
                                                 constantScalingFactorDataList=ConstantScalingFactorDataList)
    
    if session['countOperation'] != (len(session['listOfOperation']) -1):
        for i in range((len(session['listOfOperation'])-1),session['countOperation'],-1):
            session['listOfOperation'].pop(i)
        session['redo'] = False
    session['listOfOperation'].append(instanceForUndoRedo)
    session['countOperation'] += 1
    session['undo'] = True
    session['save'] = True

    return flashIndex('The constant was updated sucessfuly','success',sessionData(nameParameter=parameterName,nameForceField=ffName))


def updateParamsClass(undoRedoObject,num):
    undoRedoObject = loads(str(undoRedoObject).replace("'",'"'),object_hook=objDecoder)
    idForceField = db.session.query(ForceField.idForceField).filter(ForceField.nameForceField == undoRedoObject.nameForceField).scalar()
    idParameter = db.session.query(ParameterTable.idParameter).filter(ParameterTable.nameParameter == undoRedoObject.nameParameter).scalar()
    paramsClassInstance = undoRedoObject.parameterClassOrTypeList[num]
    
    #get the idParam to update
    updated_idParam = paramsClassInstance.idParam

    #get the params Class
    params_class_instance = db.session.query(ParamsClass).get(updated_idParam)

    #if equal to True so the class was updated
    if(paramsClassInstance.headerUpdate == "true"):
        ca_pc_instances = db.session.query(ClassAtom_ParamsClass).filter(ClassAtom_ParamsClass.idParam == updated_idParam).all()
        
        #delete the actual
        for x in ca_pc_instances:
            db.session.delete(x)
        db.session.commit()

        #create the new
        classAtomsList = list(set(paramsClassInstance.keyValue['Class'].split('-')))
        for x in classAtomsList:
            classAtomsInstance = db.session.query(ClassAtom).get((int(x),idForceField))
            ClassAtom_ParamsClass_Instance = ClassAtom_ParamsClass()
            ClassAtom_ParamsClass_Instance.classAtomsInstance = classAtomsInstance
            ClassAtom_ParamsClass_Instance.paramsClassInstance = params_class_instance
            if(len(paramsClassInstance.keyValue['Class']) > 1):
                ClassAtom_ParamsClass_Instance.description = paramsClassInstance.keyValue['Class']
            else:
                ClassAtom_ParamsClass_Instance.description = None
            db.session.add(ClassAtom_ParamsClass_Instance)
            db.session.commit()

    #change the others value
    listKeys = paramsClassInstance.keyValue.keys()
    sonParamsInstances = db.session.query(ValueClass).filter(ValueClass.idParam == updated_idParam).all()
    for x in sonParamsInstances:
        keyTemp = x.key 
        keyTemp = keyTemp.replace(' ','_')
        keyTemp = keyTemp.replace('(','_')
        keyTemp = keyTemp.replace(')','_')
        keyTemp = keyTemp.replace('-','_')
        if(keyTemp in listKeys):
            x.value = paramsClassInstance.keyValue[keyTemp]
            db.session.add(x)
    db.session.commit()



def editParamsClass(ffName,parameterName,oldRowData,newRowData):
    isClassUpdated = False
    isOk = True
    newClassList = []
    parameterClassOrTypeList = []
    #get the id ForceField 
    idForceField = db.session.query(ForceField.idForceField).filter(ForceField.nameForceField == ffName).scalar()
    
    #get the idParameter 
    idParameter = db.session.query(ParameterTable.idParameter).filter(ParameterTable.nameParameter == parameterName).scalar()
    
    #get all idParam relative to this parameter and FF
    paramsList = db.session.query(ParamsClass).filter(ParamsClass.idParameter == idParameter,ParamsClass.idForceField == idForceField).all()
    idParamsList = [x.idParam for x in paramsList]

    
    #get all instance of ClassAtom_ParamsClass that class field 
    #match to description field 
    if(len(oldRowData['Class']) == 1):
        ClassAtom_ParamsClass_instances = db.session.query(ClassAtom_ParamsClass).filter(ClassAtom_ParamsClass.idClassAtom == int(oldRowData['Class']),ClassAtom_ParamsClass.idForceField == idForceField).all()
    else:
        ClassAtom_ParamsClass_instances = db.session.query(ClassAtom_ParamsClass).filter(ClassAtom_ParamsClass.description == oldRowData['Class'],ClassAtom_ParamsClass.idForceField == idForceField).all()
    
    #get the idParam of the updated line
    for instance in ClassAtom_ParamsClass_instances:
        if(instance.idParam in idParamsList):
            updated_idParam = instance.idParam
            break;

    #now that we have the idParam we can process to update
    params_class_instance = db.session.query(ParamsClass).get(updated_idParam)
    
    if(oldRowData['Class'] != newRowData['Class']):
        isClassUpdated = True
        #i check if there is not another line in the grid that have the same class
        if(len(newRowData['Class']) == 1):
            isExist = db.session.query(ClassAtom_ParamsClass).filter(ClassAtom_ParamsClass.idForceField == idForceField,ClassAtom_ParamsClass.idClassAtom == int(newRowData['Class'])).all()
        if(len(newRowData['Class']) > 1):
            isExist = db.session.query(ClassAtom_ParamsClass).filter(ClassAtom_ParamsClass.idForceField == idForceField,ClassAtom_ParamsClass.description == newRowData['Class']).all()
        isExist = [x.idParam for x in isExist]
        for x in isExist:
            p_c_i = db.session.query(ParamsClass).get(x)
            if(p_c_i.idParameter == idParameter): 
                return flashIndex("The set "+ newRowData['Class']+' already exit in the parameter','error')
    
    #if there is change in the class
    if(isClassUpdated):
        #we have to check if the new class exist in this FF
        newClassList = newRowData['Class'].split('-')
        #remove duplicate data like 1-1
        newClassList = list(set(newClassList))
        for x in newClassList:
            classAtom_instance = db.session.query(ClassAtom).get((int(x),idForceField))
            if(not classAtom_instance):
                isOk = False
                return flashIndex('The class atom number '+ x +' doesn\'t exist.','error')
        
        #if the new class exist we can process to the changement
        if(isOk):
            #get All Instance of ClassAtom_ParamsClass relative to this idParam
            ca_pc_instances = db.session.query(ClassAtom_ParamsClass).filter(ClassAtom_ParamsClass.idParam == updated_idParam).all()
            
            #delete old 
            for x in ca_pc_instances:
                db.session.delete(x)
            db.session.commit()

            #create new
            for x in newClassList:
                classAtomsInstance = db.session.query(ClassAtom).get((int(x),idForceField))
                ClassAtom_ParamsClass_Instance = ClassAtom_ParamsClass()
                ClassAtom_ParamsClass_Instance.classAtomsInstance = classAtomsInstance
                ClassAtom_ParamsClass_Instance.paramsClassInstance = params_class_instance
                if(len(newRowData['Class']) > 1):
                    ClassAtom_ParamsClass_Instance.description = newRowData['Class']
                else:
                    ClassAtom_ParamsClass_Instance.description = None
                db.session.add(ClassAtom_ParamsClass_Instance)
                db.session.commit()


    #change the others value
    listKeys = oldRowData.keys()
    sonParamsInstances = db.session.query(ValueClass).filter(ValueClass.idParam == updated_idParam).all()
    for x in sonParamsInstances:
        keyTemp = x.key 
        keyTemp = keyTemp.replace(' ','_')
        keyTemp = keyTemp.replace('(','_')
        keyTemp = keyTemp.replace(')','_')
        keyTemp = keyTemp.replace('-','_')
        if(keyTemp in listKeys):
            x.value = newRowData[keyTemp]
            db.session.add(x)
    db.session.commit()

    #save the old param for the undo operation
    parameterClassOrTypeList.append(parameterClassOrType(typeOrClass="class",idParameter=idParameter,
                                                        descriptionForClass=oldRowData['Class'],
                                                        keyValue=oldRowData,idParam=updated_idParam,
                                                        value=newRowData['Class'],headerUpdate="true" if isClassUpdated else "false"))

    #save the new param for the redo operation
    parameterClassOrTypeList.append(parameterClassOrType(typeOrClass="class",idParameter=idParameter,
                                                        descriptionForClass=newRowData['Class'],
                                                        keyValue=newRowData,idParam=updated_idParam,
                                                        value=oldRowData['Class'],headerUpdate="true" if isClassUpdated else "false"))


    instanceForUndoRedo = UndoRedoObject("editParamsClass",ffName,nameParameter=parameterName,
                                        parameterClassOrTypeList=parameterClassOrTypeList)                        
        

    if session['countOperation'] != (len(session['listOfOperation']) -1):
        for i in range((len(session['listOfOperation'])-1),session['countOperation'],-1):
            session['listOfOperation'].pop(i)
        session['redo'] = False
    session['listOfOperation'].append(instanceForUndoRedo)
    session['countOperation'] += 1
    session['undo'] = True
    session['save'] = True

    return flashIndex('The param class was updated sucessfuly','success',sessionData(nameParameter=parameterName,nameForceField=ffName))



def updateParamsType(undoRedoObject,num):
    undoRedoObject = loads(str(undoRedoObject).replace("'",'"'),object_hook=objDecoder)
    idForceField = db.session.query(ForceField.idForceField).filter(ForceField.nameForceField == undoRedoObject.nameForceField).scalar()
    idParameter = db.session.query(ParameterTable.idParameter).filter(ParameterTable.nameParameter == undoRedoObject.nameParameter).scalar()
    paramsTypeInstance = undoRedoObject.parameterClassOrTypeList[num]
    
    #get the idParam to update
    updated_idParam = paramsTypeInstance.idParam

    #get the params Type
    params_type_instance = db.session.query(ParamsClass).get(updated_idParam)

    #if equal to True so the class was updated
    if(paramsTypeInstance.headerUpdate == "true"):
        ca_pc_instances = db.session.query(AtomsType_ParamsType).filter(AtomsType_ParamsType.idParam == updated_idParam).all()
        
        #delete the actual
        for x in ca_pc_instances:
            db.session.delete(x)
        db.session.commit()

        #create the new
        atomsTypeList = list(set(paramsTypeInstance.keyValue['Type'].split('-')))
        for x in atomsTypeList:
            AtomsTypeInstance = db.session.query(ClassAtom).get((int(x),idForceField))
            AtomsType_ParamsType_Instance = AtomsType_ParamsType()
            AtomsType_ParamsType_Instance.atomsTypeInstance  = AtomsTypeInstance
            AtomsType_ParamsType_Instance.paramsTypeInstance = params_type_instance
            if(len(paramsTypeInstance.keyValue['Type']) > 1):
                AtomsType_ParamsType_Instance.description = paramsTypeInstance.keyValue['Type']
            else:
                AtomsType_ParamsType_Instance.description = None
            db.session.add(AtomsType_ParamsType_Instance)
            db.session.commit()

    #change the others value
    listKeys = paramsTypeInstance.keyValue.keys()
    sonParamsInstances = db.session.query(ValueType).filter(ValueType.idParam == updated_idParam).all()
    for x in sonParamsInstances:
        keyTemp = x.key 
        keyTemp = keyTemp.replace(' ','_')
        keyTemp = keyTemp.replace('(','_')
        keyTemp = keyTemp.replace(')','_')
        keyTemp = keyTemp.replace('-','_')
        if(keyTemp in listKeys):
            x.value = paramsTypeInstance.keyValue[keyTemp]
            db.session.add(x)
    db.session.commit()



def editParamType(ffName,parameterName,oldRowData,newRowData):
    isTypeUpdated = False
    isOk = True
    newTypeList = []
    parameterClassOrTypeList = []
    #get the id ForceField 
    idForceField = db.session.query(ForceField.idForceField).filter(ForceField.nameForceField == ffName).scalar()
    
    #get the idParameter 
    idParameter = db.session.query(ParameterTable.idParameter).filter(ParameterTable.nameParameter == parameterName).scalar()
    
    #get all idParam relative to this parameter and FF
    paramsList = db.session.query(ParamsType).filter(ParamsType.idParameter == idParameter,ParamsType.idForceField == idForceField).all()
    idParamsList = [x.idParam for x in paramsList]

    
    #get all instance of AtomsType_ParamsType that class field 
    #match to description field 
    if(len(oldRowData['Type']) == 1):
        AtomsType_ParamsType_instances = db.session.query(AtomsType_ParamsType).filter(AtomsType_ParamsType.idAtomType == int(oldRowData['Type']),AtomsType_ParamsType.idForceField == idForceField).all()
    else:
        AtomsType_ParamsType_instances = db.session.query(AtomsType_ParamsType).filter(AtomsType_ParamsType.description == oldRowData['Type'],AtomsType_ParamsType.idForceField == idForceField).all()
    
    #get the idParam of the updated line
    for instance in AtomsType_ParamsType_instances:
        if(instance.idParam in idParamsList):
            updated_idParam = instance.idParam
            break;

    #now that we have the idParam we can process to update
    AtomsType_ParamsType_instance = db.session.query(ParamsType).get(updated_idParam)
    
    if(oldRowData['Type'] != newRowData['Type']):
        isTypeUpdated = True
        #i check if there is not another line in the grid that have the same class
        if(len(newRowData['Type']) == 1):
            isExist = db.session.query(AtomsType_ParamsType).filter(AtomsType_ParamsType.idForceField == idForceField,AtomsType_ParamsType.idAtomType == int(newRowData['Type'])).all()
        if(len(newRowData['Type']) > 1):
            isExist = db.session.query(AtomsType_ParamsType).filter(AtomsType_ParamsType.idForceField == idForceField,AtomsType_ParamsType.description == newRowData['Type']).all()
        isExist = [x.idParam for x in isExist]
        for x in isExist:
            p_c_i = db.session.query(ParamsType).get(x)
            if(p_c_i.idParameter == idParameter): 
                return flashIndex("The set "+ newRowData['Type']+' already exit in the parameter','error')
    
    #if there is change in the class
    if(isTypeUpdated):
        #we have to check if the new class exist in this FF
        newTypeList = newRowData['Type'].split('-')
        #remove duplicate data like 1-1
        newTypeList = list(set(newTypeList))
        for x in newTypeList:
            atomType_instance = db.session.query(AtomsType).get((int(x),idForceField))
            if(not atomType_instance):
                isOk = False
                return flashIndex('The atom type number '+ x +' doesn\'t exist.','error')
        
        #if the new class exist we can process to the changement
        if(isOk):
            #get All Instance of ClassAtom_ParamsClass relative to this idParam
            ca_pc_instances = db.session.query(AtomsType_ParamsType).filter(AtomsType_ParamsType.idParam == updated_idParam).all()
            
            #delete old 
            for x in ca_pc_instances:
                db.session.delete(x)
            db.session.commit()

            #Be careful there is two different variable AtomsType_ParamsType_Instance  && AtomsType_ParamsType_instance
            
            #create new
            for x in newTypeList:
                atomTypeInstance = db.session.query(AtomsType).get((int(x),idForceField))
                AtomsType_ParamsType_Instance = AtomsType_ParamsType()
                AtomsType_ParamsType_Instance.atomsTypeInstance = atomTypeInstance
                AtomsType_ParamsType_Instance.paramsTypeInstance = AtomsType_ParamsType_instance
                if(len(newRowData['Class']) > 1):
                    AtomsType_ParamsType_Instance.description = newRowData['Type']
                else:
                    AtomsType_ParamsType_Instance.description = None
                db.session.add(AtomsType_ParamsType_Instance)
                db.session.commit()


    #change the others value
    listKeys = oldRowData.keys()
    sonParamsInstances = db.session.query(ValueType).filter(ValueType.idParam == updated_idParam).all()
    for x in sonParamsInstances:
        keyTemp = x.key 
        keyTemp = keyTemp.replace(' ','_')
        keyTemp = keyTemp.replace('(','_')
        keyTemp = keyTemp.replace(')','_')
        keyTemp = keyTemp.replace('-','_')
        if(keyTemp in listKeys):
            x.value = newRowData[keyTemp]
            db.session.add(x)
    db.session.commit()

    #save the old param for the undo operation
    parameterClassOrTypeList.append(parameterClassOrType(typeOrClass="type",idParameter=idParameter,
                                                        descriptionForClass=oldRowData['Type'],
                                                        keyValue=oldRowData,idParam=updated_idParam,
                                                        value=newRowData['Type'],headerUpdate="true" if isTypeUpdated else "false"))

    #save the new param for the redo operation
    parameterClassOrTypeList.append(parameterClassOrType(typeOrClass="type",idParameter=idParameter,
                                                        descriptionForClass=newRowData['Type'],
                                                        keyValue=newRowData,idParam=updated_idParam,
                                                        value=oldRowData['Type'],headerUpdate="true" if isTypeUpdated else "false"))


    instanceForUndoRedo = UndoRedoObject("editParamsType",ffName,nameParameter=parameterName,
                                        parameterClassOrTypeList=parameterClassOrTypeList)                        
        

    if session['countOperation'] != (len(session['listOfOperation']) -1):
        for i in range((len(session['listOfOperation'])-1),session['countOperation'],-1):
            session['listOfOperation'].pop(i)
        session['redo'] = False
    session['listOfOperation'].append(instanceForUndoRedo)
    session['countOperation'] += 1
    session['undo'] = True
    session['save'] = True

    return flashIndex('The param type was updated sucessfuly','success',sessionData(nameParameter=parameterName,nameForceField=ffName))



def rename(undoRedoObject):
    undoRedoObject = loads(str(undoRedoObject).replace("'",'"'),object_hook=objDecoder)
    # So the rename was maked on forcefield name
    if undoRedoObject.nameParameter == "": 
        db.session.query(ForceField).filter(ForceField.nameForceField == undoRedoObject.nameForceField).update(
                                    {"nameForceField":undoRedoObject.oldValue})
    
    # If the rename was maked on parameter
    else:
        instanceParameterAfterRename = db.session.query(ParameterTable).filter(ParameterTable.nameParameter==undoRedoObject.nameParameter).scalar()
        instanceParameterBeforeRename = db.session.query(ParameterTable).filter(ParameterTable.nameParameter==undoRedoObject.oldValue).scalar()
        idForceField = db.session.query(ForceField.idForceField).filter(ForceField.nameForceField==undoRedoObject.nameForceField).scalar()
        if instanceParameterAfterRename.parameterType == 'SF':
            db.session.query(ScalingFactorTable).filter(ScalingFactorTable.idParameter == instanceParameterAfterRename.idParameter,
                              ScalingFactorTable.idForceField == idForceField).update({"idParameter":instanceParameterBeforeRename.idParameter})
        elif instanceParameterAfterRename.parameterType == 'Constant':
            db.session.query(ConstantTable).filter(ConstantTable.idParameter == instanceParameterAfterRename.idParameter,
                              ConstantTable.idForceField == idForceField).update({"idParameter":instanceParameterBeforeRename.idParameter})
        else:
            if instanceParameterAfterRename.classOrType == 'class':
                db.session.query(ParamsClass).filter(ParamsClass.idParameter == instanceParameterAfterRename.idParameter,
                            ParamsClass.idForceField == idForceField).update({"idParameter":instanceParameterBeforeRename.idParameter})
            else:
                db.session.query(ParamsType).filter(ParamsType.idParameter == instanceParameterAfterRename.idParameter,
                            ParamsType.idForceField == idForceField).update({"idParameter":instanceParameterBeforeRename.idParameter})
        
        db.session.query(ParametersOfForceField).filter(ParametersOfForceField.idParameter == instanceParameterAfterRename.idParameter,
                                        ParametersOfForceField.idForceField == idForceField).update({"idParameter":instanceParameterBeforeRename.idParameter})
        # THe new parameter created after rename operation is deleted
        db.session.delete(instanceParameterAfterRename)
    db.session.commit()

def isParameterExist(ffName,ParameterName):
    ParameterName = ParameterName.lower()
    parametersList = db.session.query(ParameterTable.nameParameter).all()
    parametersList = [x[0].lower() for x in parametersList]
    if ParameterName in parametersList and ffName:
        ffNameInstance = db.session.query(ForceField).filter(ForceField.nameForceField == ffName).first()
        parametersOfFFName = ffNameInstance.childrenParameter
        listOfIdParameter = [x.idParameter for x in parametersOfFFName]
        parameterNameInstance = db.session.query(ParameterTable).filter(ParameterTable.nameParameter == parameterName).first()
        idParameter = parameterNameInstance.idParameter
        if(idParameter in listOfIdParameter):
            return True
        else:
            return False
    if ParameterName in parametersList and not ffName:
        return True
    if ParameterName not in parametersList:
        return False

def undoForAddParameterToFF(undoRedoObject):
    undoRedoObject = loads(str(undoRedoObject).replace("'",'"'),object_hook=objDecoder)
    idForceField = db.session.query(ForceField.idForceField).filter(ForceField.nameForceField == undoRedoObject.nameForceField).scalar()
    listParameter = undoRedoObject.nameParameter.split(',')
    if(undoRedoObject.typeParam == "SF&Constant"):
        isExistList = undoRedoObject.oldValue.split(',')
    else:
        isExistList = [undoRedoObject.exist]
    count = 0
    for nameParameter in listParameter:
        parameterInstance = db.session.query(ParameterTable).filter(ParameterTable.nameParameter == nameParameter).scalar()
        for instance in db.session.query(ParametersOfForceField):
            if instance.idForceField == idForceField and instance.idParameter == parameterInstance.idParameter:
                db.session.delete(instance)
                db.session.flush()
        
        for instance in db.session.query(ForceField).get(idForceField).childrenParameter:
            instanceParameter = db.session.query(ParameterTable).get(instance.idParameter)
            if instanceParameter.idParameter == parameterInstance.idParameter:
                db.session.query(ForceField).get(idForceField).childrenParameter.remove(instance)
                db.session.flush()

        if isExistList[count] == "false" or isExistList[count] == False:
            db.session.delete(parameterInstance)
            db.session.flush()
        count = count + 1

def redoForAddParameterToFF(undoRedoObject):
    undoRedoObject = loads(str(undoRedoObject).replace("'",'"'),object_hook=objDecoder)
    idForceField = db.session.query(ForceField.idForceField).filter(ForceField.nameForceField == undoRedoObject.nameForceField).scalar()
    listNameParameter = undoRedoObject.nameParameter.split(',')
    if(undoRedoObject.typeParam == "SF&Constant"):
        #only in this order ,constant and the SF
        listTypeParam = ['Constant','SF']
        listIsExist = undoRedoObject.oldValue.split(',')
    else:
        listTypeParam = [undoRedoObject.typeParam]
        listIsExist = [undoRedoObject.exist]

    count = 0
    for nameParameter in listNameParameter:
        if listIsExist[count] == False or listIsExist[count] == "false":
            if listTypeParam[count] == "Parameter":
                newParameter = ParameterTable(nameParameter,listTypeParam[count],undoRedoObject.numberAtoms,undoRedoObject.classOrType)
                newParameter.columnsName = undoRedoObject.nameColumns
            else:
                newParameter = ParameterTable(nameParameter,listTypeParam[count])
            db.session.add(newParameter)
            db.session.flush()
        idParameter = db.session.query(ParameterTable.idParameter).filter(ParameterTable.nameParameter == nameParameter).scalar()
        parameterInstance = db.session.query(ParameterTable).get(idParameter)
        forcefieldInstance = db.session.query(ForceField).get(idForceField)
        ParametersOfForceFieldInstance = ParametersOfForceField()
        ParametersOfForceFieldInstance.forcefieldInstance = forcefieldInstance
        ParametersOfForceFieldInstance.parametersInstance = parameterInstance
        count = count + 1
        db.session.flush()

def addValueParameterForRedo(undoRedoObject):
    undoRedoObject = loads(str(undoRedoObject).replace("'",'"'),object_hook=objDecoder)
    idForceField = db.session.query(ForceField.idForceField).filter(ForceField.nameForceField == undoRedoObject.nameForceField).scalar()
    if undoRedoObject.nameParameter == "Atom Definition":
        objectAtom = undoRedoObject.atomClassDefinitionList[0]
        if objectAtom.existClass == False:
            newClass = ClassAtom(objectAtom.idClassAtom,idForceField,objectAtom.symbol,objectAtom.atomicNumber,
                                 objectAtom.atomicWeight,objectAtom.valence)
            db.session.add(newClass)
            db.session.flush()
        newInstance = AtomsType(objectAtom.idAtomType,objectAtom.idClassAtom,idForceField,objectAtom.description)
        db.session.add(newInstance)
    else:
        instanceParameter = db.session.query(ParameterTable).filter(ParameterTable.nameParameter == undoRedoObject.nameParameter).scalar()
        if instanceParameter.parameterType == 'SF':
            objectScaling = undoRedoObject.constantScalingFactorDataList[0]
            newInstance = ScalingFactorTable(idForceField,objectScaling.idParameter,objectScaling.key,objectScaling.value)
            db.session.add(newInstance)
        elif instanceParameter.parameterType == 'Constant':
            objectConstant = undoRedoObject.constantScalingFactorDataList[0]
            newInstance = ConstantTable(idForceField,objectConstant.idParameter,objectConstant.key,objectConstant.value)
            db.session.add(newInstance)
        else:
            objectParameter = undoRedoObject.parameterClassOrTypeList[0]
            listClassAtom = objectParameter.descriptionForClass.split('-')
            newParam = -1
            if objectParameter.typeOrClass == "class":
                newParam = ParamsClass(objectParameter.idParameter,idForceField)
                db.session.add(newParam)
                db.session.flush()
                for key in objectParameter.keyValue.keys():
                    newSon = (ValueClass(key,newParam.idParam,objectParameter.keyValue[key]))
                    db.session.add(newSon)
                if len(listClassAtom) == 1:
                    newClassAtomParams = ClassAtom_ParamsClass()
                    newClassAtomParams.classAtomsInstance =  db.session.query(ClassAtom).get((listClassAtom[0],idForceField))
                    newClassAtomParams.paramsClassInstance = db.session.query(ParamsClass).get(newParam.idParam)
                else:
                    listExistClass = []
                    for classAtom in listClassAtom:
                        if classAtom not in listExistClass:
                            newClassAtomParams = ClassAtom_ParamsClass(description=objectParameter.descriptionForClass)
                            newClassAtomParams.classAtomsInstance = db.session.query(ClassAtom).get((classAtom,idForceField))
                            newClassAtomParams.paramsClassInstance = db.session.query(ParamsClass).get(newParam.idParam)
                            listExistClass.append(classAtom)
            else:
                newParam = ParamsType(objectParameter.idParameter,idForceField)
                db.session.add(newParam)
                db.session.flush()
                for key in objectParameter.keyValue.keys():
                    newSon = (ValueType(key,newParam.idParam,objectParameter.keyValue[key]))
                    db.session.add(newSon)
                if len(listClassAtom) == 1:
                    newAtomTypeParams = AtomsType_ParamsType()
                    newAtomTypeParams.atomsTypeInstance =  session.query(AtomsType).get((listClassAtom[0],idForceField))
                    newAtomTypeParams.paramsTypeInstance = newParam
                else:
                    listExistType = []
                    for typeAtom in listClassAtom:
                        if typeAtom not in listExistType:
                            newAtomTypeParams = AtomsType_ParamsType(description=objectParameter.descriptionForClass)
                            newAtomTypeParams.atomsTypeInstance =  session.query(AtomsType).get((typeAtom,idForceField))
                            newAtomTypeParams.paramsTypeInstance = newParam 
                            listExistType.append(typeAtom) 
            session['listOfOperation'][session['countOperation']]['parameterClassOrTypeList'][0]['idParam'] = newParam.idParam                     
    db.session.flush()

def deleteValueParameterForRedo(undoRedoObject):
    undoRedoObject = loads(str(undoRedoObject).replace("'",'"'),object_hook=objDecoder)
    idForceField = db.session.query(ForceField.idForceField).filter(ForceField.nameForceField == undoRedoObject.nameForceField).scalar()
    if undoRedoObject.nameParameter == "Atom Definition":
        for objectAtom in undoRedoObject.atomClassDefinitionList:
            if objectAtom.existClass == False:
                instanceToDelete = db.session.query(ClassAtom).filter(ClassAtom.idClassAtom == objectAtom.idClassAtom,
                                                                   ClassAtom.idForceField == idForceField).scalar()
            else:
                instanceToDelete = db.session.query(AtomsType).filter(AtomsType.idAtomType == objectAtom.idAtomType,
                                                                   AtomsType.idForceField == idForceField).scalar()
            #If i delete one class or type that was used in parameter, i need to delete there parameter value
            for instance in db.session.query(ParamsClass):
                if instance.idForceField == idForceField:
                    for classAtomParamsClass in db.session.query(ClassAtom_ParamsClass):
                        if (classAtomParamsClass.idForceField == idForceField and classAtomParamsClass.idParam == instance.idParam
                            and classAtomParamsClass.idClassAtom == objectAtom.idClassAtom):
                                db.session.delete(instance)
                                db.session.flush()
            for instance in db.session.query(ParamsType):
                if instance.idForceField == idForceField:
                    for atomsTypeParamsType in db.session.query(AtomsType_ParamsType):
                        if (atomsTypeParamsType.idForceField == idForceField and atomsTypeParamsType.idParam == instance.idParam
                                and atomsTypeParamsType.idAtomType == objectAtom.idAtomType):
                                    db.session.delete(instance)
                                    db.session.flush()  
            #Here i deleted the atoms type
            db.session.delete(instanceToDelete)
    else:
        instanceParameter = db.session.query(ParameterTable).filter(ParameterTable.nameParameter == undoRedoObject.nameParameter).scalar()
        if instanceParameter.parameterType == 'SF':
            for objectScaling in undoRedoObject.constantScalingFactorDataList:
                instanceToDelete = db.session.query(ScalingFactorTable).filter(ScalingFactorTable.idParameter == objectScaling.idParameter,
                                   ScalingFactorTable.idForceField == idForceField, ScalingFactorTable.key== objectScaling.key).scalar()
                db.session.delete(instanceToDelete)
        elif instanceParameter.parameterType == 'Constant':
            for objectConstant in undoRedoObject.constantScalingFactorDataList:
                instanceToDelete = db.session.query(ConstantTable).filter(ConstantTable.idParameter == objectConstant.idParameter, 
                                   ConstantTable.idForceField == idForceField, ConstantTable.key== objectConstant.key).scalar()
                db.session.delete(instanceToDelete)
        else:
            for objectParameter in undoRedoObject.parameterClassOrTypeList:
                if objectParameter.typeOrClass == "class":
                    instanceToDelete = db.session.query(ParamsClass).filter(ParamsClass.idParam == objectParameter.idParam).scalar()
                else:
                    instanceToDelete = db.session.query(ParamsType).filter(ParamsType.idParam == objectParameter.idParam).scalar()
                db.session.delete(instanceToDelete)               


#    elif undoRedoObject.operation == "updateValueParameter":
#        updateValueParameterForRedo(undoRedoObject)
#    session.flush()
#