from pyramid.view import view_config
from pyramid.renderers import get_renderer
from nhssl.resources import NHSSL, User, ServiceLog
from nhssl.forms import UserSchema, UserEditSchema, UserExportSchema, TextFieldSchema, OwnPasswordSchema, UserPasswordSchema
import deform
import calendarstuff
from deform import Form
from pyramid.traversal import find_root
from pyramid.security import authenticated_userid
import re
import hashlib
import colander

@view_config(context='nhssl.resources.UserContainer',
             renderer='nhssl:templates/users.pt',
             permission='view')
def view_users(context, request):
    logged_in = authenticated_userid(request)
    currentuser = find_root(request.context)["users"][logged_in]
    if currentuser.isAdvisor:
        if "action" in request.params:
            activityLog = find_root(context)['activityLogs']
            if request.params["action"] == "paid":
                for username in request.params.keys():
                    if not username == "action":
                        activityLog.user_edit(currentuser,context[username],request.application_url)
                        context[username].dues = True
            if request.params["action"] == "1meet":
                for username in request.params.keys():
                    if not username == "action":
                        activityLog.user_edit(currentuser,context[username],request.application_url)
                        context[username].firstMeeting = True
            if request.params["action"] == "2meet":
                for username in request.params.keys():
                    if not username == "action":
                        activityLog.user_edit(currentuser,context[username],request.application_url)
                        context[username].secondMeeting = True
            if request.params["action"] == "3meet":
                for username in request.params.keys():
                    if not username == "action":
                        activityLog.user_edit(currentuser,context[username],request.application_url)
                        context[username].thirdMeeting = True
            if request.params["action"] == "gpa":
                for username in request.params.keys():
                    if not username == "action":
                        activityLog.user_edit(currentuser,context[username],request.application_url)
                        context[username].gpa = True
    main = get_renderer('../templates/master.pt').implementation()
    userlist = []
    for user in context.values():
        if not hasattr(user, 'deactivated'):
            user.deactivated = False
        if user.username != 'god':
            userlist.append(user)
    userlist.sort(key=lambda user: user.lastName)
    return {'red':'',
             'main':main,
             'content':'',
             'userlist':userlist,
             'logged_in':logged_in,
             'name':'Users'}
    
@view_config(context='nhssl.resources.User',
             renderer='nhssl:templates/user.pt',
             permission='view')
def view_user(context,request):
    logged_in = authenticated_userid(request)
    isloggedinuser = False
    currentuser = find_root(request.context)["users"][logged_in] 
    main = get_renderer('../templates/master.pt').implementation()
    if currentuser == context or currentuser.isAdvisor or currentuser.isOfficer:
        isloggedinuser = True 
    gradclass = calendarstuff.class_from_year(context.gradYear)
    return {'red':'',
             'main':main,
             'content':'',
             'logged_in':logged_in,
             'gradclass':gradclass,
             'userself':isloggedinuser,
             'isadvisor':currentuser.isAdvisor,
             'name':'User '+context.username}
    
@view_config(name="ownpassword",
             context="nhssl.resources.User",
             renderer="nhssl:templates/form.pt")
def own_password(context,request):
    logged_in = authenticated_userid(request)
    isloggedinuser = False
    currentuser = find_root(request.context)["users"][logged_in]
    main = get_renderer('../templates/master.pt').implementation()
    if currentuser == context:
        isloggedinuser = True 
    if not isloggedinuser:
        return {'red':'users/',
                 "main":main,
                 'logged_in':logged_in,
                 'name':'Redirecting...',
                 'form':'',
                 'content':"You do not have permission to view this page."}
    schema = OwnPasswordSchema()
    passwordform = Form(schema, buttons=('submit',))
    if 'old' in request.params:
        try:
            controls = request.POST.items()
            captured = passwordform.validate(controls)
        except deform.ValidationFailure, e:
            passwordform = e.render()
            return {'red':'',
                     'name':'Change Password',
                     'main':main,
                     'form':passwordform,
                     'content':'',
                     'logged_in':logged_in}
        old = hashlib.sha1(request.params["old"].encode('UTF-8')).digest()
        new = hashlib.sha1(request.params["confirm"].encode('UTF-8')).digest()
        if old == currentuser.password:
            currentuser.password = new
            return {'red':'users/'+currentuser.username,
                     'logged_in':logged_in,
                     'main':main,
                     'name':'Redirecting...',
                     'form':'',
                     'content':'Your password has been changed.'}
        else:
            return {'red':'',
                     'main':main,
                     'name':'Change Password',
                     'logged_in':logged_in,
                     'form':'',
                     'content':'Incorrect old password.'}
    return {'red':'',
             'main':main,
             'name':'Change Password',
             'logged_in':logged_in,
             'form':passwordform.render(),
             'content':''}
    
@view_config(name="userpassword",
             context="nhssl.resources.User",
             renderer="nhssl:templates/form.pt")
def user_password(context,request):
    logged_in = authenticated_userid(request)
    currentuser = find_root(request.context)["users"][logged_in]
    main = get_renderer('../templates/master.pt').implementation()
    if not currentuser.isAdvisor:
        return {'red':'users/',
                 'main':main,
                 'logged_in':logged_in,
                 'name':'Redirecting...',
                 'form':'',
                 'content':'You do not have permission to view this page.'}
    schema = UserPasswordSchema()
    passwordform = Form(schema, buttons=('submit',))
    if 'confirm' in request.params:
        try:
            controls = request.POST.items()
            captured = passwordform.validate(controls)
        except deform.ValidationFailure, e:
            passwordform = e.render()
            return {'red':'',
                     'name':'Change Password',
                     'main':main,
                     'form':passwordform,
                     'content':'',
                     'logged_in':logged_in}
        new = hashlib.sha1(request.params["confirm"].encode('UTF-8')).digest()
        context.password = new
        return {'red':'users/'+context.username,
                 'logged_in':logged_in,
                 'main':main,
                 'name':'Redirecting...',
                 'form':'',
                 'content':'The password has been changed.'}
        
    return {'red':'',
             'main':main,
             'name':'Change Password',
             'logged_in':logged_in,
             'form':passwordform.render(),
             'content':''}
    
@view_config(name='edit',
             context='nhssl.resources.User',
             renderer='nhssl:templates/form.pt',
             permission='edit')
def edit_user(context,request):
    logged_in = authenticated_userid(request)    
    main = get_renderer('../templates/master.pt').implementation()
    schema = UserEditSchema()
    if context.isAdvisor:
        schema = schema.bind(default='Advisor')
    elif context.isOfficer:
        schema = schema.bind(default='Officer')
    elif context.isStudent:
        schema = schema.bind(default='Student')
    userform = Form(schema, buttons=('submit',))
    if 'studentId' in request.params:
        try:
            controls = request.POST.items()
            captured = userform.validate(controls)
        except deform.ValidationFailure, e:
            userform = e.render()
            return {'red':'',
                     'main':main,
                     'form':userform,
                     'content':'',
                     'logged_in':logged_in,
                     'name':'Edit User'}
        if ('deactivate' in request.params) and (request.params['deactivate'] == "true"):
            find_root(context)['activityLogs'].user_deactivation(find_root(request.context)["users"][logged_in],context,request.application_url)
            find_root(context)["serviceLogs"][context.username]
            context.deactivated = True
            return {'red':'users/',
                     'main':main,
                     'name':'Redirecting...',
                     'form':'',
                     'content':'Deactivated '+context.firstName+' '+context.lastName,
                     'logged_in':logged_in}
        context.studentId = request.params['studentId']
        context.firstName = request.params['firstName']
        context.lastName = request.params['lastName']
        context.email = request.params['email']
        context.phone = request.params['phone']
        context.gradYear = request.params['gradYear']
        context.inductionYear = request.params['inductionYear']
        context.dues = ('dues' in request.params) and (request.params['dues'] == "true")
        context.gpa = ('gpa' in request.params) and (request.params['gpa'] == "true")
        context.firstMeeting = ('firstMeeting' in request.params) and (request.params['firstMeeting'] == "true")
        context.secondMeeting = ('secondMeeting' in request.params) and (request.params['secondMeeting'] == "true")
        context.thirdMeeting = ('thirdMeeting' in request.params) and (request.params['thirdMeeting'] == "true")
        if captured['group'] == "Student":
            context.isStudent = True
            context.isOfficer = False
            context.isAdvisor = False
        if captured['group'] == "Officer":
            context.isStudent = True
            context.isOfficer = True
            context.isAdvisor = False
        if captured['group'] == "Advisor":
            context.isStudent = True
            context.isOfficer = True
            context.isAdvisor = True
        find_root(context)['activityLogs'].user_edit(find_root(request.context)["users"][logged_in],context,request.application_url)
        return {'red':'users/'+context.username,
                 'main':main,
                 'form':'',
                 'content':'Edited the user '+context.username,
                 'logged_in':logged_in,
                 'name':'Redirecting...'}
    appstruct = {'studentId':context.studentId,
                 'firstName':context.firstName,
                 'lastName':context.lastName,
                 'email':context.email,
                 'phone':context.phone,
                 'gradYear':context.gradYear,
                 'inductionYear':context.inductionYear,
                 'dues':context.dues,
                 'gpa':context.gpa,
                 'firstMeeting':context.firstMeeting,
                 'secondMeeting':context.secondMeeting,
                 'thirdMeeting':context.thirdMeeting,}
    userform = userform.render(appstruct=appstruct)
    return {'red':'',
             'main':main,
             'form':userform,
             'content':'',
             'logged_in':logged_in,
             'name':'Edit User'}
             
         
@view_config(name='delete',
             context='nhssl.resources.User',
             renderer='nhssl:templates/form.pt',
             permission='edit')
def delete_user(context, request):
    logged_in = authenticated_userid(request)
    app = find_root(context)
    currentuser = app["users"][logged_in]
    main = get_renderer('../templates/master.pt').implementation()
    schema = colander.MappingSchema()
    form = Form(schema, buttons=('submit','cancel'))
    form = form.render()
    content = "Confirm deletion of "+context.firstName+" "+context.lastName
    red = ''
    if 'submit' in request.POST:
        app['activityLogs'].user_deletion(currentuser,context,request.application_url)
        del context.__parent__[context.username]
        del app['serviceLogs'][context.username]
        content = 'Redirecting...'
        red = 'users/'
    elif 'cancel' in request.POST:
        content = 'Redirecting...'
        red = 'users/'+context.username
    return {'red':red,
             'main':main,
             'form':form,
             'content':content,
             'logged_in':logged_in,
             'name':'Delete User'}
         
@view_config(name='reactivate',
             context='nhssl.resources.User',
             renderer='nhssl:templates/user.pt',
             permission='edit')
def reactivate_user(context, request):
    app=find_root(context)
    logged_in = authenticated_userid(request)
    isloggedinuser = False
    currentuser = find_root(request.context)["users"][logged_in] 
    main = get_renderer('../templates/master.pt').implementation()
    if currentuser == context or currentuser.isAdvisor or currentuser.isOfficer:
        isloggedinuser = True 
    gradclass = calendarstuff.class_from_year(context.gradYear)
    context.deactivated = False
    app['activityLogs'].user_reactivation(currentuser,context,request.application_url)
    return {'red':'users/'+context.username,
             'main':main,
             'content':'User Reactivated',
             'logged_in':logged_in,
             'gradclass':gradclass,
             'userself':isloggedinuser,
             'isadvisor':currentuser.isAdvisor,
             'name':'Redirecting...'}

         
@view_config(name='update',
             context='nhssl.resources.User',
             renderer='nhssl:templates/update.pt',
             permission='view')
def update_user(context, request):
    logged_in = authenticated_userid(request)
    main = get_renderer('../templates/master.pt').implementation()
    error = ""
    if request.POST.keys():
        if "firstName" in request.POST:
            context.firstName = request.POST["firstName"]
        if "lastName" in request.POST:
            context.lastName = request.POST["firstName"]
        if "email" in request.POST:
            context.email = request.POST["email"]
        if "phone" in request.POST:
            context.phone = request.POST["phone"]
        if "gradYear" in request.POST:
            try:
                context.gradYear = int(request.POST["gradYear"])
            except ValueError:
                if error:  
                    error += ",<br/>"
                error += "Graduation Year <br/> must be both a number and <br/> when you'll graduate"
        if "inductionYear" in request.POST:
            try:
                context.inductionYear = int(request.POST["inductionYear"])
            except ValueError:
                if error:  
                    error += ",<br/>"
                error += "Induction Year must <br/> be a number and the year <br/> that you were induced"
        if not error:
            return {'red':'/',
                     'error':error,
                     'main':main,
                     'form':'',
                     'content':"Your information has been updated",
                     'logged_in':logged_in,
                     'name':'Redirecting...'}
    if context.isComplete():
        return {'red':'/',
                 'error':error,
                 'main':main,
                 'content':'Your information is already complete.',
                 'logged_in':logged_in,
                 'name':'Redirecting...'}
         
    return {'red':'',
             'error':error,
             'main':main,
             'content':'',
             'logged_in':logged_in,
             'name':'Update Information'}
         
@view_config(name='add_user',
             context='nhssl.resources.UserContainer',
             renderer='nhssl:templates/form.pt',
             permission='view')
def add_user(context, request):
    logged_in = authenticated_userid(request)
    main = get_renderer('../templates/master.pt').implementation()
    schema = UserSchema()
    userform = Form(schema, buttons=('submit',),use_ajax=True)
    if 'username' in request.params:
        try:
            controls = request.POST.items()
            captured = userform.validate(controls)
        except deform.ValidationFailure, e:
            userform = e.render()
            return {'red':'',
                     'main':main,
                     'form':userform,
                     'content':'',
                     'logged_in':logged_in,
                     'name':'Add User'}
        username = request.params['username']
        if username in context:
            return {'red':'',
                     'logged_in':logged_in,
                     'main':main,
                     'form':'',
                     'content':'Sorry, the username '+username+' already exists in this system.  Please try again, or contact an administrator.',
                     'name':'Users'}
        password = hashlib.sha1(request.params["confirm"].encode('UTF-8')).digest()
        studentId = request.params['studentId']
        firstName = request.params['firstName']
        lastName = request.params['lastName']
        email = request.params['email']
        phone = request.params['phone']
        gradYear = request.params['gradYear']
        inductionYear = request.params['inductionYear']
        user = User(username,
                    password,
                    studentId,
                    firstName = firstName,
                    lastName = lastName,
                    email = email,
                    phone = phone,
                    gradYear = gradYear,
                    inductionYear = inductionYear)
        user.__parent__ = context
        context[username] = user
        serviceLog = ServiceLog(user)
        serviceLog.__parent__ = find_root(user)['serviceLogs']
        find_root(user)['serviceLogs'][username]=serviceLog
        user.serviceLog = ServiceLog
        find_root(context)['activityLogs'].user_creation(find_root(request.context)["users"][logged_in],user,request.application_url)
        return {'red':'users/',
                 'main':main,
                 'form':'',
                 'content':'The user '+firstName+' '+lastName+' was added to the system, with a username of '+username,
                 'logged_in':logged_in,
                 'name':'Redirecting...'}
    userform = userform.render()
    return {'red':'',
             'main':main,
             'form':userform,
             'content':'',
             'logged_in':logged_in,
             'name':'Users'}
    
@view_config(name='swordfishmicrocrystal',context='nhssl.resources.UserContainer',renderer='nhssl:templates/default.pt')
def swordfish(context,request):
    logged_in = authenticated_userid(request)
    main = get_renderer('../templates/register.pt').implementation()
    if not 'god' in context:
        context["god"] = User("god", hashlib.sha1("eden".encode('UTF-8')).digest(), 777777, firstName = "Jesus", lastName = "Christ", email = "God@heaven.edu", phone = "777-777-7707", gradYear = 2013, inductionYear = 0, isofficer=True, isadvisor=True); context["god"].__parent__ = context
        return {'red':'','main':get_renderer('../templates/register.pt').implementation(),'content':'And on the eighth day, Man created God','logged_in':authenticated_userid(request),'name':'Apotheosis Sucessful (:'}
    return {'red':'','main':get_renderer('../templates/register.pt').implementation(),'content':'You already have a God','logged_in':authenticated_userid(request),'name':'Apotheosis Failed D:'}


@view_config(name='register',
             context='nhssl.resources.UserContainer',
             renderer='nhssl:templates/form.pt')
def register(context, request):
    main = get_renderer('../templates/register.pt').implementation()
    schema = UserSchema()
    userform = Form(schema, buttons=('submit',),use_ajax=True)
    if 'username' in request.params:
        try:
            controls = request.POST.items()
            captured = userform.validate(controls)
        except deform.ValidationFailure, e:
            userform = e.render()
            return {'red':'',
                     'main':main,
                     'form':userform,
                     'content':'',
                     'name':'Register'}

        username = request.params['username']
        if username in context:
            return {'red':'/',
                     'logged_in':logged_in,
                     'main':main,
                     'form':'',
                     'content':'Sorry, the username '+username+' already exists in this system.  Please try again, or contact an administrator.',
                     'name':'Users'}
        password = hashlib.sha1(request.params["confirm"].encode('UTF-8')).digest()
        studentId = request.params['studentId']
        firstName = request.params['firstName']
        lastName = request.params['lastName']
        email = request.params['email']
        phone = request.params['phone']
        gradYear = request.params['gradYear']
        inductionYear = request.params['inductionYear']
        user = User(username,
                    password,
                    studentId,
                    firstName = firstName,
                    lastName = lastName,
                    email = email,
                    phone = phone,
                    gradYear = gradYear,
                    inductionYear = inductionYear)
        user.__parent__ = context
        context[username] = user
        serviceLog = ServiceLog(user)
        serviceLog.__parent__ = find_root(user)['serviceLogs']
        find_root(user)['serviceLogs'][username]=serviceLog
        user.serviceLog = ServiceLog
        find_root(context)['activityLogs'].user_registration(user,request.application_url)
        return {'red':'/',
                 'main':main,
                 'form':'',
                 'content':'The user '+firstName+' '+lastName+' was added to the system, with a username of '+username,
                 'name':'Register'}
    userform = userform.render()
    return {'red':'',
             'main':main,
             'form':userform,
             'content':'',
             'name':'Register'}

@view_config(name='csvexport',
             context='nhssl.resources.UserContainer',
             renderer='nhssl:templates/form.pt')
def csvexport(context,request):
    logged_in = authenticated_userid(request)
    main = get_renderer('../templates/master.pt').implementation()
    schema = UserExportSchema()
    exportform = Form(schema, buttons=('submit',))
    if 'submit' in request.params:
        output = ""
        for user in context.values():
            userout = ""
            if ('studentId' in request.params) and (request.params['studentId'] == "true"):
                userout += (str(user.studentId) + ", ")
            if ('firstName' in request.params) and (request.params['firstName'] == "true"):
                userout += (str(user.firstName) + ", ")
            if ('lastName' in request.params) and (request.params['lastName'] == "true"):
                userout += (str(user.lastName) + ", ")
            if ('username' in request.params) and (request.params['username'] == "true"):
                userout += (str(user.username) + ", ")
            if ('email' in request.params) and (request.params['email'] == "true"):
                userout += (str(user.email) + ", ")
            if ('phone' in request.params) and (request.params['phone'] == "true"):
                userout += (str(user.phone) + ", ")
            if ('gradYear' in request.params) and (request.params['gradYear'] == "true"):
                userout += (str(user.gradYear) + ", ")
            if ('inductionYear' in request.params) and (request.params['inductionYear'] == "true"):
                userout += (str(user.inductionYear) + ", ")
            if ('dues' in request.params) and (request.params['dues'] == "true"):
                userout += (str(user.dues) + ", ")
            if ('gpa' in request.params) and (request.params['gpa'] == "true"):
                userout += (str(user.gpa) + ", ")
            if ('firstMeeting' in request.params) and (request.params['firstMeeting'] == "true"):
                userout += (str(user.firstMeeting) + ", ")
            if ('secondMeeting' in request.params) and (request.params['secondMeeting'] == "true"):
                userout += (str(user.secondMeeting) + ", ")
            if ('thirdMeeting' in request.params) and (request.params['thirdMeeting'] == "true"):
                userout += (str(user.thirdMeeting) + ", ")
            if ('hours' in request.params) and (request.params['hours'] == "true"):
                userout += (str(user.hours) + ", ")
            if ('sponsored' in request.params) and (request.params['sponsored'] == "true"):
                userout += (str(user.sponsored))
            userout = str(userout)
            userout = "\n"+userout
            output += userout 
        schema = TextFieldSchema()
        exportform = Form(schema).render(appstruct={'text':output})
        return {'red':'',
                 'main':main,
                 'logged_in':logged_in,
                 'form':exportform,
                 'content':'To open in a spreadsheet program, copy the following into a text file and save with extension .csv:',
                 'name':'Exported to CSV'}
    return {'red':'',
             'main':main,
             'logged_in':logged_in,
             'form':exportform.render(),
             'content':'',
             'name':'Export to CSV'}

@view_config(name='csvimport',
             context='nhssl.resources.UserContainer',
             renderer='nhssl:templates/userimportcsv.pt')
def csvimport(context,request):
    logged_in = authenticated_userid(request)
    main = get_renderer('../templates/master.pt').implementation()
    schema = TextFieldSchema()
    importform = Form(schema, buttons=('submit',))
    if 'submit' in request.params:
        inputstring = str(request.params["text"])
        inputstring = inputstring.replace("\r","")
        inputstring = inputstring.replace(", ",",")
        lines = inputstring.split("\n")
        inputlist = []
        for line in lines:
            if not line == "":
                ul = line.split(",")
                user = User(
                            ul[2], #username
                            hashlib.sha1(ul[8].encode('UTF-8')).digest(), #password, encoded
                            ul[3], #studentID
                            firstName = ul[1],
                            lastName = ul[0],
                            email = ul[4],
                            phone = ul[5],
                            gradYear = ul[6],
                            inductionYear = ul[7]
                            )
                username = ul[2]
                if username in context:
                    return {'red':'',
                             'logged_in':logged_in,
                             'main':main,
                             'form':exportform.render(),
                             'content':"ERROR: the username "+username+" already exists in this system.  Please reassess your input data.",
                             'name':'Import From CSV'}
                user.__parent__ = context
                context[username] = user
                serviceLog = ServiceLog(user)
                serviceLog.__parent__ = find_root(user)['serviceLogs']
                find_root(user)['serviceLogs'][username]=serviceLog
                user.serviceLog = ServiceLog
                find_root(context)['activityLogs'].user_creation(find_root(request.context)["users"][logged_in],user,request.application_url)
        return {'red':'users/',
                 'main':main,
                 'logged_in':logged_in,
                 'form':'',
                 'content':'Imported Users from CSV',
                 'name':'Redirecting...'}
    return {'red':'',
             'main':main,
             'logged_in':logged_in,
             'form':importform.render(),
             'content':'',
             'name':'Import From CSV'}

@view_config(name='requirementsimportcsv',
             context='nhssl.resources.UserContainer',
             renderer='nhssl:templates/requirementimportcsv.pt')
def requirementsimport(context,request):
    logged_in = authenticated_userid(request)
    main = get_renderer('../templates/master.pt').implementation()
    schema = TextFieldSchema()
    importform = Form(schema, buttons=('submit',))
    if 'submit' in request.params:
        inputstring = str(request.params["text"])
        inputstring = inputstring.replace("\r","")
        inputstring = inputstring.replace(", ",",")
        lines = inputstring.split("\n")
        inputlist = []
        for line in lines:
            if not line == "":
                rl = line.split(",")
                for value in rl[1:]:
                    if value in ['Yes', 'YES', 'yes', 'Y', 'y']:
                        value = True
                    elif value in ['No', 'NO', 'no', 'N', 'n']:
                        value = False
                    if type(value) != type(True):
                        return {'red':'',
                                 'logged_in':logged_in,
                                 'main':main,
                                 'form':exportform.render(),
                                 'content':"ERROR: Input data was not either 'yes' or 'no', and could not be processed.  Please reassess your input data.",
                                 'name':'Import Requirements From CSV'}
                username = rl[0]
                if not username in context:
                    return {'red':'','logged_in':logged_in,'main':main,'form':exportform.render(), 'content':"ERROR: the username "+username+" does not exist in this system.  Please reassess your input data.",'name':'Import Requirements From CSV'}
                context[username].dues = rl[1]
                context[username].gpa = rl[2]
                context[username].firstMeeting = rl[3]
                context[username].secondMeeting = rl[4]
                context[username].thirdMeeting = rl[5]
                find_root(context)['activityLogs'].user_edit(context[logged_in],context[username],request.application_url)
        return {'red':'users/',
                 'main':main,
                 'logged_in':logged_in,
                 'form':'',
                 'content':'Imported Information from CSV',
                 'name':'Redirecting...'}
    return {'red':'',
             'main':main,
             'logged_in':logged_in,
             'form':importform.render(),
             'content':'',
             'name':'Import Requirements From CSV'}


@view_config(name='hoursimportcsv',context='nhssl.resources.UserContainer',
             renderer='nhssl:templates/hoursimportcsv.pt')
def hoursimport(context,request):
    logged_in = authenticated_userid(request)
    main = get_renderer('../templates/master.pt').implementation()
    schema = TextFieldSchema()
    importform = Form(schema, buttons=('submit',))
    if 'submit' in request.params:
        inputstring = str(request.params["text"])
        inputstring = inputstring.replace("\r","")
        inputstring = inputstring.replace(", ",",")
        lines = inputstring.split("\n")
        inputlist = []
        for line in lines:
            if not line == "":
                rl = line.split(",")
                for value in rl[1:]:
                    try:
                        value = float(value)
                    except ValueError:
                        return {'red':'',
                                 'logged_in':logged_in,
                                 'main':main,
                                 'form':exportform.render(),
                                 'content':"ERROR: Input data was not a number, and could not be processed.  Please reassess your input data.",
                                 'name':'Import Hours From CSV'}
                username = rl[0]
                if not username in context:
                    return {'red':'',
                             'logged_in':logged_in,
                             'main':main,
                             'form':exportform.render(),
                             'content':"ERROR: the username "+username+" does not exist in this system.  Please reassess your input data.",
                             'name':'Import Hours From CSV'}
                context[username].hours = rl[1]
                context[username].sponsored = rl[2]
                find_root(context)['activityLogs'].user_edit(context[logged_in],context[username],request.application_url)
        return {'red':'users/',
                 'main':main,
                 'logged_in':logged_in,
                 'form':'',
                 'content':'Imported Hours from CSV',
                 'name':'Redirecting...'}
    return {'red':'',
             'main':main,
             'logged_in':logged_in,
             'form':importform.render(),
             'content':'',
             'name':'Import Hours From CSV'}
