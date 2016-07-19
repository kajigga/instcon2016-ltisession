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

SERVER_NAME = 'flasktestapp1-kajigga2.c9users.io'
#SERVER_NAME = '0.0.0.0:5000'
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
    'custom_canvas_user_login_id',
    'ext_content_return_types',
    'ext_outcome_data_values_accepted',
    'ext_outcome_result_total_score_accepted',
    'ext_content_intended_use',
    'ext_content_return_url',
    'ext_content_file_extensions'
])

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

@app.route('/lti/launch/<tool_id>', methods=['POST'])
@lti(error=error, request='initial')
def first_lti_launch(lti, tool_id=None, *args, **kwargs):
  if tool_id == '0':
    return redirect('/lti/mapit')
  else:
    return render_template('lti_profile.html')

G_API_KEY = 'AIzaSyDS7-sUBVXPy5XIjWJFsXzLf6fDEZtjFOw'
@app.route('/lti/mapit')
@lti(error=error, request='session')
def mapit_launch(lti):
  return render_template('mapit_launch.html',G_API_KEY=G_API_KEY)

@app.route('/lti/profile', methods=['GET'])
@lti(error=error, request='session')
def lti_profile(lti, *args, **kwargs):
  return render_template('lti_profile.html')

tools = [{ 
  'domain' : SERVER_NAME,
  'title' : 'Step 4-Module',
  'description' : '''This is the step 4 LTI Tool, with differentiated
  functionality for students and teachers, course navigation, and module item
  navigation.''',
  'url':'http://{}/lti/launch/{}'.format(SERVER_NAME, 0),
  'nav' : [
    {
      'type':'course_navigation',
      'enabled': True,
      'default':'enabled',
      # 'visibility': '', # 'public', 'members', 'admins'
      'text': 'S4: Mapper',
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

# Add force to https
def _force_https():
  # my local dev is set on debug, but on AWS it's not (obviously)
  # I don't need HTTPS on local, change this to whatever condition you want.
  if not app.debug: 
      from flask import _request_ctx_stack
      if _request_ctx_stack is not None:
          reqctx = _request_ctx_stack.top
          reqctx.url_adapter.url_scheme = 'https'
app.before_request(_force_https)
  
if __name__ == '__main__':
  ''' IP and PORT are two environmental variables configured in Cloud9. They
  can change occasionally without warning so the application must be able to
  dynamically detect the change on each startup. Reasonable default values of 
  hostname 0.0.0.0 and port 5000 are set as well.'''

  app.run(host=os.getenv('IP','0.0.0.0'),port=int(os.getenv('PORT',5000)))    
