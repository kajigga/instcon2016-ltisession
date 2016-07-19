diff --git a/app.py b/app.py
index ebbeeae..5b2ce0e 100644
--- a/app.py
+++ b/app.py
@@ -2,7 +2,7 @@
 This file creates your application.
 """
 import os
-from flask import Flask, render_template, request, redirect, url_for, session, make_response
+from flask import Flask, render_template, request, redirect, url_for, session, make_response, jsonify
 
 from pylti.flask import lti
 from pylti.common import LTI_PROPERTY_LIST, LTI_ROLES
@@ -67,6 +67,8 @@ def error(*args, **kwargs):
 def first_lti_launch(lti, tool_id=None, *args, **kwargs):
   if tool_id == '0':
     return redirect('/lti/mapit')
+  elif tool_id == '1':
+    return redirect('/lti/yt_watch_for_points')
   else:
     return render_template('lti_profile.html')
 
@@ -76,6 +78,25 @@ G_API_KEY = 'AIzaSyDS7-sUBVXPy5XIjWJFsXzLf6fDEZtjFOw'
 def mapit_launch(lti):
   return render_template('mapit_launch.html',G_API_KEY=G_API_KEY)
 
+@app.route('/lti/yt_watch_for_points')
+@lti(error=error, request='session')
+#@lti(error=error, request='session', role='learner')
+#@lti(error=error, request='session', role='instructor')
+def yt_watch_for_points(lti, *args, **kwargs):
+  video_id = 'M7lc1UVf-VE'
+  return render_template('yt_watch_for_points.html', video_id=video_id)
+
+@app.route('/lti/yt_watch_for_points/finished', methods=['POST'])
+@lti(error=error, request='session')
+#@lti(error=error, request='session', role='learner')
+#@lti(error=error, request='session', role='instructor')
+def yt_watch_for_points_submit(lti, *args, **kwargs):
+  status = 'submitted'
+  response = lti.post_grade(request.form.get('score',0))
+  print('response', response)
+  return jsonify(status=response)
+
+
 @app.route('/lti/profile', methods=['GET'])
 @lti(error=error, request='session')
 def lti_profile(lti, *args, **kwargs):
@@ -97,8 +118,17 @@ tools = [{
       'text': 'S4: Mapper',
     }
   ]
-}
-]
+  },{ 
+  'domain' : SERVER_NAME,
+  'title' : 'Step 5-Watch Youtube - Get Grade',
+  'description' : '''This is the step 5 LTI Tool, with differentiated
+  functionality for students and teachers. Teach will add an assignment as
+  external tool, and select a youtube video. Students watch the video and get
+  points when they finish the video.''',
+
+  'url':'http://{}/lti/launch/{}'.format(SERVER_NAME, 1),
+  }]
+
 @app.route('/lti/config/<tool_id>')
 def lti_config(tool_id):
   tool_id = int(tool_id)
@@ -115,7 +145,7 @@ def lti_config(tool_id):
 @app.context_processor
 def inject_app_info():
   return {
-      'version':"0.0.1-step3",
+      'version':"0.0.1-step5",
       'project_name':'LTI Starter'
       }
 
diff --git a/static/video_watcher.js b/static/video_watcher.js
new file mode 100644
index 0000000..da99d9a
--- /dev/null
+++ b/static/video_watcher.js
@@ -0,0 +1,124 @@
+// This function creates an <iframe> (and YouTube player)
+// after the API code downloads.
+var player;
+function onYouTubeIframeAPIReady() {
+  get_video( function(video){
+    LTI_ENV.video = video;
+    console.log('got', video);
+
+    $('#video_id').val(video.video_id);
+    $('#minimum_percent').val(video.minimum_percent);
+    if(LTI_ENV.is_instructor){
+      $('#video_description').val(video.description);
+    }else{
+      $('#video_description').text(video.description);
+    }
+    player = new YT.Player('player', {
+      height: '390',
+      width: '640',
+      videoId: video.video_id,
+      playerVars: {
+        rel: 0,
+        modestbranding: 1
+      },
+      events: {
+        'onReady': onPlayerReady,
+        'onStateChange': onPlayerStateChange
+      }
+    });
+  
+  });
+}
+
+// The API will call this function when the video player is ready.
+var interval;
+function onPlayerReady(event) {
+  event.target.playVideo();
+  checkProgress(function(){
+    console.log('setting up interval');
+    interval = setInterval(checkProgress, 5000); // check every 10 seconds
+  });
+}
+
+// The API calls this function when the player's state changes.
+// The function indicates that when playing a video (state=1),
+// the player should play for six seconds and then stop.
+function onPlayerStateChange(event) {
+  //console.log(YT.PlayerState);
+  if (event.data == YT.PlayerState.ENDED ) {
+    console.log('currentTime', player.getCurrentTime());
+    console.log('duration', player.getDuration());
+    checkProgress();
+  }
+}
+
+function checkProgress(cb){
+  if(typeof(cb) != 'function'){ cb = function(){} };
+  if(LTI_ENV.is_instructor){
+    if(interval) { window.clearInterval(interval); }
+    cb();
+    return
+  }
+  if(player.getDuration() > 0  ){
+    // The player has watched at least 90% of the video
+    // Send signal that video is finished playing
+    // TODO make this take account of the minimum_percent
+
+    var min_duration = LTI_ENV.video.minimum_percent / 100 * player.getDuration();
+    var score = player.getCurrentTime() / min_duration; 
+    get_current_score(function(current_score){
+      var per_progress = Math.floor(current_score * 100);
+      $('#you_have_watched').text(per_progress);
+      $('#prog_bar').css('width',per_progress+'%').attr('aria-valuenow', per_progress).text(per_progress+'%');
+      console.log('updating score to ' + score);
+      if(score>=1){
+        window.clearInterval(interval);
+      }
+      if( current_score == false || score > current_score ){
+        $.post('/lti/yt_watch_for_points/finished',{score:score}).done( function(res, status){
+          scores_db.child(score_id()).set({score:score});
+          cb();
+        });
+      }else{
+        cb();
+      }
+    });
+  }else{
+    cb();
+  }
+}
+
+var firebase = new Firebase('https://burning-fire-7264.firebaseio.com/');
+var scores_db = firebase.child('scores:'+LTI_ENV.context_id);
+function get_current_score(callback){
+  var score = scores_db.child(score_id());
+  score.once('value', function(snapshot){
+    var ret_value = false;
+    if(snapshot.exists()){
+      ret_value = snapshot.val().score;
+    }
+    callback(ret_value);
+  });
+}
+
+function score_id(){
+  return LTI_ENV.resource_link_id + '::' + LTI_ENV.custom_canvas_user_id;
+}
+
+function get_video(cb){
+  var video_ref = scores_db.child('videos').child(LTI_ENV.resource_link_id);
+  video_ref.on('value', function(snapshot){
+    if (snapshot.exists()){
+      cb( snapshot.val())
+    }
+  });
+}
+
+function set_video_id(video_id, description, minimum_percent, cb){
+  scores_db.child('videos').child(LTI_ENV.resource_link_id).set({
+    video_id:video_id, 
+    description:description, 
+    minimum_percent:minimum_percent
+  },
+  cb());
+}
diff --git a/step_4.txt b/step_4.txt
deleted file mode 100644
index e69de29..0000000
diff --git a/step_5.txt b/step_5.txt
new file mode 100644
index 0000000..2068f9a
--- /dev/null
+++ b/step_5.txt
@@ -0,0 +1,8 @@
+
+In step 5 we will make an LTI app that will do:
+
+* Link selection
+* Resource selection
+* Rich Text Button, Lorem Ipsum
+* Rich Text button, iFrame Inserter
+* Student Views Page, javascript
diff --git a/templates/layout.html b/templates/layout.html
index f41f333..f18ff41 100644
--- a/templates/layout.html
+++ b/templates/layout.html
@@ -27,6 +27,7 @@
 
     <div class="container-fluid">
       <div class="header clearfix">
+        <!-- 
         <nav>
           <ul class="nav nav-pills pull-right">
             <li role="button" class="active"><a href="#">Home</a></li>
@@ -34,6 +35,7 @@
             <li role="button"><a href="#">Contact</a></li>
           </ul>
         </nav>
+        -->
         <h3 class="text-muted">{{ project_name }} <small>{{ version }}</small></h3>
       </div>
 
diff --git a/templates/mapit_launch.html b/templates/mapit_launch.html
index 59c361d..eb0e3e1 100644
--- a/templates/mapit_launch.html
+++ b/templates/mapit_launch.html
@@ -152,12 +152,13 @@
 {% endblock %}
 
 {% block extra_js %}
-<script src="https://cdn.firebase.com/js/client/2.2.1/firebase.js"></script>
 <script src="https://maps.googleapis.com/maps/api/js?key={{ G_API_KEY }}"></script>
+<script src="https://cdn.firebase.com/js/client/2.2.1/firebase.js"></script>
 <script>
 var LTI_ENV = { 
   custom_canvas_user_id: '{{ session.custom_canvas_user_id }}', 
   context_id: '{{session.context_id}}' ,
+  resource_link_id: '{{session.resource_link_id}}',
   is_instructor: false
 };
 </script>
@@ -169,11 +170,6 @@ var LTI_ENV = {
 {% endif %}
 
 <script>
-var LTI_ENV = { 
-  custom_canvas_user_id: '{{ session.custom_canvas_user_id }}', 
-  context_id: '{{session.context_id}}' ,
-  is_instructor: false
-};
 $(document).ready(function(){
   initMap();
   {% if 'Instructor' in session['ext_roles'] %}
diff --git a/templates/yt_watch_for_points.html b/templates/yt_watch_for_points.html
new file mode 100644
index 0000000..a4342bf
--- /dev/null
+++ b/templates/yt_watch_for_points.html
@@ -0,0 +1,90 @@
+{% extends "layout.html" %}
+
+{% block main_content %}
+<div class='row'>
+  <div class='col-md-12'>
+    {% if 'Learner' in session['ext_roles'] %}
+    <div class="progress">
+      <div id='prog_bar' class="progress-bar" role="progressbar" aria-valuenow="5"
+      aria-valuemin="0" aria-valuemax="5" style="width:5%">
+        70%
+      </div>
+    </div>
+    <p id='video_description'></p>
+    {% else %}
+    <form id='video_form' class='form'>
+      <div class="form-group">
+        <label for="video_id">Video ID</label>
+        <input type="textbox" class="form-control" id="video_id" placeholder="Youtube Video ID">
+      </div>
+      <div class="form-group">
+        <label for="video_description">Description</label>
+        <textarea rows='3' class="form-control" id="video_description" placeholder="e.g. description"></textarea>
+      </div>
+      <div class="form-group">
+        <label for="minimum_percent">What percentage of the video should be watched for full points?</label>
+        <input type="number" max='100' class="form-control" id="minimum_percent" placeholder="" value="100">
+      </div>
+
+      <div class="form-group">
+        <button type='submit' class='btn btn-default'>Save</button>
+      </div>
+    </form>
+    {% endif %}
+
+  </div>
+</div>
+<div class='row'>
+  <div class='col-md-12'>
+    <!-- 1. The <iframe> (and video player) will replace this <div> tag. -->
+    <div id="player"></div>
+    
+    {% if 'Learner' in session['ext_roles'] %}
+    <p>You have watched <span id="you_have_watched">...</span>% of 
+    this video. Your score is updated in the LMS every couple of seconds.
+    </p>
+    {% endif %}
+  </div>
+</div>
+{% endblock %}
+
+{% block extra_js %}
+
+<script src="https://www.youtube.com/iframe_api"></script>
+<script src="https://cdn.firebase.com/js/client/2.2.1/firebase.js"></script>
+
+<script>
+var LTI_ENV = { 
+  custom_canvas_user_id: '{{ session.custom_canvas_user_id }}', 
+  context_id: '{{session.context_id}}' ,
+  resource_link_id: '{{session.resource_link_id}}',
+  {% if 'Instructor' in session['ext_roles'] %}
+  is_instructor: true
+  {% else %}
+  is_instructor: false
+  {% endif %}
+};
+</script>
+<script src="/static/video_watcher.js"></script>
+<script>
+
+{% if 'Instructor' in session['ext_roles'] %}
+$(document).ready(function(){
+  $('#video_id').change(function(e){
+    // change_video_preview
+    // get the player, set the video to 
+    player.loadVideoById($('#video_id').val());
+  });
+  $('#video_form').submit(function(e){
+    set_video_id(
+        $('#video_id').val(), 
+        $('#video_description').val(), 
+        $('#minimum_percent').val(), 
+        function(){ });
+    e.preventDefault();
+  });
+});
+{% endif %}
+</script>
+
+{% endblock %}
