import colander
import deform
from deform import form

@colander.deferred
def deferred_select_widget(node, kw):
    choices = kw.get('choices')
    return deform.widget.SelectWidget(values=choices)
@colander.deferred
def deferred_checkbox_widget(node, kw):
    choices = kw.get('choices')
    return deform.widget.CheckboxChoiceWidget(values=choices)
@colander.deferred
def deferred_default(node, kw):
    return kw['default']

class UserSchema(colander.MappingSchema): 
    username = colander.SchemaNode(colander.String(),
                                   validator=colander.Regex("[a-zA-Z0-9]{0,15}"),
                                   title="Username: ")
    password = colander.SchemaNode(
                colander.String(),
                validator=colander.Length(min=5),
                title="Password (at least 5 characters): ",
                widget=deform.widget.CheckedPasswordWidget(size=20),
                description='Type your password and confirm it')
    studentId = colander.SchemaNode(colander.Integer(), title="Student ID: ")
    firstName = colander.SchemaNode(colander.String(), title="First Name: ")
    lastName = colander.SchemaNode(colander.String(), title="Last Name: ")
    email = colander.SchemaNode(colander.String(), title="Email Address: ",
                                validator=colander.Email())
    phone = colander.SchemaNode(colander.String(),
                                widget=deform.widget.TextInputWidget(
                                mask='999-999-9999'
                                ), title="Phone Number: ")
    gradYear = colander.SchemaNode(colander.Integer(),
                                   title="Graduation Year: ")
    inductionYear = colander.SchemaNode(colander.Integer(),
                                        title="Induction Year: ")


class OwnPasswordSchema(colander.MappingSchema):
    old = colander.SchemaNode(
        colander.String(),
        validator=colander.Length(min=5, max=100),
        title = "Enter Old Password: ",
    widget=deform.widget.PasswordWidget(size=20),
        description='Enter a password')
    new = colander.SchemaNode(
        colander.String(),
        validator=colander.Length(min=5),
        title = "New Password (at least 5 characters): ",
        widget=deform.widget.CheckedPasswordWidget(size=20),
        description='Type your password and confirm it')

        
class UserPasswordSchema(colander.MappingSchema):
    new = colander.SchemaNode(
        colander.String(),
        validator=colander.Length(min=5),
        title = "New Password (at least 5 characters): ",
        widget=deform.widget.CheckedPasswordWidget(size=20),
        description='Type your password and confirm it')

   
class UserEditSchema(colander.Schema):
    studentId = colander.SchemaNode(colander.Integer(),
                                    title="Student ID: ")
    firstName = colander.SchemaNode(colander.String(),
                                    title="First Name: ")
    lastName = colander.SchemaNode(colander.String(),
                                   title="Last Name: ")
    email = colander.SchemaNode(colander.String(),
                                title="Email Address: ")
    phone = colander.SchemaNode(colander.String(), 
                                title="Phone Number: ")
    gradYear = colander.SchemaNode(colander.Integer(), 
                                   title="Graduation Year: ")
    inductionYear = colander.SchemaNode(colander.Integer(), 
                                        title="Induction Year: ")
    dues = colander.SchemaNode(
                colander.Boolean(),
                title='Paid Dues: ') 
    gpa = colander.SchemaNode(
                colander.Boolean(),
                title='Meets GPA Requirements: ') 
    firstMeeting = colander.SchemaNode(
                colander.Boolean(),
                title='Attended First Meeting: ') 
    secondMeeting = colander.SchemaNode(
                colander.Boolean(),
                title='Attended Second Meeting: ') 
    thirdMeeting = colander.SchemaNode(
                colander.Boolean(),
                title='Attended Third Meeting: ') 
    group = colander.SchemaNode(
                colander.String(),
                title = "User Group:",
                widget=deform.widget.RadioChoiceWidget(
                    values=(("Student","Student"),
                            ("Officer","Officer"),
                            ("Advisor","Advisor")
                            )
                    ),
                default=deferred_default,
                )
    deactivate = colander.SchemaNode(
                colander.Boolean(),
                description='Are you sure you want to delete this user?',
                widget=deform.widget.CheckboxWidget(),
                title='Deactivate User') 


class UserExportSchema(colander.MappingSchema):
    studentId = colander.SchemaNode(colander.Boolean(),
                                    title='Student ID: ')
    firstName = colander.SchemaNode(colander.Boolean(),
                                    title='First Name: ') 
    lastName = colander.SchemaNode(colander.Boolean(),
                                   title='Last Name: ') 
    username = colander.SchemaNode(colander.Boolean(),
                                   title='Username: ')
    email = colander.SchemaNode(colander.Boolean(),
                                title='Email: ') 
    phone = colander.SchemaNode(colander.Boolean(),  
                                title='Phone: ') 
    gradYear = colander.SchemaNode(colander.Boolean(),
                                   title='Graduation Year: ') 
    inductionYear = colander.SchemaNode(colander.Boolean(),
                                        title='Induction Year: ') 
    dues = colander.SchemaNode(colander.Boolean(),
                               title='Paid Dues: ') 
    gpa = colander.SchemaNode(colander.Boolean(),
                              title='Meets GPA: ') 
    firstMeeting = colander.SchemaNode(colander.Boolean(),
                                       title='At 1st Meeting: ') 
    secondMeeting = colander.SchemaNode(colander.Boolean(),
                                        title='At 2nd Meeting: ') 
    thirdMeeting = colander.SchemaNode(colander.Boolean(),
                                       title='At 3rd Meeting: ') 
    hours = colander.SchemaNode(colander.Boolean(),
                                title='Total Hours: ') 
    sponsored = colander.SchemaNode(colander.Boolean(),
                                    title='Sponsored Hours: ') 


class TextFieldSchema(colander.MappingSchema):
    text = colander.SchemaNode(
                colander.String(),
                widget=deform.widget.TextAreaWidget(rows=10, cols=110),
                description='Enter some text',
                title="")


class IndependentEventSchema(colander.Schema):
    completionDate = colander.SchemaNode(colander.Date(), 
                                         title="Completion Date (YYYY-MM-DD):")
    hours = colander.SchemaNode(colander.Float(),
                                title="Number of Hours: ")
    description = colander.SchemaNode(colander.String(),
                                      title="Service: ")
    taskDescription = colander.SchemaNode(
        colander.String(),
        title = "Description:",
        widget=deform.widget.TextAreaWidget(rows=5, cols=40),
        description='Enter some text')
    contact = colander.SchemaNode(colander.String(), title="Contact Name: ")
    contactInfo = colander.SchemaNode(colander.String(),title="Contact Information: ")
    affects = colander.SchemaNode(colander.String(),
                                  widget=deform.widget.SelectWidget(values=(('','- Select -'),
                                                                            ('Yorktown','Yorktown'),
                                                                            ('Arlington','Arlington'),
                                                                            ('DC','DC area'),
                                                                            ('World','World'))),
                                  title="Affects",
                                  validator = colander.OneOf(['Yorktown','Arlington','DC','World'])
                                  )
class IndependentEventEditSchema(colander.Schema):
    eventType = colander.SchemaNode(
                colander.String(),
                title = "Event Type:",
                widget=deform.widget.SelectWidget(values=(("Independent","Independent"),("Sponsored","Sponsored")), size=2))
    completionDate = colander.SchemaNode(colander.Date(),title="Completion Date (YYYY-MM-DD):")
    hours = colander.SchemaNode(colander.Float(),
                                title="Number of Hours: ")
    description = colander.SchemaNode(colander.String(),
                                      title="Service: ")
    taskDescription = colander.SchemaNode(
                colander.String(),
                title = "Description:",
                widget=deform.widget.TextAreaWidget(rows=5, cols=40),
                description='Enter some text')
    contact = colander.SchemaNode(colander.String(),
                                  title="Contact Name: ")
    contactInfo = colander.SchemaNode(colander.String(),
                                      title="Contact Information: ")
    
#class SponsoredEventSchema(colander.MappingSchema):
    #completionDate = colander.SchemaNode(colander.Date())
    #hours = colander.SchemaNode(colander.Integer())
    #description = colander.SchemaNode(
                #colander.String(),
                #widget=deform.widget.SelectWidget(values=projectchoices, size=2)
                #)
    #taskDescription = colander.SchemaNode(
                #colander.String(),
                #validator=colander.Length(max=100),
                #widget=deform.widget.TextAreaWidget(rows=10, cols=60),
                #description='Enter some text')
    #contact = colander.SchemaNode(colander.String())
    #contactInfo = colander.SchemaNode(colander.String())

class VerifyEventSchema(colander.MappingSchema):
    comment = colander.SchemaNode(
                colander.String(),
                title = "Comment: ",
                missing = "",
                widget=deform.widget.TextAreaWidget(rows=5, cols=40),
                description='Enter some text')
    verified = colander.SchemaNode(
                colander.String(),
                title = "Verification Status: ",
                widget=deferred_select_widget,
                )

class AdvisorVerifyEventSchema(colander.MappingSchema):
    comment = colander.SchemaNode(
                colander.String(),
                title = "Comment: ",
                missing = "",
                widget=deform.widget.TextAreaWidget(rows=5, cols=40),
                description='Enter some text')
    advisorNote = colander.SchemaNode(
                colander.String(),
                title = "Advisor's Note: ",
                missing = "",
                widget=deform.widget.TextAreaWidget(rows=5, cols=40),
                description='Enter some text')
    verified = colander.SchemaNode(
                colander.String(),
                title = "Verification Status: ",
                widget=deferred_select_widget,
                )

class DeadlineSchema(colander.MappingSchema):
    dateDue = colander.SchemaNode(colander.Date(),title="Date Due (YYYY-MM-DD): ")
    hours = colander.SchemaNode(colander.Float(),title="Total Hours: ")
    sponsored = colander.SchemaNode(colander.Float(),title="Sponsored Hours: ")
    appliedClass = colander.SchemaNode(
                colander.String(),
                title="Class: ",
                widget=deform.widget.SelectWidget(values=(("All","All"),("Juniors","Juniors"),("Seniors","Seniors")), size=2))
                
class DeadlineEditSchema(colander.MappingSchema):
    dateDue = colander.SchemaNode(colander.Date(),title="Date Due (DD/MM/YYYY): ")
    hours = colander.SchemaNode(colander.Float(),title="Hours: ")
    sponsored = colander.SchemaNode(colander.Float(),title="Sponsored: ")
    appliedClass = colander.SchemaNode(
                colander.String(),title="Class: ",
                widget=deform.widget.SelectWidget(values=(("All","All"),("Juniors","Juniors"),("Seniors","Seniors")), size=2))
    delete = colander.SchemaNode(
                colander.Boolean(),
                description='Are you sure you want to delete this deadline?',
                widget=deform.widget.CheckboxWidget(),
                title='Delete Deadline') 

#class DeleteyButton(colander.MappingSchema):
    #delete = colander.SchemaNode(
                #colander.Boolean(),
                #description='Are you sure you want to delete this item?',
                #widget=deform.widget.CheckboxWidget(),
                #title='Delete Project') 

#class ProjectSchema(colander.MappingSchema):
    #service = colander.SchemaNode(colander.String(),title='Name of Service: ')
                
#class ProjectEditSchema(colander.MappingSchema):
    #service = colander.SchemaNode(colander.String(),title='Name of Service: ')
    #delete = colander.SchemaNode(
                #colander.Boolean(),
                #description='Are you sure you want to delete this project?',
                #widget=deform.widget.CheckboxWidget(),
                #title='Delete Project') 
                
class ProjectSequence(colander.SequenceSchema):
    project = colander.SchemaNode(
        colander.String(),
        title = "Project:")
        
class ProjectsSchema(colander.Schema):
    projects = ProjectSequence()
     
class EmailSchema(colander.MappingSchema):
    to = colander.SchemaNode(
                colander.String(),
                title="To: ",
                widget=deform.widget.SelectWidget(values=(("all","All"),
                                                          ("officers","Officers"),
                                                          ("seniors","Seniors"),
                                                          ("juniors","Juniors"),
                                                          ("dues","Dues Unpaid"),
                                                          ("gpa","GPA Unmet"),
                                                          ("thours","Total Hours Incomplete"),
                                                          ("shours","Sponsored Hours Incomplete")), size=2))
                                                          #Said Sean Connery   
    subject = colander.SchemaNode(colander.String(),title="Subject: ")
    message = colander.SchemaNode(
                colander.String(),
                title = "Message:",
                widget=deform.widget.TextAreaWidget(rows=10, cols=60))
