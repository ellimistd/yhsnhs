from pyramid.view import view_config
from pyramid.renderers import get_renderer
from nhssl.resources import Deadline
from nhssl.forms import DeadlineSchema, DeadlineEditSchema
import deform
import calendarstuff
from deform import Form
from pyramid.traversal import find_root
from pyramid.security import authenticated_userid

@view_config(context='nhssl.resources.DeadlineContainer', 
             renderer='nhssl:templates/deadlines.pt',
             permission='view')
def view_deadlines(context, request):
    logged_in = authenticated_userid(request)
    main = get_renderer('../templates/master.pt').implementation()
    return {'red':'',
            'main':main, 
            'content':"", 
            'logged_in':logged_in,
            'name':'Deadlines'}
    
@view_config(context='nhssl.resources.Deadline',
             renderer='nhssl:templates/deadline.pt',
             permission='view')
def view_deadline(context,request):
    logged_in = authenticated_userid(request)
    main = get_renderer('../templates/master.pt').implementation()
    return {'red':'',
            'main':main, 
            'content':"",
            'logged_in':logged_in,
            'name':'Deadline'}
  
@view_config(name='add_deadline', 
             context='nhssl.resources.DeadlineContainer',
             renderer='nhssl:templates/form.pt',
             permission='edit')
def add_deadline(context, request):
    logged_in = authenticated_userid(request)
    main = get_renderer('../templates/master.pt').implementation()
    schema = DeadlineSchema()
    deadlineform = Form(schema, buttons=('submit',),use_ajax=True)
    if 'dateDue' in request.params:
        try:
            controls = request.POST.items()
            captured = deadlineform.validate(controls)
        except deform.ValidationFailure, e:
            deadlineform = e.render()
            return {'red':'',
                    'main':main, 
                    'form':deadlineform, 
                    'content':'',
                    'logged_in':logged_in,
                    'name':'Add Deadline'}
        dateDue = calendarstuff.datetime_from_str(request.params['dateDue'])
        hours = request.params['hours']
        sponsored = request.params['sponsored']
        appliedClass = request.params['appliedClass']
        context.count += 1
        deadline = Deadline(dateDue,hours,sponsored,appliedClass,context.count)
        deadline.__parent__ = context
        context[str(context.count)] = deadline
        find_root(context)['activityLogs'].deadline_creation(find_root(request.context)["users"][logged_in],deadline,request.application_url)
        return {'red':'deadlines/',
                'main':main,
                'form':'',
                'content':"Added a Deadline",
                'logged_in':logged_in,
                'name':'Redirecting...'}
    deadlineform = deadlineform.render()
    return {'red':'',
            'main':main, 
            'form':deadlineform, 
            'content':'',
            'logged_in':logged_in,
            'name':'Add Deadline'}

@view_config(name='edit',
             context='nhssl.resources.Deadline',
             renderer='nhssl:templates/form.pt',
             permission='edit')
def edit_deadline(context,request):
    logged_in = authenticated_userid(request)
    main = get_renderer('../templates/master.pt').implementation()
    schema = DeadlineEditSchema()
    deadlineform = Form(schema, buttons=('submit',),use_ajax=True)
    if 'dateDue' in request.params:
        try:
            controls = request.POST.items()
            captured = deadlineform.validate(controls)
        except deform.ValidationFailure, e:
            deadlineform = e.render()
            return {'red':'',
                    'main':main, 
                    'form':deadlineform, 
                    'content':'',
                    'logged_in':logged_in,
                    'name':'Edit Deadline'}
        if ('delete' in request.params) and (request.params['delete'] == "true"):
            activityLog = find_root(context)['activityLogs']
            activityLog.deadline_deletion(find_root(request.context)["users"][logged_in],context,request.application_url)
            del context.__parent__[str(context.ID)]
            return {'red':'deadlines/',
                    'main':main,
                    'name':'Redirecting...', 
                    'form':'',
                    'content':"Deleted this deadline",
                    'logged_in':logged_in}
        dateDue = calendarstuff.datetime_from_str(request.params['dateDue'])
        context.hours = request.params['hours']
        context.sponsored = request.params['sponsored']
        context.appliedClass = request.params['appliedClass']
        activityLog=find_root(context)['activityLogs']
        activityLog.deadline_edit(find_root(request.context)["users"][logged_in],context,request.application_url)
        return {'red':'deadlines/',
                'main':main,
                'form':'',
                'content':"Edited the Deadline",
                'logged_in':logged_in,
                'name':'Redirecting...'}
    appstruct = {'dateDue':context.dateDue,
                 'hours':context.hours,
                 'sponsored':context.sponsored,
                 'appliedClass':context.appliedClass}
    deadlineform = deadlineform.render(appstruct=appstruct)
    return {'red':'',
            'main':main, 
            'form':deadlineform, 
            'content':'',
            'logged_in':logged_in,
            'name':'Edit Deadline'}
