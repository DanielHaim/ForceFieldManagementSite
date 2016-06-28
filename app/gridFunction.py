from app import db
from .models import * 
from flask import session
import math

gridSize = 780

#def find_type(column):
#    tableName = session['tableName']
#    tableName = eval(tableName)
#    Column = getattr(tableName,column)
#    columnType = Column.property.columns[0].type
#    if "VARCHAR" in str(columntype):
#        return 'string'
#    if "INTEGER" in str(columntype):
#        return 'int'
#    else:
#        return ''

def find_type(column):
    if column in ['symbol','description','Configuration','Type','Class']:
        return ''
    else:
        return 'd'

def data_to_json(rowList,keyList):
    if(len(rowList) == 0):
        return "[]"
    result="["
    counter = 1
    for elementRow in rowList:
        result += "{'numberOfRow':'" + str(counter) + "',"
        result += "'checkBoxColumn':false," 
        counter = counter + 1
        count = 0
        while(count < len(keyList)):
            if (count < len(elementRow.result)):
                result += "'" + keyList[count] + "': '" + str(elementRow.result[count]) + "', "
            else:
                result += "'" + keyList[count] + "':'',"
            count = count + 1
        #delete the  two last charachter in result
        result = result[:-2]
        result += " }, "
    result = result[:-2]
    result += "]"
    #target = open("/Users/daniel/Desktop/data1.txt",'a')
    #target.write(result)
    #target.close()
    return result

def sizeComputation(rowList,keyList):
    sizeArray = []
    total = 0
    count = 0
    #width est egal au plus grand entre:
    #la taille du nom de la colonne
    #et la taille du plus long element de la colone
    for elementKey in keyList:
        width = len(elementKey)*10
        for elementRow in rowList:
            if (count < len(elementRow.result)):
                if (len(str(elementRow.result[count]))*10 > width):
                    width = len(str(elementRow.result[count])*10)
        sizeArray.append(width)
        count = count + 1
        
    total = sum(sizeArray)
    if(total < gridSize):
        total = gridSize - total
        total = math.trunc(total / len(keyList))
        if(total > 1):
            x = 0 
            for elementArray in sizeArray:
                sizeArray[x] = (elementArray + total)
                x = x + 1
    total = sum(sizeArray)
    if(total < gridSize):
        sizeArray[0] = sizeArray[0] + (gridSize - total)

    return sizeArray



def columnsList_to_json (keyList,sizeArray,var):
    #for x in keyList:
    #    print(x, file=sys.stderr)
    count = 0
    result = "[" 
    if(var):
        result += "{ text:'', datafield: 'checkBoxColumn', columntype: 'checkbox' ,width:30},"
    else:
        result += "{ text:'', datafield: 'checkBoxColumn', columntype: 'checkbox' ,width:30,editable:false},"
    result += "{ text:'row', datafield: 'numberOfRow' , width:40,editable:false},"
    for elementKey in keyList:
        result += "{ text: '" + elementKey + "', datafield: '" + elementKey + "', width:'" +  str(sizeArray[count]) + "'},"
        count = count + 1
    result += "]"
    return result

def columnsList_to_JS(keyList):
    result = "["
    for columnsName in keyList:
        result += "'" + columnsName + "',"
    result = result[:-1]
    result += "]"
    return result

def dataFieldGrid_to_json(keyList):
    result = "["
    result += "{name:'numberOfRow',type:'string'},"
    result += "{name:'checkBoxColumn',type:'bool'},"
    for elementKey in keyList:
        result += "{name:'" + elementKey + "',type:'string'},"
    result = result[:-1]
    result += "]"
    return result

def getKeyList(ForcefieldName,parameterName):
    ff = db.session.query(ForceField).filter(ForceField.nameForceField == ForcefieldName).scalar()
    param = db.session.query(ParameterTable).filter(ParameterTable.nameParameter == parameterName).scalar()
    ff_param = db.session.query(ParametersOfForceField).get((ff.idForceField,param.idParameter))
    keyList = []
    if(ff_param.columnsName and (len(ff_param.columnsName) >0)):
        columnNameList = ff_param.columnsName.split(',')
    else:
        columnNameList = param.columnsName.split(',') if param.columnsName else " "
    
    for column in columnNameList:
        keyList.append(column) 
    
    session['numberOfColumns'] = len(columnNameList)
    session['keyList'] = keyList

# This class help the next function retreiveValue to return the necessary
class row:
    resultList = []
    result = []
    def __init__(self,ResultList,Result):
        self.resultList = ResultList
        self.result = Result


# Function that get forceFieldName and ParameterName and return all value of this parameter from this forcfield
def retrieveValue(forcefieldName,parameterName):
    numberOfColumns = 0
    tableName = ''
    keyList=[]
    rowList = []
    id_forcefield = db.session.query(ForceField.idForceField).filter(ForceField.nameForceField == forcefieldName)
    parameter = db.session.query(ParameterTable).filter(ParameterTable.nameParameter == parameterName).first()
    session['numberOfAtoms'] = parameter.numberOfAtoms
    id_parameter = parameter.idParameter
    if('Scaling Factors' in parameterName):
        scalingFactor_instances = db.session.query(ScalingFactorTable).filter(ScalingFactorTable.idParameter == id_parameter , ScalingFactorTable.idForceField == id_forcefield).all()
        tableName = 'ScalingFactorTable'
        keyList.append('Configuration')
        keyList.append('Value')
        for instance in scalingFactor_instances:
            resultList = []
            result  = []
            result.append(instance.key)
            result.append(instance.value)
            rowList.append(row(resultList,result))
        numberOfColumns = 2
        session['numberOfColumns'] = numberOfColumns
        session['keyList'] = keyList
        session['tableName'] = tableName
        return rowList
    if('Constants' in parameterName):
        constant_instances = db.session.query(ConstantTable).filter(ConstantTable.idParameter == id_parameter , ConstantTable.idForceField == id_forcefield).all()
        tableName = 'ConstantTable'
        keyList.append('Key')
        keyList.append('Value')
        for instance in constant_instances:
            resultList = []
            result  = []
            result.append(instance.key)
            result.append(instance.value)
            rowList.append(row(resultList,result))
        numberOfColumns = 2
        session['numberOfColumns'] = numberOfColumns
        session['keyList'] = keyList
        session['tableName'] = tableName
        return rowList
    else:
        #why this line , there is parameter above!??
        parameter_instance = db.session.query(ParameterTable).filter(ParameterTable.nameParameter == parameterName).scalar()
        if(parameter_instance.classOrType == "class"):
            keyList.append("Class")
            list_paramsClass = db.session.query(ParamsClass).filter(ParamsClass.idParameter == id_parameter , ParamsClass.idForceField == id_forcefield).all()

            for instance in list_paramsClass:
                #print(instance.idParam,file=sys.stderr)
                resultList = db.session.query(ValueClass).filter(ValueClass.idParam == instance.idParam).all()
                #for x in resultList:
                #    print(x.key,file=sys.stderr)
                #    print(x.value,file=sys.stderr)
                
                #pour avoir le nombre de colonnes
                result_length = len(resultList)
                if(numberOfColumns < result_length):
                    numberOfColumns = result_length
            
                classAtoms = db.session.query(ClassAtom_ParamsClass).filter(ClassAtom_ParamsClass.idParam == instance.idParam , ClassAtom_ParamsClass.idForceField == id_forcefield).all()
                
                if (classAtoms and len(classAtoms) == 1 and classAtoms[0].description == None):
                    classAtoms = classAtoms[0].idClassAtom
                elif(classAtoms and (len(classAtoms) > 1 or classAtoms[0].description != None)):
                    classAtoms = classAtoms[0].description

                result = []
                result.append(classAtoms)
                for instance in resultList:
                    result.append(instance.value)
            
                rowList.append(row(resultList,result))
        
        else:
            keyList.append("Type")
            list_paramsClass = db.session.query(ParamsType).filter(ParamsType.idParameter == id_parameter , ParamsType.idForceField == id_forcefield).all()

            for instance in list_paramsClass:
                resultList = db.session.query(ValueType).filter(ValueType.idParam == instance.idParam).all()
            
                #pour avoir le nombre de colonnes
                result_length = len(resultList)
                if(numberOfColumns < result_length):
                    numberOfColumns = result_length

                classAtoms = db.session.query(AtomsType_ParamsType).filter(AtomsType_ParamsType.idParam == instance.idParam,AtomsType_ParamsType.idForceField == id_forcefield).all()

                if (classAtoms and len(classAtoms) == 1 and classAtoms[0].description == None):
                    classAtoms = classAtoms[0].idAtomType
                elif(classAtoms and (len(classAtoms) > 1 or classAtoms[0].description != None)):
                    classAtoms = classAtoms[0].description
            
                result = []
                result.append(classAtoms)
                for instance in resultList:
                    result.append(instance.value)

                rowList.append(row(resultList,result))

        #pour avoir la liste des Keys
        
        for x in rowList:
            if(len(x.resultList) == numberOfColumns):
                for xx in x.resultList:
                    keyList.append(xx.key)
                break
        
        print(keyList,file=sys.stderr)
        #on ajoute la colonne "class"
        #ici seulement on ajoute et pas avant!!
        if(len(keyList) > 1):
            numberOfColumns += 1
            session['keyList'] = keyList
            session['numberOfColumns'] = numberOfColumns
        
        else:
            getKeyList(forcefieldName,parameterName)
        
        return rowList

#This function will retrieve that value of Atom Definition
def retrieveAtmoDefTable(forcefieldName):
    #global keyList
    keyList = []
    rowList = []
    idForceField = db.session.query(ForceField.idForceField).filter(ForceField.nameForceField == forcefieldName)
    atomTypeList = db.session.query(AtomsType).filter(AtomsType.idForceField == idForceField).all()
    for atomType in atomTypeList:
        result = []
        result.append(atomType.idAtomType)
        result.append(atomType.class_atomParent.idClassAtom)
        result.append(atomType.class_atomParent.symbol)
        result.append(atomType.description)
        result.append(atomType.class_atomParent.atomicNumber)
        result.append(atomType.class_atomParent.atomicWeight)
        result.append(atomType.class_atomParent.valence)       
        rowList.append(row([],result))
    keyList.append("idAtomType")
    keyList.append("idClassAtom")
    keyList.append("symbol")
    keyList.append("description")
    keyList.append("atomicNumber")
    keyList.append("atomicWeight")
    keyList.append("valence")
    session['keyList'] = keyList
    return rowList

# Function that return the list of paramater name from idForceField
def ParameterOfForceField(IdForceField):
    nameParameterOfForceField = ["Atom Definition"]
    listOfParameter = db.session.query(ForceField).get(IdForceField).childrenParameter
    for instance in listOfParameter:
        nameParameterOfForceField.append(db.session.query(ParameterTable).get(instance.idParameter).nameParameter)

    return nameParameterOfForceField


class ff_params:
	nameForceField = ""
	listOfParameter = []
	def __init__(self,NameForceField,ListOfParameter):
		self.nameForceField = NameForceField
		self.listOfParameter = ListOfParameter

def getFFnameByUser(id):
    result = []
    user = db.session.query(User).get(id)
    for ff in user.forcefield_list:
        result.append(db.session.query(ForceField).get(ff.idForceField).nameForceField)
    return result

def getFFnameAndOwnerByUser(id):
    result = []
    user = db.session.query(User).get(id)
    for ff in user.forcefield_list:
        nameForceField = db.session.query(ForceField).get(ff.idForceField).nameForceField
        result.append([nameForceField,ff.isAuthor])
    return result

def getAuthorsByForceFieldName(ffName):
    ffInstance = db.session.query(ForceField).filter(ForceField.nameForceField == ffName).first()
    ownersList = ffInstance.owners
    result =[]

    for x in ownersList:
        result.append(x.idUser)
    
    return result


def is_author(user_id,forcefieldName):
    user = db.session.query(User).filter(User.user_id == user_id).first()
    if user:
        forcefield_id = db.session.query(ForceField).filter(ForceField.nameForceField == forcefieldName).first().idForceField
        idForcefieldList = (instance.idForceField for instance in user.forcefield_list)
        return forcefield_id in idForcefieldList
    else:
        return False

#get the all the authors of FF
def allAuthorsForcefied(idforcefield):
    userNameList = []
    ff_instance = db.session.query(ForceField).get(idforcefield)
    user_ff_instance_list = ff_instance.owners
    for instance in user_ff_instance_list:
        userName = db.session.query(User).get(instance.idUser).username
        userNameList.append(userName)
    return userNameList

#get only the owner(the person whom create the ff)
def getOwnerOfFF(idForceField):
    ownerId = -1
    result = ""
    ff_instance = db.session.query(ForceField).get(idForceField)
    for x in ff_instance.owners:
        print(x.isAuthor)
        if(x.isAuthor):
            ownerId = x.idUser

    if(ownerId != -1):
        ownerInstance = db.session.query(User).get(ownerId)
        result = ownerInstance.username
    else:
        result = None
    
    return result