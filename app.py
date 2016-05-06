"""
This file creates your application.
"""
import os
from flask import Flask, render_template, request, redirect, url_for, session, make_response, jsonify

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
  if tool_id == '0':
    return redirect('mapit')
  elif tool_id == '1':
    #return redirect('/lti/yt_watch_for_points')
    return redirect(url_for('yt_watch_for_points'))
  elif tool_id == '2':
    return redirect(url_for('baconIpsumChoose'))
  else:
    return render_template('lti_profile.html')

G_API_KEY = 'AIzaSyDS7-sUBVXPy5XIjWJFsXzLf6fDEZtjFOw'
@app.route('/lti/mapit')
@lti(error=error, request='session')
def mapit_launch(lti):
  return render_template('mapit_launch.html',G_API_KEY=G_API_KEY)

@app.route('/lti/yt_watch_for_points')
@lti(error=error, request='session')
#@lti(error=error, request='session', role='learner')
#@lti(error=error, request='session', role='instructor')
def yt_watch_for_points(lti, *args, **kwargs):
  video_id = 'M7lc1UVf-VE'
  return render_template('yt_watch_for_points.html', video_id=video_id)

@app.route('/lti/yt_watch_for_points/finished', methods=['POST'])
@lti(error=error, request='session')
#@lti(error=error, request='session', role='learner')
#@lti(error=error, request='session', role='instructor')
def yt_watch_for_points_submit(lti, *args, **kwargs):
  status = 'submitted'
  response = lti.post_grade(request.form.get('score',0))
  print('response', response)
  return jsonify(status=response)

@app.route('/lti/baconipsum/fetch')
@lti(error=error, request='session')
def baconIpsumFetch(lti,*args,**kwargs):
    num_para = int(request.args.get('num_para',5))
    with_bacon = request.args.get('with_bacon','no').lower()
    show = request.args.get('show','none').lower()
    resp = {
      'version': '1.0',
      'type': 'rich',
      'width': '240',
      'height': '160',
      'provider_name': 'BaconIpsum',
      'html':'<p>lkjlkjlkj</p>'
    }
    

    #print 'with_bacon', with_bacon
    if with_bacon == 'yes':
      # Now get the bacon ipsum
      bacon_url = "http://baconipsum.com/api/?type=meat-and-filler&paras=%d&start-with-lorem=0" % num_para 

      try:
        paragraphs = requests.get(bacon_url).json()
        # paragraphs = json_decode('%s' % bacon_response)
      except Exception,err:
        print 'err',err
        bacon_response = "Hello, this is an error."
        bacon_response = ''.join(bacon_response.splitlines())

        paragraphs = ['',]
      resp['html'] = "<p>%s</p>" % "</p><p>".join(paragraphs)
    elif show in ('arresteddevelopment','doctorwho','dexter','futurama','holygrail','simpsons','starwars'):

      fillerama_url = "http://api.chrisvalleskey.com/fillerama/get.php?count=100&format=json&show=%s" % show
      response = requests.get(fillerama_url).json()
      paragraphs = [x['quote'] for x in response['db']]
      resp['html'] = "<p>%s</p>" % "</p><p>".join(paragraphs)
    else:
      # No bacon wanted, get regular Lorem Ipsum
      options = ['short','headers','decorate','link','ul','ul','dl','bq']
      lorem_url = "http://loripsum.net/api/%d/%s" % (num_para,'/'.join(options))
      paragraphs = requests.get(lorem_url).text
      paragraphs = paragraphs.replace('loripsum.net',settings.LTI_BASE_DOMAIN.split('/')[-1])
      resp['html'] = paragraphs

    return render_template('baconIpsumFetch.html',dict(paragraphs=paragraphs))
    #if request.args.get('html','no')=='yes':
    #  return render_template('baconIpsumFetch.html',dict(paragraphs=paragraphs))
    #else:
    #  return HttpResponse(json.dumps(resp), content_type="application/json")

@app.route('/lti/baconipsum/choose', methods=['GET', 'POST'])
@lti(error=error, request='session')
def baconIpsumChoose(lti, *args, **kwargs):
  if request.method == 'GET':
    # Prompt the user to select the size of the bacon 
    return render_template('baconIpsumChoose.html')

  elif request.method=='POST':
    # Then do an api request to http://baconipsum.com/api/
    # to get some bacon.  Write the text to a file and return to the LTI "on done" url"
    # TODO This needs to be fixed to  be
    # an oEmbed link.  i.e. http://oembed.com/
    #
    # https://canvas.instructure.com/doc/api/editor_button_tools.html

    # For some reason, we can't use https here... see
    # canvas-lms/app/controllers/external_content_controller.rb
    with_bacon = request.form.get('with_bacon','no').lower()
    red_args = {'oembed' :{
        'url':     url_for('baconIpsumFetch',args=['lkjlkjlk']), 
        'endpoint':'',
        'width':'400',
        'height':'400',
        'embed_type':'oembed',
        },
    'link': { # works
        'url':     url_for('baconIpsumFetch',args=['lkjlkjlk']), 
        'title':'this is the title',
        'text':'link text',
        'embed_type':'link'
        },
    'img': { # works
        # Other options: 
        # - http://placehold.it/
        # - http://www.webresourcesdepot.com/8-free-placeholder-image-services-for-instant-dummy-images/
        'url':     'https://placekitten.com/g/%d/%d',
        'title':'this is the title',
        'alt': 'random kitten',
        'embed_type':'image',
        'width':300,
        'height':250
      },
    'iframe': { # works, the iframe is created but something on the
                # Canvas side is borking up the iframe code
        'url':     'https://icanhascheezburger.files.wordpress.com',
        'title':'this is the title',
        'alt': 'ceiling cat',
        'embed_type':'iframe',
        'width':600,
        'height':250
        }
    }
  
    success_url = session.get('launch_presentation_return_url','')

    #redirect_url = success_url % urllib.urlencode(red_args['oembed'])
    wanted_type = request.form.get('wanted_type','oembed')
    if wanted_type in ('img','link','iframe','oembed'):
      #redirect_url = success_url % urllib.urlencode(red_args['img'])
      print 'wanted ', wanted_type
      if wanted_type == 'img':
        height = int(request.args.get('height',100))
        width  = int(request.args.get('width',100))
        red_args['img']['url'] = red_args['img']['url'] % (height,width)
        red_args['img']['height'] = height
        red_args['img']['width']  = width
      elif wanted_type == 'iframe':
        pass
      elif wanted_type == 'link':
        pass
      elif wanted_type == 'oembed':
        show = request.form.get('show','none')
        url_for('baconIpsumFetch',args=['lkjlkjlk']) 
        red_args['oembed']['endpoint'] = url_for('baconIpsumFetch',args=['lkjlkjlk'])
        red_args['oembed']['url'] = red_args['oembed']['endpoint'] #.replace('https','http')

      redirect_url = success_url +"?"+ urllib.urlencode(red_args[wanted_type])
    return redirect(redirect_url)




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
  'url':'https://{}/lti/launch/{}'.format(SERVER_NAME, 0),
  'nav' : [
    {
      'type':'course_navigation',
      'enabled': True,
      'default':'enabled',
      # 'visibility': '', # 'public', 'members', 'admins'
      'text': 'S4: Mapper',
    }
  ]
  },{ 
    'domain' : SERVER_NAME,
    'title' : 'Step 5-Watch Youtube - Get Grade',
    'description' : '''This is the step 5 LTI Tool, with differentiated
    functionality for students and teachers. Teach will add an assignment as
    external tool, and select a youtube video. Students watch the video and get
    points when they finish the video.''',

    'url':'https://{}/lti/launch/{}'.format(SERVER_NAME, 1),
  },
  { 
    'domain' : SERVER_NAME,
    'title' : 'Step 6-Lorem Ipsum',
    'description' : '''This is the step 6 LTI Tool, which enables a richtext
    editor button that, when clicked, allows the user to insert a Lorem Ipsum
    text snippet.''',

    'url':'https://{}/lti/launch/{}'.format(SERVER_NAME, 2),
    'editor_button':{
        'icon_url':'https://dl.dropboxusercontent.com/u/1647772/lorem.png',
        "selection_width":500,
        "selection_height":300
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

