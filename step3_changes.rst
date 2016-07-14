 import os
-from flask import Flask, render_template, request, redirect, url_for, session
+from flask import Flask, render_template, request, redirect, url_for, session, make_response
+
+from pylti.flask import lti
+from pylti.common import LTI_PROPERTY_LIST, LTI_ROLES
+
 app = Flask(__name__)
 app.debug = True
 
+# set the secret key.  keep this really secret:
+app.secret_key = 'a0lkanvoiuas9d8faskdjaksjnvalisdfJ:{}{OIUzR98J/3Yx r~xhh!JMn]lwx/,?rt'
+
+
+# LTI Consumers
+consumers = {
+    "abc123": {"secret": "secretkey-for-abc123"}
+}
+
+SERVER_NAME = '0.0.0.0:5000'
+
+# Configure flask app with PYLTI config, specifically the consumers
+app.config['PYLTI_CONFIG'] = {'consumers': consumers}
+
+# Canvas sends some custom LTI launch parameters. Add these to the list of
+# known parameters so that pylti will save them.
+LTI_PROPERTY_LIST.extend([
+    'custom_canvas_api_domain',
+    'custom_canvas_course_id',
+    'custom_canvas_enrollment_state',
+    'custom_canvas_user_id',
+    'custom_canvas_user_login_id'
+])
+
+# Canvas uses full standard roles from the LTI spec. PYLTI does not include
+# them by default so we add these to the list of known roles.
+
+# NOTE: We can use my pylti package unless the main pylti maintainers accept my
+# pull request
+
+# This is the Administrator role and all of the different variations
+#LTI_ROLES[ 'urn:lti:instrole:ims/lis/Administrator' ] = [ 
+#    'urn:lti:instrole:ims/lis/Administrator', 
+#    'urn:lti:sysrole:ims/lis/SysAdmin'
+#]
+
+# This is the Instructor role
+#LTI_ROLES[ 'urn:lti:instrole:ims/lis/Instructor' ] = [ 'urn:lti:instrole:ims/lis/Instructor', ]
+
+# This is the student role
+#LTI_ROLES[ 'urn:lti:instrole:ims/lis/Student' ] = [ 
+#    'urn:lti:instrole:ims/lis/Student', 
+#    'urn:lti:instrole:ims/lis/Learner'
+#]
+
+
+#app.config['SERVER_NAME'] = 'localhost'
+# Make sure app uses https everywhere. This will become important when there
+# are actually LTI endpoints and configuration used.
+#app.config['PREFERRED_URL_SCHEME'] = 'https'
 
 @app.route('/')
 def index():
     # "index.html" is a file found in the "templates" folder. It is mostly regular
     # HTML with some special templating syntax mixed in. The templating
     # language is called Jinja.
-    return render_template('layout.html')
+    return render_template('index.html')
 
 @app.route('/hello_world')
 def hello_world():
     return 'Hello World!'
 
-@app.route('/lti/testlaunch', methods=['GET', 'POST'])
-def lti_test_launch():
-  # POST parameters
-  # print request.form.keys()
-  print request.args.keys()
-  return render_template('lti_test_launch.html', post=request.form, get=request.args)
+def error(*args, **kwargs):
+  # TODO Make a better Error Message screen
+  return '{}'.format(kwargs['exception'])
+
+@app.route('/lti/launch', methods=['POST'])
+@lti(error=error, request='initial')
+def first_lti_launch(lti, *args, **kwargs):
+  # return render_template('first_lti_launch.html')
+  return redirect('/lti/profile')
+
+@app.route('/lti/profile', methods=['GET'])
+@lti(error=error, request='session')
+def lti_profile(lti, *args, **kwargs):
+  return render_template('lti_profile.html')
+
+tools = [{ 
+  'domain' : SERVER_NAME,
+  'title' : 'Step 3 Config',
+  'description' : 'This is the step 3 config xml'
+},
+{ 
+  'domain' : SERVER_NAME,
+  'title' : 'Step 3.1 Config',
+  'description' : 'This is the step 3.1 config xml',
+  'nav' : [
+    {
+      'type':'course_navigation',
+      'enabled': True,
+      'default':'enabled',
+      # 'url':'', Is there a different launch URL for this navigation?
+      # 'visibility': '', # 'public', 'members', 'admins'
+      'text': 'course navigation text',
+      'labels': [
+        { 'locale': 'es', 'label': 'Utilidad LTI'},
+        { 'locale': 'en', 'label': 'LTI Tool'},
+      ]
+    },
+    { 
+      'type':'account_navigation',
+      'enabled': True,
+      'text': 'Acct. Link Text',
+      # 'url':'', Is there a different launch URL for this navigation?
+    }
+  ]
+}
+]
+@app.route('/lti/config/<tool_id>')
+def lti_config(tool_id):
+  tool_id = int(tool_id)
+  config_xml = render_template('xml/config.xml', tool=tools[tool_id])
+  response = make_response(config_xml)
+  response.headers["Content-Type"] = "application/xml"    
+
+  return response
 
 # I like to make certain values available on any rendered template without
 # explicitly naming them. While these values won't change very often, I would
@@ -32,7 +136,7 @@ def lti_test_launch():
 @app.context_processor
 def inject_app_info():
   return {
-      'version':"0.0.2-step2",
+      'version':"0.0.1-step3",
       'project_name':'LTI Starter'
       }
 
diff --git a/requirements.txt b/requirements.txt
index 5f2e95b..49e5573 100644
--- a/requirements.txt
+++ b/requirements.txt
@@ -6,7 +6,7 @@ flask
 #----
 # LTI stuff
 #----
-pylti
+git+https://github.com/kajigga/pylti.git
 
 
 
diff --git a/step_2.txt b/step_2.txt
deleted file mode 100644
index e69de29..0000000
diff --git a/step_3.txt b/step_3.txt
new file mode 100644
index 0000000..e69de29
diff --git a/templates/index.html b/templates/index.html
index 1ab149a..cc779ed 100644
--- a/templates/index.html
+++ b/templates/index.html
@@ -2,8 +2,7 @@
 
 {% block main_content %}
   {% if session['name'] %}
-  <p>Hello, {{ session['name'] }}, how are you?</p>
-  {% else %}
-  <p>Hello!  How are you?</p>
+  <p>Hello, {{ session['name'] }}!</p>
   {% endif %}
+  {{ session }}
 {% endblock %}
diff --git a/templates/lti_profile.html b/templates/lti_profile.html
new file mode 100644
index 0000000..71af392
--- /dev/null
+++ b/templates/lti_profile.html
@@ -0,0 +1,17 @@
+{% extends "layout.html" %}
+
+{% block main_content %}
+  {% if session['lis_person_name_full'] %}
+  <h2>{{ session['lis_person_name_full'] }}</h2>
+  {% endif %}
+
+  <h3>LTI Session Values</h3>
+  <table class='table table-striped'>
+      {% for key in session|sort %}
+      <tr>
+        <th>{{ key }}</th>
+        <td>{{ session[key] }}</td>
+      </tr>
+      {% endfor %}
+  </dl>
+{% endblock %}
diff --git a/templates/lti_test_launch.html b/templates/lti_test_launch.html
deleted file mode 100644
index 17509fa..0000000
--- a/templates/lti_test_launch.html
+++ /dev/null
@@ -1,30 +0,0 @@
-{% extends "layout.html" %}
-
-{% block main_content %}
-
-<div class='row'>
-  <div class='col-md-12'>
-    <h3>GET Parameters</h3>
-    <table class='table table-striped'>
-      <tr><th>key</th><th>value</th></tr>
-      {% for k in get | dictsort %}
-      <tr>
-        <td>{{ k[0] }}</td>
-        <td>{{ k[1] }}</td>
-      </tr>
-      {% endfor %}
-    </table>
-    <h3>POST Parameters</h3>
-    <table class='table table-striped'>
-      <tr><th>key</th><th>value</th></tr>
-      {% for k in post | dictsort %}
-      <tr>
-        <td>{{ k[0] }}</td>
-        <td>{{ k[1] }}</td>
-      </tr>
-      {% endfor %}
-    </table>
-
-  </div>
-</div>
-{% endblock %}
diff --git a/templates/xml/config.xml b/templates/xml/config.xml
new file mode 100644
index 0000000..78af11d
--- /dev/null
+++ b/templates/xml/config.xml
@@ -0,0 +1,32 @@
+<?xml version="1.0" encoding="UTF-8"?>
+<cartridge_basiclti_link xmlns="http://www.imsglobal.org/xsd/imslticc_v1p0"
+    xmlns:blti = "http://www.imsglobal.org/xsd/imsbasiclti_v1p0"
+    xmlns:lticm ="http://www.imsglobal.org/xsd/imslticm_v1p0"
+    xmlns:lticp ="http://www.imsglobal.org/xsd/imslticp_v1p0"
+    xmlns:xsi = "http://www.w3.org/2001/XMLSchema-instance"
+    xsi:schemaLocation = "http://www.imsglobal.org/xsd/imslticc_v1p0 http://www.imsglobal.org/xsd/lti/ltiv1p0/imslticc_v1p0.xsd
+    http://www.imsglobal.org/xsd/imsbasiclti_v1p0 http://www.imsglobal.org/xsd/lti/ltiv1p0/imsbasiclti_v1p0.xsd
+    http://www.imsglobal.org/xsd/imslticm_v1p0 http://www.imsglobal.org/xsd/lti/ltiv1p0/imslticm_v1p0.xsd
+    http://www.imsglobal.org/xsd/imslticp_v1p0 http://www.imsglobal.org/xsd/lti/ltiv1p0/imslticp_v1p0.xsd">
+    <blti:launch_url>{{ protocol|default('http') }}://{{ tool.domain }}/lti/launch</blti:launch_url>
+    <blti:title>{{ tool.title }}</blti:title>
+    <blti:description>{{ tool.description }}</blti:description>
+    <blti:extensions platform="canvas.instructure.com">
+      <lticm:property name="privacy_level">public</lticm:property>
+      <lticm:property name="domain">{{ tool.domain }}</lticm:property>
+      <lticm:property name="text">{{ tool.title }}</lticm:property>
+      {% for nav in tool.nav %}
+      <lticm:options name="{{ nav.type }}">
+        <lticm:property name="enabled">{{ nav.enabled }}</lticm:property>
+        <lticm:property name="default">{{ nav.default }}</lticm:property>
+        {% if nav.url %}<lticm:property name="url">nav.url</lticm:property>{% endif %}
+        {% if nav.icon_url %}<lticm:property name="icon_url">https://dl.dropboxusercontent.com/u/1647772/lti.png</lticm:property>{% endif %}
+        {% if nav.labels %}<lticm:options name="labels">
+        {% for label in nav.labels %}
+        <lticm:property name="{{ label.locale }}">{{ label.label }}</lticm:property> 
+        {% endfor %}</lticm:options>
+        {% endif %}
+      </lticm:options>
+      {% endfor %}
+    </blti:extensions>
+</cartridge_basiclti_link>
