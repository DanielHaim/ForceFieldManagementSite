from .views import *

#class to get object back form dict
def getObjBack(obj):
    for a, b in obj.items():
        if isinstance(b, (list, tuple)):
           setattr(self, a, [obj(x) if isinstance(x, dict) else x for x in b])
        else:
           setattr(self, a, obj(b) if isinstance(b, dict) else b)

class UndoRedoObject:

	operation = ''
	nameForceField = ''
	nameParameter = ''
	constantScalingFactorDataList = []
	atomClassDefinitionList = []
	parameterClassOrTypeList = []

	def __init__(self, operation,nameForceField,nameParameter="",atomClassDefinitionList=[],constantScalingFactorDataList=[],
                 parameterClassOrTypeList=[]):
        self.operation = operation # l'operation qui a ete operer add/delete/update
        self.nameForceField = nameForceField
        self.nameParameter = nameParameter
        #There is an object of AtomClassDefinition/constantSF/parameterClassOrType
        for instance in atomClassDefinitionList:
        	self.atomClassDefinitionList.append(instance.__dict__)
        #self.atomClassDefinitionList = atomClassDefinitionList[:] #copy the list of AtomClassDefinition object
        for instance in constantScalingFactorDataList:
        	self.constantScalingFactorDataList.append(instance.__dict__)
        #self.constantScalingFactorDataList = constantScalingFactorDataList[:] #copy the list of constantScalingFactorData object
        for instance in parameterClassOrTypeList:
        	self.parameterClassOrTypeList.append(instance.__dict__)
        #self.parameterClassOrTypeList = parameterClassOrTypeList[:]
    	

        
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

#function that handle the view of application after undo operation
#def undoApplication():
#        instanceUndo = session['listOfOperation'][session['countOperation']]
#        undoFunction()
#        
#        #code of tree
#        populateTree(None)
#
#        #THe next code refresh the view after the undo opered
#        if instanceUndo.operation == "addForceField" or instanceUndo.operation=="deleteForceField":
#            #We empty the central value table
#            self.tableParamsValue.setColumnCount(0)
#            self.tableParamsValue.setRowCount(0)
#        elif instanceUndo.operation == "deleteParameterToFF" or instanceUndo.operation == "addParameterToFF":
#            self.tableParamsValue.setColumnCount(0)
#            self.tableParamsValue.setRowCount(0)
#            for j in range (0,self.treeWidget.topLevelItemCount()):
#                if self.treeWidget.topLevelItem(j).text(0) == instanceUndo.nameForceField:
#                    self.treeWidget.topLevelItem(j).setExpanded(True)
#                    self.treeWidget.setCurrentItem(self.treeWidget.topLevelItem(j),0)
#                    break                 
#        else:
#            for j in range (0,self.treeWidget.topLevelItemCount()):
#                if self.treeWidget.topLevelItem(j).text(0) == instanceUndo.nameForceField:
#                    self.treeWidget.topLevelItem(j).setExpanded(True)
#                    for i in range(self.treeWidget.topLevelItem(j).childCount()):
#                        if self.treeWidget.topLevelItem(j).child(i).text(0) == instanceUndo.nameParameter:
#                            self.treeWidget.setCurrentItem(self.treeWidget.topLevelItem(j).child(i),0)
#                            break
#
##function that handle the logical operation after undo
#@app.route('/undoFunction')
#def undoFunction():
#    #undo/redo button 
#    session['redo'] = True
#    if session['countOperation'] == -1:
#        session['undo'] = False
#    else:
#    	if(session['countOperation']>-1):
#    		undoRedoObject = session['listOfOperation'][session['countOperation']]
#    		session['countOperation'] -=1
#    if session['countOperation'] == -1:
#    	session['undo'] = False 
#    	session['save'] = False
#    
#    # Now I analysis the last operation and back him, like she is never maked
#    if undoRedoObject.operation == "addForceField": # so i need to delete this forcefield
#        forceField = session.query(ForceField).filter(ForceField.nameForceField == undoRedoObject.nameForceField).scalar()
#        session.delete(forceField)
#        #####################################################
#    #elif undoRedoObject.operation == "deleteForceField":
#    #    newForceField = ForceField(undoRedoObject.nameForceField)
#    #    session.add(newForceField) 
#    #    session.flush()
#    #    recoverAtomDefinition(undoRedoObject.atomClassDefinitionList,newForceField.idForceField)
#    #    recoverScalingFactorConstant(undoRedoObject.constantScalingFactorDataList, newForceField.idForceField)
#    #    recoverParameter(undoRedoObject.parameterClassOrTypeList,newForceField.idForceField)
#    #    #####################################################
#    #elif undoRedoObject.operation == "addParameterToFF": #so i need to remove the added parameter
#    #    idForceField = session.query(ForceField.idForceField).filter(ForceField.nameForceField == undoRedoObject.nameForceField).scalar()
#    #    parameterInstance = session.query(ParameterTable).filter(ParameterTable.nameParameter == undoRedoObject.nameParameter).scalar()
#    #    for instance in session.query(ParametersOfForceField):
#    #        if instance.idForceField == idForceField and instance.idParameter == parameterInstance.idParameter:
#    #            session.delete(instance)
#    #            session.flush()
#    #    for instance in session.query(ForceField).get(idForceField).childrenParameter:
#    #        instanceParameter = session.query(ParameterTable).get(instance.idParameter)
#    #        if instanceParameter.idParameter == parameterInstance.idParameter:
#    #            session.query(ForceField).get(idForceField).childrenParameter.remove(instance)
#    #    #####################################################
#    #elif undoRedoObject.operation == "deleteParameterToFF": # The last operation was deleted parameter.
#    #    forceFieldId = session.query(ForceField.idForceField).filter(ForceField.nameForceField==undoRedoObject.nameForceField).scalar()
#    #    if undoRedoObject.nameParameter == "Atom Definition":
#    #        recoverAtomDefinition(undoRedoObject.atomClassDefinitionList,forceFieldId)
#    #        recoverScalingFactorConstant(undoRedoObject.constantScalingFactorDataList, forceFieldId)
#    #        recoverParameter(undoRedoObject.parameterClassOrTypeList,forceFieldId)
#    #    elif 'Scaling' in undoRedoObject.nameParameter or 'Constant' in  undoRedoObject.nameParameter:
#    #        recoverScalingFactorConstant(undoRedoObject.constantScalingFactorDataList, forceFieldId)
#    #    else:
#    #        recoverParameter(undoRedoObject.parameterClassOrTypeList,forceFieldId)
#    #    #####################################################
#    #elif undoRedoObject.operation == "addValueParameter":
#    #    deleteOneLineValue(undoRedoObject)
#    #    #####################################################
#    #elif undoRedoObject.operation == "deleteValueParameter":
#    #    addOneLineValue(undoRedoObject)
#    #    #####################################################
#    #elif undoRedoObject.operation == "updateValueParameter":
#    #    updateOneLineValue(undoRedoObject)
#    session.flush()


