from persistent import Persistent
from persistent.mapping import PersistentMapping
from pyramid.security import Allow
from pyramid.security import Everyone
import datetime


class User(Persistent):
    def __init__(self, username, password, studentId, firstName, lastName,
                 email, phone, gradYear, inductionYear, isstudent=True,
                 isofficer=False, isadvisor=False):
        super(User, self).__init__()
        self.username = username
        self.password = password
        self.studentId = studentId
        self.firstName = firstName
        self.lastName = lastName
        self.email = email
        self.phone = phone
        self.gradYear = gradYear
        self.inductionYear = inductionYear
        self.isStudent = isstudent
        self.isOfficer = isofficer
        self.isAdvisor = isadvisor
        self.dues = False
        self.gpa = False
        self.firstMeeting = False
        self.secondMeeting = False
        self.thirdMeeting = False
        self.deactivated = False
        self.hours = 0
        self.sponsored = 0
        self.__name__ = None

    def __unicode__(self):
        return u"{0} [{1}]".format(self.username, self.lastName)

    def isComplete(self):
        return self.firstName and self.lastName and self.email and self.gradYear and self.inductionYear

class UserContainer(PersistentMapping):
    def __init__(self):
        super(UserContainer, self).__init__()
        self.__name__ = None


class Deadline(Persistent):
    def __init__(self, dateDue, hours, sponsored, appliedClass, ID):
        super(Deadline, self).__init__()
        self.dateDue = dateDue
        self.hours = hours
        self.sponsored = sponsored
        self.appliedClass = appliedClass
        self.ID = ID
        self.__name__ = None


class DeadlineContainer(PersistentMapping):
    def __init__(self):
        super(DeadlineContainer, self).__init__()
        self.count = 0
        self.__name__ = None


class Event(Persistent):
    def __init__(self, eventType, completionDate, hours, description,
                 taskDescription, contact, contactInfo, user, ID, affects=None):
        super(Event, self).__init__()
        self.deleted = False
        self.submitted = datetime.datetime.now()
        self.verified = u"Unverified"
        self.eventType = eventType
        self.completionDate = completionDate
        self.hours = hours
        self.description = description
        self.taskDescription = taskDescription
        self.contact = contact
        self.contactInfo = contactInfo
        self.user = user
        self.comment = ""
        self.advisorNote = ""
        self.ID = ID
        self.__name__ = None
        self.affects = affects

    def __unicode__(self):
        return "{0} Event on {1}".format(self.verified, self.completionDate)


class ServiceLog(PersistentMapping):
    def __init__(self, user):
        super(ServiceLog,self).__init__()
        self.user = user
        self.eventcount = 0
        self.__name__ = None

    def flagged_hours(self):
        flagged_hours = 0
        for event in self.values():
            if event.verified == 'Flagged':
                flagged_hours += float(event.hours)
        return flagged_hours
 
    def unverified_hours(self):
        unverified_hours = 0
        for event in self.values():
            if event.verified == "Unverified":
                unverified_hours += float(event.hours)
        return unverified_hours
             

            
class ServiceLogContainer(PersistentMapping):
    def __init__(self):
        super(ServiceLogContainer, self).__init__()
        self.__name__ = None
            
            
#class Project(Persistent):
    #def __init__(self, service):
        #super(Project, self).__init__()
        #self.__name__ = None
        #self.service = service
            
#class Settings(PersistentMapping):
    #def __init__(self):
        #super(Settings,self).__init__()
        #self.__name__ = None
        #self.maintext = "Welcome to the NHS Service Log webpage for Yorktown High School."

class Settings(Persistent):
    def __init__(self):
        super(Settings,self).__init__()
        self.__name__ = None
        self.maintext = "Welcome to the NHS Service Log webpage for Yorktown High School."
        self.projects = ["(not applicable)"]
        
class Activity(Persistent):
    def __init__(self, message, ID):
        super(Activity, self).__init__()
        self.time = datetime.datetime.time(datetime.datetime.now())
        self.message = message
        self.ID = ID
        self.__name__ = None


class ActivityLog(PersistentMapping):
    def __init__(self,date):
        super(ActivityLog, self).__init__()
        self.date = date
        self.activitycount = 0
        self.__name__ = None


class ActivityLogContainer(PersistentMapping):
    def __init__(self):
        super(ActivityLogContainer, self).__init__()
        self.__name__ = None
        today = str(datetime.date.today())
        starter  = ActivityLog(today)
        starter.__parent__ = self
        self[today] = starter

    def time_check(self):
        today = str(datetime.date.today())
        if not today in self:
            starter  = ActivityLog(today)
            starter.__parent__ = self
            self[today] = starter

    def user_deletion(self, actor, target,url):
        self.time_check()
        self[str(datetime.date.today())].activitycount += 1
        count = (self[str(datetime.date.today())].activitycount)
        message = "<a href="+url+"/users/"+actor.username+"> "+actor.firstName+" "+actor.lastName+"</a> deleted "+target.firstName+" "+target.lastName
        activity = Activity(message, count)
        activity.__parent__ = self[str(datetime.date.today())]
        self[str(datetime.date.today())][str(count)] = activity
    def user_deactivation(self, actor, target,url):
        self.time_check()
        self[str(datetime.date.today())].activitycount += 1
        count = (self[str(datetime.date.today())].activitycount)
        message = "<a href="+url+"/users/"+actor.username+"> "+actor.firstName+" "+actor.lastName+"</a> deactivated the user <a href="+url+"/users/"+target.username+"> "+target.firstName+" "+target.lastName+"</a>"
        activity = Activity(message, count)
        activity.__parent__ = self[str(datetime.date.today())]
        self[str(datetime.date.today())][str(count)] = activity
    def user_reactivation(self, actor, target,url):
        self.time_check()
        self[str(datetime.date.today())].activitycount += 1
        count = (self[str(datetime.date.today())].activitycount)
        message = "<a href="+url+"/users/"+actor.username+"> "+actor.firstName+" "+actor.lastName+"</a> reactivated the user <a href="+url+"/users/"+target.username+"> "+target.firstName+" "+target.lastName+"</a>"
        activity = Activity(message, count)
        activity.__parent__ = self[str(datetime.date.today())]
        self[str(datetime.date.today())][str(count)] = activity
    def user_creation(self, actor, target,url):
        self.time_check()
        self[str(datetime.date.today())].activitycount += 1
        count = (self[str(datetime.date.today())].activitycount)
        message = "<a href="+url+"/users/"+actor.username+"> "+actor.firstName+" "+actor.lastName+"</a> created the user <a href="+url+"/users/"+target.username+"> "+target.firstName+" "+target.lastName+"</a>"
        activity = Activity(message, count)
        activity.__parent__ = self[str(datetime.date.today())]
        self[str(datetime.date.today())][str(count)] = activity
    def user_registration(self,actor,url):
        self.time_check()
        self[str(datetime.date.today())].activitycount += 1
        count = (self[str(datetime.date.today())].activitycount)
        message = "<a href="+url+"/users/"+actor.username+"> "+actor.firstName+" "+actor.lastName+"</a> registered as a new user"
        activity = Activity(message, count)
        activity.__parent__ = self[str(datetime.date.today())]
        self[str(datetime.date.today())][str(count)] = activity
    def user_edit(self, actor, target,url):
        self.time_check()
        self[str(datetime.date.today())].activitycount += 1
        count = (self[str(datetime.date.today())].activitycount)
        message = "<a href="+url+"/users/"+actor.username+"> "+actor.firstName+" "+actor.lastName+"</a> edited the information of <a href="+url+"/users/"+target.username+"> "+target.firstName+" "+target.lastName+"</a>"
        activity = Activity(message, count)
        activity.__parent__ = self[str(datetime.date.today())]
        self[str(datetime.date.today())][str(count)] = activity
    def event_creation(self, actor, target,url):
        self.time_check()
        self[str(datetime.date.today())].activitycount += 1
        count = (self[str(datetime.date.today())].activitycount)
        message = "<a href="+url+"/users/"+actor.username+"> "+actor.firstName+" "+actor.lastName+"</a> created the event <a href="+url+"/serviceLogs/"+target.__parent__.user.username+"/"+str(target.ID)+"> "+target.description+" ("+target.hours+" hours)</a>"
        activity = Activity(message, count)
        activity.__parent__ = self[str(datetime.date.today())]
        self[str(datetime.date.today())][str(count)] = activity
    def event_edit(self, actor, target,url):
        self.time_check()
        self[str(datetime.date.today())].activitycount += 1
        count = (self[str(datetime.date.today())].activitycount)
        message = "<a href="+url+"/users/"+actor.username+"> "+actor.firstName+" "+actor.lastName+"</a> edited the event <a href="+url+"/serviceLogs/"+target.__parent__.user.username+"/"+str(target.ID)+"> "+target.description+"</a>"
        activity = Activity(message, count)
        activity.__parent__ = self[str(datetime.date.today())]
        self[str(datetime.date.today())][str(count)] = activity
    def event_deletion(self, actor, target,url):
        self.time_check()
        self[str(datetime.date.today())].activitycount += 1
        count = (self[str(datetime.date.today())].activitycount)
        message = "<a href="+url+"/users/"+actor.username+"> "+actor.firstName+" "+actor.lastName+"</a> deleted the event "+target.description
        activity = Activity(message, count)
        activity.__parent__ = self[str(datetime.date.today())]
        self[str(datetime.date.today())][str(count)] = activity
    def event_verification(self, actor, target,url):
        self.time_check()
        self[str(datetime.date.today())].activitycount += 1
        count = (self[str(datetime.date.today())].activitycount)
        message = "<a href="+url+"/users/"+actor.username+"> "+actor.firstName+" "+actor.lastName+"</a> verified the event <a href="+url+"/serviceLogs/"+target.__parent__.user.username+"/"+str(target.ID)+"> "+target.description+"</a>"
        activity = Activity(message, count)
        activity.__parent__ = self[str(datetime.date.today())]
        self[str(datetime.date.today())][str(count)] = activity
    def event_deactivation(self, actor, target,url):
        self.time_check()
        self[str(datetime.date.today())].activitycount += 1
        count = (self[str(datetime.date.today())].activitycount)
        message = "<a href="+url+"/users/"+actor.username+"> "+actor.firstName+" "+actor.lastName+"</a> deactivated the event <a href="+url+"/serviceLogs/"+target.__parent__.user.username+"/"+str(target.ID)+"> "+target.description+"</a>"
        activity = Activity(message, count)
        activity.__parent__ = self[str(datetime.date.today())]
        self[str(datetime.date.today())][str(count)] = activity
    def event_reactivation(self, actor, target,url):
        self.time_check()
        self[str(datetime.date.today())].activitycount += 1
        count = (self[str(datetime.date.today())].activitycount)
        message = "<a href="+url+"/users/"+actor.username+"> "+actor.firstName+" "+actor.lastName+"</a> reactivated the event <a href="+url+"/serviceLogs/"+target.__parent__.user.username+"/"+str(target.ID)+"> "+target.description+"</a>"
        activity = Activity(message, count)
        activity.__parent__ = self[str(datetime.date.today())]
        self[str(datetime.date.today())][str(count)] = activity
    def event_unverification(self, actor, target,url):
        self.time_check()
        self[str(datetime.date.today())].activitycount += 1
        count = (self[str(datetime.date.today())].activitycount)
        message = "<a href="+url+"/users/"+actor.username+"> "+actor.firstName+" "+actor.lastName+"</a> unverified the event <a href="+url+"/serviceLogs/"+target.__parent__.user.username+"/"+str(target.ID)+"> "+target.description+"</a>"
        activity = Activity(message, count)
        activity.__parent__ = self[str(datetime.date.today())]
        self[str(datetime.date.today())][str(count)] = activity
    def event_flagging(self, actor, target,url):
        self.time_check()
        self[str(datetime.date.today())].activitycount += 1
        count = (self[str(datetime.date.today())].activitycount)
        message = "<a href="+url+"/users/"+actor.username+"> "+actor.firstName+" "+actor.lastName+"</a> flagged the event <a href="+url+"/serviceLogs/"+target.__parent__.user.username+"/"+str(target.ID)+"> "+target.description+"</a>"
        activity = Activity(message, count)
        activity.__parent__ = self[str(datetime.date.today())]
        self[str(datetime.date.today())][str(count)] = activity
    def settings_change(self, actor,url):
        self.time_check()
        self[str(datetime.date.today())].activitycount += 1
        count = (self[str(datetime.date.today())].activitycount)
        message = "<a href="+url+"/users/"+actor.username+"> "+actor.firstName+" "+actor.lastName+"</a> changed the site settings"
        activity = Activity(message, count)
        activity.__parent__ = self[str(datetime.date.today())]
        self[str(datetime.date.today())][str(count)] = activity
    def deadline_creation(self, actor, target,url):
        self.time_check()
        self[str(datetime.date.today())].activitycount += 1
        count = (self[str(datetime.date.today())].activitycount)
        message = "<a href="+url+"/users/"+actor.username+"> "+actor.firstName+" "+actor.lastName+"</a> created a deadline for <a href="+url+"/deadlines/"+str(target.ID)+"> "+str(target.dateDue)+"</a>"
        activity = Activity(message, count)
        activity.__parent__ = self[str(datetime.date.today())]
        self[str(datetime.date.today())][str(count)] = activity
    def deadline_edit(self, actor, target,url):
        self.time_check()
        self[str(datetime.date.today())].activitycount += 1
        count = (self[str(datetime.date.today())].activitycount)
        message = "<a href="+url+"/users/"+actor.username+"> "+actor.firstName+" "+actor.lastName+"</a> edited a deadline for <a href="+url+"/deadlines/"+str(target.ID)+"> "+str(target.dateDue)+"</a>"
        activity = Activity(message, count)
        activity.__parent__ = self[str(datetime.date.today())]
        self[str(datetime.date.today())][str(count)] = activity
    def deadline_deletion(self, actor, target,url):
        self.time_check()
        self[str(datetime.date.today())].activitycount += 1
        count = (self[str(datetime.date.today())].activitycount)
        message = "<a href="+url+"/users/"+actor.username+"> "+actor.firstName+" "+actor.lastName+"</a> deleted a deadline for "+str(target.dateDue)
        activity = Activity(message, count)
        activity.__parent__ = self[str(datetime.date.today())]
        self[str(datetime.date.today())][str(count)] = activity
    
                   
class NHSSL(PersistentMapping):
    __acl__ = [ (Allow, 'group:registered', 'view'),
                (Allow, 'group:student', 'view'),
                (Allow, 'group:officers', 'verify'),
                (Allow, 'group:advisors', 'edit') ]
    __parent__ = __name__ = None
    def __init__(self):
        super(NHSSL,self).__init__()
        
        users = UserContainer()
        users.__parent__ = self
        self['users']=users
        
        deadlines = DeadlineContainer()
        deadlines.__parent__ = self
        self['deadlines']=deadlines
        
        serviceLogs = ServiceLogContainer()
        serviceLogs.__parent__ = self
        self['serviceLogs']=serviceLogs
        
        settings = Settings()
        settings.__parent__=self
        self['settings']=settings
        
        activityLogs = ActivityLogContainer()
        activityLogs.__parent__ = self
        self['activityLogs']=activityLogs
        
def appmaker(zodb_root):
    if not 'app_root' in zodb_root:
        app_root = NHSSL()
        zodb_root['app_root'] = app_root
        import transaction
        transaction.commit()
    return zodb_root['app_root']
    
