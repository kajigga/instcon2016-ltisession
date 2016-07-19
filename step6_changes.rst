diff --git a/app.py b/app.py
index 5b2ce0e..5490fe1 100644
--- a/app.py
+++ b/app.py
@@ -2,10 +2,12 @@
 This file creates your application.
 """
 import os
-from flask import Flask, render_template, request, redirect, url_for, session, make_response, jsonify
+from flask import Flask, render_template, render_template_string, request, redirect, url_for, session, make_response, jsonify
+import requests
 
 from pylti.flask import lti
 from pylti.common import LTI_PROPERTY_LIST, LTI_ROLES
+import urllib
 
 app = Flask(__name__)
 app.debug = True
@@ -13,6 +15,10 @@ app.debug = True
 # set the secret key.  keep this really secret:
 app.secret_key = 'a0lkanvoiuas9d8faskdjaksjnvalisdfJ:{}{OIUzR98J/3Yx r~xhh!JMn]lwx/,?rt'
 
+# set the secret key.  keep this really secret:
+app.secret_key = 'a0lkanvoiuas9d8faskdjaksjnvalisdfJ:{}{OIUzR98J/3Yx r~xhh!JMn]lwx/,?rt'
+
+app.config['PREFERRED_URL_SCHEME'] = 'https'
 
 # LTI Consumers
 consumers = {
@@ -20,7 +26,8 @@ consumers = {
 }
 
 #SERVER_NAME = 'inst-ic-proj.herokuapp.com'
-SERVER_NAME = '0.0.0.0:5000'
+#SERVER_NAME = '0.0.0.0:5000'
+SERVER_NAME = 'flasktestapp1-kajigga2.c9users.io'
 #app.config['SERVER_NAME'] = SERVER_NAME
 
 # Configure flask app with PYLTI config, specifically the consumers
@@ -66,9 +73,12 @@ def error(*args, **kwargs):
 @lti(error=error, request='initial')
 def first_lti_launch(lti, tool_id=None, *args, **kwargs):
   if tool_id == '0':
-    return redirect('/lti/mapit')
+    return redirect(url_for('mapit', _scheme='https', _external=True))
   elif tool_id == '1':
-    return redirect('/lti/yt_watch_for_points')
+    #return redirect('/lti/yt_watch_for_points')
+    return redirect(url_for('yt_watch_for_points', _scheme='https', _external=True))
+  elif tool_id == '2':
+    return redirect(url_for('baconIpsumChoose', _scheme='https', _external=True))
   else:
     return render_template('lti_profile.html')
 
@@ -83,8 +93,7 @@ def mapit_launch(lti):
 #@lti(error=error, request='session', role='learner')
 #@lti(error=error, request='session', role='instructor')
 def yt_watch_for_points(lti, *args, **kwargs):
-  video_id = 'M7lc1UVf-VE'
-  return render_template('yt_watch_for_points.html', video_id=video_id)
+  return render_template('yt_watch_for_points.html')
 
 @app.route('/lti/yt_watch_for_points/finished', methods=['POST'])
 @lti(error=error, request='session')
@@ -97,6 +106,199 @@ def yt_watch_for_points_submit(lti, *args, **kwargs):
   return jsonify(status=response)
 
 
+lorem_types = {
+  'regular':{
+    'name':'regular',
+    'label':'Regular Lorem Ipsum text'
+  },
+  'with_bacon':{
+    'name':'with_bacon',
+    'label':'Bacon Ipsum - tasty but not so good looking'
+  },
+  'random_text':{
+    'name':'random_text',
+    'label':'Random Text'
+  },
+  'arresteddevelopment_quotes': {
+    'name': 'arresteddevelopment_quotes',
+    'label':'Quotes from Arrested Development'
+  },
+  'doctorwho_quotes':{
+    'name':'doctorwho_quotes',
+    'label':'Quotes from Dr. Who'
+  },
+  'dexter_quotes':{
+    'name':'dexter_quotes',
+    'label':'Quotes from Dexter'
+  },
+  'futurama_quotes':{
+    'name':'futurama_quotes',
+    'label':'Quotes from Futurama'
+  },
+  'holygrail_quotes':{
+    'name':'holygrail_quotes',
+    'label':'Quotes from Monty Python and the Holy Grail'
+  },
+  'simpsons_quotes':{
+    'name':'simpsons_quotes',
+    'label':'Quotes from the Simpsons'
+  },
+  'starwars_quotes':{
+    'name':'starwars_quotes',
+    'label':'Quotes from Star Wars'
+  }}
+
+# Make sure you don't include the @lti decorator on this route. Canvas won't be
+# able to request the information otherwise.
+
+@app.route('/lti/baconipsum/fetch')
+def baconIpsumFetch(*args,**kwargs):
+    num_para = int(request.args.get('num_para',5))
+    lorem_type = request.args.get('lorem_type','regular').lower()
+    show = request.args.get('show','none').lower()
+    resp = {
+      'version': '1.0',
+      'type': 'rich',
+      'width': '240',
+      'height': '160',
+      'provider_name': 'BaconIpsum',
+      'html':'<p>lkjlkjlkj</p>'
+    }
+    
+
+    #print 'with_bacon', with_bacon
+    if lorem_type == 'with_bacon':
+      # Now get the bacon ipsum
+      bacon_url = "http://baconipsum.com/api/?type=meat-and-filler&paras=%d&start-with-lorem=0" % num_para 
+
+      try:
+        paragraphs = requests.get(bacon_url).json()
+        # paragraphs = json_decode('%s' % bacon_response)
+      except Exception,err:
+        print 'err',err
+        bacon_response = "Hello, this is an error."
+        bacon_response = ''.join(bacon_response.splitlines())
+
+        paragraphs = ['',]
+      resp['html'] = "<p>%s</p>" % "</p><p>".join(paragraphs)
+    elif lorem_type == 'random_text':
+      lorem_url = 'http://randomtext.me/api/lorem/p-{}/5-15/'.format(num_para)
+
+      try:
+        paragraphs = requests.get(bacon_url).json()
+        # paragraphs = json_decode('%s' % bacon_response)
+      except Exception,err:
+        print 'err',err
+
+        paragraphs = ['']
+      resp['html'] = paragraphs['text_out']
+    #elif show in ('arresteddevelopment','doctorwho','dexter','futurama','holygrail','simpsons','starwars'):
+    #elif show in ('arresteddevelopment','doctorwho','dexter','futurama','holygrail','simpsons','starwars'):
+    elif '_quotes' in lorem_type:
+      show = lorem_type.replace('_quotes', '')
+      fillerama_url = "http://api.chrisvalleskey.com/fillerama/get.php?count=10&format=json&show=%s" % show
+      response = requests.get(fillerama_url).json()
+      paragraphs = [x['quote'] for x in response['db']]
+      resp['html'] = render_template('show_quotes.html', paragraphs=response['db'], lorem=lorem_types[lorem_type])
+    elif lorem_type == 'regular':
+      # No bacon wanted, get regular Lorem Ipsum
+      options = ['short','headers','decorate','link','ul','ul','dl','bq']
+      lorem_url = "http://loripsum.net/api/%d/%s" % (num_para,'/'.join(options))
+      paragraphs = requests.get(lorem_url).text
+      paragraphs = paragraphs.replace('loripsum.net', 'canvaslms.com')
+      resp['html'] = paragraphs
+
+    #return render_template('baconIpsumFetch.html',paragraphs=paragraphs)
+    if request.args.get('html','no')=='yes':
+      return render_template('baconIpsumFetch.html',dict(paragraphs=paragraphs))
+    else:
+      return jsonify(resp)
+
+
+@app.route('/lti/baconipsum/choose', methods=['GET', 'POST'])
+#@lti(error=error, request='session')
+def baconIpsumChoose(*args, **kwargs):
+  if request.method == 'GET':
+    # Prompt the user to select the size of the bacon 
+    return render_template('baconIpsumChoose.html', lorem_types=lorem_types)
+
+  elif request.method=='POST':
+    # Then do an api request to http://baconipsum.com/api/
+    # to get some bacon.  Write the text to a file and return to the LTI "on done" url"
+    # TODO This needs to be fixed to  be
+    # an oEmbed link.  i.e. http://oembed.com/
+    #
+    # https://canvas.instructure.com/doc/api/editor_button_tools.html
+
+    # For some reason, we can't use https here... see
+    # canvas-lms/app/controllers/external_content_controller.rb
+    red_args = {'oembed' :{
+        'url':     url_for('baconIpsumFetch', _external=True, _scheme='https', args=['lkjlkjlk']), 
+        'endpoint':'',
+        'width':'400',
+        'height':'400',
+        'embed_type':'oembed',
+        },
+    'link': { # works
+        'url':     url_for('baconIpsumFetch', _external=True, _scheme='https',args=['lkjlkjlk']), 
+        'title':'this is the title',
+        'text':'link text',
+        'embed_type':'link'
+        },
+    'img': { # works
+        # Other options: 
+        # - http://placehold.it/
+        # - http://www.webresourcesdepot.com/8-free-placeholder-image-services-for-instant-dummy-images/
+        'url':     'https://placekitten.com/g/%d/%d',
+        'title':'this is the title',
+        'alt': 'random kitten',
+        'embed_type':'image',
+        'width':300,
+        'height':250
+      },
+    'iframe': { # works, the iframe is created but something on the
+                # Canvas side is borking up the iframe code
+        'return_type':'iframe',
+        'embed_type':'iframe',
+        }
+    }
+  
+    success_url = session.get('launch_presentation_return_url','')
+
+    #redirect_url = success_url % urllib.urlencode(red_args['oembed'])
+    wanted_type = request.form.get('wanted_type','oembed')
+    print('wanted_type: ' + wanted_type)
+    if wanted_type in red_args.keys():
+      #redirect_url = success_url % urllib.urlencode(red_args['img'])
+      if wanted_type == 'img':
+        height = int(request.args.get('height',100))
+        width  = int(request.args.get('width',100))
+        red_args['img']['url'] = red_args['img']['url'] % (height,width)
+        red_args['img']['height'] = height
+        red_args['img']['width']  = width
+      elif wanted_type == 'iframe':
+        height = request.form.get('iframe_height',100)
+        width  = request.form.get('iframe_width',100)
+        red_args['iframe']['url'] = request.form.get('iframe_url')
+        red_args['iframe']['title'] = request.form.get('iframe_title')
+        red_args['iframe']['height'] = height
+        red_args['iframe']['width']  = width
+        print 'form args', request.form
+        print 'red_args[iframe]', red_args['iframe']
+      elif wanted_type == 'link':
+        pass
+      elif wanted_type == 'oembed':
+        show = request.form.get('show','none')
+        url_for('baconIpsumFetch', _external=True, _scheme='https',args=['lkjlkjlk']) 
+        red_args['oembed']['endpoint'] = url_for('baconIpsumFetch', _external=True, _scheme='https',**dict(request.form))
+        red_args['oembed']['url'] = red_args['oembed']['endpoint'] #.replace('https','http')
+
+      redirect_url = success_url +"?"+ urllib.urlencode(red_args[wanted_type])
+    return redirect(redirect_url)
+
+
+
+
 @app.route('/lti/profile', methods=['GET'])
 @lti(error=error, request='session')
 def lti_profile(lti, *args, **kwargs):
@@ -108,7 +310,7 @@ tools = [{
   'description' : '''This is the step 4 LTI Tool, with differentiated
   functionality for students and teachers, course navigation, and module item
   navigation.''',
-  'url':'http://{}/lti/launch/{}'.format(SERVER_NAME, 0),
+  'url':'https://{}/lti/launch/{}'.format(SERVER_NAME, 0),
   'nav' : [
     {
       'type':'course_navigation',
@@ -119,15 +321,30 @@ tools = [{
     }
   ]
   },{ 
-  'domain' : SERVER_NAME,
-  'title' : 'Step 5-Watch Youtube - Get Grade',
-  'description' : '''This is the step 5 LTI Tool, with differentiated
-  functionality for students and teachers. Teach will add an assignment as
-  external tool, and select a youtube video. Students watch the video and get
-  points when they finish the video.''',
+    'domain' : SERVER_NAME,
+    'title' : 'Step 5-Watch Youtube - Get Grade',
+    'description' : '''This is the step 5 LTI Tool, with differentiated
+    functionality for students and teachers. Teach will add an assignment as
+    external tool, and select a youtube video. Students watch the video and get
+    points when they finish the video.''',
+
+    'url':'https://{}/lti/launch/{}'.format(SERVER_NAME, 1),
+  },
+  { 
+    'domain' : SERVER_NAME,
+    'title' : 'Step 6-Lorem Ipsum',
+    'description' : '''This is the step 6 LTI Tool, which enables a richtext
+    editor button that, when clicked, allows the user to insert a Lorem Ipsum
+    text snippet.''',
 
-  'url':'http://{}/lti/launch/{}'.format(SERVER_NAME, 1),
-  }]
+    'url':'https://{}/lti/launch/{}'.format(SERVER_NAME, 2),
+    'editor_button':{
+        'icon_url':'https://dl.dropboxusercontent.com/u/1647772/lorem.png',
+        "selection_width":550,
+        "selection_height":400
+        }
+  }
+]
 
 @app.route('/lti/config/<tool_id>')
 def lti_config(tool_id):
@@ -145,10 +362,21 @@ def lti_config(tool_id):
 @app.context_processor
 def inject_app_info():
   return {
-      'version':"0.0.1-step5",
+      'version':"0.0.1-step6",
       'project_name':'LTI Starter'
       }
 
+def _force_https():
+  # my local dev is set on debug, but on AWS it's not (obviously)
+  # I don't need HTTPS on local, change this to whatever condition you want.
+  if not app.debug: 
+      from flask import _request_ctx_stack
+      if _request_ctx_stack is not None:
+          reqctx = _request_ctx_stack.top
+          reqctx.url_adapter.url_scheme = 'https'
+
+app.before_request(_force_https)
+
 if __name__ == '__main__':
   ''' IP and PORT are two environmental variables configured in Cloud9. They
   can change occasionally without warning so the application must be able to
@@ -156,3 +384,4 @@ if __name__ == '__main__':
   hostname 0.0.0.0 and port 5000 are set as well.'''
 
   app.run(host=os.getenv('IP','0.0.0.0'),port=int(os.getenv('PORT',5000)))    
+
diff --git a/static/lorem_ipsum.js b/static/lorem_ipsum.js
new file mode 100644
index 0000000..35b0217
--- /dev/null
+++ b/static/lorem_ipsum.js
@@ -0,0 +1,43 @@
+$(document).ready(function(){ 
+    $('button').click(function(){
+      $('#wanted_submit_btn').show();
+    });
+
+    $('#kitten_btn').click(function(){
+      $('#wanted_type').val('img');
+      $('#kitten_fields').show();
+      $('#lorem_fields, #iframe_fields').hide();
+    });
+    $('#kitten_fields').change(function(){
+      // height/width
+      var img_src = 'https://placekitten.com/g/'+ $('#height').val() +'/'+ $('#width').val() ;
+      $('#kitten_preview')
+        .attr('height', $('#height').val() + 'px')
+        .attr('width', $('#width').val() + 'px')
+        .attr('src', img_src)
+    });
+    $('#lorem_btn').click(function(){
+      $('#wanted_type').val('oembed');
+      $('#lorem_fields').show();
+      $('#kitten_fields, #iframe_fields').hide();
+    });
+    $('#embed_iframe_btn').click(function(){
+      $('#wanted_type').val('iframe');
+      $('#iframe_fields').show();
+      $('#lorem_fields, #kitten_fields').hide();
+    });
+    $('#random_btn').click(function(){
+      $('#wanted_type').val('iframe');
+      $('#random_fields').show();
+      $('#iframe_fields, lorem_fields, #kitten_fields').hide();
+    });
+    $('#iframe_fields').change(function(){
+      var height = $('#iframe_height').val() == '' ?  $('#iframe_preview').attr('height') : $('#iframe_height').val();
+      var width = $('#iframe_width').val() == '' ?  $('#iframe_preview').attr('width') : $('#iframe_width').val();
+      $('#iframe_preview')
+        .attr('src', $('#iframe_url').val())
+        .attr('height', height + 'px')
+        .attr('width', width + 'px');
+    });
+});
+
diff --git a/step_5.txt b/step_5.txt
deleted file mode 100644
index 2068f9a..0000000
--- a/step_5.txt
+++ /dev/null
@@ -1,8 +0,0 @@
-
-In step 5 we will make an LTI app that will do:
-
-* Link selection
-* Resource selection
-* Rich Text Button, Lorem Ipsum
-* Rich Text button, iFrame Inserter
-* Student Views Page, javascript
diff --git a/step_6.txt b/step_6.txt
new file mode 100644
index 0000000..2068f9a
--- /dev/null
+++ b/step_6.txt
@@ -0,0 +1,8 @@
+
+In step 5 we will make an LTI app that will do:
+
+* Link selection
+* Resource selection
+* Rich Text Button, Lorem Ipsum
+* Rich Text button, iFrame Inserter
+* Student Views Page, javascript
diff --git a/templates/baconIpsumChoose.html b/templates/baconIpsumChoose.html
new file mode 100644
index 0000000..fc369a4
--- /dev/null
+++ b/templates/baconIpsumChoose.html
@@ -0,0 +1,96 @@
+{% extends 'layout.html'%}
+{% block page_title %}Choose your Bacon{% endblock %}
+
+{% block main_content %}
+<div class='col-sm-12'>
+    <p>What would you like?</p>
+    <div class='btn-group' role='group' aria-label=''>
+      <button class='btn btn-default' type='button' id='kitten_btn'>Kitten Image</button>
+      <button class='btn btn-default' type='button' id='lorem_btn'>Lorem Ipsum</button>
+      <button class='btn btn-default' type='button' id='embed_iframe_btn'>Embed iFrame</button>
+      <button class='btn btn-default' type='button' id='random_dilbert_btn'>Random Dilbert</button>
+    </div>
+    <form class='form-vertical' action='{{ url_for("baconIpsumChoose" ) }}' method='POST'>
+      <input type='hidden' name='wanted_type' id='wanted_type' value='img'/> 
+
+      <div id='kitten_fields' style='display:none'>
+        <div class="form-group">
+          <label for="width" class="control-label">Width</label>
+          <div class="">
+            <input type="number" class="form-control" id="width" name='width' placeholder="width">
+          </div>
+        </div>
+        <div class="form-group">
+          <label for="height" class="control-label">Height</label>
+          <div class="">
+            <input type="number" class="form-control" id="height" name='height' placeholder="height">
+          </div>
+        </div>
+        <img id='kitten_preview' src='https://placekitten.com/g/100/100' height='100px' width='100px' alt='kitten image'/>
+      </div>
+
+      <div id='lorem_fields' style='display:none'>
+        <div class="form-group">
+          
+          {% for lorem_type in lorem_types %}
+          <div class="radio">
+            <label>
+              <input type="radio" name="lorem_type" 
+                     value="{{lorem_types[lorem_type].name}}">
+              {{ lorem_types[lorem_type].label }}
+            </label>
+          </div>
+          {% endfor %}
+        </div>
+
+        <div class='form-group'>
+          <label for="num_para" class="control-label">number of paragraphs</label>
+          <div class=''>
+            <select name='num_para' class='form-control'>
+              <option value='5'>5</option>
+              <option value='4'>4</option>   
+              <option value='3'>3</option>    
+              <option value='2'>2</option>    
+              <option value='1'>1</option>    
+
+            </select>      
+          </div>
+        </div>
+      </div>
+
+      <div id='iframe_fields' style='display:none'>
+        <div class="form-group">
+          <label for="iframe_title" class="control-label">Title</label>
+          <input type="textbox" class="form-control" id="iframe_title"
+                 name='iframe_title' placeholder="optional, iframe title" />
+        </div>
+        <div class="form-group">
+          <label for="iframe_width" class="control-label">Width</label>
+          <input type="number" class="form-control" id="iframe_width"
+          name='iframe_width' placeholder="width" value="640px"/>
+        </div>
+        <div class="form-group">
+          <label for="iframe_height" class="control-label">Height</label>
+          <input type="number" class="form-control" id="iframe_height"
+          name='iframe_height' placeholder="height" value="200px"/>
+        </div>
+        <div class="form-group">
+          <label for="iframe_url" class="control-label">URL</label>
+          <input type="textbox" name="iframe_url" id="iframe_url" 
+                 class="form-control" placeholder="src for iframe"/>
+        </div>
+
+        <iframe id="iframe_preview" src="" height="200" width="640"></iframe>
+      </div>
+
+      <button class='btn btn-primary' type='submit' 
+        name='submit' value='submit' id='wanted_submit_btn' style='display:none'>Get Content</button>
+    </form>      
+
+</div>
+
+{% endblock %}
+
+{% block extra_js %}
+<script type='text/javascript' src='/static/lorem_ipsum.js'></script>
+{% endblock %}
diff --git a/templates/baconIpsumFetch.html b/templates/baconIpsumFetch.html
new file mode 100644
index 0000000..b74f747
--- /dev/null
+++ b/templates/baconIpsumFetch.html
@@ -0,0 +1,5 @@
+<div class='ipsum'>
+{% for p in paragraphs %}
+  <p>{{ p | safe }}</p>
+{% endfor %}
+</div>
diff --git a/templates/show_quotes.html b/templates/show_quotes.html
new file mode 100644
index 0000000..ce3a2e2
--- /dev/null
+++ b/templates/show_quotes.html
@@ -0,0 +1,14 @@
+<h3>{{ lorem.label }}</h3>
+{% for p in paragraphs %}
+<div class='content-box'>
+  <div class='grid-row'>
+    <div class='col-xs-1'>
+      <img class='avatar' style="width:75px; height: 75px" src="http://loremflickr.com/75/75?randomstuff={{ loop.index }}" width="75px" height="75px"/>
+    </div>
+    <div class='col-xs-11'>
+      <p>{{ p.quote | safe }}</p> 
+      <footer class='text-right'><cite title="{{ p.source }}"><em>{{ p.source }}</em></cite></footer>
+    </div>
+  </div>
+</div>
+{% endfor %}
diff --git a/templates/xml/config.xml b/templates/xml/config.xml
index df0ca36..0090ae3 100644
--- a/templates/xml/config.xml
+++ b/templates/xml/config.xml
@@ -28,5 +28,13 @@
         {% endif %}
       </lticm:options>
       {% endfor %}
+      {% if tool.editor_button %}
+      <lticm:options name="editor_button">
+        <lticm:property name="enabled">true</lticm:property>
+        <lticm:property name="icon_url">{{ tool.editor_button.icon_url }}</lticm:property>
+        <lticm:property name="selection_width">{{ tool.editor_button.selection_width }}</lticm:property>
+        <lticm:property name="selection_height">{{ tool.editor_button.selection_height }}</lticm:property>
+      </lticm:options>
+      {% endif %}
     </blti:extensions>
 </cartridge_basiclti_link>
