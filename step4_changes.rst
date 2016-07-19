diff --git a/app.py b/app.py
index df374dc..ebbeeae 100644
--- a/app.py
+++ b/app.py
@@ -33,31 +33,15 @@ LTI_PROPERTY_LIST.extend([
     'custom_canvas_course_id',
     'custom_canvas_enrollment_state',
     'custom_canvas_user_id',
-    'custom_canvas_user_login_id'
+    'custom_canvas_user_login_id',
+    'ext_content_return_types',
+    'ext_outcome_data_values_accepted',
+    'ext_outcome_result_total_score_accepted',
+    'ext_content_intended_use',
+    'ext_content_return_url',
+    'ext_content_file_extensions'
 ])
 
-# Canvas uses full standard roles from the LTI spec. PYLTI does not include
-# them by default so we add these to the list of known roles.
-
-# NOTE: We can use my pylti package unless the main pylti maintainers accept my
-# pull request
-
-# This is the Administrator role and all of the different variations
-#LTI_ROLES[ 'urn:lti:instrole:ims/lis/Administrator' ] = [ 
-#    'urn:lti:instrole:ims/lis/Administrator', 
-#    'urn:lti:sysrole:ims/lis/SysAdmin'
-#]
-
-# This is the Instructor role
-#LTI_ROLES[ 'urn:lti:instrole:ims/lis/Instructor' ] = [ 'urn:lti:instrole:ims/lis/Instructor', ]
-
-# This is the student role
-#LTI_ROLES[ 'urn:lti:instrole:ims/lis/Student' ] = [ 
-#    'urn:lti:instrole:ims/lis/Student', 
-#    'urn:lti:instrole:ims/lis/Learner'
-#]
-
-
 #app.config['SERVER_NAME'] = 'localhost'
 # Make sure app uses https everywhere. This will become important when there
 # are actually LTI endpoints and configuration used.
@@ -78,11 +62,19 @@ def error(*args, **kwargs):
   # TODO Make a better Error Message screen
   return '{}'.format(kwargs['exception'])
 
-@app.route('/lti/launch', methods=['POST'])
+@app.route('/lti/launch/<tool_id>', methods=['POST'])
 @lti(error=error, request='initial')
-def first_lti_launch(lti, *args, **kwargs):
-  # return render_template('first_lti_launch.html')
-  return redirect('/lti/profile')
+def first_lti_launch(lti, tool_id=None, *args, **kwargs):
+  if tool_id == '0':
+    return redirect('/lti/mapit')
+  else:
+    return render_template('lti_profile.html')
+
+G_API_KEY = 'AIzaSyDS7-sUBVXPy5XIjWJFsXzLf6fDEZtjFOw'
+@app.route('/lti/mapit')
+@lti(error=error, request='session')
+def mapit_launch(lti):
+  return render_template('mapit_launch.html',G_API_KEY=G_API_KEY)
 
 @app.route('/lti/profile', methods=['GET'])
 @lti(error=error, request='session')
@@ -91,31 +83,18 @@ def lti_profile(lti, *args, **kwargs):
 
 tools = [{ 
   'domain' : SERVER_NAME,
-  'title' : 'Step 3 Config',
-  'description' : 'This is the step 3 config xml'
-},
-{ 
-  'domain' : SERVER_NAME,
-  'title' : 'Step 3.1 Config',
-  'description' : 'This is the step 3.1 config xml',
+  'title' : 'Step 4-Module',
+  'description' : '''This is the step 4 LTI Tool, with differentiated
+  functionality for students and teachers, course navigation, and module item
+  navigation.''',
+  'url':'http://{}/lti/launch/{}'.format(SERVER_NAME, 0),
   'nav' : [
     {
       'type':'course_navigation',
       'enabled': True,
       'default':'enabled',
-      # 'url':'', Is there a different launch URL for this navigation?
       # 'visibility': '', # 'public', 'members', 'admins'
-      'text': 'course navigation text',
-      'labels': [
-        { 'locale': 'es', 'label': 'Utilidad LTI'},
-        { 'locale': 'en', 'label': 'LTI Tool'},
-      ]
-    },
-    { 
-      'type':'account_navigation',
-      'enabled': True,
-      'text': 'Acct. Link Text',
-      # 'url':'', Is there a different launch URL for this navigation?
+      'text': 'S4: Mapper',
     }
   ]
 }
diff --git a/static/map_lti.js b/static/map_lti.js
new file mode 100644
index 0000000..760b061
--- /dev/null
+++ b/static/map_lti.js
@@ -0,0 +1,141 @@
+var firebase = new Firebase('https://burning-fire-7264.firebaseio.com/'); //#-KGMjngqOsfdYmQVAuOQ|84de6e0176b2809975487d2c428c4965');
+var marker_db = firebase.child('markers:'+LTI_ENV.context_id);
+var map;
+var gc = new google.maps.Geocoder();
+var infowindow;
+var all_markers = {};
+
+function initMap() {
+  map = new google.maps.Map(document.getElementById('map'), {
+    zoom: 8,
+    center: {lat: 39.57605638518604, lng: -105.9521484375},  // Keystone, Colorado
+    zoomControl: true,
+    mapTypeControl: false,
+    scaleControl: false,
+    streetViewControl: false,
+    rotateControl: false,
+    fullscreenControl: false
+  });
+
+  infowindow = new google.maps.InfoWindow();
+  google.maps.event.addListener(infowindow, 'domready', function() {
+
+   // Reference to the DIV which receives the contents of the infowindow using jQuery
+   var iwOuter = $('.gm-style-iw');
+
+   /* The DIV we want to change is above the .gm-style-iw DIV.
+    * So, we use jQuery and create a iwBackground variable,
+    * and took advantage of the existing reference to .gm-style-iw for the previous DIV with .prev().
+    */
+   var iwBackground = iwOuter.prev();
+
+   // Remove the background shadow DIV
+   iwBackground.children(':nth-child(2)').css({'display' : 'none'});
+
+   // Remove the white background DIV
+   iwBackground.children(':nth-child(4)').css({'display' : 'none'});
+
+   var iwCloseBtn = iwOuter.next();
+
+    // Apply the desired effect to the close button
+    iwCloseBtn.css({
+      opacity: '1', // by default the close button has an opacity of 0.7
+      right: '9px', top: '-4px', // button repositioning
+      border: '7px solid #48b5e9', // increasing button border and new color
+      'width':  '40px',
+      'height': '40px',
+      'background-color': '#fff',
+      'border-radius': '20px', // circular effect
+      'box-shadow': '0 0 5px #3990B9' // 3D effect to highlight the button
+      });
+    iwCloseBtn.find('img').css({
+      left: '5px',
+      top: '-328px'
+    });
+
+
+    // The API automatically applies 0.7 opacity to the button after the mouseout event.
+    // This function reverses this event to the desired value.
+    iwCloseBtn.mouseout(function(){
+      $(this).css({opacity: '1'});
+    });
+
+});
+}
+
+marker_db.orderByChild("order").on("child_added", function(snapshot, prevChildKey) {
+  // Get latitude and longitude from Firebase.
+  var newPosition = snapshot.val();
+
+  // Create a google.maps.LatLng object for the position of the marker.
+  // A LatLng object literal (as above) could be used, but the heatmap
+  // in the next step requires a google.maps.LatLng object.
+  var latLng = new google.maps.LatLng(newPosition.lat, newPosition.lng);
+  setupMarker(latLng, newPosition);
+});
+
+function marker_id(info){
+  return LTI_ENV.custom_canvas_user_id +'::'+LTI_ENV.context_id+'::'+
+      info.lat.toString().replace('.','')+
+      '::'+info.lng.toString().replace('.','')
+}
+
+function setupMarker(latLng, info){
+  if(info.id == undefined || info.id == ''){
+    info.id = marker_id(info) ;
+  }
+
+  // Place a marker at that location.
+  var draggable = LTI_ENV.is_instructor;
+  var marker = new google.maps.Marker({
+    position: latLng,
+    map: map,
+    title:' some title ',
+    draggable: draggable
+  });
+
+  info.marker = marker;
+  all_markers[info.id] = info;
+  // Add a click handler to the marker so it shows the info window when...clicked
+  marker.addListener('click', function(){
+    show_info_window( info );
+    setSelectedMarker(marker, all_markers[info.id]);
+  });
+  if(LTI_ENV.is_instructor){
+    marker.addListener('dragend', function(e){
+
+      var m_info = all_markers[info.id];
+      m_info.lat = e.latLng.lat();
+      m_info.lng = e.latLng.lng();
+      saveMarker( m_info);
+    });
+  }
+
+  $('#marker-list>ul li').remove();
+  if(prep_m_list){ prep_m_list(); };
+}
+
+function setSelectedMarker( marker, info){
+  $('#selected_marker_id').val(info.id); 
+  $('#selected_marker_label').val(info.label); 
+  $('#selected_marker_description').val(info.description); 
+  $('#selected_marker_image').val(info.image); 
+  selected_marker = {marker:marker, info: info};
+};
+
+function show_info_window( info ){
+  var img_src = (all_markers[info.id].image) ? '<img src="'+ all_markers[info.id].image+'" width="100px" />' : '' ;
+  var content = '<div id="iw-container" data-info-id="'+all_markers[info.id].id+'"> ' +
+                  '<div class="iw-title">'+ all_markers[info.id].label +'</div>' +
+                  '<div class="iw-content">' +
+                    '<div class="iw-subTitle">subtitle</div>' +
+                    img_src+
+                    '<p class="marker_description">'+ all_markers[info.id].description +'</p>' +
+                  '</div>' +
+                  '<div class="iw-bottom-gradient"></div>' +
+                '</div>';
+
+  infowindow.setContent(content);
+  infowindow.open(map, info.marker); 
+};
+
diff --git a/static/map_lti_inst.js b/static/map_lti_inst.js
new file mode 100644
index 0000000..42c783e
--- /dev/null
+++ b/static/map_lti_inst.js
@@ -0,0 +1,125 @@
+function searchAndRecenter(search){
+  console.log('search', search);
+  gc.geocode(search, function(results, status){
+    if (status == google.maps.GeocoderStatus.OK) {
+      map.setCenter(results[0].geometry.location);
+      var marker = new google.maps.Marker({
+          map: map,
+          position: results[0].geometry.location
+      });
+    } else {
+      alert("Geocode was not successful for the following reason: " + status);
+    }
+  });
+
+}
+
+function saveMarker(info){
+  if(info.id == undefined || info.id == ''){
+    info.id = marker_id(info) ;
+  }
+  var info_to_save = $.extend({}, info, {});
+  delete info_to_save.marker;
+  marker_db.child(info.id).set(info_to_save);
+}
+
+function delete_marker( id, callback) {
+  marker_db.child(id).remove( callback);
+}
+
+
+var initMapInstructor = function(){
+  $('#instructor_controls').submit(function(e){
+    var search = {
+     address: $('#newLocation').val(),
+    };
+    searchAndRecenter( search );
+    e.preventDefault(); 
+  });
+  $('#marker_editor').change(function(e){
+
+    var m_info = all_markers[$('#selected_marker_id').val()];
+    m_info.label = $('#selected_marker_label').val();
+    m_info.description = $('#selected_marker_description').val();
+    m_info.image = $('#selected_marker_image').val();
+
+    saveMarker( m_info);
+    prep_m_list();
+    e.preventDefault();
+  });
+  /*$('#marker_editor').submit(function(e){
+    // Save the values from the marker editor to Firebase
+    console.log('editor submitted');
+    var m_info = all_markers[$('#selected_marker_id').val()];
+    m_info.label = $('#selected_marker_label').val();
+    m_info.description = $('#selected_marker_description').val();
+    m_info.image = $('#selected_marker_image').val();
+
+    saveMarker( m_info);
+    prep_m_list();
+    e.preventDefault();
+  });
+  */
+
+  map.addListener('click', function(e) {
+    var info = {order: all_markers.length, lat: e.latLng.lat(), lng: e.latLng.lng(), label: '', description:''};
+
+    saveMarker(info)
+    //marker_db.push(info);
+
+    var latLng = new google.maps.LatLng(e.latLng.lat(), e.latLng.lng());
+    setupMarker(latLng, info)
+
+  });
+};
+
+function prep_m_list(){
+  $('#marker-list>ul').empty();
+  $.each(all_markers, function(idx, mark){
+    var el = $('<li data-id="'+ mark.id +'" class="marker-row"><i class="glyphicon glyphicon-trash"></i><i class="glyphicon glyphicon-move"></i> <span class="_label">'+mark.label+'<span></li>');
+    $('#marker-list>ul').append(el);
+    //el.find('i.glyphicon.glyphicon-trash').click(function(mark.id){ 
+    el.find('i.glyphicon.glyphicon-trash').click(function(e){ 
+      console.log('delete clicked ' ); 
+      console.log(mark.id);
+      mark.marker.setMap(null);
+      delete all_markers[mark.id];
+      delete_marker(mark.id, function(){
+        prep_m_list();
+      });
+    });
+    el.find('._label, .glyphicon.glyphicon-move').click(function(e){
+     show_info_window( mark );
+     setSelectedMarker(mark.marker, mark);
+    });
+  });
+  setListSortable($('#marker-list ul')[0]);
+}
+
+function setListSortable(el){
+  // var sortable = Sortable.create(el);
+  var sortable = new Sortable(el, {
+  // dragging started
+    onStart: function (/**Event*/evt) {
+        evt.oldIndex;  // element index within parent
+    },
+
+    // dragging ended
+    onEnd: function (/**Event*/evt) {
+        console.log($(evt.item).data('id'));
+        var id = $(evt.item).data('id');
+
+        all_markers[id].order = evt.newIndex;
+        saveMarker(all_markers[id]);
+        var items = $(evt.target).find('li');
+        for(var x=evt.newIndex+1, l=items.length; x<l; x++){
+          id = $(items[x]).data('id');
+          all_markers[id].order = x+1;
+          saveMarker(all_markers[id]);
+        }
+        //evt.oldIndex;  // element's old index within parent
+        //evt.newIndex;  // element's new index within parent
+        //
+    },
+  });
+}
diff --git a/static/map_lti_student.js b/static/map_lti_student.js
new file mode 100644
index 0000000..e69de29
diff --git a/step_3.txt b/step_3.txt
deleted file mode 100644
index e69de29..0000000
diff --git a/step_4.txt b/step_4.txt
new file mode 100644
index 0000000..e69de29
diff --git a/templates/layout.html b/templates/layout.html
index d8cb913..f41f333 100644
--- a/templates/layout.html
+++ b/templates/layout.html
@@ -3,7 +3,7 @@
   <head>
     <meta charset="utf-8">
     <meta http-equiv="X-UA-Compatible" content="IE=edge">
-    <meta name="viewport" content="width=device-width, initial-scale=1">
+    <meta name="viewport" content="width=device-width, initial-scale=1, user-scalable=no">
     <!-- The above 3 meta tags *must* come first in the head; any other head content must come *after* these tags -->
 
     <title>{{ project_name }} : LTI Index</title>
@@ -20,6 +20,7 @@
       <script src="https://oss.maxcdn.com/html5shiv/3.7.2/html5shiv.min.js"></script>
       <script src="https://oss.maxcdn.com/respond/1.4.2/respond.min.js"></script>
     <![endif]-->
+    {% block extra_css %}{% endblock %}
   </head>
 
   <body>
@@ -40,23 +41,7 @@
       <div class="starter-template">
         <h1>{{ page_title }}</h1>
 
-        {% block main_content %}
-          <p class="lead">If you are seeing this text, then you haven't 
-          extended the <em>main_content</em> block. All you get is this text and a mostly barebones HTML
-          document.</p>
-<pre>
-<code>
-{% raw %}
-{% extends "layout.html" %}
-
-{% block main_content %}
-Anything here will be the content of the block.
-{% endblock %}
-
-{% endraw %}
-</code>
-</pre>
-        {% endblock %}
+        {% block main_content %}{% endblock %}
       </div>
 
     </div><!-- /.container -->
@@ -70,5 +55,7 @@ Anything here will be the content of the block.
     <!-- Latest compiled and minified JavaScript -->
     <script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.6/js/bootstrap.min.js" integrity="sha384-0mSbJDEHialfmuBBQP6A4Qrprq5OVfW37PRR3j5ELqxss1yVqOtnepnHVP9aJ7xS" crossorigin="anonymous"></script>
 
+    {% block extra_js %}{% endblock %}
+
   </body>
 </html>
diff --git a/templates/mapit_launch.html b/templates/mapit_launch.html
new file mode 100644
index 0000000..59c361d
--- /dev/null
+++ b/templates/mapit_launch.html
@@ -0,0 +1,188 @@
+{% extends "layout.html" %}
+
+{% block main_content %}
+<div class='row'>
+  <div class='col-md-6'>
+    {% if 'Learner' in session['ext_roles'] %}
+      <p>You are a student, this page should load a map that was created by the
+      instructor before the course was published.</p>
+    {% endif %}
+
+    {% if 'Instructor' in session['ext_roles'] %}
+    <p>You are an instructor.</p>
+
+    <form id='instructor_controls'>
+      <div class='form-group'>
+        <label for='recenterLocation'>Search Location</label>
+        <input type='textbox' class='form-control' id='newLocation'
+        placeholder='e.g. "Dallas, Texas"'>
+      </div>
+    </form>
+    {% endif %}
+    <div id='map'></div>
+    
+  </div>
+  
+  <div class='col-md-6'>
+    <div id='total'></div>
+    <div id='right-panel'>
+      <h2>Marks</h2> 
+      {% if 'Instructor' in session['ext_roles'] %}
+      <form id='marker_editor'>
+        <input type='hidden' id='selected_marker_id'>
+        <div class='form-group'>
+          <label for='marker_label'>Label</label>
+          <input type='textbox' class='form-control' name='marker_label'
+          id='selected_marker_label'
+          placeholder='e.g. Place where Pecos Bill shot his first buffalo.'>
+        </div>
+        <div class='form-group'>
+          <label for='marker_image'>Image</label>
+          <input type='textbox' class='form-control' name='image'
+          id='selected_marker_image'
+          placeholder='e.g. url to image'>
+        </div>
+        <div class='form-group'>
+          <label for='marker_description'>Description</label>
+          <textarea rows='4' type='textbox' class='form-control' name='description'
+          id='selected_marker_description'
+          placeholder='e.g. Description about place where Pecos Bill shot his first buffalo.'>
+          </textarea>
+        </div>
+      </form>
+      <div id='marker-list'>
+        <ul >
+        </ul> 
+      </div>
+      {% else %}
+      <dl>
+        <dt>Label</dt>
+        <dd id='marker_label'></dd>
+        <dt>Description</dt>
+        <dd id='marker_description'></dd>
+      </dl>
+      {% endif %}
+    </div>
+  </div>
+</div>
+
+{% endblock %}
+
+{% block extra_css %}
+<style>
+  html, body {
+    height: 100%;
+    margin: 0;
+    padding: 0;
+  }
+  #map {
+    width: 100%%;
+    height: 500px;
+  }
+
+  /* Google Map Styles see
+     http://en.marnoto.com/2014/09/5-formas-de-personalizar-infowindow.html */
+  #map-canvas {
+    margin: 0;
+    padding: 0;
+    height: 400px;
+    max-width: none;
+  }
+  #map-canvas img {
+    max-width: none !important;
+  }
+  .gm-style-iw {
+    width: 350px !important; 
+    top: 15px !important;
+    left: 0px !important;
+    background-color: #fff;
+    box-shadow: 0 1px 6px rgba(178, 178, 178, 0.6);
+    border: 1px solid rgba(72, 181, 233, 0.6);
+    border-radius: 2px 2px 10px 10px;
+  }
+  #iw-container {
+    margin-bottom: 10px;
+  }
+  #iw-container .iw-title {
+    font-family: 'Open Sans Condensed', sans-serif;
+    font-size: 22px;
+    font-weight: 400;
+    padding: 10px;
+    background-color: #48b5e9;
+    color: white;
+    margin: 0;
+    border-radius: 2px 2px 0 0;
+  }
+  #iw-container .iw-content {
+    font-size: 13px;
+    line-height: 18px;
+    font-weight: 400;
+    margin-right: 1px;
+    padding: 15px 5px 20px 15px;
+    max-height: 140px;
+    overflow-y: auto;
+    overflow-x: hidden;
+    width: 350px;
+  }
+  .iw-content img {
+    float: right;
+    margin: 0 5px 5px 10px;	
+  }
+  .iw-subTitle {
+    font-size: 16px;
+    font-weight: 700;
+    padding: 5px 0;
+  }
+  .iw-bottom-gradient {
+    position: absolute;
+    width: 326px;
+    height: 25px;
+    bottom: 10px;
+    right: 18px;
+    background: linear-gradient(to bottom, rgba(255,255,255,0) 0%, rgba(255,255,255,1) 100%);
+    background: -webkit-linear-gradient(top, rgba(255,255,255,0) 0%, rgba(255,255,255,1) 100%);
+    background: -moz-linear-gradient(top, rgba(255,255,255,0) 0%, rgba(255,255,255,1) 100%);
+    background: -ms-linear-gradient(top, rgba(255,255,255,0) 0%, rgba(255,255,255,1) 100%);
+  }
+
+  .marker-row { cursor: pointer; }
+  .marker-row i { color: green; }
+
+</style>
+{% endblock %}
+
+{% block extra_js %}
+<script src="https://cdn.firebase.com/js/client/2.2.1/firebase.js"></script>
+<script src="https://maps.googleapis.com/maps/api/js?key={{ G_API_KEY }}"></script>
+<script>
+var LTI_ENV = { 
+  custom_canvas_user_id: '{{ session.custom_canvas_user_id }}', 
+  context_id: '{{session.context_id}}' ,
+  is_instructor: false
+};
+</script>
+
+<script src="/static/map_lti.js"></script>
+{% if 'Instructor' in session['ext_roles'] %}
+<script src="/static/map_lti_inst.js"></script>
+<script src="//cdnjs.cloudflare.com/ajax/libs/Sortable/1.4.2/Sortable.min.js"></script>
+{% endif %}
+
+<script>
+var LTI_ENV = { 
+  custom_canvas_user_id: '{{ session.custom_canvas_user_id }}', 
+  context_id: '{{session.context_id}}' ,
+  is_instructor: false
+};
+$(document).ready(function(){
+  initMap();
+  {% if 'Instructor' in session['ext_roles'] %}
+  LTI_ENV.is_instructor = true;
+  initMapInstructor();
+  {% else %}
+  LTI_ENV.is_instructor = false;
+  {% endif %}
+});
+</script>
+
+{% endblock %}
diff --git a/templates/mapit_launch_with_directions.html b/templates/mapit_launch_with_directions.html
new file mode 100644
index 0000000..5853bc8
--- /dev/null
+++ b/templates/mapit_launch_with_directions.html
@@ -0,0 +1,192 @@
+{% extends "layout.html" %}
+
+{% block main_content %}
+<div class='row'>
+  <div class='col-md-6'>
+    {% if 'Learner' in session['ext_roles'] %}
+      <p>You are a student, this page should load a map that was created by the
+      instructor before the course was published.</p>
+    {% endif %}
+
+    {% if 'Instructor' in session['ext_roles'] %}
+    <p>You are an instructor.</p>
+
+    <form id='instructor_controls'>
+      <div class='form-group'>
+        <label for='recenterLocation'>Search Location</label>
+        <input type='textbox' class='form-control' id='newLocation'
+        placeholder='e.g. "Dallas, Texas"'>
+      </div>
+      <!--
+      <div class='form-group'>
+        <label for='recenterLocation'>Start Location</label>
+        <input type='textbox' class='form-control' id='startLocation'
+        placeholder='e.g. "Dallas, Texas"'>
+      </div>
+      <div class='form-group'>
+        <label for='recenterLocation'>End Location</label>
+        <input type='textbox' class='form-control' id='endLocation'
+        placeholder='e.g. "Dallas, Texas"'>
+      </div>
+      -->
+    </form>
+    {% endif %}
+    <div id='map'></div>
+    
+  </div>
+  
+  <div class='col-md-6'>
+    <div id='total'></div>
+    <div id='right-panel'>
+    
+    </div>
+  </div>
+</div>
+{% endblock %}
+
+{% block extra_css %}
+<style>
+  html, body {
+    height: 100%;
+    margin: 0;
+    padding: 0;
+  }
+  #map {
+    width: 100%%;
+    height: 500px;
+  }
+</style>
+{% endblock %}
+
+{% block extra_js %}
+<script src="https://cdn.firebase.com/js/client/2.2.1/firebase.js"></script>
+<script src="https://maps.googleapis.com/maps/api/js?key={{ G_API_KEY }}"></script>
+
+<script>
+var g_api_key='{{ G_API_KEY }}';
+var firebase = new Firebase('https://burning-fire-7264.firebaseio.com/'); //#-KGMjngqOsfdYmQVAuOQ|84de6e0176b2809975487d2c428c4965');
+var marker_db = firebase.child('markers');
+var map;
+var gc = new google.maps.Geocoder();
+
+function initMap() {
+  map = new google.maps.Map(document.getElementById('map'), {
+    zoom: 1,
+    center: {lat: 39.57605638518604, lng: -105.9521484375},  // Keystone, Colorado
+    zoomControl: false,
+    mapTypeControl: false,
+    scaleControl: false,
+    streetViewControl: false,
+    rotateControl: false,
+    fullscreenControl: false
+  });
+
+  var directionsService = new google.maps.DirectionsService;
+  var directionsDisplay = new google.maps.DirectionsRenderer({
+    draggable: true,
+    map: map,
+    panel: document.getElementById('right-panel')
+  });
+
+  directionsDisplay.addListener('directions_changed', function() {
+    computeTotalDistance(directionsDisplay.getDirections());
+  });
+
+  displayRoute('Denver, CO', 'Keystone, CO', directionsService,
+      directionsDisplay);
+
+  map.addListener('click', function(e) {
+    var info = {lat: e.latLng.lat(), lng: e.latLng.lng(), label: '', description:''};
+    marker_db.push(info);
+
+    var latLng = new google.maps.LatLng(e.latLng.lat(), e.latLng.lng());
+    setupMarker(latLng, info)
+
+  });
+}
+
+marker_db.on("child_added", function(snapshot, prevChildKey) {
+  // Get latitude and longitude from Firebase.
+  var newPosition = snapshot.val();
+
+  // Create a google.maps.LatLng object for the position of the marker.
+  // A LatLng object literal (as above) could be used, but the heatmap
+  // in the next step requires a google.maps.LatLng object.
+  var latLng = new google.maps.LatLng(newPosition.lat, newPosition.lng);
+  setupMarker(latLng, newPosition);
+});
+
+function setupMarker(latLng, info){
+
+  var infowindow = new google.maps.InfoWindow({ content: info.description });
+  // Place a marker at that location.
+  var marker = new google.maps.Marker({
+    position: latLng,
+    map: map,
+    title:'',
+  });
+
+  // Add a click handler to the marker so it shows the info window when...clicked
+  marker.addListener('click', function(){
+    infowindow.open(map, marker); 
+  });
+}
+
+function displayRoute(origin, destination, service, display) {
+  service.route({
+    origin: origin,
+    destination: destination,
+    waypoints: [{location: 'Boulder, CO'}, {location: 'Black Hawk, CO'}],
+    travelMode: google.maps.TravelMode.DRIVING,
+    avoidTolls: true
+  }, function(response, status) {
+    if (status === google.maps.DirectionsStatus.OK) {
+      display.setDirections(response);
+    } else {
+      alert('Could not display directions due to: ' + status);
+    }
+  });
+}
+
+function computeTotalDistance(result) {
+  var total = 0;
+  var myroute = result.routes[0];
+  for (var i = 0; i < myroute.legs.length; i++) {
+    total += myroute.legs[i].distance.value;
+  }
+  total = total / 1000;
+  document.getElementById('total').innerHTML = total + ' km';
+}
+
+function searchAndRecenter(search){
+  console.log('search', search);
+  gc.geocode(search, function(results, status){
+    if (status == google.maps.GeocoderStatus.OK) {
+      map.setCenter(results[0].geometry.location);
+      var marker = new google.maps.Marker({
+          map: map,
+          position: results[0].geometry.location
+      });
+    } else {
+      alert("Geocode was not successful for the following reason: " + status);
+    }
+  });
+
+}
+
+
+google.maps.event.addDomListener(window, "load", initMap);
+
+$(document).ready(function(){
+  $('#instructor_controls').submit(function(e){
+    var search = {
+     address: $('#newLocation').val(),
+    };
+    searchAndRecenter( search );
+    event.preventDefault(); 
+  });
+});
+
+</script>
+
+{% endblock %}
diff --git a/templates/xml/config.xml b/templates/xml/config.xml
index 78af11d..df0ca36 100644
--- a/templates/xml/config.xml
+++ b/templates/xml/config.xml
@@ -8,7 +8,7 @@
     http://www.imsglobal.org/xsd/imsbasiclti_v1p0 http://www.imsglobal.org/xsd/lti/ltiv1p0/imsbasiclti_v1p0.xsd
     http://www.imsglobal.org/xsd/imslticm_v1p0 http://www.imsglobal.org/xsd/lti/ltiv1p0/imslticm_v1p0.xsd
     http://www.imsglobal.org/xsd/imslticp_v1p0 http://www.imsglobal.org/xsd/lti/ltiv1p0/imslticp_v1p0.xsd">
-    <blti:launch_url>{{ protocol|default('http') }}://{{ tool.domain }}/lti/launch</blti:launch_url>
+    <blti:launch_url>{{ tool.url }}</blti:launch_url>
     <blti:title>{{ tool.title }}</blti:title>
     <blti:description>{{ tool.description }}</blti:description>
     <blti:extensions platform="canvas.instructure.com">
