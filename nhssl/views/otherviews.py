from pyramid.view import view_config
from pyramid.renderers import get_renderer
from nhssl.resources import NHSSL, Settings#, Project
from pyramid.url import resource_url
from nhssl.forms import EmailSchema, TextFieldSchema, ProjectsSchema
from deform import Form
from pyramid.security import authenticated_userid
from pyramid.traversal import find_root
import calendarstuff
import deform
import datetime

@view_config(context=NHSSL, 
             permission='view', 
             renderer='nhssl:templates/main.pt')
def home(context, request):
    name = 'Home Page'
    logged_in = authenticated_userid(request)
    main = get_renderer('../templates/master.pt').implementation()
    user = find_root(request.context)['users'][logged_in]
    if not user.isComplete():
        return {'red': 'users/'+logged_in+'/update', 
            'main': main, 
            'content': context['settings'].maintext,
            'logged_in': logged_in,
            'hours':{'V_hours':0, #VUSIT 
                      'U_hours':0,
                      'S_hours':0,
                      'I_hours':0,
                      'T_hours':0,
                      'J_hours':0,
                      'Se_hours':0
                     },
            'name': "Redirecting to User Update..."}
    serv_log = find_root(request.context)['serviceLogs']
    deadlines = find_root(request.context)['deadlines'].values()
    deadlines.sort(key=lambda deadline: abs(deadline.dateDue - datetime.datetime.today()))
    current_deadline = deadlines[0]
    if user.isStudent and not user.isAdvisor:
        for log in serv_log.values():
            if log.user.username == logged_in:
                main_log = log
        verified_hours = 0
        unverified_hours = 0
        sponsored_hours = 0
        independent_hours = 0
        total_hours = 0
        flagged_events = []
        for event in main_log.values():
            total_hours += float(event.hours)
            if event.verified == u'Verified':
                verified_hours += float(event.hours)
            else:
                unverified_hours += float(event.hours)
            if event.eventType == 'Sponsored':
                sponsored_hours += float(event.hours)
            else:
                independent_hours += float(event.hours)
            if event.verified == 'Flagged':
                flagged_events.append(event)
        hours_dict = {'V_hours':verified_hours, #VUSIT 
                      'U_hours':unverified_hours,
                      'S_hours':sponsored_hours,
                      'I_hours':independent_hours,
                      'T_hours':total_hours,
                     }
    if user.isAdvisor:
        verified_hours = 0
        unverified_hours = 0
        sponsored_hours = 0
        independent_hours = 0
        total_hours = 0
        senior_hours = 0
        junior_hours = 0
        for log in serv_log.values():
            for event in log.values():
                total_hours += float(event.hours)
                if event.verified == u'Verified':
                    verified_hours += float(event.hours)
                else:
                    unverified_hours += float(event.hours)
                if event.eventType == 'Sponsored':
                    sponsored_hours += float(event.hours)
                else:
                    independent_hours += float(event.hours)
                if calendarstuff.class_from_year(event.user.gradYear) == "Junior":
                    junior_hours += float(event.hours)
                else:
                    senior_hours += float(event.hours)
        hours_dict = {'V_hours':verified_hours, #VUSITJSe 
                      'U_hours':unverified_hours,
                      'S_hours':sponsored_hours,
                      'I_hours':independent_hours,
                      'T_hours':total_hours,
                      'J_hours':junior_hours,
                      'Se_hours':senior_hours,
                     }       
        flagged_events = []
    return {'red': '', 
            'main': main, 
            'content': context['settings'].maintext,
            'hours':hours_dict,
            'flagged':flagged_events,
            'deadline':current_deadline,
            'logged_in': logged_in,
            'name': name}
   
@view_config(context=NHSSL, 
             name="email", 
             permission='edit', 
             renderer='nhssl:templates/form.pt') 
def email(context,request):
    logged_in = authenticated_userid(request)
    main = get_renderer('../templates/master.pt').implementation()
    schema = EmailSchema()
    emailform = Form(schema, buttons=('submit',))
    if 'message' in request.params:
        try:
            controls = request.POST.items()
            captured = emailform.validate(controls)
        except deform.ValidationFailure, e:
            emailform = e.render()
            return {'red': '', 
                    'main': main, 
                    'form': emailform, 
                    'content': '', 
                    'logged_in': logged_in}
        to = request.params["to"]
        subject = request.params["subject"]
        message = request.params["message"]
        users = context["users"]
        url = request.application_url
        deadlines = find_root(context)['deadlines']
        nextsdl = ''
        nextjdl = ''
        for dl in deadlines.values():
            if dl.appliedClass == "Juniors" or dl.appliedClass == 'All':
                if not nextjdl:
                    nextjdl = dl
                elif nextjdl > dl:
                    nextjdl = dl
            if dl.appliedClass == "Seniors" or dl.appliedClass == 'All':
                if not nextsdl:
                    nextsdl = dl
                elif nextsdl > dl:
                    nextsdl = dl
        for user in users.values():
            if calendarstuff.class_from_year(user.gradYear) == "Junior":
                appldeadline = nextjdl
            elif calendarstuff.class_from_year(user.gradYear) == "Senior":
                appldeadline = nextsdl
            if to == "all":
                calendarstuff.email(subject, user.email, message, url)
            elif to == "officers" and user.isOfficer:
                calendarstuff.email(subject, user.email, message, url)
            elif to == "juniors" and calendarstuff.class_from_year(user.gradYear) == "Junior":
                calendarstuff.email(subject, user.email, message, url)
            elif to == "seniors" and calendarstuff.class_from_year(user.gradYear) == "Senior":
                calendarstuff.email(subject, user.email, message, url)
            elif to == "dues" and  not user.dues:
                calendarstuff.email(subject, user.email, message, url)
            elif to == "gpa" and not user.gpa:
                calendarstuff.email(subject, user.email, message, url)
            elif to == "thours" and user.hours > appldeadline.hours:
                calendarstuff.email(subject, user.email, message, url)
            elif to == "shours" and user.sponsored > appldeadline.sponsored:
                calendarstuff.email(subject, user.email, message, url)
    return {'red': '',
            'main': main, 
            'content': '', 
            'form': emailform.render(), 
            'logged_in': logged_in, 
            'name': 'Email'}
    

@view_config(context=NHSSL, 
             name="TupleTupleTuple", 
             permission='verify', 
             renderer='nhssl:templates/main.pt')
def tupletuple(context,request):
    name = 'TupleTupleTuple'
    logged_in = authenticated_userid(request)
    main = get_renderer('../templates/master.pt').implementation()
    info = str(context)
    logs = find_root(context)['serviceLogs'] 
    for events in logs.values():
        for event in events.values():
            if event.verified == "Deactivated":
               event.verified = "Rejected/Recanted"
    return {'red': '', 
            'main': main, 
            'content': info, 
            'logged_in': logged_in, 
            'name': name}

@view_config(context='nhssl.resources.Settings', 
             renderer='nhssl:templates/settings.pt',
             permission='verify')
def view_settings(context, request):
    logged_in = authenticated_userid(request)
    main = get_renderer('../templates/master.pt').implementation()
    schema = TextFieldSchema()
    titleform = Form(schema, buttons=('submit',), use_ajax=True)
    schema = ProjectsSchema()
    projectsform = Form(schema, buttons=('submit',), use_ajax=True)
    if 'text' in request.params:
        try:
            controls = request.POST.items()
            captured = titleform.validate(controls)
        except deform.ValidationFailure, e:
            titleform = e.render()
            return {'red': '',
                    'main': main, 
                    'titleform': titleform, 
                    'projectsform':projectsform.render(appstruct={'projects':context.projects}), 
                    'content': '', 
                    'logged_in': logged_in, 
                    'name': 'Settings'}
        context.maintext = request.params['text']
    if 'project' in request.params:
        try:
            controls = request.POST.items()
            captured = projectsform.validate(controls)
        except deform.ValidationFailure, e:
            projectsform = e.render()
            return {'red': '', 
                    'main': main, 
                    'titleform': titleform.render(appstruct={'text':context.maintext}), 
                    'projectsform':projectsform, 'content': '', 
                    'logged_in': logged_in, 
                    'name': 'Settings'}
        context.projects = request.params.getall("project")
    titleform = titleform.render(appstruct = {'text':context.maintext})
    projectsform = projectsform.render(appstruct = {'projects':context.projects})
    return {'red': '',
            'main': main, 
            'content': "", 
            'titleform':titleform,
            'projectsform':projectsform,
            'logged_in': logged_in,
            'name': 'Settings'}

#@view_config(name='add_project', context='nhssl.resources.Settings',
             #renderer='nhssl:templates/form.pt',permission='edit')
#def add_project(context, request):
    #logged_in = authenticated_userid(request)
    #main = get_renderer('../templates/master.pt').implementation()
    #schema = ProjectSchema()
    #projectform = Form(schema, buttons=('submit',), use_ajax=True)
    #if 'service' in request.params:
        #try:
            #controls = request.POST.items()
            #captured = projectform.validate(controls)
        #except deform.ValidationFailure, e:
            #projectform = e.render()
            #return {'red': '', 'main': main, 'form': projectform, 'content': '', 'logged_in': logged_in, 'name': 'Add Project'}
            
        #service = request.params['service']
        #project = Project(service)
        #project.__parent__ = context
        #context[service] = project
        #return {'red': 'settings/','main': main,'form': '','content': "Added a Project",'logged_in': logged_in,'name': 'Redirecting...'}
    #projectform = projectform.render()
    #return {'red': '', 'main': main, 'form': projectform, 'content': '','logged_in': logged_in, 'name': 'Add Project'}

#@view_config(context='nhssl.resources.Project',
             #renderer='nhssl:templates/project.pt',permission='edit')
#def project(context,request):
    #logged_in = authenticated_userid(request)
    #main = get_renderer('../templates/master.pt').implementation()
    #schema = ProjectEditSchema()
    #projectform = Form(schema, buttons=('submit',), use_ajax=True)
    #if 'service' in request.params:
        #try:
            #controls = request.POST.items()
            #captured = projectform.validate(controls)
        #except deform.ValidationFailure, e:
            #projectform = e.render()
            #return {'red': '','main': main, 'form': projectform, 'content': '','logged_in': logged_in,'name': 'Edit Project'}
        #if ('delete' in request.params) and (request.params['delete'] == "true"):
            #del context.__parent__[context.service]
            #return {'red': 'settings/',"main": main,'name': 'Redirecting...', 'form': '',"content": "Deleted this project","logged_in": logged_in}
        #context.service = request.params['service']
        #return {'red': 'settings/', 'main': main, 'form': '', 'content': "Edited the Project", 'logged_in': logged_in, 'name': 'Redirecting...'}
    #appstruct = {'service': context.service}
    #projectform = projectform.render(appstruct=appstruct)
    #return {'red': '', 'main': main, 'form': projectform, 'content': '', 'logged_in': logged_in, 'name': 'Edit Project'}
