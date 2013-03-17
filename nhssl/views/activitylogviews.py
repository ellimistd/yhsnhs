from pyramid.view import view_config
from pyramid.renderers import get_renderer
from nhssl.resources import ActivityLog
from nhssl.forms import UserSchema, UserEditSchema#, DeleteyButton
import deform
from deform import Form
from pyramid.traversal import find_root
from pyramid.security import authenticated_userid


@view_config(context='nhssl.resources.ActivityLogContainer', 
             renderer='nhssl:templates/activitylogs.pt',
             permission='edit')
def view_activitylogs(context, request):
    logged_in = authenticated_userid(request)
    main = get_renderer('../templates/master.pt').implementation()
    logs = context.values()
    logs.sort(key=lambda date: date.date)
    return {'red':'',
            'main':main, 
            'content':"",
            'logs':logs,
            'logged_in':logged_in,
            'name':'Activity Logs'}
    
@view_config(context='nhssl.resources.ActivityLog',
             renderer='nhssl:templates/activitylog.pt',
             permission='edit')
def view_activitylog(context,request):
    logged_in = authenticated_userid(request)
    main = get_renderer('../templates/master.pt').implementation()
    return {'red':'', 
            'main':main, 
            'content':"", 
            'logged_in':logged_in, 
            'name':'Activity Logs'}
    
@view_config(context='nhssl.resources.Activity',
             renderer='nhssl:templates/form.pt', 
             permission='edit')
def edit_activity(context,request):
    logged_in = authenticated_userid(request)
    main = get_renderer('../templates/master.pt').implementation()
    del context.__parent__[str(context.ID)]
    return {'red':'activityLogs/', 
            'main':main, 
            'form':'', 
            'content':"Viewed Activity Log", 
            'logged_in':logged_in, 
            'name':'Redirecting...'}
