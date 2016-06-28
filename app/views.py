from flask import render_template, flash, redirect, session, url_for, request, g ,current_app,jsonify,Markup,send_from_directory
from app import app ,db , lm 
from flask.ext.login import login_user, logout_user, current_user, login_required
from .form import *
from .token import *
from .models import *
from .gridFunction import *
from .OAuth import OAuthSignIn
from .email import send_confirmation_email,send_password_recovery_email
import json,anyjson,math,time,datetime,numpy as np
from time import gmtime, strftime
from json import dumps
from datetime import timedelta
from collections import Counter , OrderedDict
from werkzeug import secure_filename
from .undo_redo import sessionData , flashIndex , recoverAtomDefinition , recoverScalingFactorConstant, recoverParameter , UndoRedoObject ,\
 ConstantScalingFactorData , AtomClassDefinition , parameterClassOrType , recoverParameterNameFF , recoverUserOfFF,deleteOneLineValue,addOneLineValue,\
 deleteClassAtom,updateAtomClass,updateAtomType,deleteAllparameterOfClassAtom,editScalingFactor,updateScalingFactor,editParamsClass,updateParamsClass,rename,isParameterExist,\
 undoForAddParameterToFF,redoForAddParameterToFF,addValueParameterForRedo,deleteValueParameterForRedo,addClassAtomRedo,addAtomTypeRedo,deleteAtomType,editConstant,\
 updateConstant,updateParamsType,editParamType



#http://stackoverflow.com/questions/32909851/flask-session-vs-g
#g on the other hand is data shared between different parts of your 
#code base within one request cycle.
#c'est pour cela qu'avant chaque requette je redis g.user = curent_user
#pour pouvoir garder les infos constament de current_user dans g.
@app.before_request
def before_request():
    g.user = current_user
    #if the session expire(there is no session object)
    # as we have to disconnect the user.
    if not session:
        logout_user()
        flash('your session have expired','info')
        return redirect(url_for('index')) 


def login(user):
     session['numberOfColumns'] = -1
     session['keyList'] = []
     session['listOfOperation'] = []
     session['countOperation'] = -1
     session['undo'] = False
     session['redo'] = False
     session['save'] = False
     session['tableName'] = ''
     session['numberOfAtoms'] = -1
     login_user(user)
     session.permanent = True
     app.permanent_session_lifetime = timedelta(hours=1)
     

@app.route('/checkIsSaved')
def checkIsSaved():
    if(session['save']):
        return "False"
    else:
        return "True"


@app.route('/logOut',methods=['GET','POST'])
@app.route('/logOut/<string:toSave>')
def logOut(toSave=None):
    if(toSave == "0"):
        count = session['countOperation']
        while(count > -1):
            undoFunction()
            count = session['countOperation']      
    #i can do session.clear() so.
    del session['numberOfColumns']
    del session['keyList']
    del session['listOfOperation']
    del session['countOperation']
    del session['undo']
    del session['redo']
    del session['save']
    del session['tableName']
    del session['numberOfAtoms']
    #session.clear()
    logout_user()
    flash('logout user','danger')
    return redirect(url_for('index'))

@lm.user_loader
def load_user(id):
    return db.session.query(User).get(int(id))

@app.route('/')
@app.route('/index/')
def index():
    #result = []
    #forcefields_schema = ForceFieldSchema(many=True)
    #result = forcefields_schema.dump(forcefields).data
    #They are global fields that represent the columns number of Parameter and value
    dataTree = populateTree(None)
    dataGrid = "[]"
    columnsGrid = "[]"

    return render_template('index.html',
                       title='Home',
                       dataTree=dataTree,
                       dataGrid=dataGrid,
                       columnsGrid=columnsGrid)


@app.route('/signIn',methods=['GET','POST'])
def signIn():
    form = SignInForm()
    if form.validate_on_submit():
        user = db.session.query(User).filter(User.username == form.username.data).first()
        if(user and (user.password == form.password.data)):
            if(user.confirmed == False):
                token = generate_confirmation_token(user.email)
                confirm_url = url_for('confirm_email',token=token,_external=True)
                send_confirmation_email(user,confirm_url)
                flash('You have ton confirm your account via email activation link.','warning')
                flash('Please check your email and activate your account','warning')
                return redirect(url_for('signIn'))
            login(user)
            flash('Welcome!','success')
            return redirect('/index')
        else:
            flash('Username and password don\'t match','danger')
    return render_template('signIn.html',
                            title='SignIn',
                           form=form)


#_external=True allow to add "http://localhost:5000/" au URL
#la reference du url n'est pas le dossier actuelle mais 
#une reference externe a l'app
@app.route('/signUp',methods=['GET','POST'])
def signUp():
    form = SignUpForm()
    if form.validate_on_submit():
        firstname = form.firstname.data
        lastname = form.lastname.data
        username = form.username.data
        email = form.email.data
        password = form.password.data
        db.session.add(User(firstname,lastname,username,email,password))
        db.session.commit()
        user = db.session.query(User).filter(User.username == username).first()
        token = generate_confirmation_token(email)
        confirm_url = url_for('confirm_email',token=token,_external=True)
        send_confirmation_email(user,confirm_url)
        flash('Please check your email to complete activation account','success')
    return render_template('signUp.html',
                            title='SignUp',
                            form=form)

@app.route('/authorize/<sign_type>/<provider>')
def oauth_authorize(sign_type,provider):
    session['sign_type'] = sign_type
    if not current_user.is_anonymous:
        return redirect(url_for('index'))
    oauth = OAuthSignIn.get_provider(provider)
    return oauth.authorize()


@app.route('/callback/<provider>')
def oauth_callback(provider):
    if not current_user.is_anonymous:
        return redirect(url_for('index'))
    oauth = OAuthSignIn.get_provider(provider)
    user_info = oauth.callback()
    if user_info['social_network'] is None:
        flash('Authentication failed.')
        return redirect(url_for('signIn'))
    user = db.session.query(User).filter(User.username == user_info['username']).first()
    user_again = db.session.query(User).filter(User.email == user_info['email']).first()
    logOutProvider_url = user_info['logOutProvider_url']
    if((not user and not user_again) or (not user and user_again.confirmed == False)):
        if(session['sign_type'] == 'signUp'):
            user = User(user_info['firstname'],user_info['lastname'],user_info['username'],user_info['email'],social_network=user_info['social_network'])
            db.session.add(user)
            db.session.commit()
            flash('Your account successfuly created.Please signIn to continue.','success')
            return redirect(logOutProvider_url+'signIn')
        else:
            flash('You don\'t have an account.Please create an account to signIn.','warning')
            return redirect(logOutProvider_url+'signUp')
    else:
        if(session['sign_type'] == 'signUp'):
            flash('You have already registered,please signIn to continue.','warning')
            return redirect(logOutProvider_url+'signIn')
        else:
            if user:
                login(user)
            else:
                login(user_again)
            return redirect(logOutProvider_url+'index')



@app.route('/confirm/<token>')
def confirm_email(token):
    try:
        email = get_confirm_token(token)
    except:
        flash('The confirmation link is invalid or has expired.', 'danger')
    user = db.session.query(User).filter(User.email == email).first()
    if(user != None):
        if(user.confirmed):
            flash('Account already confirmed. Please login.', 'success')
        else:
            user.is_confirmed()
            db.session.add(user)
            db.session.commit()
            flash('You have confirmed your account.Thanks!.You can signIn now.', 'success')
    else:
        flash('The user account has been deleted', 'danger')
    return redirect(url_for('signIn'))


@app.route('/forgotPassword',methods=['GET','POST'])
def forgotPassword():
    form = forgotPasswordForm()
    if form.validate_on_submit():
        email = form.email.data
        user = db.session.query(User).filter(User.email == email).first()
        if(user):
            token = generate_passwordRecovery_token(email)
            passwordRecovery_url = url_for('passwordRecovery',token=token,_external=True)
            send_password_recovery_email(user,passwordRecovery_url)
            flash('Please check your email to get new password','info')
        else:
            flash('This email doesn\'t belong to any user','danger')
    return render_template('forgotPassword.html',title='Forgot Password',form=form) 


@app.route('/passwordRecovery/<token>',methods=['GET','POST'])
def passwordRecovery(token):
    try:
        email = get_passwordRecovery_token(token)
    except:
        flash('The link is invalid or has expired.', 'danger')
        return redirect(url_for('signIn'))
    user = db.session.query(User).filter(User.email == email).first()
    if(user):
        form = passwordRecoveryForm()
        if(form.validate_on_submit()):
            password = form.new_password.data
            user.password = password
            db.session.add(user)
            db.session.commit()
            flash('Your password was updated.You can sign In with it.','success')
            return redirect(url_for('signIn'))
    else:
        flash('This email doesn\'t belong to any user.')
        return redirect(url_for('signIn'))
    return render_template('passwordRecovery.html',form=form)



@app.route('/normal_profile',methods=['GET','POST'])
@login_required
def normal_profile():
    remove_account_form = removeAccountForm()
    password_form = changePasswordForm()
    user_info_form = userInfoForm()
    
    if(len(request.form) == 0):
        session['firstname'] = g.user.firstname
        session['lastname'] = g.user.lastname
        session['username'] = g.user.username
        session['email'] = g.user.email
        tag = ""

    if("firstname" in request.form):
        tag = "#user_info"
        if(user_info_form.validate_on_submit()):
            db.session.query(User).filter(User.user_id == g.user.user_id).update({'firstname':user_info_form.firstname.data})
            db.session.query(User).filter(User.user_id == g.user.user_id).update({'lastname':user_info_form.lastname.data})
            db.session.query(User).filter(User.user_id == g.user.user_id).update({'username':user_info_form.username.data})
            db.session.query(User).filter(User.user_id == g.user.user_id).update({'email':user_info_form.email.data})
            db.session.commit()
            flash('Your personnal information are saved','success')
            return redirect(url_for('normal_profile'))
        else:
            for fieldName,value in user_info_form.errors.items():
                session[fieldName] = getattr(user_info_form,fieldName).data
            flash('We can\'t update your personal info','danger')
    if("old_password" in request.form):
        tag = "#changePassword"
        if(password_form.validate_on_submit()):
            if(g.user.password == password_form.old_password.data):
                db.session.query(User).filter(User.user_id == g.user.user_id).update({'password':password_form.new_password.data})
                db.session.query(User).filter(User.user_id == g.user.user_id).update({'password_registered_on': datetime.datetime.now()})
                db.session.commit()
                flash('Your new password is now in use','success')
                return redirect(url_for('normal_profile'))
            else:
                flash('The password is incorect','danger')
    if("password" in request.form):
        tag = "#removeAccount"
        if(remove_account_form.validate_on_submit()):
            if(g.user.password == remove_account_form.password.data):
               user =  db.session.query(User).get(g.user.user_id)
               db.session.delete(user)
               db.session.commit()
               flash("Your account has been removed",'success')
               return redirect(url_for('signUp'))
            else:
                flash("Your password is incorect",'danger')
    
    user_info_form.firstname.data = session['firstname']
    user_info_form.lastname.data = session['lastname']
    user_info_form.username.data = session['username']
    user_info_form.email.data = session['email']
    ff_name_list = getFFnameByUser(g.user.user_id)
    return render_template('normal_profile.html',title="Profile",form1=user_info_form,form2=password_form,form3=remove_account_form,ff_name_list=ff_name_list,scroll=tag)

@app.route('/socialNetwork_profile',methods=['GET','POST'])
#@login_required
def socialNetwork_profile():
    network_user_info_form = networkUserInfoForm()
    if(len(request.form) == 0):
        session['firstname'] = g.user.firstname
        session['lastname'] = g.user.lastname
        session['email'] = g.user.email
    if("firstname" in request.form):
        if(network_user_info_form.validate_on_submit()):
            db.session.query(User).filter(User.user_id == g.user.user_id).update({'firstname':network_user_info_form.firstname.data})
            db.session.query(User).filter(User.user_id == g.user.user_id).update({'lastname':network_user_info_form.lastname.data})
            db.session.query(User).filter(User.user_id == g.user.user_id).update({'email':network_user_info_form.email.data})
            db.session.commit()
            flash('Your personnal information are saved','success')
            return redirect(url_for('socialNetwork_profile'))
        else:
            for fieldName,value in network_user_info_form.errors.items():
                session[fieldName] = getattr(network_user_info_form,fieldName).data
            flash('We can\'t update your personal info','danger')
    
    network_user_info_form.firstname.data = session['firstname']
    network_user_info_form.lastname.data = session['lastname']
    network_user_info_form.email.data = session['email']
    ff_name_list = getFFnameByUser(g.user.user_id)
    return render_template('socialNetwork_profile.html',form=network_user_info_form,ff_name_list=ff_name_list)

@app.route('/removeAccount/<token>')
def removeAccount(token):
    if(g.user.checkUserToken(token)):
        db.session.delete(g.user)
        db.session.commit()
        flash('Your account was successfully deleted.','success')
    else:
        flash('Bad token , we can\'t remove the user.','danger')
    return redirect(url_for('signUp'))

@app.route('/dataTree/<string:input>')
def populateTree(input = None):
    #get the Forcefield list of current_user
    authorList = []
    if not current_user.is_anonymous():
        authorList = getFFnameByUser(current_user.user_id)
    
    forcefields = db.session.query(ForceField).all()
    ff_params_list = []
    for ff in forcefields:
        if (input == None or input == "None"):
            ff_params_list.append(ff_params(ff.nameForceField,ParameterOfForceField(ff.idForceField)))
        elif((ff.nameForceField.lower()).startswith(input.lower())):
            ff_params_list.append(ff_params(ff.nameForceField,ParameterOfForceField(ff.idForceField)))

    source = "["
    for instance in ff_params_list:
        if(instance.nameForceField in authorList):
            source += "{ html:\"<span style='color:green;'>" + instance.nameForceField + "</span>\""
        else:
            source += "{ label:\"" + instance.nameForceField + "\""
        if (len(instance.listOfParameter) > 0):
            source += ",items:["
            for paramsInstance in instance.listOfParameter:
                if(instance.nameForceField in authorList):
                    source += "{ html:\"<span style='color:green;'>" + paramsInstance + "</span>\"},"
                else:
                    source += "{ label:'" + paramsInstance + "'},"
            source = source[:-1]
            source += "]},"
        elif(len(instance.listOfParameter) == 0):
            source += "},"
    if(source != "["):
        source = source[:-1]
    if(input == "None"):
        source += ",{label:'toRemove'}"
    source += "]"
        
    #target = open("/Users/daniel/Desktop/data1.txt",'w')
    #target.write(source)
    #target.close()
    
    return source 


@app.route('/dataGrid/<string:ForceFieldName>/<string:ParameterName>')
def dataGrid(ForceFieldName,ParameterName):
        if(ParameterName == "Atom Definition"):
            rowList = retrieveAtmoDefTable(ForceFieldName)
        else:
            rowList = retrieveValue(ForceFieldName,ParameterName)
        data = data_to_json(rowList,session['keyList'])
        return(data)


@app.route('/columsGrid/<string:ForceFieldName>/<string:ParameterName>')
def columsGrid(ForceFieldName,ParameterName):
    if(not g.user.is_anonymous()):
        userId = g.user.user_id
        var  = is_author(userId,ForceFieldName)
    else:
        var = False
    if(ParameterName == "Atom Definition"):
        rowList = retrieveAtmoDefTable(ForceFieldName)
    else:
        rowList = retrieveValue(ForceFieldName,ParameterName)
    array = sizeComputation(rowList,session['keyList'])
    columnsList = columnsList_to_json(session['keyList'],array,var)
    return (columnsList)

@app.route('/columnsList/<string:ParameterName>/')
def columnsList(ParameterName):
    parameterObject = db.session.query(ParameterTable).filter(ParameterTable.nameParameter == ParameterName).scalar()
    ffId = parameterObject.associatedForcefield[0].idForceField
    ffName = db.session.query(ForceField).get(ffId).nameForceField
    if(ParameterName == "Atom Definition"):
        rowList = retrieveAtmoDefTable(ffName)
    else:
        rowList = retrieveValue(ffName,ParameterName)
    columnsList = columnsList_to_JS(session['keyList'])
    return (columnsList)

@app.route('/dataFieldGrid/<string:ForceFieldName>/<string:ParameterName>')
def dataFieldGrid(ForceFieldName,ParameterName):
    """
    a l'origine ces lignes de code etait juste pour recuperer la 
    keyList , mais je ne pense pas necessaire d'appeller la fonction
    retrieveValue a chaque fois pour avoir la keyList vu que cette
    fonction (dataFieldGrid) est appeller a chaque fois apres la fonction
    dataGrid , qui elle appelle retrieveValue qui rempli la keyList
    donc je suppose que la keyList est deja rempli avec les bonnes
    valeurs. (a verifier!)
    """
    #if(ParameterName == "Atom Definition"):
    #    rowList = retrieveAtmoDefTable(ForceFieldName)
    #else:
    #    rowList = retrieveValue(ForceFieldName,ParameterName)
    dataField = dataFieldGrid_to_json(session['keyList'])
    return dataField

@app.route('/getKeyList/')
def getKeyList():
    #result = "['checkBoxColumn','numberOfRow',"
    result = "["
    for elementKey in session['keyList']:
        result += "'" + elementKey + "',"
    result = result[:-1]
    result += "]"

    return result


@app.route('/getHtmlKeyList/')
def getHtmlKeyList():
    #result = Markup("<h1>Salut les coco je fait un test</h1>")
    htmlKeyList = ""
    for elementKey in session['keyList']:
        htmlKeyList += """
                    <tr>
                        <td align='left'>"""+elementKey[0].upper() + elementKey[1:] +""":</td>
                        <td align='left'><input """

        if(elementKey == "idClassAtom"):
            htmlKeyList += """onkeyup='fulfillClassAtomData(this,"")'"""
        if(elementKey == "idAtomType"):
            htmlKeyList += """onkeyup='fulfillAtomTypeData(this,"")'"""
        
        htmlKeyList += """style='border-radius:3px;box-shadow:0 0 0;' id="""+elementKey.replace(" ","_").replace("(","_").replace(")","_").replace("-","_")+"""_ /></td>
                    </tr>
                    <tr>
                        <td></td>
                        <td>
                            <div style='min-height:15px;color:red;font-size:12px;' id="""+elementKey.replace(" ","_").replace("(","_").replace(")","_").replace("-","_")+"""Error_></div>
                        </td>
                    </tr>"""

    htmlKeyList += """
            <tr>
                <td style='padding-top: 10px;' colspan=2>
                    <span id='general_error_' style='width:60%;min-height:20px;float:left;color:red;font-size:12px;'></span>
                    <span style='width:40%;float:right;'>
                        <input id='cancelButton_' style='float:right;' type='button' value='Cancel' />
                        <input style='margin-right: 5px;float:right;' type='button' id='saveButton_' value='Save' />
                    </span>
                </td>
            </tr>
        
    """
    if("idAtomType" in session['keyList'] and "idClassAtom" in session['keyList']):
        listkeyClass = ["idClassAtom","symbol","atomicNumber","atomicWeight","valence"]
        listkeyAtom = ["idAtomType","idClassAtom","description"]
        htmlKeyList += "%%%"
        htmlKeyList += """
                        <tr style="height:30px;">
                            <td colspan=2 >
                                <span>List of class atom:</span>
                                <div style="float:right" id="ddl_classAtom">
                                </div>
                            </td>
                        </tr>
                        <tr style="height:13px;">
                            <td colspan=2 style="text-align:center;">
                                <a style="font-size:13px;" href="#" onclick="addClassAtomLink('Class')">add new atom class:</a>
                            </td>
                        </tr>
                """
        for elementKey in listkeyClass:
            htmlKeyList += """
                    <tr style="height:30px;">
                        <td align='left'>"""+elementKey[0].upper() + elementKey[1:] +""":</td>
                        <td align='left'><input """

            if(elementKey == "idClassAtom"):
                htmlKeyList += """onkeyup='fulfillClassAtomData(this,"Class")'"""
            if(elementKey == "idAtomType"):
                htmlKeyList += """onkeyup='fulfillAtomTypeData(this,"Class")'"""
        
            htmlKeyList += """style='border-radius:3px;box-shadow:0 0 0;' id="""+elementKey.replace(" ","_").replace("(","_").replace(")","_").replace("-","_")+"""_Class /></td>
                        </tr>
                        <tr style="height:20px;">
                            <td></td>
                            <td>
                                <div style='min-height:15px;color:red;font-size:12px;' id="""+elementKey.replace(" ","_").replace("(","_").replace(")","_").replace("-","_")+"""Error_Class></div>
                            </td>
                        </tr>"""

        htmlKeyList += """
                <tr>
                    <td style='padding-top: 10px;vertical-align:bottom;' colspan=2>
                        <span id='general_error_Class' style='width:60%;min-height:20px;float:left;color:red;font-size:12px;'></span>
                        <span style='width:40%;float:right;'>
                            <input id='cancelButton_Class' style='float:right;' type='button' value='Cancel' />
                            <input style='margin-right: 5px;float:right;' type='button' id='saveButton_Class' value='Save' />
                        </span>
                    </td>
                </tr>
            
        """
        htmlKeyList += "%%%"
        htmlKeyList += """
                <tr style="height:30px;">
                    <td colspan=2 >
                        <span>List of atom type:</span>
                        <div style="float:right" id="ddl_AtomType">
                        </div>
                    </td>
                </tr>
                <tr style="height:20px;"></tr>
                <tr style="height:13px;">
                    <td colspan=2 style="text-align:center;">
                        <a style="font-size:13px;" href="#" onclick="addAtomTypeLink('Type')">add new atom type:</a>
                    </td>
                </tr>
                <tr style="height:20px;"></tr>
        """
        for elementKey in listkeyAtom:
            htmlKeyList += """
                    <tr style="height:30px;">
                        <td align='left'>"""+elementKey[0].upper() + elementKey[1:] +""":</td>
                        <td align='left'><input """

            if(elementKey == "idAtomType"):
                htmlKeyList += """onkeyup='fulfillAtomTypeData(this,"Type")'"""
        
            htmlKeyList += """style='border-radius:3px;box-shadow:0 0 0;' id="""+elementKey.replace(" ","_").replace("(","_").replace(")","_").replace("-","_")+"""_Type /></td>
                        </tr>
                        <tr style="height:20px">
                            <td></td>
                            <td>
                                <div style='min-height:15px;color:red;font-size:12px;' id="""+elementKey.replace(" ","_").replace("(","_").replace(")","_").replace("-","_")+"""Error_Type></div>
                            </td>
                        </tr>"""

        htmlKeyList += """
                <tr>
                    <td style='padding-top: 10px;vertical-align:bottom;' colspan=2>
                        <span id='general_error_Type' style='width:60%;min-height:20px;float:left;color:red;font-size:12px;'></span>
                        <span style='width:40%;float:right;'>
                            <input id='cancelButton_Type' style='float:right;' type='button' value='Cancel' />
                            <input style='margin-right: 5px;float:right;' type='button' id='saveButton_Type' value='Save' />
                        </span>
                    </td>
                </tr>
            
        """
    return htmlKeyList+"@"+str(session["numberOfAtoms"])               
   

@app.route('/getDataAtomType/<string:ffName>/<string:idAtomType>')
def getDataAtomType(ffName,idAtomType):
    idForceField = db.session.query(ForceField.idForceField).filter(ForceField.nameForceField == ffName)
    if(idAtomType != "" and idAtomType.isdigit()):
        atomType_instance = db.session.query(AtomsType).filter(AtomsType.idAtomType == int(idAtomType) , AtomsType.idForceField == idForceField).first()
        if(atomType_instance):
            classAtomInstance = db.session.query(ClassAtom).filter(ClassAtom.idClassAtom == atomType_instance.idClassAtom,ClassAtom.idForceField == idForceField).first()
            result = '{"idClassAtom":'+str(classAtomInstance.idClassAtom)+',"symbol":"'+str(classAtomInstance.symbol)+'","description":"'+str(atomType_instance.description)+'","atomicNumber":'+str(classAtomInstance.atomicNumber)\
                +',"atomicWeight":'+str(classAtomInstance.atomicWeight)+',"valence":'+str(classAtomInstance.valence)+'}'
        else:
            result = "None"
    else:
        result = "None"
    return result


@app.route('/getDataClassAtom/<string:ffName>/<string:idClassAtom>')
def getDataClassAtom(ffName,idClassAtom):
    idForceField = db.session.query(ForceField.idForceField).filter(ForceField.nameForceField == ffName).scalar()
    print(idForceField,file=sys.stderr)
    if(idClassAtom != "" and idClassAtom.isdigit()):
        instance = db.session.query(ClassAtom).filter(ClassAtom.idClassAtom == int(idClassAtom) , ClassAtom.idForceField == idForceField).first()
        if(instance):
            result = '{"symbol":"'+str(instance.symbol)+'","atomicNumber":'+str(instance.atomicNumber)\
                +',"atomicWeight":'+str(instance.atomicWeight)+',"valence":'+str(instance.valence)+'}'
        else:
            result = "None"
    else:
        result = "None"
    return result

@app.route('/getAllForceField/')
def getAllForceField():
    forcefields = db.session.query(ForceField).all()
    FFList = "["
    for ff in forcefields:
        FFList += "'" + ff.nameForceField + "',"
    FFList = FFList[:-1]
    FFList += "]"

    return FFList

@app.route('/getForceFieldList/')
def getForceFieldList():
    #forcefields = db.session.query(ForceField).all()
    forcefields = getFFnameByUser(g.user.user_id)
    FFList = "["
    for ff in forcefields:
        FFList += "'" + ff + "',"
    FFList = FFList[:-1]
    FFList += "]"

    return FFList

@app.route('/getForceFieldListForMaster')
def getForceFieldListForMaster():
    forcefields = getFFnameAndOwnerByUser(g.user.user_id)
    FFList = "["
    for ff in forcefields:
        FFList += "{'ffName':"+"'" + ff[0] + "','owner':"+"'"+str(ff[1])+"'},"
    
    if(FFList != "["):
        FFList = FFList[:-1]
    FFList += "]"

    return FFList

@app.route('/addUserToFF/<string:ffName>/<string:username>')
def addUserToFF(ffName,username):
    #check if the user exist
    isUser = db.session.query(User).filter(User.username == username).first()
    if(not isUser):
        return flashIndex('The user '+username+' dosen\'t exist on our database.','error')
    else:
        #check if is already on this ff and if not add him
        ffInstance = db.session.query(ForceField).filter(ForceField.nameForceField == ffName).first()
        idAuthorList = ffInstance.owners
        idAuthorList = [x.idUser for x in idAuthorList]
        if(isUser.user_id in idAuthorList):
            return flashIndex('The user '+username +' is already an author of the selected forcefield.','error')
        else:
            #we add the user to the selected ff
            newInstance = UserForceField()
            newInstance.ff_instance = ffInstance
            newInstance.user_instance = isUser
            newInstance.isAuthor = False
            db.session.add(newInstance)
            db.session.commit()
            return flashIndex('The user '+ username +' is successfully added to the forcefield '+ffName+'.','success')

@app.route('/deleteUserToFF/<string:ffName>/<string:username>')
def deleteUserToFF(ffName,username):
    isHimself = False
    #check if the user exist
    isUser = db.session.query(User).filter(User.username == username).first()
    if(not isUser):
        return flashIndex('The user '+username+' dosen\'t exist on our database.','error',sessionData(nameParameter=str(isHimself)))
    else:
        #check if is already on this ff and if yes so delete him
        ffInstance = db.session.query(ForceField).filter(ForceField.nameForceField == ffName).first()
        idAuthorList = ffInstance.owners
        idAuthorList = [x.idUser for x in idAuthorList]
        if(isUser.user_id in idAuthorList):
            #before i deleted him i check if the username is current user of the session
            if(isUser.user_id == g.user.user_id):
                isHimself = True
            #we delete the user from the selected ff
            instanceToDelete = db.session.query(UserForceField).get((isUser.user_id,ffInstance.idForceField))
            db.session.delete(instanceToDelete)
            db.session.commit() 
            return flashIndex('The user '+ username +' is successfully deleted from the forcefield '+ffName+'.','success',sessionData(nameParameter=str(isHimself)))
        else:
            return flashIndex('The user '+username +' is already an author of the selected forcefield.','error',sessionData(nameParameter=str(isHimself)))


@app.route('/getAuthorsForDetails/<string:ffName>')
def getAuthorsForDetails(ffName):
    idAuthorsList = getAuthorsByForceFieldName(ffName)
    authorsList = "["
    
    for idAuthor in idAuthorsList:
        authorInstance = db.session.query(User).get(idAuthor)
        authorsList += "{'username':'"+authorInstance.username+"',"
        authorsList += "'firstname':'"+authorInstance.firstname+"',"
        authorsList += "'lastname':'"+authorInstance.lastname+"',"
        authorsList += "'email':'"+authorInstance.email+"'},"

    if(authorsList != "["):
        authorsList = authorsList[:-1]
    authorsList += "]"

    return authorsList

@app.route('/isOldAtomClassStillUsed/<string:forceFieldName>/<string:idClassAtom>')
def isOldAtomClassStillUsed(forceFieldName,idClassAtom):
    idForceField = db.session.query(ForceField.idForceField).filter(ForceField.nameForceField == forceFieldName).scalar()
    atomTypeInstances = db.session.query(AtomsType).filter(AtomsType.idClassAtom == int(idClassAtom),AtomsType.idForceField == idForceField).all()
    if(len(atomTypeInstances) > 1):
        return "still"
    if(len(atomTypeInstances) == 1):
        ClassAtom_ParamsClass_Instances = db.session.query(ClassAtom_ParamsClass).filter(ClassAtom_ParamsClass.idForceField == idForceField,ClassAtom_ParamsClass.idClassAtom == int(idClassAtom)).all()
        if(ClassAtom_ParamsClass_Instances):
            return "noStill"
        else:
            return "False"

@app.route('/isClassAtomExist/<string:forceFieldName>/<string:idClassAtom>')
def isClassAtomExist(forceFieldName,idClassAtom):
    idForceField = db.session.query(ForceField.idForceField).filter(ForceField.nameForceField == forceFieldName).scalar()
    classAtomInstance = db.session.query(ClassAtom).get((int(idClassAtom),idForceField))
    if(classAtomInstance):
        return "True"
    else:
        return "False"

@app.route('/getClassAtomList/<string:forcefieldName>')
def getClassAtomList(forcefieldName):
    idForceField = db.session.query(ForceField.idForceField).filter(ForceField.nameForceField == forcefieldName).scalar()
    idClassAtoms = db.session.query(ClassAtom.idClassAtom).filter(ClassAtom.idForceField == idForceField).all()
    resultList = "["
    for idClassAtom in idClassAtoms:
        resultList += str(idClassAtom[0]) + ','
    resultList = resultList[:-1]
    resultList += "]"
    return resultList

@app.route('/getAtomTypeList/<string:forcefieldName>')
def getAtomTypeList(forcefieldName):
    idForceField = db.session.query(ForceField.idForceField).filter(ForceField.nameForceField == forcefieldName).scalar()
    idAtomTypes = db.session.query(AtomsType.idAtomType).filter(AtomsType.idForceField == idForceField).all()
    #get all number as list of number and not as list of (list of number)
    idAtomTypes = [x[0] for x in idAtomTypes]
    #remove all duplicate data
    idAtomTypes = list(set(idAtomTypes))
    
    resultList = "["
    for idAtomType in idAtomTypes:
        resultList += str(idAtomType) + ','
    resultList = resultList[:-1]
    resultList += "]"
    return resultList


@app.route('/getParameterOfForceField/<string:ForceFieldName>/')
def getParameterOfForceField(ForceFieldName):
    idForceField = db.session.query(ForceField.idForceField).filter(ForceField.nameForceField == ForceFieldName).scalar()
    parameter = ParameterOfForceField(idForceField)
    #parameter.remove('Atom Definition')
    result = "["

    for instance in parameter:
        result += "'" + instance + "',"
    if(len(result)>1):
        result = result[:-1]
    
    result += "]"
    return result

@app.route('/getOtherParameterOfForceField/<string:ForceFieldName>/')
def getOtherParameterOfForceField(ForceFieldName):
    idForceField = db.session.query(ForceField.idForceField).filter(ForceField.nameForceField == ForceFieldName).scalar()
    parameter = ParameterOfForceField(idForceField)
    parameterList = db.session.query(ParameterTable).filter(ParameterTable.parameterType == 'Parameter').all()
    parameterList = [x.nameParameter for x in parameterList]
    if 'Atom Definition' in parameterList:
        parameterList.remove('Atom Definition')
    result = "["
    for instance in parameterList:
        if(instance not in parameter):
            result += "'" + instance + "',"
    result = result[:-1]
    result += "]"
    return result

@app.route('/isParameterInForcefield/<string:ForceFieldName>/<string:ParameterName>/')
def isParameterInForcefield(ForceFieldName,ParameterName):
    idForceField = db.session.query(ForceField.idForceField).filter(ForceField.nameForceField == ForceFieldName).scalar()
    parameter = ParameterOfForceField(idForceField)
    parameter = [x.lower() for x in parameter]
    if(ParameterName.lower() in parameter):
        return "True"
    else:
        return "False"


@app.route('/isAuthor/<int:user_id>/<string:forcefieldName>')
def isAuthor(user_id,forcefieldName):
    if(is_author(user_id,forcefieldName)):
        return "True"
    else:
        return "False"

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']


@app.route('/upload_file/<string:format>', methods=['GET','POST'])
def upload_file(format):
    file = request.files['file']
    target = open("/Users/daniel/Desktop/data1.txt",'w')
    target.write(str(format))
    target.close()
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    return redirect(url_for('index') or url_for('uploaded_file',
                                    filename=filename))



@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)

#for x in parametersList:
#print(x, file=sys.stderr)

@app.route('/addForcefield/<string:ForceFieldName>')
def createForceFieldOk(ForceFieldName):
    #try:
    usernameList = []
    UserNamesList = []
    for key,value in request.args.items():
        usernameList.append(value)

    print(usernameList,file=sys.stderr)
    ff_list = db.session.query(ForceField.nameForceField).all()
    ff_list = [x[0] for x in ff_list]

    user_list = db.session.query(User.username).all()
    user_list = [x[0] for x in user_list]
    
    #check if ff exist
    if ForceFieldName in ff_list:
        return flashIndex('Existing forcefield.','error',sessionData(operation='addForcefield'))

    #check if authors are registered user on database
    for username in usernameList:
        if(username not in user_list):
            return flashIndex('Username ' + username + ": doesn't exist",'error',sessionData(operation='addForcefield'))
    
    #check duplicate value of username
    duplicateList = [k for k,v in Counter(usernameList).items() if v>1]
    if(len(duplicateList) > 0):
        return flashIndex('There is two authors with the same username!','error',sessionData(operation='addForcefield'))
    

    #if the FF not already exist so we can add it
    newForceField = ForceField(ForceFieldName)
    db.session.add(newForceField)
    db.session.flush()
    
    #we assign the user of usernameList as authors of this ff
    for username in usernameList:
        user = db.session.query(User).filter(User.username == username).one()
        UserNamesList.append(username)
        if(user.user_id == g.user.user_id):
            isAuthor = True
        else:
            isAuthor = False
        user_ff_instance = UserForceField()
        user_ff_instance.ff_instance = newForceField
        user_ff_instance.user_instance = user
        user_ff_instance.isAuthor = isAuthor
        db.session.add(user_ff_instance)
        db.session.commit()


    #for the undo operation
    instanceForUndoRedo = UndoRedoObject("addForceField",newForceField.nameForceField,listUserOfForceField=UserNamesList,ownerFF=g.user.username)
    #countOperation is an index so we are doing minus 1 to the lenght
    if session['countOperation'] != (len(session['listOfOperation']) -1):
        for i in range((len(session['listOfOperation'])-1),session['countOperation'],-1):
            session['listOfOperation'].pop(i)
        
        #there is no redo operation so we put the redo button in disabled mode
        session['redo'] = False
                   
    #we added a FF so count is incremented by one
    session['countOperation'] +=1
    session['listOfOperation'].append(instanceForUndoRedo)
    session['undo']= True
    session['save']= True

    return flashIndex('Forcefield added','success',sessionData(operation='addForceField'))   
    #except:
    #    return flashIndex('Process error.','error',sessionData())

#aple = session['listOfOperation'][0]
#pie = session['listOfOperation'][0]
#print(aple,file=sys.stderr)
#print(pie,file=sys.stderr)
#print(aple['operation'],file=sys.stderr)
#print(pie['operation'],file=sys.stderr) 



#function that handle the logical operation after undo
@app.route('/undoFunction')
def undoFunction():
    #we execute this code because you clicked on undo so there is redo 
    session['redo'] = True
    if session['countOperation'] == -1:
        session['undo'] = False
    else:
       if(session['countOperation'] > -1):
               undoRedoObject = session['listOfOperation'][session['countOperation']]
               session['countOperation'] -=1
    if session['countOperation'] == -1:
       session['undo'] = False
       session['save'] = False

    # Now I analysis the last operation and back him, like she is never maked
    if undoRedoObject['operation'] == "addForceField": # so i need to delete this forcefield
        forceField = db.session.query(ForceField).filter(ForceField.nameForceField == undoRedoObject['nameForceField']).scalar()
        db.session.delete(forceField)
        #####################################################
    elif undoRedoObject['operation'] == "deleteForceField":
        #add New FF in forcefield table
        newForceField = ForceField(undoRedoObject['nameForceField'])
        db.session.add(newForceField)
        db.session.commit()

        #Link in UserForceField current_user as author of this FF
        #user = current_user
        #UserForceFieldInstance = UserForceField()
        #UserForceFieldInstance.user_instance = user
        #UserForceFieldInstance.ff_instance = newForceField
        
        #db.session.add(UserForceFieldInstance)
        #db.session.commit()
        recoverParameterNameFF(undoRedoObject['listParameterNameFF'],newForceField.idForceField)
        recoverUserOfFF(undoRedoObject['ownerFF'],undoRedoObject['listUserOfForceField'],newForceField.idForceField)
        recoverAtomDefinition(undoRedoObject['atomClassDefinitionList'],newForceField.idForceField)
        recoverScalingFactorConstant(undoRedoObject['constantScalingFactorDataList'], newForceField.idForceField)
        recoverParameter(undoRedoObject['parameterClassOrTypeList'],newForceField.idForceField)
        #####################################################
    elif undoRedoObject['operation'] == "addParameterToFF" or undoRedoObject['operation'] == "addSFToFF" or undoRedoObject['operation'] == "addConstantToFF":
        undoForAddParameterToFF(undoRedoObject)
        #####################################################
    elif undoRedoObject['operation'] == "deleteParameterToFF": # The last operation was deleted parameter.
        forceFieldId = db.session.query(ForceField.idForceField).filter(ForceField.nameForceField==undoRedoObject['nameForceField']).scalar()
        if undoRedoObject['nameParameter'] == "Atom Definition":
            recoverParameterNameFF(undoRedoObject['listParameterNameFF'],forceFieldId)
            recoverAtomDefinition(undoRedoObject['atomClassDefinitionList'],forceFieldId)
            recoverScalingFactorConstant(undoRedoObject['constantScalingFactorDataList'], forceFieldId)
            recoverParameter(undoRedoObject['parameterClassOrTypeList'],forceFieldId)
        elif 'Scaling' in undoRedoObject['nameParameter'] or 'Constant' in  undoRedoObject['nameParameter']:
            recoverScalingFactorConstant(undoRedoObject['constantScalingFactorDataList'], forceFieldId)
            recoverParameterNameFF([undoRedoObject['nameParameter']],forceFieldId)
        else:
            recoverParameter(undoRedoObject['parameterClassOrTypeList'],forceFieldId)
            recoverParameterNameFF([undoRedoObject['nameParameter']],forceFieldId)
        #####################################################
    elif undoRedoObject['operation'] == "addValueParameter":
        deleteOneLineValue(undoRedoObject)
    elif undoRedoObject['operation'] == "deleteValueParameter":
        addOneLineValue(undoRedoObject)
    elif undoRedoObject['operation'] == "addClassAtom":
        deleteClassAtom(undoRedoObject)
    elif undoRedoObject['operation'] == "addAtomType":
        deleteAtomType(undoRedoObject)
    elif undoRedoObject['operation'] == "editAtomClass":
        updateAtomClass(undoRedoObject,0)
    elif undoRedoObject['operation'] == "editAtomType":
        updateAtomType(undoRedoObject,0)
    elif undoRedoObject['operation'] == "editAtomDefinition":
        updateAtomType(undoRedoObject,0)
    elif undoRedoObject['operation'] == "editScalinFactor":
        updateScalingFactor(undoRedoObject,0)
    elif undoRedoObject['operation'] == "editConstant":
        updateConstant(undoRedoObject,0)       
    elif undoRedoObject['operation'] == "editParamsClass":
        updateParamsClass(undoRedoObject,0)
    elif undoRedoObject['operation'] == "editParamsType":
        updateParamsType(undoRedoObject,0)
    elif undoRedoObject['operation'] == "renameFF" or undoRedoObject['operation'] == "renameParameter":
        rename(undoRedoObject)

    
    db.session.commit()
    
    if(undoRedoObject):
        operation = undoRedoObject['operation']
        nameForceField = undoRedoObject['nameForceField']
        nameParameter = undoRedoObject['nameParameter']
    else:
        operation = None
        nameForceField = None
        nameParameter = None

    if(undoRedoObject['operation'] == 'renameFF'):
        nameForceField = undoRedoObject['oldValue']
    if(undoRedoObject['operation'] == 'renameParameter'):
        nameParameter = undoRedoObject['oldValue']

    return flashIndex('','',sessionData(operation,nameForceField,nameParameter))


@app.route('/removeForceFieldOk/<string:nameFF>')
def removeForceFieldOk(nameFF):
    listForAtom = []
    listForConstantScaling = []
    listForParameter = []
    listNameParameter=[]
    listUserOfForceField=[]
    keyValue = {}
    description = ""

    idForceField = db.session.query(ForceField.idForceField).filter(ForceField.nameForceField == nameFF).scalar()
    
    #retrieve all instance belong to this ff from AtomType Table
    listClassAtom = db.session.query(ClassAtom).filter(ClassAtom.idForceField == idForceField).all()
    for instanceClass in listClassAtom:
        listAtomsType = db.session.query(AtomsType).filter(AtomsType.idClassAtom == instanceClass.idClassAtom,AtomsType.idForceField == idForceField).all()
        for instanceAtom in listAtomsType:
            newAtom = AtomClassDefinition(instanceAtom.idClassAtom,instanceClass.symbol,instanceClass.atomicNumber,
                                              instanceClass.atomicWeight,instanceClass.valence,instanceAtom.idAtomType,
                                              instanceAtom.description)
            listForAtom.append(newAtom)

    #retrieve all parameter of this ff
    for instance in ParameterOfForceField(idForceField):
        if instance != "Atom Definition":
            listNameParameter.append(instance)

    #retrieve all author of this ff
    listUserOfForceField = allAuthorsForcefied(idForceField)
    #get owner of this ff
    ownerUsername = getOwnerOfFF(idForceField)

    
    listSF = db.session.query(ScalingFactorTable).filter(ScalingFactorTable.idForceField == idForceField).all()
    listParameter = [x.idParameter for x in listSF]
    listParameter = list(set(listParameter))
    for idParameter in listParameter:
        count = 0
        keyValue = {}
        rowSF = [instance for instance in listSF if instance.idParameter == idParameter]
        for instance in rowSF:
            keyValue[str(count)+'_'+instance.key] = instance.value
            count = count + 1
        newScaling = ConstantScalingFactorData(instance.idParameter,keyValue)
        listForConstantScaling.append(newScaling)
            

    listConstant = db.session.query(ConstantTable).filter(ConstantTable.idForceField == idForceField).all()
    listParameter = [x.idParameter for x in listConstant]
    listParameter = list(set(listParameter))
    for idParameter in listParameter:
        count = 0
        keyValue = {}
        rowConstant = [instance for instance in listConstant if instance.idParameter == idParameter]
        for instance in rowConstant:
            keyValue[str(count)+'_'+instance.key] = instance.value
            count = count + 1
        newConstant = ConstantScalingFactorData(instance.idParameter,keyValue)
        listForConstantScaling.append(newConstant)
            
    listParamClass = db.session.query(ParamsClass).filter(ParamsClass.idForceField == idForceField)
    for instance in listParamClass:
        count = 0
        keyValue = {}
        ClassAtomParamsClassInstance = db.session.query(ClassAtom_ParamsClass).filter(ClassAtom_ParamsClass.idParam == instance.idParam).first()
        description = ClassAtomParamsClassInstance.description if ClassAtomParamsClassInstance.description else ClassAtomParamsClassInstance.idClassAtom
        listSon = db.session.query(ValueClass).filter(ValueClass.idParam == instance.idParam).all()
        for x in listSon:
            keyValue[str(count)+'_'+x.key] = x.value
            count = count + 1
        newInstance = parameterClassOrType("class",instance.idParameter,'',description,keyValue)
        listForParameter.append(newInstance)

    listParamType = db.session.query(ParamsType).filter(ParamsType.idForceField == idForceField)
    for instance in listParamType:
        count = 0
        keyValue = {}
        AtomsTypeParamsTypeInstance = db.session.query(AtomsType_ParamsType).filter(AtomsType_ParamsType.idParam == instance.idParam).first()
        description = AtomsTypeParamsTypeInstance.description if AtomsTypeParamsTypeInstance.description else AtomsTypeParamsTypeInstance.idAtomType
        listSon = db.session.query(ValueType).filter(ValueType.idParam == instance.idParam).all()
        for x in listSon:
            keyValue[str(count)+'_'+x.key] = x.value
            count = count + 1
        newInstance = parameterClassOrType("type",instance.idParameter,'',description,keyValue)
        listForParameter.append(newInstance)


    instanceForUndoRedo = UndoRedoObject("deleteForceField",nameFF,atomClassDefinitionList=listForAtom,
                                         constantScalingFactorDataList=listForConstantScaling,
                                         parameterClassOrTypeList=listForParameter,
                                         listParameterNameFF=listNameParameter,
                                         listUserOfForceField=listUserOfForceField,ownerFF=ownerUsername)
    
    #si l'index ne se trouve pas aux dernier element de la liste
    if session['countOperation'] != (len(session['listOfOperation']) -1):
        for i in range((len(session['listOfOperation'])-1),session['countOperation'],-1):
            session['listOfOperation'].pop(i)
        session['redo'] = False
    
    session['listOfOperation'].append(instanceForUndoRedo)   
    session['countOperation'] +=1
    
    #button undo/redo
    session['undo'] = True
    session['save'] = True
    
    #THe remove is maked in this line
    forceFieldInstance = db.session.query(ForceField).filter(ForceField.nameForceField == nameFF).one()
    db.session.delete(forceFieldInstance)
    db.session.commit()

    return flashIndex('ForceField deleted.','success',sessionData())

@app.route('/addParameterOk')
def addParameterOk():
    parameterType = request.args.get('parameterType')
    isClass = request.args.get('isClass')
    numberOfAtoms = request.args.get('numberOfAtoms')
    isNewParameter = request.args.get('isNewParameter')
    forcefieldName = request.args.get('forcefieldName')
    parameterName = request.args.get('parameterName')
    constantName = request.args.get('constantName')
    sfName = request.args.get('sfName')
    ClassOrType = request.args.get('ClassOrType')
    operation = ""
    msg = ""
    isNew = False
    name_parameter =""
    columnPropertyName = ""
    signForSFConstant = ""

    if(isClass == "true"):
        typeOrClass = "class"
    else:
        typeOrClass = "type"

    forceFieldId = db.session.query(ForceField.idForceField).filter(ForceField.nameForceField==forcefieldName).scalar() 

    if(parameterType == "Parameter"):
        msg = "Parameter: " + parameterName
        if(isNewParameter == "true"):
            if(isParameterExist(None,parameterName) == True):
                return flashIndex('Existing parameter please choose another name','error')
            isNew = True
        name_parameter = parameterName
        operation = 'addParameterToFF'
        listOfProperty = [ClassOrType]
        
        #new dict of parameters
        parametersDict = {}
        for key , value in request.args.items():
            if("parameters" in key):
                parametersDict[key] = value
        
        #sort new dict of parameters
        parametersDict = OrderedDict(sorted(parametersDict.items()))
        for key , value in parametersDict.items():
            listOfProperty.append(value)
        
        
        for instance in listOfProperty:
            columnPropertyName += instance + ',' 
        columnPropertyName = columnPropertyName[:-1]
        
        if(isNewParameter == "true"):
            newParameter = ParameterTable(parameterName,"Parameter",numberOfAtoms,typeOrClass)
            newParameter.columnsName=columnPropertyName
            db.session.add(newParameter)
            db.session.flush()
            parameterId = newParameter.idParameter
        else:
            parameterId = db.session.query(ParameterTable.idParameter).filter(ParameterTable.nameParameter==parameterName).scalar()

    if(parameterType == "SF"):
        name_parameter = sfName
        msg = "Scaling Factor: " + sfName
        operation = 'addSFToFF'
        if(isParameterExist(None,sfName)):
            newParameter = db.session.query(ParameterTable).filter(ParameterTable.nameParameter == sfName).first()
        else:
            isNew = True
            newParameter = ParameterTable(sfName,parameterType)
            db.session.add(newParameter)
            db.session.flush()
        parameterId = newParameter.idParameter

    if(parameterType == "Constant"):
        name_parameter = constantName
        msg = "Constant: " + constantName
        operation = 'addConstantToFF'
        if(isParameterExist(None,constantName)):
            newParameter = db.session.query(ParameterTable).filter(ParameterTable.nameParameter == constantName).first()
        else:
            isNew = True
            newParameter = ParameterTable(constantName,parameterType)
            db.session.add(newParameter)
            db.session.flush()
        parameterId = newParameter.idParameter

    if(parameterType == "SF" or parameterType == "Parameter" or parameterType == "Constant"):
        ff_instance = db.session.query(ForceField).get(forceFieldId)
        param_Instance = db.session.query(ParameterTable).get(parameterId)
        
        parametersOfForceFieldInstance = ParametersOfForceField()
        parametersOfForceFieldInstance.forcefieldInstance =  ff_instance
        parametersOfForceFieldInstance.parametersInstance = param_Instance
    
    if(parameterType == "Parameter"):
        parametersOfForceFieldInstance.columnsName = columnPropertyName
    db.session.flush()


    if(parameterType == "SF&Constant"):
        name_parameter = sfName + "," + constantName
        msg = "Constant: " + constantName + " and Scaling Factor: " + sfName
        operation = 'addConstantToFF'
        if(not isParameterExist(None,constantName)):
            signForSFConstant += "true"
            newParameter1 = ParameterTable(constantName,"Constant")
            db.session.add(newParameter1)
            db.session.flush()
        else:
            signForSFConstant += "false"
            newParameter1 = db.session.query(ParameterTable).filter(ParameterTable.nameParameter == constantName).first()
        if(not isParameterExist(None,sfName)):
            signForSFConstant += ",true"
            newParameter2 = ParameterTable(sfName,"SF")
            db.session.add(newParameter2)
            db.session.flush()
        else:
            signForSFConstant += ",false"
            newParameter2 = db.session.query(ParameterTable).filter(ParameterTable.nameParameter == sfName).first()

        ff_instance = db.session.query(ForceField).get(forceFieldId)
        param_Instance1 = db.session.query(ParameterTable).get(newParameter1.idParameter)
        param_Instance2 = db.session.query(ParameterTable).get(newParameter2.idParameter)

        parametersOfForceFieldInstance1 = ParametersOfForceField()
        parametersOfForceFieldInstance1.forcefieldInstance =  ff_instance
        parametersOfForceFieldInstance1.parametersInstance = param_Instance1
        parametersOfForceFieldInstance2 = ParametersOfForceField()
        parametersOfForceFieldInstance2.forcefieldInstance =  ff_instance
        parametersOfForceFieldInstance2.parametersInstance = param_Instance2


    instanceForUndoRedo = UndoRedoObject(operation,forcefieldName,nameParameter=name_parameter,typeParam=parameterType,nameColumns=columnPropertyName,classOrType=typeOrClass,exist=False if isNew else True,oldValue=signForSFConstant)
    if session['countOperation'] != (len(session['listOfOperation']) -1):
        for i in range((len(session['listOfOperation'])-1),session['countOperation'],-1):
            session['listOfOperation'].pop(i)
        session['redo'] = False
    session['listOfOperation'].append(instanceForUndoRedo)
    session['countOperation'] +=1
    session['undo'] = True
    session['save'] = True
    db.session.commit()

    return flashIndex(msg +' added','success',sessionData(operation=operation,nameForceField=forcefieldName,nameParameter=parameterName))


@app.route('/removeParameterOk/<string:forcefieldName>/<string:parameterName>')
def removeParameterOk(forcefieldName,parameterName):
    idForceFieldDelete = db.session.query(ForceField.idForceField).filter(ForceField.nameForceField==forcefieldName).scalar()
    parameterToDelete = db.session.query(ParameterTable).filter(ParameterTable.nameParameter == parameterName).scalar()
    listForAtom = []
    listForConstantScaling = []
    listForParameter = []
    listAlreadyExist = []
    listNameParameter = []
    keyValue = {}
    description = ""
    idParameter = -1
    listParameter = []
    
    if parameterName == "Atom Definition":
        #retrieve all instance belong to this ff from AtomType Table
        listClassAtom = db.session.query(ClassAtom).filter(ClassAtom.idForceField == idForceFieldDelete).all()
        for instanceClass in listClassAtom:
            listAtomsType = db.session.query(AtomsType).filter(AtomsType.idClassAtom == instanceClass.idClassAtom,AtomsType.idForceField == idForceFieldDelete).all()
            for instanceAtom in listAtomsType:
                newAtom = AtomClassDefinition(instanceAtom.idClassAtom,instanceClass.symbol,instanceClass.atomicNumber,
                                                  instanceClass.atomicWeight,instanceClass.valence,instanceAtom.idAtomType,
                                                  instanceAtom.description)
                listForAtom.append(newAtom)
        

        for instance in ParameterOfForceField(idForceFieldDelete):
            if instance != "Atom Definition":
                listNameParameter.append(instance)

        listSF = db.session.query(ScalingFactorTable).filter(ScalingFactorTable.idForceField == idForceFieldDelete).all()   
        listParameter = [x.idParameter for x in listSF]
        listParameter = list(set(listParameter))
            
        for idParameter in listParameter:
            count = 0
            keyValue = {}
            rowSF = [instance for instance in listSF if instance.idParameter == idParameter]
            for instance in rowSF:
                keyValue[str(count)+'_'+instance.key] = instance.value
                count = count + 1
            newScaling = ConstantScalingFactorData(instance.idParameter,keyValue)
            listForConstantScaling.append(newScaling)
                
        listConstant = db.session.query(ConstantTable).filter(ConstantTable.idForceField == idForceFieldDelete).all()
        listParameter = [x.idParameter for x in listConstant]
        listParameter = list(set(listParameter))
        for idParameter in listParameter:
            count = 0
            keyValue = {}
            rowConstant = [instance for instance in listConstant if instance.idParameter == idParameter]
            for instance in rowConstant:
                keyValue[str(count)+'_'+instance.key] = instance.value
                count = count + 1
            newConstant = ConstantScalingFactorData(instance.idParameter,keyValue)
            listForConstantScaling.append(newConstant)
                
        listParamClass = db.session.query(ParamsClass).filter(ParamsClass.idForceField == idForceFieldDelete).all()
        for instance in listParamClass:
            count = 0
            keyValue = {}
            ClassAtomParamsClassInstance = db.session.query(ClassAtom_ParamsClass).filter(ClassAtom_ParamsClass.idParam == instance.idParam).first()
            description = ClassAtomParamsClassInstance.description if ClassAtomParamsClassInstance.description else ClassAtomParamsClassInstance.idClassAtom
            listSon = db.session.query(ValueClass).filter(ValueClass.idParam == instance.idParam).all()
            for x in listSon:
                keyValue[str(count)+'_'+x.key] = x.value
                count = count + 1
            newInstance = parameterClassOrType("class",instance.idParameter,'',description,keyValue)
            listForParameter.append(newInstance)
        
        listParamType = db.session.query(ParamsType).filter(ParamsType.idForceField == idForceFieldDelete).all()
        for instance in listParamType:
            count = 0 
            keyValue = {}
            AtomsTypeParamsTypeInstance = db.session.query(AtomsType_ParamsType).filter(AtomsType_ParamsType.idParam == instance.idParam).first()
            description = AtomsTypeParamsTypeInstance.description if AtomsTypeParamsTypeInstance.description else AtomsTypeParamsTypeInstance.idAtomType
            listSon = db.session.query(ValueType).filter(ValueType.idParam == instance.idParam).all()
            for x in listSon:
                keyValue[str(count)+'_'+x.key] = x.value
                count = count + 1
            newInstance = parameterClassOrType("type",instance.idParameter,'',description,keyValue)
            listForParameter.append(newInstance)
                
        instanceForUndoRedo = UndoRedoObject("deleteParameterToFF",forcefieldName,nameParameter=parameterName,
                            atomClassDefinitionList=listForAtom,constantScalingFactorDataList=listForConstantScaling,
                            parameterClassOrTypeList=listForParameter,listParameterNameFF=listNameParameter)

        #get athors of this ff
        usernameList = allAuthorsForcefied(idForceFieldDelete)
        #get owner
        ownerUsername = getOwnerOfFF(idForceFieldDelete)
        #THe remove is maked in this line
        forceFieldInstance = db.session.query(ForceField).filter(ForceField.nameForceField == forcefieldName).one()
        db.session.delete(forceFieldInstance)
        db.session.commit()
        instanceForceField = ForceField(forcefieldName)
        db.session.add(instanceForceField)
        db.session.commit()
        #assign authors to the ff
        recoverUserOfFF(ownerUsername,usernameList,instanceForceField.idForceField)
        db.session.commit()
        
    else:
        if parameterToDelete.parameterType == 'SF':
            # I copy the scaling factor value for the undo operation. and delete them
            listSF = db.session.query(ScalingFactorTable).filter(ScalingFactorTable.idForceField == idForceFieldDelete,ScalingFactorTable.idParameter == parameterToDelete.idParameter)
            count = 0
            for instance in listSF:
                keyValue[str(count)+'_'+instance.key] = instance.value
                idParameter = instance.idParameter
                db.session.delete(instance)
                count = count + 1
            newScaling = ConstantScalingFactorData(idParameter,keyValue)
            listForConstantScaling.append(newScaling)
            instanceForUndoRedo = UndoRedoObject("deleteParameterToFF",forcefieldName,nameParameter=parameterName,
                                                 constantScalingFactorDataList=listForConstantScaling)
            

            ParametersOfForceFieldInstance =  db.session.query(ParametersOfForceField).filter(ParametersOfForceField.idForceField == idForceFieldDelete,ParametersOfForceField.idParameter == parameterToDelete.idParameter).one()
            db.session.delete(ParametersOfForceFieldInstance)
            db.session.commit()

        elif parameterToDelete.parameterType == 'Constant':
            # I copy the constants value for the undo operation. and delete them
            listConstant = db.session.query(ConstantTable).filter(ConstantTable.idForceField == idForceFieldDelete,ConstantTable.idParameter == parameterToDelete.idParameter)
            count = 0
            for instance in listConstant:
                keyValue[str(count)+'_'+instance.key] = instance.value;
                idParameter = instance.idParameter
                db.session.delete(instance)
                count = count + 1
            newConstant = ConstantScalingFactorData(idParameter,keyValue)
            listForConstantScaling.append(newConstant)
            instanceForUndoRedo = UndoRedoObject("deleteParameterToFF",forcefieldName,nameParameter=parameterName,
                                                 constantScalingFactorDataList=listForConstantScaling)

            #delete parameter of ff instance of this parameter
            ParametersOfForceFieldInstance =  db.session.query(ParametersOfForceField).filter(ParametersOfForceField.idForceField == idForceFieldDelete,ParametersOfForceField.idParameter == parameterToDelete.idParameter).one()
            db.session.delete(ParametersOfForceFieldInstance)
            db.session.commit()

        else: 
            if parameterToDelete.classOrType == 'class':
                # I copy parameter based to class value for the undo operation.
                listParamClass = db.session.query(ParamsClass).filter(ParamsClass.idForceField == idForceFieldDelete,ParamsClass.idParameter == parameterToDelete.idParameter).all()
                for instance in listParamClass:
                    keyValue = {}
                    ClassAtomParamsClassInstance = db.session.query(ClassAtom_ParamsClass).filter(ClassAtom_ParamsClass.idParam == instance.idParam).first()
                    description = ClassAtomParamsClassInstance.description if ClassAtomParamsClassInstance.description else ClassAtomParamsClassInstance.idClassAtom
                    listSon = db.session.query(ValueClass).filter(ValueClass.idParam == instance.idParam).all()
                    count = 0
                    for x in listSon:
                        keyValue[str(count)+'_'+x.key] = x.value
                        count = count + 1
                    newInstance = parameterClassOrType("class",instance.idParameter,'',description,keyValue)
                    listForParameter.append(newInstance)
                    #here i am deleted the parameter based to class that was clicked 
                    db.session.delete(instance)
                instanceForUndoRedo = UndoRedoObject("deleteParameterToFF",forcefieldName,nameParameter=parameterName,
                                                 parameterClassOrTypeList=listForParameter)
                
            else:
                # I copy parameter based to type value for the undo operation.
                listParamType = db.session.query(ParamsType).filter(ParamsType.idForceField == idForceFieldDelete,ParamsType.idParameter == parameterToDelete.idParameter).all()
                for instance in listParamType:
                    keyValue = {}
                    AtomsTypeParamsTypeInstance = db.session.query(AtomsType_ParamsType).filter(AtomsType_ParamsType.idParam == instance.idParam).first()
                    description = AtomsTypeParamsTypeInstance.description if AtomsTypeParamsTypeInstance.description else AtomsTypeParamsTypeInstance.idAtomType
                    listSon = db.session.query(ValueType).filter(ValueType.idParam == instance.idParam).all()
                    count = 0
                    for x in listSon:
                        keyValue[str(count)+'_'+x.key] = x.value
                        count = count + 1
                    newInstance = parameterClassOrType("type",instance.idParameter,'',description,keyValue)
                    listForParameter.append(newInstance)
                    #here i am deleted the parameter based to type that was clicked 
                    db.session.delete(instance)
                        
                instanceForUndoRedo = UndoRedoObject("deleteParameterToFF",forcefieldName,nameParameter=parameterName,
                                                 parameterClassOrTypeList=listForParameter)
  
            
            #delete parameter of ff instance of this parameter
            ParametersOfForceFieldInstance =  db.session.query(ParametersOfForceField).filter(ParametersOfForceField.idForceField == idForceFieldDelete,ParametersOfForceField.idParameter == parameterToDelete.idParameter).one()
            db.session.delete(ParametersOfForceFieldInstance)
            db.session.commit()
    
    if session['countOperation'] != (len(session['listOfOperation']) -1):
        for i in range((len(session['listOfOperation'])-1),session['countOperation'],-1):
            session['listOfOperation'].pop(i)
        session['redo'] = False
    session['listOfOperation'].append(instanceForUndoRedo)
    session['countOperation'] +=1
    session['undo'] = True
    session['save'] = True
    db.session.flush()
    db.session.commit()

    return flashIndex(parameterName+' deleted.','success',sessionData(operation='deleteParameterToFF'))


@app.route('/addRowOk/<string:ffName>/<string:paramName>')
def addRowOk(ffName,paramName):
    valueDict = {}
    for key,value in request.args.items():
        valueDict[key] = value

    ListValue = []
    listColumns = []
    listForKeepUndo = []
   
    #sorted the dict and insert value on listValue
    valueDict = OrderedDict(sorted(valueDict.items()))
    for key,value in valueDict.items():
        ListValue.append(value)
    
    exist = False
    
    idForceFieldAdd = db.session.query(ForceField.idForceField).filter(ForceField.nameForceField == ffName).scalar()
    parameterAddValue = db.session.query(ParameterTable).filter(ParameterTable.nameParameter == paramName).scalar() 
        
    if paramName == "Atom Definition":
        #i don't need to check if all value are filled
        #check if type already existing 
        atomTypeInstance = db.session.query(AtomsType).filter(AtomsType.idAtomType == int(ListValue[0]),AtomsType.idForceField == idForceFieldAdd).first()
        if(atomTypeInstance):
            return flashIndex('Type entered already exist,please enter new type','error')
        #if type dosen't exist
        if(not atomTypeInstance):
            #check if the class atom exist to know if we need to create new instance of classAtom
            classAtomInstance = db.session.query(ClassAtom).filter(ClassAtom.idClassAtom == int(ListValue[1]),ClassAtom.idForceField == idForceFieldAdd).first()
            #create new instance of class Atom
            if(not classAtomInstance):
                newClass = ClassAtom(ListValue[1], idForceFieldAdd, ListValue[2], ListValue[4],ListValue[5], ListValue[6])
                db.session.add(newClass)
                db.session.flush()
                db.session.commit()
                exist = False
            #if classAtom exist we check if description of the atom
            #is not used for another atomType, valueDict['3'] it's the value of 
            #description
            else:
                description = valueDict['3']
                AtomTypeList = classAtomInstance.atoms_typeChildren
                for instance in AtomTypeList:
                    if instance.description == description:
                        return flashIndex('The description already exist,please choose another one.','error')
                exist = True
                
            newAtom = AtomsType(ListValue[0], ListValue[1], idForceFieldAdd, ListValue[3])
            db.session.add(newAtom)
            db.session.commit()
            #THe next line allow to keep the new row value of Atoms added, for the undo operation
            newAtomForUndo = AtomClassDefinition(idClassAtom=ListValue[1],idAtomType=newAtom.idAtomType,
                                                 existClass=exist,symbol=ListValue[2],description=ListValue[3],
                                                 atomicNumber=ListValue[4],atomicWeight=ListValue[5],
                                                 valence=ListValue[6])
            listForKeepUndo.append(newAtomForUndo)
            instanceForUndoRedo = UndoRedoObject("addValueParameter",ffName,nameParameter="Atom Definition",
                                                 atomClassDefinitionList=listForKeepUndo)                    
    else:
        if parameterAddValue.parameterType == 'SF':
            #check if the key already exist 
            sfInstance = db.session.query(ScalingFactorTable).filter(ScalingFactorTable.idForceField == idForceFieldAdd,ScalingFactorTable.idParameter == parameterAddValue.idParameter,ScalingFactorTable.key == ListValue[0]).first()
            #if key exist there is an error
            if(sfInstance):
                return flashIndex('Entered Key already exist,please enter new key','error')
            #if key doesn't exist
            else:
                newScalingFactor = ScalingFactorTable(idForceFieldAdd,parameterAddValue.idParameter,ListValue[0],ListValue[1])
                db.session.add(newScalingFactor)
                #THe next line allow to keep the new row value of Atoms added, for the undo operation
                newScalingForUndo = ConstantScalingFactorData(idParameter=parameterAddValue.idParameter,key=ListValue[0],value=ListValue[1])
                listForKeepUndo.append(newScalingForUndo)
                instanceForUndoRedo = UndoRedoObject("addValueParameter",ffName,nameParameter=paramName,
                                                        constantScalingFactorDataList=listForKeepUndo) 
            
                            
        elif parameterAddValue.parameterType == 'Constant':
            #check if the key already exist
            constantInstance = db.session.query(ConstantTable).filter(ConstantTable.idForceField == idForceFieldAdd,ConstantTable.idParameter == parameterAddValue.idParameter,ConstantTable.key == ListValue[0]).first()
            #if key exist
            if(constantInstance):
                return flashIndex("The entering key already exist in this constant",'error')
            else:
                newConstant = ConstantTable(idForceFieldAdd,parameterAddValue.idParameter,ListValue[0],ListValue[1])
                db.session.add(newConstant)
                #THe next line allow to keep the new row value of Atoms added, for the undo operation
                newScalingForUndo = ConstantScalingFactorData(idParameter=parameterAddValue.idParameter, 
                                                              key=ListValue[0],value=ListValue[1])
                listForKeepUndo.append(newScalingForUndo)
                instanceForUndoRedo = UndoRedoObject("addValueParameter",ffName,nameParameter=paramName,
                                                         constantScalingFactorDataList=listForKeepUndo) 
        
        #the parameterName corespond to normal parameter 
        else:
            idParamForUndo = -1
            keyValues = {}
            # I separate the value description class Atom or type to check if each atom existing
            listValueAtom = ListValue[0].split('-')
            number = len(listValueAtom)
            #remove duplicate value
            listValueAtom = list(set(listValueAtom))
            
            if session['keyList'][0] == 'Type':
                # I check if each type atom is existing in this forcefield
                for atomNumber in listValueAtom:
                    typeAtomAlreadyExist = db.session.query(AtomsType).filter(AtomsType.idForceField == idForceFieldAdd,
                                                   AtomsType.idAtomType == int(atomNumber)).all()
                    if not typeAtomAlreadyExist:
                        return flashIndex("The entering type doesn't exist in this force field",'error')
                        
                #get all idParamType of this forcefield wich are linked to this AtomType
                if(number == 1):
                    typeAtomParam = db.session.query(AtomsType_ParamsType).filter(AtomsType_ParamsType.idForceField == idForceFieldAdd,
                                               AtomsType_ParamsType.idAtomType == int(ListValue[0])).all()
                else:
                    typeAtomParam = db.session.query(AtomsType_ParamsType).filter(AtomsType_ParamsType.idForceField == idForceFieldAdd,
                                            AtomsType_ParamsType.description == ListValue[0]).all()
                

                for instance in typeAtomParam:
                    paramTypeInstance = db.session.query(ParamsType).filter(ParamsType.idParam == instance.idParam,ParamsType.idParameter == parameterAddValue.idParameter).first()
                    if(paramTypeInstance):
                        return flashIndex('This type already exist in this parameter,please enter another type or update the coresponding line','error')
                
                param = ParamsType(parameterAddValue.idParameter, idForceFieldAdd)
                db.session.add(param)
                db.session.flush()
                idParamForUndo = param.idParam
                
                descrip = ListValue[0]
                if(number == 1):
                    descrip = None
                
                for atomNumber in listValueAtom:
                    param_instance = db.session.query(ParamsType).get(param.idParam)
                    atomType_instance = db.session.query(AtomsType).get((atomNumber,idForceFieldAdd))
                    typeAtomParam = AtomsType_ParamsType(description = descrip)
                    typeAtomParam.atomsTypeInstance = atomType_instance
                    typeAtomParam.paramsTypeInstance = param_instance
                    db.session.flush()


                # Now we add the new row value in the son of parmasClass (like ONeINstance/TwoINstance etc..)
                for index in range(1,len(ListValue)):
                    sonParam = ValueType(session['keyList'][index],param.idParam,ListValue[index])
                    keyValues[session['keyList'][index]] = ListValue[index];
                    db.session.add(sonParam)
                #THe next line allow to keep the new row value of parameter added, for the undo operation
                newParamForUndo = parameterClassOrType(typeOrClass="type",idParameter=parameterAddValue.idParameter,
                                                        descriptionForClass=ListValue[0],
                                                        idParam=idParamForUndo,keyValue=keyValues)
                listForKeepUndo.append(newParamForUndo)
                
                instanceForUndoRedo = UndoRedoObject("addValueParameter",ffName,nameParameter=paramName,
                                                             parameterClassOrTypeList=listForKeepUndo)
            
            # If the parameter using class for his calculating
            else:
                # I separate the value description class Atom. to check if each atom existing
                listValueAtom = ListValue[0].split('-')
                number = len(listValueAtom)
                listValueAtom = list(set(listValueAtom))
                exist = False
                
                # I check if each class atom is existing in this forcefield
                for numberAtoms in listValueAtom:
                    classAtomAlreadyExist = db.session.query(ClassAtom).filter(ClassAtom.idForceField == idForceFieldAdd,
                                                   ClassAtom.idClassAtom == int(numberAtoms)).all()
                    if not classAtomAlreadyExist:
                        return flashIndex("The entering class doesn't exist in this force field",'error')
                      
                

                # If all each entered class atom is existing in this force field so we can continue 
                #get all idParam of this ff wich linked to this idClassAtom
                if(number == 1):
                    classAtomParam = db.session.query(ClassAtom_ParamsClass).filter(ClassAtom_ParamsClass.idForceField == idForceFieldAdd,
                                               ClassAtom_ParamsClass.idClassAtom == int(ListValue[0])).all()
                else:
                    classAtomParam = db.session.query(ClassAtom_ParamsClass).filter(ClassAtom_ParamsClass.idForceField == idForceFieldAdd,
                                               ClassAtom_ParamsClass.description == ListValue[0]).all()
            
                for instance in classAtomParam:
                    paramClassInstance = db.session.query(ParamsClass).filter(ParamsClass.idParam == instance.idParam,ParamsClass.idParameter == parameterAddValue.idParameter).all()
                    if(paramClassInstance):
                        return flashIndex("This class is already used in this parameter,please choose another class or update the coresponding class",'error')  
                
                descrip = ListValue[0]
                if number == 1:
                    descrip = None

                    
                param = ParamsClass(parameterAddValue.idParameter, idForceFieldAdd)
                db.session.add(param)
                db.session.flush()
                idParamForUndo = param.idParam
                for numberAtom in listValueAtom:
                    classAtom_instance = db.session.query(ClassAtom).get((numberAtom,idForceFieldAdd))
                    param_instance = db.session.query(ParamsClass).get(param.idParam)
                    classAtomParam = ClassAtom_ParamsClass(description = descrip)
                    classAtomParam.classAtomsInstance = classAtom_instance
                    classAtomParam.paramsClassInstance = param_instance
                    db.session.flush()
                           
                for instance in range(1,len(ListValue)):
                    sonParam = ValueClass(session['keyList'][instance],param.idParam,ListValue[instance])
                    keyValues[session['keyList'][instance]] = ListValue[instance]
                    db.session.add(sonParam)
                
                # The next line is for the undo operation
                newParamForUndo = parameterClassOrType(typeOrClass="class",idParameter=parameterAddValue.idParameter,
                                                       descriptionForClass=ListValue[0],
                                                       idParam=idParamForUndo,keyValue=keyValues)
                listForKeepUndo.append(newParamForUndo)
                
                instanceForUndoRedo = UndoRedoObject("addValueParameter",ffName,nameParameter=paramName,
                                                             parameterClassOrTypeList=listForKeepUndo)           

    db.session.flush()
    db.session.commit()

    # Add this new operation for keeping to undo/redo
    if session['countOperation'] != (len(session['listOfOperation']) -1):
        for i in range((len(session['listOfOperation'])-1),session['countOperation'],-1):
            session['listOfOperation'].pop(i)
        session['redo'] = False
    session['listOfOperation'].append(instanceForUndoRedo)
    session['countOperation'] +=1
    session['undo'] = True
    session['save'] = True

    return flashIndex('Row added sucessfuly','success',sessionData(nameForceField=ffName,nameParameter=paramName))

@app.route('/addAtomTypeOk')
def addAtomTypeOk():
    dictValues = {}
    for key,value in request.args.items():
        dictValues[key] = value

    #get idForceField
    idForceField = db.session.query(ForceField.idForceField).filter(ForceField.nameForceField == dictValues['ForceField']).scalar()
   
    #check if Class Atom exist
    atomClass = db.session.query(ClassAtom).get((int(dictValues['idClassAtom']),idForceField))
    if(not atomClass):
        return flashIndex("The class atom number "+dictValues['idClassAtom'] + " dosen't exist,Please create it before.",'error')

    #check that the description for the idclassAtom dosen't already exist
    descriptionList = db.session.query(AtomsType.description).filter(AtomsType.idClassAtom == int(dictValues['idClassAtom']),AtomsType.idForceField == idForceField).all()
    descriptionList = [x[0] for x in descriptionList]
    isIn = False
    for x in descriptionList:
        if x == dictValues['description']:
            isIn = True
    if(isIn):
        #it's means that there is duplicate data
        return flashIndex("This description already exist for the class atom number" + dictValues['idClassAtom'],'error')
    
    #create new instance of AtomType
    newAtomType = AtomsType(dictValues['idAtomType'],dictValues['idClassAtom'],idForceField,dictValues['description'])
    #add new instance in data base
    db.session.add(newAtomType)
    db.session.commit()

    #create atomClassDefinition object 
    AtomClassDefinitionInstance = AtomClassDefinition(idClassAtom=newAtomType.idClassAtom,idAtomType=newAtomType.idAtomType,description=newAtomType.description)

    #for undo/redo
    instanceForUndoRedo = UndoRedoObject("addAtomType",dictValues['ForceField'],
                                         nameParameter="Atom Definition",atomClassDefinitionList=[AtomClassDefinitionInstance])
    

    if session['countOperation'] != (len(session['listOfOperation']) -1):
        for i in range((len(session['listOfOperation'])-1),session['countOperation'],-1):
            session['listOfOperation'].pop(i)
        session['redo'] = False
    session['listOfOperation'].append(instanceForUndoRedo)
    session['countOperation'] += 1
    session['undo'] = True
    session['save'] = True
    return flashIndex("Atom Type number "+ str(newAtomType.idAtomType)+" successfuly added",'success',sessionData(nameParameter="Atom Definition",nameForceField=dictValues['ForceField']))


def editAtomDefinition(ffName,oldRowData,newRowData,deleteOldClassAtom):
    isIdUpdated = False
    isIdClassAtomUpdated = False
    atomClassDefinitionList = []
    parameterClassOrTypeList = []
    resultDict = {}

    #get idForceField
    idForceField = db.session.query(ForceField.idForceField).filter(ForceField.nameForceField == ffName).scalar()
  
    #get the  old atom type 
    idOldAtomType = int(oldRowData['idAtomType'])
    oldAtomType = db.session.query(AtomsType).get((idOldAtomType,idForceField))

    #get the old instance of class atom
    old_classAtonInstance = db.session.query(ClassAtom).get((int(oldRowData['idClassAtom']),idForceField))
    

    #if the idAtomType was updated
    if(idOldAtomType != int(newRowData['idAtomType'])):
        isIdUpdated = True
        isExist = db.session.query(AtomsType).get((int(newRowData['idAtomType']),idForceField))
        if(isExist):
            return flashIndex("The atom type number " + newRowData['idAtomType'] +" already existing please choose another number",'error')


    #if symbol was updated
    if(oldRowData['symbol'] != newRowData['symbol']):
        #check if it is already exist
        isExist = db.session().query(ClassAtom).filter(ClassAtom.symbol == newRowData['symbol'],ClassAtom.idForceField == idForceField).scalar()
        if(isExist and isExist.idClassAtom != int(newRowData['idClassAtom'])):
            return flashIndex("symbol "+newRowData['symbol'] +" already existing by classAtom number "+ str(isExist.idClassAtom),'error')



    #i save the old atom type for undo redo operation
    atomClassDefinitionList.append(AtomClassDefinition(idClassAtom=oldAtomType.idClassAtom,
                                                       idAtomType=oldAtomType.idAtomType,
                                                       description=oldAtomType.description,
                                                       actualValue=newRowData['idAtomType'],
                                                       headerUpdate="idAtomType",
                                                       oldValue=oldRowData['idAtomType']))
    
    #i save the new atom type for redo operation
    atomClassDefinitionList.append(AtomClassDefinition(idClassAtom=newRowData['idClassAtom'],
                                                       idAtomType=newRowData['idAtomType'],
                                                       description=newRowData['description'],
                                                       actualValue=oldRowData['idAtomType'],
                                                       headerUpdate="idAtomType",
                                                       oldValue=newRowData['idAtomType']))
    

    #if the update is not on the Id
    if(not isIdUpdated):
        oldAtomType.idClassAtom = newRowData['idClassAtom']
        oldAtomType.description = newRowData['description']
        db.session.add(oldAtomType)
        db.session.commit()
    
    #if idAtomType updated i have to change all instance with 
    #the old number by the new number
    if(isIdUpdated):
        #create the new instance 
        newAtomTypeInstance = AtomsType(newRowData['idAtomType'],newRowData['idClassAtom'],idForceField,newRowData['description'])
        db.session.add(newAtomTypeInstance)
        db.session.commit()
        #i retrieve in the AtomType_ParamsType Table all instance
        #with old atom type id number and replace  with actual atom type id number
        db.session.query(AtomsType_ParamsType).filter(AtomsType_ParamsType.idAtomType == int(oldRowData['idAtomType']),\
            AtomsType_ParamsType.idForceField == idForceField).update({'idAtomType':newRowData['idAtomType']})
        db.session.commit()
        #i need to update all the description field that contains the old number
        listAtomsType_ParamsType = db.session.query(AtomsType_ParamsType).all()
        for instance in listAtomsType_ParamsType:
            if(instance.description):
                listDescription = instance.description.split('-')
                if(str(oldAtomType.idAtomType) in listDescription):
                    listDescription = [ newRowData['idAtomType'] if x == oldRowData['idAtomType'] else x for x in listDescription ]
                instance.description = '-'.join(listDescription)
                db.session.add(instance)
        db.session.commit()

        #delete the old instance
        db.session.delete(oldAtomType)
        db.session.commit()

    #if the idclassAtom was updated i already checked on client side
    #if it's existing or not, and  i also checked on client side if i need to
    #delete it or not [in case is no more used in this ff] i store this info in
    #in deleteOldClassAtom' 
    if(oldRowData['idClassAtom'] != newRowData['idClassAtom']):
        isIdClassAtomUpdated = True
        #if i need to delete this atom class
        if(deleteOldClassAtom):
            resultDict = deleteAllparameterOfClassAtom(idForceField,old_classAtonInstance)
            atomClassDefinitionList[:0] = resultDict['atomClassDefinitionList']
            parameterClassOrTypeList = resultDict['parameterClassOrTypeList']
    

    #now i need to take the idClassAtom from the new AtomType
    #so i request the database to get the last updated instance of
    #class atom.(it's the more actual at this step of the program)
    atomTypeInstance = db.session.query(AtomsType).get((int(newRowData['idAtomType']),idForceField))
    
    if(oldRowData['idClassAtom'] == newRowData['idClassAtom'] or (oldRowData['idClassAtom'] != newRowData['idClassAtom'] and not deleteOldClassAtom)):
        #i have to save the class atom datas before change it
        atomClassDefinitionList.insert(0,
                                    AtomClassDefinition(idClassAtom=atomTypeInstance.idClassAtom,
                                    symbol=oldRowData['symbol'],
                                    atomicNumber=oldRowData['atomicNumber'],
                                    atomicWeight=oldRowData['atomicWeight'],
                                    valence=oldRowData['valence'],
                                    headerUpdate='idClassAtom',
                                    existClass=True))


    
    classAtomInstance = db.session.query(ClassAtom).get((atomTypeInstance.idClassAtom,idForceField))
    classAtomInstance.symbol = newRowData['symbol']
    classAtomInstance.atomicNumber = newRowData['atomicNumber']
    classAtomInstance.atomicWeight = newRowData['atomicWeight']
    classAtomInstance.valence = newRowData['valence']
    db.session.add(classAtomInstance)
    db.session.commit()

    #for undo/redo 
    instanceForUndoRedo = UndoRedoObject("editAtomDefinition",ffName,
                                        nameParameter="Atom Definition",
                                        atomClassDefinitionList=atomClassDefinitionList,
                                        parameterClassOrTypeList=parameterClassOrTypeList)



    if session['countOperation'] != (len(session['listOfOperation']) -1):
        for i in range((len(session['listOfOperation'])-1),session['countOperation'],-1):
            session['listOfOperation'].pop(i)
        session['redo'] = False
    session['listOfOperation'].append(instanceForUndoRedo)
    session['countOperation'] += 1
    session['undo'] = True
    session['save'] = True

    return flashIndex('The atom definition was updated sucessfuly','success',sessionData(nameParameter="Atom Definition",nameForceField=ffName))

 

@app.route('/editAtomType')
def editAtomType():
    isIdUpdated = False
    isIdClassAtomUpdated = False
    dictValues = {}
    resultDict = {}
    atomClassDefinitionList = []
    parameterClassOrTypeList = []
    for key,value in request.args.items():
        dictValues[key] = value

    #get idForceField
    idForceField = db.session.query(ForceField.idForceField).filter(ForceField.nameForceField == dictValues['ForceField']).scalar()
  
    #get the atom type selected by the drop down list in UI
    idAtomTypeSelected = int(dictValues['ddl_AtomType'])
    atomTypeSelected = db.session.query(AtomsType).get((idAtomTypeSelected,idForceField))

    #get the old instance of class atom
    old_classAtonInstance = db.session.query(ClassAtom).get((int(dictValues['old_idClassAtom']),idForceField))
    

    if(atomTypeSelected.idClassAtom != int(dictValues['idClassAtom'])):
        isIdClassAtomUpdated = True

    #if the idAtomType was updated
    if(atomTypeSelected.idAtomType != int(dictValues['idAtomType'])):
        isIdUpdated = True
        isExist = db.session.query(AtomsType).get((int(dictValues['idAtomType']),idForceField))
        if(isExist):
            return flashIndex("The atom type number " + dictValues['idAtomType'] +" already existing please choose another number",'error')


    #i save the old atom type for undo  operation
    atomClassDefinitionList.append(AtomClassDefinition(idClassAtom=atomTypeSelected.idClassAtom,
                                                       idAtomType=atomTypeSelected.idAtomType,
                                                       description=atomTypeSelected.description,
                                                       actualValue=dictValues['idAtomType'],
                                                       headerUpdate="idAtomType",
                                                       oldValue=dictValues['ddl_AtomType']))
    
    #i save the old atom type for redo  operation
    atomClassDefinitionList.append(AtomClassDefinition(idClassAtom=dictValues['idClassAtom'],
                                                       idAtomType=dictValues['idAtomType'],
                                                       description=dictValues['description'],
                                                       actualValue=dictValues['ddl_AtomType'],
                                                       headerUpdate="idAtomType",
                                                       oldValue=dictValues['idAtomType']))
    

    #if the update is not on the Id
    if(not isIdUpdated):
        atomTypeSelected.idClassAtom = int(dictValues['idClassAtom'])
        atomTypeSelected.description = dictValues['description']
        db.session.add(atomTypeSelected)
        db.session.commit()
    
    #if idAtomType updated i have to change all instance with 
    #the old number by the new number
    if(isIdUpdated):
        #create the new instance 
        newAtomTypeInstance = AtomsType(dictValues['idAtomType'],dictValues['idClassAtom'],idForceField,dictValues['description'])
        db.session.add(newAtomTypeInstance)
        db.session.commit()
        #i retrieve in the AtomType_ParamsType Table all instance
        #with old atom type id number and replace  with actual atom type id number
        db.session.query(AtomsType_ParamsType).filter(AtomsType_ParamsType.idAtomType == idAtomTypeSelected,\
            AtomsType_ParamsType.idForceField == idForceField).update({'idAtomType':dictValues['idAtomType']})
        db.session.commit()
        #i need to update all the description field that contains the old number
        listAtomsType_ParamsType = db.session.query(AtomsType_ParamsType).all()
        for instance in listAtomsType_ParamsType:
            if(instance.description):
                listDescription = instance.description.split('-')
                if(str(atomTypeSelected.idAtomType) in listDescription):
                    listDescription = [ dictValues['idAtomType'] if x == str(atomTypeSelected.idAtomType) else x for x in listDescription ]
                instance.description = '-'.join(listDescription)
                db.session.add(instance)
        db.session.commit()

        #delete the old instance
        db.session.delete(atomTypeSelected)
        db.session.commit()


    #if the idclassAtom was updated i already checked on client side
    #that is existing , and so i checked on client side if i need to
    #delete it , if is no more used in this ff , i store this info in
    #dictValues['deleteOldClassAtom'] 
    if(isIdClassAtomUpdated):
        #if i need to delete this atom class
        if(dictValues['deleteOldClassAtom'] == "True"):
            resultDict = deleteAllparameterOfClassAtom(idForceField,old_classAtonInstance)
            atomClassDefinitionList[:0] = resultDict['atomClassDefinitionList']
            parameterClassOrTypeList = resultDict['parameterClassOrTypeList']
    

    #for undo/redo 
    instanceForUndoRedo = UndoRedoObject("editAtomType",dictValues['ForceField'],
                                        nameParameter="Atom Definition",
                                        atomClassDefinitionList=atomClassDefinitionList,
                                        parameterClassOrTypeList=parameterClassOrTypeList)

    if session['countOperation'] != (len(session['listOfOperation']) -1):
        for i in range((len(session['listOfOperation'])-1),session['countOperation'],-1):
            session['listOfOperation'].pop(i)
        session['redo'] = False
    session['listOfOperation'].append(instanceForUndoRedo)
    session['countOperation'] += 1
    session['undo'] = True
    session['save'] = True

    return flashIndex('The atom type was updated sucessfuly','success',sessionData(nameParameter="Atom Definition",nameForceField=dictValues['ForceField']))
        



@app.route('/editAtomClassOk')
def editAtomClassOk():
    dictValues = {}
    isIdUpdated = False
    atomClassDefinitionList = []
    for key,value in request.args.items():
        dictValues[key] = value

    #get idForceField
    idForceField = db.session.query(ForceField.idForceField).filter(ForceField.nameForceField == dictValues['ForceField']).scalar()
  
    #the class atom number selected by the drop down list in UI
    idClassAtomSelected = int(dictValues['ddl_classAtom'])
    atomClassSelected = db.session.query(ClassAtom).get((idClassAtomSelected,idForceField))
    
    #check if atom class number already exist or not
    if(atomClassSelected.idClassAtom != int(dictValues['idClassAtom'])):
        isIdUpdated = True
        isExist = db.session.query(ClassAtom).get((int(dictValues['idClassAtom']),idForceField))
        if(isExist):
            return flashIndex("The class atom number " + dictValues['idClassAtom'] +" already existing please choose another number",'error')
    
    #check if symbol already exist in case the update was NOT in ID
    if(atomClassSelected.symbol != dictValues['symbol'] and not isIdUpdated):
        isExist = db.session().query(ClassAtom).filter(ClassAtom.symbol == dictValues['symbol'],ClassAtom.idForceField == idForceField).scalar()
        if(isExist):
            return flashIndex("symbol "+dictValues['symbol'] +" already existing by classAtom number "+ str(isExist.idClassAtom),'error')

    #before update i nedd to save all value that i will change
    #for the undo operation in the goal to put them back
    atomClassDefinitionList.append(AtomClassDefinition(idClassAtom=atomClassSelected.idClassAtom,
                                                 headerUpdate='idClassAtom',
                                                 symbol=atomClassSelected.symbol,
                                                 atomicNumber=atomClassSelected.atomicNumber,
                                                 atomicWeight=atomClassSelected.atomicWeight,
                                                 valence=atomClassSelected.valence,
                                                 actualValue=dictValues['idClassAtom'],
                                                 oldValue=str(idClassAtomSelected)))
    
    #for the redo operation in the goal to put them back
    atomClassDefinitionList.append(AtomClassDefinition(idClassAtom=dictValues['idClassAtom'],
                                             headerUpdate='idClassAtom',
                                             symbol=dictValues['symbol'],
                                             atomicNumber=dictValues['atomicNumber'],
                                             atomicWeight=dictValues['atomicWeight'],
                                             valence=dictValues['valence'],
                                             actualValue=str(idClassAtomSelected),
                                             oldValue=dictValues['idClassAtom']))
    
    instanceForUndoRedo = UndoRedoObject("editAtomClass",dictValues['ForceField'],
                                             nameParameter="Atom Definition",atomClassDefinitionList=atomClassDefinitionList)

    if(not isIdUpdated):
        #update the class atom
        db.session.query(ClassAtom).filter(ClassAtom.idClassAtom == idClassAtomSelected,ClassAtom.idForceField == idForceField).update({'symbol':dictValues['symbol']})
        db.session.query(ClassAtom).filter(ClassAtom.idClassAtom == idClassAtomSelected,ClassAtom.idForceField == idForceField).update({'atomicNumber':dictValues['atomicNumber']})
        db.session.query(ClassAtom).filter(ClassAtom.idClassAtom == idClassAtomSelected,ClassAtom.idForceField == idForceField).update({'atomicWeight':dictValues['atomicWeight']})
        db.session.query(ClassAtom).filter(ClassAtom.idClassAtom == idClassAtomSelected,ClassAtom.idForceField == idForceField).update({'valence':dictValues['valence']})
        db.session.commit()


    #if the number of the class atom was updated
    #i need to change all parameter wich linked with this 
    #old class atom number to the new class atom number.
    if(isIdUpdated):
        #create the new instance 
        newClassInstance = ClassAtom(dictValues['idClassAtom'],idForceField,dictValues['symbol'],dictValues['atomicNumber'],dictValues['atomicWeight'],dictValues['valence'])
        db.session.add(newClassInstance)
        db.session.commit()
        #i loop over the atomtype table and change all instance 
        #wich are linked with oldIdClassATom by the newIdClassAtom
        atomTypesInstances = db.session.query(AtomsType).filter(AtomsType.idForceField == idForceField,AtomsType.idClassAtom == idClassAtomSelected).all()
        for instance in atomTypesInstances:
            instance.idClassAtom = dictValues['idClassAtom']
            db.session.add(instance)
        db.session.commit()
        #i retrieve in the classAtomParam Table all instance
        #with old class atom number and replace  with actual class atom number
        db.session.query(ClassAtom_ParamsClass).filter(ClassAtom_ParamsClass.idClassAtom == idClassAtomSelected,\
            ClassAtom_ParamsClass.idForceField == idForceField).update({'idClassAtom':dictValues['idClassAtom']})
        db.session.commit()
        #i need to update all the description field that contains the old number
        listClassAtomParams = db.session.query(ClassAtom_ParamsClass).all()
        for instance in listClassAtomParams:
            if(instance.description):
                listDescription = instance.description.split('-')
                if(str(atomClassSelected.idClassAtom) in listDescription):
                    listDescription = [ dictValues['idClassAtom'] if x == str(atomClassSelected.idClassAtom) else x for x in listDescription ]
                instance.description = '-'.join(listDescription)
                db.session.add(instance)
        db.session.commit()

        #delete the old instance
        db.session.delete(atomClassSelected)
        db.session.commit()


    if session['countOperation'] != (len(session['listOfOperation']) -1):
        for i in range((len(session['listOfOperation'])-1),session['countOperation'],-1):
            session['listOfOperation'].pop(i)
        session['redo'] = False
    session['listOfOperation'].append(instanceForUndoRedo)
    session['countOperation'] += 1
    session['undo'] = True
    session['save'] = True

    return flashIndex('The class atom was updated sucessfuly','success',sessionData(nameParameter="Atom Definition",nameForceField=dictValues['ForceField']))


@app.route('/addAtomClassOk')
def addAtomClassOk():
    dictValues = {}
    for key,value in request.args.items():
        dictValues[key] = value

    #check if symbol already exist
    atomClassInstance = db.session().query(ClassAtom).filter(ClassAtom.symbol == dictValues['symbol']).scalar()
    if(atomClassInstance):
        return flashIndex("symbol "+dictValues['symbol'] +" already existing by classAtom number "+ str(atomClassInstance.idClassAtom),'error')

    #get idForceField
    idForceField = db.session.query(ForceField.idForceField).filter(ForceField.nameForceField == dictValues['ForceField']).scalar()
    #create new instance of ClassAtom
    atomClassInstance = ClassAtom(dictValues['idClassAtom'],idForceField,dictValues['symbol'],dictValues['atomicNumber'],dictValues['atomicWeight'],dictValues['valence'])
    #add the new ClassAtom in the table
    db.session.add(atomClassInstance)
    db.session.commit()

    #create atomClassDefinition object 
    AtomClassDefinitionInstance = AtomClassDefinition(idClassAtom=atomClassInstance.idClassAtom,symbol=dictValues['symbol'],atomicNumber=dictValues['atomicNumber'],\
                                    atomicWeight=dictValues['atomicWeight'],valence=dictValues['valence'])

    #for undo/redo
    instanceForUndoRedo = UndoRedoObject("addClassAtom",dictValues['ForceField'],
                                         nameParameter="Atom Definition",atomClassDefinitionList=[AtomClassDefinitionInstance])
    

    if session['countOperation'] != (len(session['listOfOperation']) -1):
        for i in range((len(session['listOfOperation'])-1),session['countOperation'],-1):
            session['listOfOperation'].pop(i)
        session['redo'] = False
    session['listOfOperation'].append(instanceForUndoRedo)
    session['countOperation'] += 1
    session['undo'] = True
    session['save'] = True
    return flashIndex("classAtom number "+ str(atomClassInstance.idClassAtom)+" successfuly added",'success',sessionData())



@app.route('/removeRowOk/<string:ffName>/<string:paramName>')
def removeRowOk(ffName,paramName):
    existClass = False
    listForAtom= []
    listForConstantScaling = []
    listForParameter =[]
    listOfValues = []
    idForceFieldDelete = db.session.query(ForceField.idForceField).filter(ForceField.nameForceField == ffName).scalar()
    parameterDelete = db.session.query(ParameterTable).filter(ParameterTable.nameParameter == paramName).scalar()
    

    for key , value in request.args.items():
        print(key,value,file=sys.stderr)
        listOfValues.append(value)

    #loop over all data to remove
    for value in listOfValues:
        if paramName == "Atom Definition":
            #c'est le idAtomType a suprimer , don't forget each row in the grid
            #represent one instance of atom type
            listIdParamToDeleteClass=[]
            listIdParamToDeleteType=[]
            description = ""
            #verification dans le forcefield et le meme atomType
            instanceToDelete = db.session.query(AtomsType).filter(AtomsType.idForceField == idForceFieldDelete,
                                 AtomsType.idAtomType == value).scalar()                                   
            
            isOtherInstanceOfClass = db.session.query(AtomsType).filter(AtomsType.idClassAtom == instanceToDelete.idClassAtom,AtomsType.idForceField == idForceFieldDelete).all()
            if(isOtherInstanceOfClass and isOtherInstanceOfClass[len(isOtherInstanceOfClass)-1].idAtomType != instanceToDelete.idAtomType):
                existClass = True

            
            # FOr the operation Undo in order to keep the atom deleted
            instanceClass = db.session.query(ClassAtom).filter(ClassAtom.idForceField == idForceFieldDelete,
                                 ClassAtom.idClassAtom == instanceToDelete.idClassAtom).first()                               
            newAtom = AtomClassDefinition(instanceToDelete.idClassAtom,instanceClass.symbol,instanceClass.atomicNumber,
                                          instanceClass.atomicWeight,instanceClass.valence,instanceToDelete.idAtomType,
                                          instanceToDelete.description,existClass=existClass)
            listForAtom.append(newAtom)
            
            #If i delete one class or type that was used in parameter, i need to delete there parameter value
            #retrieve all ClassAtom_ParamsClass that linked with idForceFieldDelete and idClassAtom 
            if(not existClass):
                classAtom_paramClass_instances = db.session.query(ClassAtom_ParamsClass).filter(ClassAtom_ParamsClass.idForceField == idForceFieldDelete,\
                                                                ClassAtom_ParamsClass.idClassAtom == instanceToDelete.idClassAtom).all()
                for instance in classAtom_paramClass_instances:
                    paramClass_instance = db.session.query(ParamsClass).get(instance.idParam)
                    count = 0
                    keyValue = {}
                    description = instance.description if instance.description else instance.idClassAtom
                    listIdParamToDeleteClass.append(instance.idParam)
                    classSon_instances = db.session.query(ValueClass).filter(ValueClass.idParam == instance.idParam).all()
                    for classSonInstance in classSon_instances:
                        keyValue[str(count)+'_'+classSonInstance.key] = classSonInstance.value;
                        count = count + 1
                    newInstance = parameterClassOrType("class",paramClass_instance.idParameter,'',description,keyValue)
                    listForParameter.append(newInstance)
                        
            #retrieve all atomType_paramType that linked with idForceFieldDelete and idClassAtom
            atomType_paramType_instances = db.session.query(AtomsType_ParamsType).filter(AtomsType_ParamsType.idForceField == idForceFieldDelete,\
                                                            AtomsType_ParamsType.idAtomType == instanceToDelete.idAtomType).all()
            for instance in atomType_paramType_instances:
                count = 0
                keyValue = {}
                paramType_instance = db.session.query(ParamsType).get(instance.idParam)
                description = instance.description if instance.description else instance.idAtomType
                listIdParamToDeleteType.append(instance.idParam)
                classSon_instances = db.session.query(ValueType).filter(ValueType.idParam == instance.idParam).all()
                for typeSonInstance in classSon_instances:
                    keyValue[str(count)+'_'+typeSonInstance.key] = typeSonInstance.value;
                    count = count + 1
                newInstance = parameterClassOrType("type",paramType_instance.idParameter,'',description,keyValue)
                listForParameter.append(newInstance)                        
    
            # Delete here the atom line value
            db.session.delete(instanceToDelete)
            db.session.flush()
            if existClass == False:
                # the last class before updtated is not more existing in this ff, i deleted now
                db.session.delete(db.session.query(ClassAtom).get((instanceToDelete.idClassAtom,idForceFieldDelete)))
                db.session.flush() 
            
            #I delete all parameter that was calculated by the deleted type/class
            for idParam in listIdParamToDeleteClass:
                db.session.delete(db.session.query(ParamsClass).get(idParam))
            
            for idParam in listIdParamToDeleteType:
                db.session.delete(db.session.query(ParamsType).get(idParam))
            db.session.flush()
        else:
            if parameterDelete.parameterType == 'SF':
                keyValue = {}
                #retrieve the key of sf 
                sf_key = value
                instanceToDelete = db.session.query(ScalingFactorTable).filter(ScalingFactorTable.idForceField == idForceFieldDelete,
                                     ScalingFactorTable.key == sf_key,
                                     ScalingFactorTable.idParameter == parameterDelete.idParameter).scalar()
                
                # The next code is using to keep the delete scaling data for the case that the user make undo operation
                keyValue['0_'+instanceToDelete.key] = instanceToDelete.value;
                newScaling = ConstantScalingFactorData(instanceToDelete.idParameter,keyValue,key=sf_key)
                listForConstantScaling.append(newScaling)
                db.session.delete(instanceToDelete)
                db.session.flush()
            elif parameterDelete.parameterType == 'Constant':
                keyValue = {}
                constant_key = value
                instanceToDelete = db.session.query(ConstantTable).filter(ConstantTable.idForceField == idForceFieldDelete,
                                     ConstantTable.key == constant_key,
                                     ConstantTable.idParameter == parameterDelete.idParameter).scalar()
                # The next codde is using to keep the delete constant data for the case that the user make undo operation
                keyValue['0_'+instanceToDelete.key] = instanceToDelete.value;
                newScaling = ConstantScalingFactorData(instanceToDelete.idParameter,keyValue,key=constant_key)
                listForConstantScaling.append(newScaling)
                db.session.delete(instanceToDelete)
                db.session.flush()                    
            else: # IF the selected parameter is a real parameter
                classOrTypeText = value
                idParamToDelete = 0
                keyValue = {}
                description = ""
                if parameterDelete.classOrType == "type": # CHeck if the parameter calculated based on type
                    if '-' in classOrTypeText:
                        atomTypeParam = db.session.query(AtomsType_ParamsType).filter(AtomsType_ParamsType.idForceField == idForceFieldDelete,
                                        AtomsType_ParamsType.description == classOrTypeText).all()
                    else:
                        atomTypeParam = db.session.query(AtomsType_ParamsType).filter(AtomsType_ParamsType.idForceField == idForceFieldDelete,
                                        AtomsType_ParamsType.idAtomType == classOrTypeText).all()
                    for instance in atomTypeParam:
                        paramType_instances = db.session.query(ParamsType).filter(ParamsType.idParam == instance.idParam,ParamsType.idParameter == parameterDelete.idParameter).scalar()
                        if(paramType_instances):
                            idParamToDelete = paramType_instances.idParam
                            break


                    instanceToDelete = db.session.query(ParamsType).get(idParamToDelete)
                    # NOw i keep the data of the value deleted for the undo operation
                    atomsType_paramsType_instances = db.session.query(AtomsType_ParamsType).filter(AtomsType_ParamsType.idForceField == idForceFieldDelete,AtomsType_ParamsType.idParam == instanceToDelete.idParam).first()
                    description = atomsType_paramsType_instances.description if atomsType_paramsType_instances.description else atomsType_paramsType_instances.idAtomType
                    
                    typesSon_instances = db.session.query(ValueType).filter(ValueType.idParam == instanceToDelete.idParam).all()
                    count = 0
                    for typeSon in typesSon_instances:
                        keyValue[str(count)+'_'+typeSon.key] = typeSon.value;
                        count = count + 1
                    
                    newInstance = parameterClassOrType("type",instanceToDelete.idParameter,'',
                                                       description,keyValue,idParam=idParamToDelete)
                    listForParameter.append(newInstance)
                    db.session.delete(instanceToDelete)
                    db.session.flush()
                else:   # CHeck if the parameter calculated based on class
                    if '-' in classOrTypeText:
                        classAtomParam = db.session.query(ClassAtom_ParamsClass).filter(ClassAtom_ParamsClass.idForceField == idForceFieldDelete,
                                        ClassAtom_ParamsClass.description == classOrTypeText).all()
                    else:
                        classAtomParam = db.session.query(ClassAtom_ParamsClass).filter(ClassAtom_ParamsClass.idForceField == idForceFieldDelete,
                                        ClassAtom_ParamsClass.idClassAtom == classOrTypeText).all()
                    for instance in classAtomParam:
                        paramsClass_instances = db.session.query(ParamsClass).filter(ParamsClass.idParam == instance.idParam,ParamsClass.idParameter == parameterDelete.idParameter).all()
                        if(paramsClass_instances):
                            idParamToDelete = instance.idParam
                            break
                    
                    instanceToDelete = db.session.query(ParamsClass).get(idParamToDelete)
                    # NOw i keep the data of the value deleted for the undo operation
                    ClassAtom_ParamsClass_instance = db.session.query(ClassAtom_ParamsClass).filter(ClassAtom_ParamsClass.idForceField == idForceFieldDelete,ClassAtom_ParamsClass.idParam == instanceToDelete.idParam).first()
                    description = ClassAtom_ParamsClass_instance.description if ClassAtom_ParamsClass_instance.description else ClassAtom_ParamsClass_instance.idClassAtom
                    classSon_instances = db.session.query(ValueClass).filter(ValueClass.idParam == instanceToDelete.idParam).all()
                    count = 0
                    for classSon in classSon_instances:
                        keyValue[str(count)+'_'+classSon.key] = classSon.value
                        count = count + 1
                    newInstance = parameterClassOrType("class",instanceToDelete.idParameter,'',
                                                       description,keyValue,idParam=idParamToDelete)
                    listForParameter.append(newInstance)
                    db.session.delete(instanceToDelete)
                    db.session.flush()
        

    instanceForUndoRedo = UndoRedoObject("deleteValueParameter",ffName,
                                         nameParameter=paramName,atomClassDefinitionList=listForAtom,
                                         constantScalingFactorDataList = listForConstantScaling,
                                         parameterClassOrTypeList=listForParameter)
    # FOr the undo/redo operation
    if session['countOperation'] != (len(session['listOfOperation']) -1):
        for i in range((len(session['listOfOperation'])-1),session['countOperation'],-1):
            session['listOfOperation'].pop(i)
        session['redo'] = False
    session['listOfOperation'].append(instanceForUndoRedo)
    session['countOperation'] += 1
    session['undo'] = True
    session['save'] = True

    db.session.commit()
    return flashIndex('This row has been successfuly removed from database','success',sessionData(operation='deleteValueParameter',nameForceField=ffName,nameParameter=paramName))


@app.route('/updateValueRowOk/<string:ffName>/<string:paramName>')
def updateValueRowOk(ffName,paramName):

    oldRowData = {}
    newRowData = {}
    listKeyChanged = []
    deleteOldClassAtom = False
    
    for key,value in request.args.items():
        if('new' in key):
            keyTemp = key.split('_')
            keyTemp.pop(0)
            keyTemp = '_'.join(keyTemp)
            newRowData[keyTemp] = value
        if('old' in key):
            keyTemp = key.split('_')
            keyTemp.pop(0)
            keyTemp = '_'.join(keyTemp)
            oldRowData[keyTemp] = value
        if('deleteOldClassAtom' in key):
            deleteOldClassAtom = True if value == "True" else False

    #list of colums in the grid wich was edited
    listKeyChanged = [x for x in newRowData.keys() if(oldRowData[x] != newRowData[x])]
    print(listKeyChanged)

    idForceFieldUpdate = db.session.query(ForceField.idForceField).filter(ForceField.nameForceField == ffName).scalar()
    parameterUpdate = db.session.query(ParameterTable).filter(ParameterTable.nameParameter == paramName).scalar()

    if paramName == "Atom Definition":
        return editAtomDefinition(ffName,oldRowData,newRowData,deleteOldClassAtom)
    if "Scaling" in paramName:
        return editScalingFactor(ffName,paramName,oldRowData,newRowData)
    if "Constant" in paramName:
        return editConstant(ffName,paramName,oldRowData,newRowData)
    if parameterUpdate.classOrType == 'class':
        return editParamsClass(ffName,paramName,oldRowData,newRowData)
    if parameterUpdate.classOrType == 'type':
        return editParamType(ffName,paramName,oldRowData,newRowData)


@app.route('/renameParameterOk/<string:ffName>/<string:oldName>/<string:newName>')
def renameParameterOk(ffName,oldName,newName):
    #the idea in this function is that we don't remove
    #the oldName from the parameterTable , we add the new one
    #and save the old in parameterTable. but we are updating the many to many.
    idForceField = db.session.query(ForceField.idForceField).filter(ForceField.nameForceField == ffName).scalar()
    
    #i already check in client side , that it can't change atom definition

    #i check if the parameter exist or not 
    if(isParameterExist(ffName,newName)):
        return flashIndex("The parameter " +newName + " already exist",'error')


    oldParameter = db.session.query(ParameterTable).filter(ParameterTable.nameParameter == oldName).scalar()
    newParameter = ParameterTable(newName,oldParameter.parameterType, oldParameter.numberOfAtoms,oldParameter.classOrType)
    newParameter.columnsName = oldParameter.columnsName
    db.session.add(newParameter)
    db.session.commit()
        
    db.session.query(ParametersOfForceField).filter(ParametersOfForceField.idParameter == oldParameter.idParameter,
                                ParametersOfForceField.idForceField == idForceField).update({"idParameter":newParameter.idParameter})
    db.session.commit()
    if newParameter.parameterType == 'SF':
        db.session.query(ScalingFactorTable).filter(ScalingFactorTable.idParameter == oldParameter.idParameter,
                                ScalingFactorTable.idForceField == idForceField).update({"idParameter":newParameter.idParameter})
    elif newParameter.parameterType == 'Constant':
        db.session.query(ConstantTable).filter(ConstantTable.idParameter == oldParameter.idParameter,
                                ConstantTable.idForceField == idForceField).update({"idParameter":newParameter.idParameter})
    else:
        if newParameter.classOrType == 'class':
            db.session.query(ParamsClass).filter(ParamsClass.idParameter == oldParameter.idParameter,
                        ParamsClass.idForceField == idForceField).update({"idParameter":newParameter.idParameter})
        else:
            db.session.query(ParamsType).filter(ParamsType.idParameter == oldParameter.idParameter,
                        ParamsType.idForceField == idForceField).update({"idParameter":newParameter.idParameter})

    db.session.commit()
    instanceForUndoRedo = UndoRedoObject("renameParameter",ffName,nameParameter =newName,oldValue=oldName)

    # FOr the undo/redo operation
    if session['countOperation'] != (len(session['listOfOperation']) -1):
        for i in range((len(session['listOfOperation'])-1),session['countOperation'],-1):
            session['listOfOperation'].pop(i)
        session['redo'] = False
    session['listOfOperation'].append(instanceForUndoRedo)
    session['countOperation'] += 1
    session['undo'] = True
    session['save'] = True

    return flashIndex('The parameter name '+ oldName +' was updated to '+ newName ,'success',sessionData(nameParameter=newName,nameForceField=ffName,operation="renameParameter"))


@app.route('/renameFFOk/<string:oldName>/<string:newName>')      
def renameFFOk(oldName,newName):
    #uppercase the name
    newName = newName.upper()
    #i have already did the verification , if the newName 
    #already exist or not in client side
    db.session.query(ForceField).filter(ForceField.nameForceField == oldName).update(
                                      {"nameForceField":newName})
    db.session.commit()
    
    instanceForUndoRedo = UndoRedoObject("renameFF",newName,nameParameter ="",oldValue=oldName)
    
    # FOr the undo/redo operation
    if session['countOperation'] != (len(session['listOfOperation']) -1):
        for i in range((len(session['listOfOperation'])-1),session['countOperation'],-1):
            session['listOfOperation'].pop(i)
        session['redo'] = False
    session['listOfOperation'].append(instanceForUndoRedo)
    session['countOperation'] += 1
    session['undo'] = True
    session['save'] = True
    
    return flashIndex('The forcefield name '+ oldName +' was updated to '+ newName,'success',sessionData(nameParameter="",nameForceField=newName,operation="renameFF"))

@app.route('/redoFunction')
def redoFunction():
    session['undo']= True
    session['save']= True
    if session['countOperation'] == (len(session['listOfOperation'])-1):
        session['redo']= False
    else:
        session['countOperation'] +=1
        undoRedoObject = session['listOfOperation'][session['countOperation']]
        if session['countOperation'] == (len(session['listOfOperation'])-1):
            session['redo'] = False
    
    # Now I analysis the count operation and execute him, like she is never maked
    #("rename",newNameFF,nameParameter =newNameParameter,oldValue=nameBeforeRename)
    if undoRedoObject['operation'] == "renameFF":
        db.session.query(ForceField).filter(ForceField.nameForceField == undoRedoObject['oldValue']).update(
                                      {"nameForceField":undoRedoObject['nameForceField']})
    if undoRedoObject['operation'] == "renameParameter":
        parameterBeforeRename = db.session.query(ParameterTable).filter(ParameterTable.nameParameter==undoRedoObject['oldValue']).scalar()
        parameterAfterRename = ParameterTable(undoRedoObject['nameParameter'],parameterBeforeRename.parameterType,
                                              parameterBeforeRename.numberOfAtoms,parameterBeforeRename.classOrType)
        parameterAfterRename.columnsName = parameterBeforeRename.columnsName
        db.session.add(parameterAfterRename)
        db.session.flush()
        
        idForceField = db.session.query(ForceField.idForceField).filter(ForceField.nameForceField==undoRedoObject['nameForceField']).scalar()
        db.session.query(ParametersOfForceField).filter(ParametersOfForceField.idParameter == parameterBeforeRename.idParameter,
                                        ParametersOfForceField.idForceField == idForceField).update({"idParameter":parameterAfterRename.idParameter})
                                        
        if parameterBeforeRename.parameterType == 'SF':
                db.session.query(ScalingFactorTable).filter(ScalingFactorTable.idParameter == parameterBeforeRename.idParameter,
                              ScalingFactorTable.idForceField == idForceField).update({"idParameter":parameterAfterRename.idParameter})
        elif parameterBeforeRename.parameterType == 'Constant':
            db.session.query(ConstantTable).filter(ConstantTable.idParameter == parameterBeforeRename.idParameter,
                              ConstantTable.idForceField == idForceField).update({"idParameter":parameterAfterRename.idParameter})
        else:
            if parameterBeforeRename.classOrType == 'class':
                db.session.query(ParamsClass).filter(ParamsClass.idParameter == parameterBeforeRename.idParameter,
                            ParamsClass.idForceField == idForceField).update({"idParameter":parameterAfterRename.idParameter})
            else:
                db.session.query(ParamsType).filter(ParamsType.idParameter == parameterBeforeRename.idParameter,
                            ParamsType.idForceField == idForceField).update({"idParameter":parameterAfterRename.idParameter})
                    
    elif undoRedoObject['operation'] == "addForceField":
        forceField = ForceField(undoRedoObject['nameForceField'])
        db.session.add(forceField)
        db.session.commit()
        recoverUserOfFF(undoRedoObject['ownerFF'],undoRedoObject['listUserOfForceField'],forceField.idForceField)
        #####################################################
    elif undoRedoObject['operation'] == "deleteForceField":
        forceField = db.session.query(ForceField).filter(ForceField.nameForceField == undoRedoObject['nameForceField']).scalar()
        db.session.delete(forceField)
        #####################################################
    elif undoRedoObject['operation'] == "addParameterToFF" or undoRedoObject['operation'] == "addSFToFF" or undoRedoObject['operation'] == "addConstantToFF":
        redoForAddParameterToFF(undoRedoObject)
        #####################################################
    elif undoRedoObject['operation'] == "deleteParameterToFF": # The last operation was deleted parameter.
        forceFieldId = db.session.query(ForceField.idForceField).filter(ForceField.nameForceField==undoRedoObject['nameForceField']).scalar()
        if undoRedoObject['nameParameter'] == "Atom Definition":
            
            #get athors of this ff
            usernameList = allAuthorsForcefied(forceFieldId)
            #get owner of FF
            ownerUsername = getOwnerOfFF(forceFieldId)
            instanceToDelete = db.session.query(ForceField).get(forceFieldId)                  
            db.session.delete(instanceToDelete)
            instanceForceField = ForceField(undoRedoObject['nameForceField'])
            db.session.add(instanceForceField)
            db.session.flush()
            #assign authors to the ff
            recoverUserOfFF(ownerUsername,usernameList,instanceForceField.idForceField)
        else:
            instanceParameter = db.session.query(ParameterTable).filter(ParameterTable.nameParameter == undoRedoObject['nameParameter']).scalar()
            ParametersOfForceFieldInstance = db.session.query(ParametersOfForceField).filter(ParametersOfForceField.idForceField == forceFieldId,ParametersOfForceField.idParameter == instanceParameter.idParameter).all()
            for x in ParametersOfForceFieldInstance:
                db.session.delete(x)
            
            if instanceParameter.parameterType == 'SF':
                SFInstance = db.session.query(ScalingFactorTable).filter(ScalingFactorTable.idForceField == forceFieldId,ScalingFactorTable.idParameter == instanceParameter.idParameter).all()
                for x in SFInstance:
                    db.session.delete(x)
            elif instanceParameter.parameterType == 'Constant':
                ConstantTableInstance = db.session.query(ConstantTable).filter(ConstantTable.idForceField == forceFieldId,ConstantTable.idParameter == instanceParameter.idParameter).all()
                for x in ConstantTableInstance:
                    db.session.delete(x)
            else:
                if instanceParameter.classOrType == 'class':
                    ParamsClassInstance = db.session.query(ParamsClass).filter(ParamsClass.idForceField == forceFieldId,ParamsClass.idParameter == instanceParameter.idParameter).all()
                    for x in ParamsClassInstance:
                        db.session.delete(x)
                else:
                    ParamsTypeInstance = db.session.query(ParamsType).filter(ParamsType.idForceField == forceFieldId,ParamsType.idParameter == instanceParameter.idParameter).all()
                    for x in ParamsTypeInstance:
                        db.session.delete(x)
        #####################################################
    elif undoRedoObject['operation'] == "addValueParameter":
        addValueParameterForRedo(undoRedoObject)
        #####################################################
    elif undoRedoObject['operation'] == "deleteValueParameter":
        deleteValueParameterForRedo(undoRedoObject)
        #####################################################
    elif undoRedoObject['operation'] == "addClassAtom":
        addClassAtomRedo(undoRedoObject)
    elif undoRedoObject['operation'] == "addAtomType":
        addAtomTypeRedo(undoRedoObject)
    elif undoRedoObject['operation'] == "editAtomClass":
        updateAtomClass(undoRedoObject,1)
    elif undoRedoObject['operation'] == "editAtomType":
        updateAtomType(undoRedoObject,1)
    elif undoRedoObject['operation'] == "editAtomDefinition":
        updateAtomType(undoRedoObject,1)
    elif undoRedoObject['operation'] == "editScalinFactor":
        updateScalingFactor(undoRedoObject,1)
    elif undoRedoObject['operation'] == "editConstant":
        updateConstant(undoRedoObject,1)  
    elif undoRedoObject['operation'] == "editParamsClass":
        updateParamsClass(undoRedoObject,1)
    elif undoRedoObject['operation'] == "editParamsType":
        updateParamsType(undoRedoObject,1)

    db.session.commit()
    if(undoRedoObject):
        operation = undoRedoObject['operation']
        nameForceField = undoRedoObject['nameForceField']
        nameParameter = undoRedoObject['nameParameter']
    else:
        operation = None
        nameForceField = None
        nameParameter = None


    return flashIndex("","",sessionData(operation=operation,nameForceField=nameForceField,nameParameter=nameParameter))

@app.route('/saveOperation')
def saveOperation():
    session['undo'] = False
    session['redo'] = False
    session['save'] = False
    session['numberOfColumns'] = -1
    session['keyList'] = []
    session['listOfOperation'] = []
    session['countOperation'] = -1
    session['tableName'] = ''
    session['numberOfAtoms'] = -1
    return flashIndex("Your(s) operation(s) are now saved.",'success',sessionData())


