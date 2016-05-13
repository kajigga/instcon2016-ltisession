# -*- coding: utf-8 -*-
"""
This file creates your application.
"""
import os
from flask import Flask, render_template, render_template_string, request, redirect, url_for, session, make_response, jsonify
import requests

from pylti.flask import lti
from pylti.common import LTI_PROPERTY_LIST, LTI_ROLES
import urllib

app = Flask(__name__)
app.debug = True

# set the secret key.  keep this really secret:
app.secret_key = 'a0lkanvoiuas9d8faskdjaksjnvalisdfJ:{}{OIUzR98J/3Yx r~xhh!JMn]lwx/,?rt'

# set the secret key.  keep this really secret:
app.secret_key = 'a0lkanvoiuas9d8faskdjaksjnvalisdfJ:{}{OIUzR98J/3Yx r~xhh!JMn]lwx/,?rt'

app.config['PREFERRED_URL_SCHEME'] = 'https'

# LTI Consumers
consumers = {
    "abc123": {"secret": "secretkey-for-abc123"}
}

#SERVER_NAME = 'inst-ic-proj.herokuapp.com'
#SERVER_NAME = '0.0.0.0:5000'
SERVER_NAME = 'flasktestapp1-kajigga2.c9users.io'
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
  return redirect(url_for('special_chars_choose', _scheme='https', _external=True))



# Make sure you don't include the @lti decorator on this route. Canvas won't be
# able to request the information otherwise.

@app.route('/lti/special_chars/fetch')
def specialchars_fetch(*args,**kwargs):
    character = request.args.get('char','')
    resp = {
      'version': '1.0',
      'type': 'rich',
      'width': '240',
      'height': '160',
      'provider_name': 'BaconIpsum',
      'html':character
    }

    return jsonify(resp)

special_chars = {
  'fr': {
      'label':'fr',
      'name':u'Français',
      'english_name': 'French',
      'characters':[ 
        {'char':u'À','win_alt_code':'0192'},
        {'char':u'à', 'win_alt_code':'133'},
        {'char':u'Â','win_alt_code':'0194'},
        {'char':u'â','win_alt_code':'131'},
        {'char':u'Ä','win_alt_code':'142'},
        {'char':u'ä','win_alt_code':'132'},
        {'char':u'Æ','win_alt_code':'146'},
        {'char':u'æ','win_alt_code':'145'},
        {'char':u'Ç','win_alt_code':'128'},
        {'char':u'ç','win_alt_code':'135'},
        {'char':u'È','win_alt_code':'0200'},
        {'char':u'è','win_alt_code':'138'},
        {'char':u'É','win_alt_code':'144'},
        {'char':u'é','win_alt_code':'130'},
        {'char':u'Ê','win_alt_code':'0202'},
        {'char':u'ê','win_alt_code':'136'},
        {'char':u'Ë','win_alt_code':'0203'},
        {'char':u'ë','win_alt_code':'137'},
        {'char':u'Î','win_alt_code':'0206'},
        {'char':u'î','win_alt_code':'140'},
        {'char':u'Ï','win_alt_code':'0207'},
        {'char':u'ï','win_alt_code':'139'},
        {'char':u'Ô','win_alt_code':'0212'},
        {'char':u'ô','win_alt_code':'147'},
        {'char':u'Œ','win_alt_code':'0140'},
        {'char':u'œ','win_alt_code':'0156'},
        {'char':u'Ù','win_alt_code':'0217'},
        {'char':u'ù','win_alt_code':'151'},
        {'char':u'Û','win_alt_code':'0219'},
        {'char':u'û','win_alt_code':'150'},
        {'char':u'Ü','win_alt_code':'154'},
        {'char':u'ü','win_alt_code':'129'}
      ]
    },
  'es': {
      'label':'es',
      'name':u'Español',
      'english_name': 'Spanish',
      'characters':[ 
        {'char':u'Á', 'win_alt_code': '0193'},
        {'char':u'á', 'win_alt_code': '160'},
        {'char':u'É', 'win_alt_code': '144'},
        {'char':u'é', 'win_alt_code': '130'},
        {'char':u'Ê', 'win_alt_code': '0202'},
        {'char':u'Í', 'win_alt_code': '0205'},
        {'char':u'í', 'win_alt_code': '161'},
        {'char':u'Ñ', 'win_alt_code': '165'},
        {'char':u'ñ', 'win_alt_code': '164'},
        {'char':u'Ó', 'win_alt_code': '0211'},
        {'char':u'ó', 'win_alt_code': '162'},
        {'char':u'Ú', 'win_alt_code': '0218'},
        {'char':u'ú', 'win_alt_code': '163'},
        {'char':u'Ü', 'win_alt_code': '154'},
        {'char':u'ü', 'win_alt_code': '129'},
        {'char':u'¿', 'win_alt_code': '168'},
        {'char':u'¡', 'win_alt_code': '173'},
      ]
    },
  'it': {
      'label':'it',
      'name':u'Italiano',
      'english_name': 'Italian',
      'characters':[ 
        {'char': u'à', 'win_alt_code': '133'},
        {'char': u'è', 'win_alt_code': '138'},
        {'char': u'ì', 'win_alt_code': '141'},
        {'char': u'ò', 'win_alt_code': '149'},
        {'char': u'ù', 'win_alt_code': '151'},
        {'char': u'À', 'win_alt_code': '0192'},
        {'char': u'È', 'win_alt_code': '0200'},
        {'char': u'Ì', 'win_alt_code': '0204'},
        {'char': u'Ò', 'win_alt_code': '0210'},
        {'char': u'Ù', 'win_alt_code': '0217'}
      ]
    },
  'de': {
      'label':'de',
      'name':u'Deutsch',
      'english_name': 'German',
      'characters':[ 
        {'char': u'Ä', 'win_alt_code': '142'},
        {'char': u'ä', 'win_alt_code': '132'},
        {'char': u'Å', 'win_alt_code': '143'},
        {'char': u'å', 'win_alt_code': '134'},
        {'char': u'Æ', 'win_alt_code': '146'},
        {'char': u'æ', 'win_alt_code': '145'},
        {'char': u'Ğ', 'win_alt_code': '0208'},
        {'char': u'ğ', 'win_alt_code': '0240'},
        {'char': u'Ë', 'win_alt_code': '0206'},
        {'char': u'ë', 'win_alt_code': '037'},
        {'char': u'Ö', 'win_alt_code': '153'},
        {'char': u'ö', 'win_alt_code': '148'},
        {'char': u'Ø', 'win_alt_code': '0216'},
        {'char': u'ø', 'win_alt_code': '0248'},
        {'char': u'Ş', 'win_alt_code': '0222'},
        {'char': u'ş', 'win_alt_code': '0254'},
        {'char': u'Ü', 'win_alt_code': '154'},
        {'char': u'ü', 'win_alt_code': '129'},
        {'char': u'ÿ', 'win_alt_code': '152'},
        {'char': u'ß', 'win_alt_code': '225'}
      ]
    }
}

@app.route('/lti/special_chars/choose', methods=['GET', 'POST'])
#@lti(error=error, request='session')
def special_chars_choose(*args, **kwargs):
  if request.method == 'GET':
    # Prompt the user to select the size of the bacon 
    return render_template('special_chars_chooser.html', special_chars=special_chars)

  elif request.method=='POST':
    # Then do an api request to http://baconipsum.com/api/
    # to get some bacon.  Write the text to a file and return to the LTI "on done" url"
    # TODO This needs to be fixed to  be
    # an oEmbed link.  i.e. http://oembed.com/
    #
    # https://canvas.instructure.com/doc/api/editor_button_tools.html

    # For some reason, we can't use https here... see
    # canvas-lms/app/controllers/external_content_controller.rb
    red_args = {'oembed' :{
        'url':     url_for('specialchars_fetch', _external=True, _scheme='https', args=['lkjlkjlk']), 
        'endpoint':'',
        'width':'16',
        'height':'16',
        'embed_type':'oembed',
        },
    }
  
    success_url = session.get('launch_presentation_return_url','')

    red_args['oembed']['endpoint'] = url_for('specialchars_fetch', _external=True, _scheme='https',**dict(request.form))
    red_args['oembed']['url'] = red_args['oembed']['endpoint'] #.replace('https','http')

    redirect_url = '{}?{}'.format(success_url, urllib.urlencode(red_args['oembed']))

    print 'redirect_url', redirect_url
    return redirect(redirect_url)




@app.route('/lti/profile', methods=['GET'])
@lti(error=error, request='session')
def lti_profile(lti, *args, **kwargs):
  return render_template('lti_profile.html')

tools = [{ 
    'domain' : SERVER_NAME,
    'title' : 'Step 7-Foreign Language Characters',
    'description' : '''This is the step 7 LTI Tool, which enables a richtext
    editor button that, when clicked, enables the user to insert special
    characters.''',

    'url':'https://{}/lti/launch/{}'.format(SERVER_NAME, 2),
    'editor_button':{
        'icon_url':'https://dl.dropboxusercontent.com/u/1647772/lorem.png',
        "selection_width":450,
        "selection_height":600
        }
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
      'version':"0.0.1-step6",
      'project_name':'LTI Starter'
      }

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

