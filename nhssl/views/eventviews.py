from pyramid.view import view_config
from pyramid.renderers import get_renderer
from nhssl.forms import IndependentEventSchema, VerifyEventSchema, AdvisorVerifyEventSchema, IndependentEventEditSchema
from nhssl.resources import NHSSL, Event
import calendarstuff
import colander
import deform
from deform import Form
from pyramid.security import authenticated_userid
from pyramid.traversal import find_root
import datetime

@view_config(name='add_independent_event',
             context='nhssl.resources.ServiceLog', 
             renderer='nhssl:templates/form.pt',
             permission='view')
def add_independent_event(context,request):
    logged_in = authenticated_userid(request)
    main = get_renderer('../templates/master.pt').implementation()
    schema = IndependentEventSchema()
    eventform = Form(schema, buttons=('submit',))
    if 'description' in request.params:
        try:
            controls = request.POST.items()
            captured = eventform.validate(controls)
        except deform.ValidationFailure, e:
            eventform = e.render()
            return {'red':'',
                    'main':main, 
                    'form':eventform, 
                    'content':'',
                    'logged_in':logged_in,
                    'name':'Add Independent Event'}
        completionDate = calendarstuff.datetime_from_str(request.params['completionDate'])
        hours = request.params['hours']
        description = request.params['description']
        taskDescription = request.params['taskDescription']
        contact = request.params['contact']
        contactInfo = request.params['contactInfo']
        affects = request.params['affects']
        context.eventcount += 1
        user = context.user
        event = Event("Independent",
                      completionDate,
                      hours,
                      description,
                      taskDescription,
                      contact,contactInfo,
                      user,
                      context.eventcount,
                      affects=affects)
        event.__parent__ = context
        context[str(context.eventcount)]=event
        activitylog=find_root(context)['activityLogs']
        activitylog.event_creation(find_root(request.context)["users"][logged_in],event,request.application_url)
        return {'red':'serviceLogs/'+context.user.username,
                'main':main,
                'form':'',
                'content':"Added independent event for "+description,
                'logged_in':logged_in,
                'name':'Redirecting...'}
    eventform = eventform.render()
    return {'red':'',
            'main':main, 
            'form':eventform, 
            'content':'',
            'logged_in':logged_in,
            'name':'Add Independent Event'}
   
 
@view_config(name='add_sponsored_event', 
             context='nhssl.resources.ServiceLog', 
             renderer='nhssl:templates/form.pt',
             permission='view')    
def add_sponsored_event(context,request):
    logged_in = authenticated_userid(request)
    main = get_renderer('../templates/master.pt').implementation()
    projectList = find_root(context)["settings"].projects
    projectTupleList = []
    for project in projectList:
        projectTupleList.append((project,project))
    projectTupleTuple=tuple(projectTupleList)   #sorry about this.  It was more fun than a ListList
    class SponsoredEventSchema(colander.MappingSchema):
        completionDate = colander.SchemaNode(colander.Date(),title="Completion Date (YYYY-MM-DD): ")
        hours = colander.SchemaNode(colander.Float(), title="Number of Hours: ")
        description = colander.SchemaNode(
                colander.String(),
                validator=colander.OneOf([x[0] for x in projectTupleTuple]),
                widget=deform.widget.RadioChoiceWidget(values=projectTupleTuple),
                title='Project',
                description='Select a Project')
        taskDescription = colander.SchemaNode(
                    colander.String(), title="Description: ",
                    widget=deform.widget.TextAreaWidget(rows=5, cols=40),
                    description='Enter some text')
        contact = colander.SchemaNode(colander.String(),title="Contact Name: ")
        contactInfo = colander.SchemaNode(colander.String(),title="Contact Info: ")
    schema=SponsoredEventSchema()
    eventform = Form(schema, buttons=('submit',))
    if 'taskDescription' in request.params:
        try:
            controls = request.POST.items()
            captured = eventform.validate(controls)
        except deform.ValidationFailure, e:
            eventform = e.render()
            return {'red':'',
                    'main':main, 
                    'form':eventform, 
                    'content':'',
                    'logged_in':logged_in,
                    'name':'Add Sponsored Event'}
        completionDate = calendarstuff.datetime_from_str(request.params['completionDate'])
        hours = request.params['hours']
        description = request.params['deformField3']
        taskDescription = request.params['taskDescription']
        contact = request.params['contact']
        contactInfo = request.params['contactInfo']
        context.eventcount += 1
        user = context.user
        event = Event("Sponsored",completionDate,hours,description,taskDescription,contact,contactInfo,user,context.eventcount)
        event.__parent__ = context
        context[str(context.eventcount)] = event
        activitylog = find_root(context)['activityLogs']
        activitylog.event_creation(find_root(request.context)["users"][logged_in],event,request.application_url)
        return {'red':'serviceLogs/'+context.user.username,
                'main':main,
                'form':'',
                'content':"Added sponsored event for "+description,
                'logged_in':logged_in,
                'name':'Redirecting...'}
    eventform = eventform.render()
    return {'red':'',
            'main':main, 
            'form':eventform, 
            'content':'',
            'logged_in':logged_in,
            'name':'Add Sponsored Event'}


@view_config(context='nhssl.resources.Event',
             renderer='nhssl:templates/event.pt',
             permission='view')
def view_event(context,request):
    logged_in = authenticated_userid(request)
    currentuser = find_root(request.context)["users"][logged_in]
    main = get_renderer('../templates/master.pt').implementation()
    activityLog = find_root(context)['activityLogs']
    if currentuser.isOfficer:
        choices = [("Unverified","Unverified"),
                      ("Verified","Verified"),
                      ("Flagged","Flag with Comment")]
        if currentuser.isAdvisor:
            choices.append(("Rejected/Recanted","Rejected/Recanted"))
        choices = tuple(choices)
        if currentuser.isAdvisor:
            schema = AdvisorVerifyEventSchema().bind(choices=choices,default=context.verified)
        else:
            schema = VerifyEventSchema().bind(choices=choices,default=context.verified)
        verifyform = Form(schema, buttons=('submit and go to the list of all unverified entries',
                                           'submit and stay on this page',
                                           'submit and go to student log'))
        if ('submit_and_stay_on_this_page' in request.params) or ('submit_and_go_to_student_log' in request.params) \
         or ('submit_and_go_to_the_list_of_all_unverified_entries' in request.params):
            try:
                controls = request.POST.items()
                captured = verifyform.validate(controls)
            except deform.ValidationFailure, e:
                verifyform = e.render()
                return {'red':'',
                        'main':main,
                        'form':verifyform,
                        'isOfficer':currentuser.isOfficer,
                        'isAdvisor':currentuser.isAdvisor,
                        'content':context,
                        'logged_in':logged_in,
                        'name':'View Event'}
            if request.params["verified"] != context.verified:
                if request.params["verified"] == "Flagged":
                    if context.verified == "Verified":
                        context.user.hours -= float(context.hours)
                    activityLog.event_flagging(find_root(request.context)["users"][logged_in],context,request.application_url)
                if request.params["verified"] == "Unverified":
                    if context.verified == "Verified":
                        context.user.hours -= float(context.hours)
                        if context.eventType == "Sponsored":
                            context.user.sponsored -= float(context.hours)
                        activityLog.event_unverification(find_root(request.context)["users"][logged_in],context,request.application_url)
                if request.params["verified"] == "Verified":
                    activityLog.event_verification(find_root(request.context)["users"][logged_in],context,request.application_url)
                    context.user.hours += float(context.hours)
                    if context.eventType == "Sponsored":
                        context.user.sponsored += float(context.hours)
                if request.params["verified"] == "Rejected/Recanted":
                    if context.verified == "Verified":
                                context.user.hours -= float(context.hours)
                                if context.eventType == "Sponsored":
                                    context.user.sponsored -= float(context.hours)
                    activityLog.event_deactivation(find_root(request.context)["users"][logged_in],context,request.application_url)
            context.verified = request.params["verified"]
            context.comment = request.params["comment"]
            if find_root(request.context)['users'][logged_in].isAdvisor:
                context.advisorNote = request.params["advisorNote"]
            if 'submit_and_go_to_the_list_of_all_unverified_entries' in request.params:
                return {'red':'serviceLogs/unverified',
                        'main':main,
                        'form':verifyform,
                        'isOfficer':currentuser.isOfficer,
                        'isAdvisor':currentuser.isAdvisor,
                        'content':context,
                        'logged_in':logged_in,
                        'name':'Redirecting...'}
            elif 'submit_and_go_to_student_log' in request.params:
                return {'red':'serviceLogs/'+context.user.username,
                        'main':main,
                        'form':verifyform,
                        'isOfficer':currentuser.isOfficer,
                        'isAdvisor':currentuser.isAdvisor,
                        'content':context,
                        'logged_in':logged_in,
                        'name':'Redirecting...'}
            elif 'submit_and_stay_on_this_page' in request.params:        
                appstruct = {'comment':context.comment,
                            'verified':context.verified,
                            'advisorNote':context.advisorNote}
                verifyform = verifyform.render(appstruct=appstruct)
                return {'red':'',
                        'main':main,
                        'form':verifyform,
                        'isOfficer':currentuser.isOfficer,
                        'isAdvisor':currentuser.isAdvisor,
                        'content':context,
                        'logged_in':logged_in,
                        'name':'View Event'}        
        appstruct = {'comment':context.comment,
                     'advisorNote':context.advisorNote,
                    'verified':context.verified}
        verifyform = verifyform.render(appstruct=appstruct)
        return {'red':'',
                'main':main,
                'form':verifyform,
                'isOfficer':currentuser.isOfficer,
                'isAdvisor':currentuser.isAdvisor,
                'content':context,
                'logged_in':logged_in,
                'name':'View Event'}
    return {'red':'',
            'main':main,
            'form':'',
            'isOfficer':currentuser.isOfficer,
            'isAdvisor':currentuser.isAdvisor,
            'content':context,
            'logged_in':logged_in,
            'name':'View Event'}
    
@view_config(name='reactivate',
             context='nhssl.resources.Event',
             renderer='nhssl:templates/event.pt',
             permission='verify')
def reactivate_event(context, request):
    app=find_root(context)
    logged_in = authenticated_userid(request)
    isloggedinuser = False
    currentuser = find_root(request.context)["users"][logged_in] 
    main = get_renderer('../templates/master.pt').implementation()
    if currentuser == context or currentuser.isAdvisor or currentuser.isOfficer:
        isloggedinuser = True 
    context.verified = 'Unverified'
    app['activityLogs'].event_reactivation(currentuser,context,request.application_url)
    return {'red':'serviceLogs/'+context.user.username+'/'+str(context.ID),
             'main':main,
             'content':'Event Reactivated',
             'logged_in':logged_in,
             'userself':isloggedinuser,
             'isOfficer':currentuser.isOfficer,
             'isAdvisor':currentuser.isAdvisor,
             'name':'Redirecting...'}

@view_config(name='delete',
             context='nhssl.resources.Event',
             renderer='nhssl:templates/form.pt',
             permission='edit')
def delete_event(context, request):
    logged_in = authenticated_userid(request)
    app = find_root(context)
    currentuser = app["users"][logged_in]
    main = get_renderer('../templates/master.pt').implementation()
    schema = colander.MappingSchema()
    form = ''
    app['activityLogs'].event_deletion(currentuser,context,request.application_url)
    del app['serviceLogs'][context.user.username][str(context.ID)]
    content = 'Redirecting...'
    red = 'users/'
    return {'red':red,
             'main':main,
             'form':form,
             'content':content,
             'logged_in':logged_in,
             'name':'Delete Event'}
    
@view_config(context='nhssl.resources.Event',
             renderer='nhssl:templates/form.pt', 
             name='edit',
             permission='view')
def edit_event(context,request):
    logged_in = authenticated_userid(request)
    main = get_renderer('../templates/master.pt').implementation()
    activityLog = find_root(context)['activityLogs']
    user = context.user
    if not logged_in == context.user.username:
        if not (find_root(context)['users'][logged_in].isAdvisor or find_root(context)['users'][logged_in].isOfficer): 
            return {'red':'/serviceLogs/'+context.user.username+'/'+str(context.ID),
                    'main':main,
                    'form':"", 
                    'content':'Permission Denied',
                    'logged_in':logged_in,
                    'name':"Redirecting..."}
    if context.verified == "Verified":
        if not (find_root(context)['users'][logged_in].isAdvisor or find_root(context)['users'][logged_in].isOfficer): 
            return {'red':'/serviceLogs/'+context.user.username+'/'+str(context.ID),
                    'main':main,
                    'form':"", 
                    'content':'Permission Denied',
                    'logged_in':logged_in,
                    'name':"Redirecting..."}
    if context.eventType == "Independent":
        schema = IndependentEventEditSchema()
        eventform = Form(schema, buttons=('submit',))
        if 'description' in request.params:
            try:
                controls = request.POST.items()
                captured = eventform.validate(controls)
            except deform.ValidationFailure, e:
                eventform = e.render()
                return {'red':'',
                        'main':main, 
                        'form':eventform, 
                        'content':'',
                        'logged_in':logged_in,
                        'name':'Editing Independent Event'}
            context.completionDate = calendarstuff.datetime_from_str(request.params['completionDate'])
            context.eventType = request.params['eventType']
            if context.hours != request.params['hours']:
                if context.verified == "Verified": 
                    deltahours = float(request.params['hours'])-float(context.hours)
                    user.hours += deltahours   
            context.hours = request.params['hours']
            context.description = request.params['description']
            context.taskDescription = request.params['taskDescription']
            context.contact = request.params['contact']
            context.contactInfo = request.params['contactInfo']
            activityLog.event_edit(find_root(request.context)["users"][logged_in],context,request.application_url)
            return {'red':'serviceLogs/'+context.user.username,
                    'main':main,
                    'form':'',
                    'content':'Edited the event for '+context.description,
                    'logged_in':logged_in,
                    'name':'Redirecting...'}
        appstruct={'completionDate':context.completionDate,
                   'hours':context.hours,
                   'description':context.description,
                   'taskDescription':context.taskDescription,
                   'contact':context.contact,
                   'contactInfo':context.contactInfo,
                   'eventType':context.eventType}
        eventform = eventform.render(appstruct=appstruct)
        return {'red':'',
                'main':main, 
                'form':eventform, 
                'content':'',
                'logged_in':logged_in,
                'name':'Editing Independent Event'}
        
    elif context.eventType == "Sponsored":
        projectList = find_root(context)["settings"].projects
        projectTupleList = []
        for project in projectList:
            projectTupleList.append((project,project))
        projectTupleTuple=tuple(projectTupleList) 
        class SponsoredEventSchema(colander.MappingSchema):
            eventType = colander.SchemaNode(
                        colander.String(),
                        title = "Event Type:",
                        widget=deform.widget.SelectWidget(values=(("Independent","Independent"),
                                                                  ("Sponsored","Sponsored")), 
                                                                  size=2))
            completionDate = colander.SchemaNode(colander.Date(),title="Completion Date (YYYY-MM-DD): ")
            hours = colander.SchemaNode(colander.Float(), title="Number of Hours: ")
            description = colander.SchemaNode(
                colander.String(),
                validator=colander.OneOf([x[0] for x in projectTupleTuple]),
                widget=deform.widget.RadioChoiceWidget(values=projectTupleTuple),
                title='Project',
                description='Select a Project')
            taskDescription = colander.SchemaNode(
                        colander.String(), title="Description: ",
                        widget=deform.widget.TextAreaWidget(rows=5, cols=40),
                        description='Enter some text')
            contact = colander.SchemaNode(colander.String(),title="Contact Name: ")
            contactInfo = colander.SchemaNode(colander.String(),title="Contact Info: ") 
        schema=SponsoredEventSchema()
        eventform = Form(schema, buttons=('submit',))
        if 'taskDescription' in request.params:
            try:
                controls = request.POST.items()
                captured = eventform.validate(controls)
            except deform.ValidationFailure, e:
                eventform = e.render()
                return {'red':'',
                        'main':main, 
                        'form':eventform, 
                        'content':'',
                        'logged_in':logged_in,
                        'name':'Attempting to Edit Event'}
            context.completionDate = calendarstuff.datetime_from_str(request.params['completionDate'])
            if context.hours != request.params['hours']:
                if context.verified == "Verified": 
                    deltahours = float(request.params['hours'])-float(context.hours)
                    user.hours += deltahours    
            context.hours = request.params['hours']
            #context.description = request.params['description']
            context.taskDescription = request.params['taskDescription']
            context.contact = request.params['contact']
            context.contactInfo = request.params['contactInfo']
            activitylog = find_root(context)['activityLogs']
            activitylog.event_edit(find_root(request.context)["users"][logged_in],context,request.application_url)
            return {'red':'serviceLogs/'+context.user.username,
                    'main':main,
                    'form':'',
                    'content':'Edited the event for '+context.description,
                    'logged_in':logged_in,
                    'name':'Redirecting...'}
        appstruct={'completionDate':context.completionDate,
                   'hours':context.hours,
                   'description':context.description,
                   'taskDescription':context.taskDescription,
                   'contact':context.contact,
                   'contactInfo':context.contactInfo,
                   'eventType':context.eventType} 
        eventform = eventform.render(appstruct=appstruct)
        return {'red':'',
                'main':main, 
                'form':eventform, 
                'content':'',
                'logged_in':logged_in,
                'name':'Editing Sponsored Event'}

    return {'red':'',
            'main':main, 
            'form':'',
            'name':'Attempting to Edit Event', 
            'content':"Not independent <br\> neither a sponsored event <br\> you can't edit it.",
            'logged_in':logged_in}

