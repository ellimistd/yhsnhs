from pyramid.view import view_config
from pyramid.renderers import get_renderer
from nhssl.resources import NHSSL, ServiceLog
from pyramid.url import resource_url
from pyramid.security import authenticated_userid
from pyramid.traversal import find_root
from datetime import datetime
import calendarstuff

@view_config(context='nhssl.resources.ServiceLogContainer', 
             renderer='nhssl:templates/servicelogs.pt',
             permission='view')
def view_servicelogs(context, request):
    logged_in = authenticated_userid(request)
    main = get_renderer('../templates/master.pt').implementation()
    isadmin = find_root(context)['users'][logged_in].isAdvisor \
     or find_root(context)['users'][logged_in].isOfficer
    deadlines = find_root(context)["deadlines"]
    nextsdl = ''
    nextjdl = ''
    contextlist = []
    if not deadlines:
        for servicelog in context.values():
            contextlist.append((servicelog,
                                True,
                                True,
                                servicelog.unverified_hours(),
                                servicelog.flagged_hours(),))
    
    else:
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
        for servicelog in context.values():  #servlog = (obj, bool, bool, #, #)
            if calendarstuff.class_from_year(servicelog.user.gradYear) == "Junior":
                if nextjdl:
                    contextlist.append((servicelog, 
                               float(servicelog.user.hours)>=float(nextjdl.hours), #bool
                               float(servicelog.user.sponsored)>=float(nextjdl.hours), #bool
                               servicelog.unverified_hours(),
                               servicelog.flagged_hours()))
                else:
                    contextlist.append((servicelog,
                                True,
                                True,
                                servicelog.unverified_hours(),
                                servicelog.flagged_hours(),))
            elif calendarstuff.class_from_year(servicelog.user.gradYear) == "Senior":
                if nextsdl:
                    contextlist.append((servicelog,
                               float(servicelog.user.hours)>=float(nextsdl.hours),
                               float(servicelog.user.sponsored)>=float(nextsdl.sponsored),
                               servicelog.unverified_hours(),
                               servicelog.flagged_hours()))
                else:
                    contextlist.append((servicelog,
                                True,
                                True,
                                servicelog.unverified_hours(),
                                servicelog.flagged_hours(),))
    return {'red':'',
            'main':main, 
            'content':context,
            'logged_in':logged_in,
            'name':'Service Logs',
            'isadmin':isadmin,
            'contentlist':contextlist,}

    
@view_config(context='nhssl.resources.ServiceLogContainer', 
             renderer='nhssl:templates/unverified.pt',
             permission='verify',
             name='unverified')
def unverified(context, request):
    logged_in = authenticated_userid(request)
    currentuser = find_root(request.context)["users"][logged_in]
    app = find_root(context)
    if currentuser.isOfficer:
        if "action" in request.params:
            for event in request.params.keys():
                if not event in ['action','comment']:
                    eventinfo = event.split("-")
                    event = context[eventinfo[1]][eventinfo[0]]
                    if request.params["action"] == "deactivate":
                        if event.verified == "Verified":
                            event.user.hours -= float(event.hours)
                            if event.eventType == "Sponsored":
                                event.user.sponsored -= float(event.hours)
                        event.verified = "Rejected/Recanted"
                        app['activityLogs'].event_deactivation(currentuser,event,request.application_url)
                    elif request.params["action"] == "verify":
                        if not event.verified == "Verified":
                            event.user.hours += float(event.hours)
                            if event.eventType == "Sponsored":
                                event.user.sponsored += float(event.hours)
                        event.verified = "Verified"
                        app['activityLogs'].event_verification(currentuser,event,request.application_url)
                    elif request.params["action"] == "flag":
                        if event.verified == "Verified":
                            event.user.hours -= float(event.hours)
                            if event.eventType == "Sponsored":
                                event.user.sponsored -= float(event.hours)
                        event.verified = "Flagged"
                        find_root(context)['activityLogs'].event_flagging(currentuser,event,request.application_url)
                    elif request.params["action"] == "unverify":
                        if event.verified == "Verified":
                            event.user.hours -= float(event.hours)
                            if event.eventType == "Sponsored":
                                event.user.sponsored -= float(event.hours)
                        event.verified = "Unverified"
                        find_root(context)['activityLogs'].event_unverification(currentuser,event,request.application_url)
                    if request.params["comment"]:
                        if event.comment:
                            event.comment += " "+request.params['comment']
                        else:
                            event.comment = request.params['comment']
    main = get_renderer('../templates/master.pt').implementation()
    isadmin = find_root(context)['users'][logged_in].isOfficer
    indEvents = []
    sponsEvents = []
    deactivatedEvents = []
    for log in context.values():
        for event in log.values():
            if event.verified in ["Unverified","Flagged"]: 
                if event.eventType == "Sponsored":
                    sponsEvents.append(event)
                elif event.eventType == "Independent":
                    indEvents.append(event)
            elif event.verified == 'Rejected/Recanted':
                deactivatedEvents.append(event)
    indEvents.sort(key=lambda event: event.completionDate)
    sponsEvents.sort(key=lambda event: event.completionDate)
    return {'red':'',
            'main':main, 
            'content':{'ind':indEvents, 
                       'spons':sponsEvents,
                       'deact':deactivatedEvents},
            'logged_in':logged_in,
            'name':'Unverified Events',
            'isadmin':isadmin,}
                        
                        
@view_config(context='nhssl.resources.ServiceLog',
             renderer='nhssl:templates/servicelog.pt',
             permission='view')
def view_servicelog(context,request):
    logged_in = authenticated_userid(request)
    currentuser = find_root(request.context)["users"][logged_in]
    main = get_renderer('../templates/master.pt').implementation()
    app = find_root(request.context)
    if currentuser.isOfficer:
        if "action" in request.params:
            for ID in request.params.keys():
                if not ID in ['action','comment','note']:
                    event = context[ID]
                    if request.params["action"] == "delete":
                        if event.verified == "Verified":
                            event.user.hours -= float(event.hours)
                            if event.eventType == "Sponsored":
                                event.user.sponsored -= float(event.hours)
                        app['activityLogs'].event_deactivation(currentuser,event,request.application_url)
                        del event.__parent__[str(event.ID)]
                    elif request.params["action"] == "verify":
                        if not event.verified == "Verified":
                            event.user.hours += float(event.hours)
                            if event.eventType == "Sponsored":
                                event.user.sponsored += float(event.hours)
                        event.verified = "Verified"
                        app['activityLogs'].event_verification(currentuser,event,request.application_url)
                    elif request.params["action"] == "flag":
                        if event.verified == "Verified":
                            event.user.hours -= float(event.hours)
                            if event.eventType == "Sponsored":
                                event.user.sponsored -= float(event.hours)
                        event.verified = "Flagged"
                        find_root(context)['activityLogs'].event_flagging(currentuser,event,request.application_url)
                    elif request.params["action"] == "unverify":
                        if event.verified == "Verified":
                            event.user.hours -= float(event.hours)
                            if event.eventType == "Sponsored":
                                event.user.sponsored -= float(event.hours)
                        event.verified = "Unverified"
                        find_root(context)['activityLogs'].event_unverification(currentuser,event,request.application_url)
                    if request.params["comment"]:
                        if event.comment:
                            event.comment += " "+request.params['comment']
                        else:
                            event.comment = request.params['comment']
    permission=True
    red=''
    if not logged_in == context.user.username:
        if not find_root(context)['users'][logged_in].isAdvisor and not find_root(context)['users'][logged_in].isOfficer:
            permission=False
            red = 'serviceLogs'
    userclass = calendarstuff.class_from_year(context.user.gradYear)
    deadlines = find_root(context)["deadlines"]
    now = datetime.now()
    return {'red':red,
             'main':main,
             'content':context,
             'logged_in':logged_in,
             'name':'Service Logs',
             'isallowed':permission,
             'deadlines':deadlines}

def sumlisttuplelist(listtuplelist,index):
    sum = 0
    for tuplelist in listtuplelist:
        tlist = tuplelist[index]
        for event in tlist:
            sum += float(event.hours)
    return sum
