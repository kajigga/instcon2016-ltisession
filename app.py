"""
This file creates your application.
"""
import os
from flask import Flask, render_template, request, redirect, url_for, session, make_response

from pylti.flask import lti
from pylti.common import LTI_PROPERTY_LIST, LTI_ROLES

app = Flask(__name__)
app.debug = True

# set the secret key.  keep this really secret:
app.secret_key = 'a0lkanvoiuas9d8faskdjaksjnvalisdfJ:{}{OIUzR98J/3Yx r~xhh!JMn]lwx/,?rt'


# LTI Consumers
consumers = {
    "abc123": {"secret": "secretkey-for-abc123"}
}

#SERVER_NAME = 'inst-ic-proj.herokuapp.com'
SERVER_NAME = '0.0.0.0:5000'
#app.config['SERVER_NAME'] = SERVER_NAME

# Configure flask app with PYLTI config, specifically the consumers
app.config['PYLTI_CONFIG'] = {'consumers': consumers}

# Canvas sends some custom LTI launch parameters. Add these to the list of
# known parameters so that pylti will save them.
LTI_PROPERTY_LIST.extend([
    'custom_canvas_api_domain',
    'custom_canvas_course_id',
    'custom_canvas_enrollment_state',
    'custom_canvas_user_id',
    'custom_canvas_user_login_id'
])

# Canvas uses full standard roles from the LTI spec. PYLTI does not include
# them by default so we add these to the list of known roles.

# NOTE: We can use my pylti package unless the main pylti maintainers accept my
# pull request

# This is the Administrator role and all of the different variations
LTI_ROLES[ 'urn:lti:instrole:ims/lis/Administrator' ] = [ 
    'urn:lti:instrole:ims/lis/Administrator', 
    'urn:lti:sysrole:ims/lis/SysAdmin'
]

# This is the Instructor role
LTI_ROLES[ 'urn:lti:instrole:ims/lis/Instructor' ] = [ 'urn:lti:instrole:ims/lis/Instructor', ]

# This is the student role
LTI_ROLES[ 'urn:lti:instrole:ims/lis/Student' ] = [ 
    'urn:lti:instrole:ims/lis/Student', 
    'urn:lti:instrole:ims/lis/Learner'
]


#app.config['SERVER_NAME'] = 'localhost'
# Make sure app uses https everywhere. This will become important when there
# are actually LTI endpoints and configuration used.
#app.config['PREFERRED_URL_SCHEME'] = 'https'

@app.route('/')
def index():
    # "index.html" is a file found in the "templates" folder. It is mostly regular
    # HTML with some special templating syntax mixed in. The templating
    # language is called Jinja.
    return render_template('index.html')

@app.route('/hello_world')
def hello_world():
    return 'Hello World!'

def error(*args, **kwargs):
  # TODO Make a better Error Message screen
  return '{}'.format(kwargs['exception'])

@app.route('/lti/launch', methods=['POST'])
@lti(error=error, request='initial')
def first_lti_launch(lti, *args, **kwargs):
  # return render_template('first_lti_launch.html')
  return redirect('/lti/profile')

@app.route('/lti/profile', methods=['GET'])
@lti(error=error, request='session')
def lti_profile(lti, *args, **kwargs):
  return render_template('lti_profile.html')

tools = [{ 
  'domain' : SERVER_NAME,
  'title' : 'Step 3 Config',
  'description' : 'This is the step 3 config xml'
},
{ 
  'domain' : SERVER_NAME,
  'title' : 'Step 3.1 Config',
  'description' : 'This is the step 3.1 config xml',
  'nav' : [
    {
      'type':'course_navigation',
      'enabled': True,
      'default':'enabled',
      # 'url':'', Is there a different launch URL for this navigation?
      # 'visibility': '', # 'public', 'members', 'admins'
      'text': 'course navigation text',
      'labels': [
        { 'locale': 'es', 'label': 'Utilidad LTI'},
        { 'locale': 'en', 'label': 'LTI Tool'},
      ]
    },
    { 
      'type':'account_navigation',
      'enabled': True,
      'text': 'Acct. Link Text',
      # 'url':'', Is there a different launch URL for this navigation?
    }
  ]
}
]
@app.route('/lti/config/<tool_id>')
def lti_config(tool_id):
  tool_id = int(tool_id)
  config_xml = render_template('xml/config.xml', tool=tools[tool_id])
  response = make_response(config_xml)
  response.headers["Content-Type"] = "application/xml"    

  return response

# I like to make certain values available on any rendered template without
# explicitly naming them. While these values won't change very often, I would
# rather not keep track of where they are used so I don't have to remember to
# change the value everywhere.  Programmers are lazy :)
@app.context_processor
def inject_app_info():
  return {
      'version':"0.0.1-step3",
      'project_name':'LTI Starter'
      }

if __name__ == '__main__':
  ''' IP and PORT are two environmental variables configured in Cloud9. They
  can change occasionally without warning so the application must be able to
  dynamically detect the change on each startup. Reasonable default values of 
  hostname 0.0.0.0 and port 5000 are set as well.'''

  app.run(host=os.getenv('IP','0.0.0.0'),port=int(os.getenv('PORT',5000)))    
