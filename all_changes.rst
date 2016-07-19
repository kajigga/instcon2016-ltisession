Step 2 Changes
===============

modify app.py
-------------
line 20, change
    return render_template('index.html')
to
    return render_template('layout.html')
 
Add new route
-------------
@app.route('/lti/testlaunch', methods=['GET', 'POST'])
def lti_test_launch():
  # POST parameters
  # print request.form.keys()
  return render_template('lti_test_launch.html', post=request.form, get=request.args)
 
Change Version in inject_app_info
---------------------------------
'version':"0.0.2-step2",
 
create new file templates/lti_test_launch.html
----------------------------------------------
templates/lti_test_launch.html
{% extends "layout.html" %}

{% block main_content %}

<div class='row'>
  <div class='col-md-12'>
    <h3>GET Parameters</h3>
    <table class='table table-striped'>
      <tr><th>key</th><th>value</th></tr>
      {% for k in get | dictsort %}
      <tr>
        <td>{{ k[0] }}</td>
        <td>{{ k[1] }}</td>
      </tr>
      {% endfor %}
    </table>
    <h3>POST Parameters</h3>
    <table class='table table-striped'>
      <tr><th>key</th><th>value</th></tr>
      {% for k in post | dictsort %}
      <tr>
        <td>{{ k[0] }}</td>
        <td>{{ k[1] }}</td>
      </tr>
      {% endfor %}
    </table>

  </div>
</div>
{% endblock %}


Step 3 Changes
==============

* add make response import 
from flask make_response

* Add pylti library imports
from pylti.flask import lti
from pylti.common import LTI_PROPERTY_LIST, LTI_ROLES

* set the secret key Keep it super secret
app.secret_key = 'a0lkanvoiuas9d8faskdjaksjnvalisdfJ:{}{OIUzR98J/3Yx r~xhh!JMn]lwx/,?rt'

* Add a dictionary of consumers
# LTI Consumers
consumers = {
    "abc123": {"secret": "secretkey-for-abc123"}
}

* set the SERVER_NAME 
SERVER_NAME = '0.0.0.0:5000'
* inform flask about pylti
# Configure flask app with PYLTI config, specifically the consumers
app.config['PYLTI_CONFIG'] = {'consumers': consumers}
* Add custom LTI parameters
# Canvas sends some custom LTI launch parameters. Add these to the list of
# known parameters so that pylti will save them.
LTI_PROPERTY_LIST.extend([
    'custom_canvas_api_domain',
    'custom_canvas_course_id',
    'custom_canvas_enrollment_state',
    'custom_canvas_user_id',
    'custom_canvas_user_login_id'
])

* Add fully-scoped LTI roles

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

* create templates/index.html
* Change index to use new index.html file that is based on the layout file
    return render_template('index.html')
* remove lti_test_launch route
* add error_function

def error(*args, **kwargs):
  # TODO Make a better Error Message screen
  return '{}'.format(kwargs['exception'])

* add first_lti_launch route
@app.route('/lti/launch', methods=['POST'])
@lti(error=error, request='initial')
def first_lti_launch(lti, *args, **kwargs):
  # return render_template('first_lti_launch.html')
  return redirect('/lti/profile')

* add lti_profile route
@app.route('/lti/profile', methods=['GET'])
@lti(error=error, request='session')
def lti_profile(lti, *args, **kwargs):
  return render_template('lti_profile.html')

* add templates/lti_profile.html
{% extends "layout.html" %}

{% block main_content %}
{% if session['lis_person_name_full'] %}
<h2>{{ session['lis_person_name_full'] }}</h2>
{% endif %}

<h3>LTI Session Values</h3>
<table class='table table-striped'>
    {% for key in session|sort %}
    <tr>
      <th>{{ key }}</th>
      <td>{{ session[key] }}</td>
    </tr>
    {% endfor %}
</dl>
{% endblock %}

* Add tools dictionary
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

* add route for lti_config

@app.route('/lti/config/<tool_id>')
def lti_config(tool_id):
  tool_id = int(tool_id)
  config_xml = render_template('xml/config.xml', tool=tools[tool_id])
  response = make_response(config_xml)
  response.headers["Content-Type"] = "application/xml"    

* Add templates/xml/config.xml 
<?xml version="1.0" encoding="UTF-8"?>
<cartridge_basiclti_link xmlns="http://www.imsglobal.org/xsd/imslticc_v1p0"
    xmlns:blti = "http://www.imsglobal.org/xsd/imsbasiclti_v1p0"
    xmlns:lticm ="http://www.imsglobal.org/xsd/imslticm_v1p0"
    xmlns:lticp ="http://www.imsglobal.org/xsd/imslticp_v1p0"
    xmlns:xsi = "http://www.w3.org/2001/XMLSchema-instance"
    xsi:schemaLocation = "http://www.imsglobal.org/xsd/imslticc_v1p0 http://www.imsglobal.org/xsd/lti/ltiv1p0/imslticc_v1p0.xsd
    http://www.imsglobal.org/xsd/imsbasiclti_v1p0 http://www.imsglobal.org/xsd/lti/ltiv1p0/imsbasiclti_v1p0.xsd
    http://www.imsglobal.org/xsd/imslticm_v1p0 http://www.imsglobal.org/xsd/lti/ltiv1p0/imslticm_v1p0.xsd
    http://www.imsglobal.org/xsd/imslticp_v1p0 http://www.imsglobal.org/xsd/lti/ltiv1p0/imslticp_v1p0.xsd">
    <blti:launch_url>{{ protocol|default('http') }}://{{ tool.domain }}/lti/launch</blti:launch_url>
    <blti:title>{{ tool.title }}</blti:title>
    <blti:description>{{ tool.description }}</blti:description>
    <blti:extensions platform="canvas.instructure.com">
      <lticm:property name="privacy_level">public</lticm:property>
      <lticm:property name="domain">{{ tool.domain }}</lticm:property>
      <lticm:property name="text">{{ tool.title }}</lticm:property>
      {% for nav in tool.nav %}
      <lticm:options name="{{ nav.type }}">
        <lticm:property name="enabled">{{ nav.enabled }}</lticm:property>
        <lticm:property name="default">{{ nav.default }}</lticm:property>
        {% if nav.url %}<lticm:property name="url">nav.url</lticm:property>{% endif %}
        {% if nav.icon_url %}<lticm:property name="icon_url">https://dl.dropboxusercontent.com/u/1647772/lti.png</lticm:property>{% endif %}
        {% if nav.labels %}<lticm:options name="labels">
        {% for label in nav.labels %}
        <lticm:property name="{{ label.locale }}">{{ label.label }}</lticm:property> 
        {% endfor %}</lticm:options>
        {% endif %}
      </lticm:options>
      {% endfor %}
    </blti:extensions>
</cartridge_basiclti_link>

* change version in inject_app_info

* add pylti as requirement for pip

Step 4 Changes
===============

* Add additional LTI_PROPERTY_LIST values
LTI_PROPERTY_LIST.extend([
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

* modify first_lti_launch
@app.route('/lti/launch/<tool_id>', methods=['POST'])
def first_lti_launch(lti, tool_id=None, *args, **kwargs):
  if tool_id == '0':
    return redirect('/lti/mapit')
  else:
    return render_template('lti_profile.html')

* Get Google API Key (can they use mine?)
G_API_KEY = 'AIzaSyDS7-sUBVXPy5XIjWJFsXzLf6fDEZtjFOw'

* Add mapit_launch route
@app.route('/lti/mapit')
@lti(error=error, request='session')
def mapit_launch(lti):
  return render_template('mapit_launch.html',G_API_KEY=G_API_KEY)

* Change configuration dictionary
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

* add static/map_lti.js 
var firebase = new Firebase('https://burning-fire-7264.firebaseio.com/'); //#-KGMjngqOsfdYmQVAuOQ|84de6e0176b2809975487d2c428c4965');
var marker_db = firebase.child('markers:'+LTI_ENV.context_id);
var map;
var gc = new google.maps.Geocoder();
var infowindow;
var all_markers = {};

function initMap() {
  map = new google.maps.Map(document.getElementById('map'), {
    zoom: 8,
    center: {lat: 39.57605638518604, lng: -105.9521484375},  // Keystone, Colorado
    zoomControl: true,
    mapTypeControl: false,
    scaleControl: false,
    streetViewControl: false,
    rotateControl: false,
    fullscreenControl: false
  });

  infowindow = new google.maps.InfoWindow();
  google.maps.event.addListener(infowindow, 'domready', function() {

   // Reference to the DIV which receives the contents of the infowindow using jQuery
   var iwOuter = $('.gm-style-iw');

   /* The DIV we want to change is above the .gm-style-iw DIV.
    * So, we use jQuery and create a iwBackground variable,
    * and took advantage of the existing reference to .gm-style-iw for the previous DIV with .prev().
    */
   var iwBackground = iwOuter.prev();

   // Remove the background shadow DIV
   iwBackground.children(':nth-child(2)').css({'display' : 'none'});

   // Remove the white background DIV
   iwBackground.children(':nth-child(4)').css({'display' : 'none'});

   var iwCloseBtn = iwOuter.next();

    // Apply the desired effect to the close button
    iwCloseBtn.css({
      opacity: '1', // by default the close button has an opacity of 0.7
      right: '9px', top: '-4px', // button repositioning
      border: '7px solid #48b5e9', // increasing button border and new color
      'width':  '40px',
      'height': '40px',
      'background-color': '#fff',
      'border-radius': '20px', // circular effect
      'box-shadow': '0 0 5px #3990B9' // 3D effect to highlight the button
      });
    iwCloseBtn.find('img').css({
      left: '5px',
      top: '-328px'
    });


    // The API automatically applies 0.7 opacity to the button after the mouseout event.
    // This function reverses this event to the desired value.
    iwCloseBtn.mouseout(function(){
      $(this).css({opacity: '1'});
    });

});
}

marker_db.orderByChild("order").on("child_added", function(snapshot, prevChildKey) {
  // Get latitude and longitude from Firebase.
  var newPosition = snapshot.val();

  // Create a google.maps.LatLng object for the position of the marker.
  // A LatLng object literal (as above) could be used, but the heatmap
  // in the next step requires a google.maps.LatLng object.
  var latLng = new google.maps.LatLng(newPosition.lat, newPosition.lng);
  setupMarker(latLng, newPosition);
});

function marker_id(info){
  return LTI_ENV.custom_canvas_user_id +'::'+LTI_ENV.context_id+'::'+
      info.lat.toString().replace('.','')+
      '::'+info.lng.toString().replace('.','')
}

function setupMarker(latLng, info){
  if(info.id == undefined || info.id == ''){
    info.id = marker_id(info) ;
  }

  // Place a marker at that location.
  var draggable = LTI_ENV.is_instructor;
  var marker = new google.maps.Marker({
    position: latLng,
    map: map,
    title:' some title ',
    draggable: draggable
  });

  info.marker = marker;
  all_markers[info.id] = info;
  // Add a click handler to the marker so it shows the info window when...clicked
  marker.addListener('click', function(){
    show_info_window( info );
    setSelectedMarker(marker, all_markers[info.id]);
  });
  if(LTI_ENV.is_instructor){
    marker.addListener('dragend', function(e){

      var m_info = all_markers[info.id];
      m_info.lat = e.latLng.lat();
      m_info.lng = e.latLng.lng();
      saveMarker( m_info);
    });
  }

  $('#marker-list>ul li').remove();
  if(prep_m_list){ prep_m_list(); };
}

function setSelectedMarker( marker, info){
  $('#selected_marker_id').val(info.id); 
  $('#selected_marker_label').val(info.label); 
  $('#selected_marker_description').val(info.description); 
  $('#selected_marker_image').val(info.image); 
  selected_marker = {marker:marker, info: info};
};

function show_info_window( info ){
  var img_src = (all_markers[info.id].image) ? '<img src="'+ all_markers[info.id].image+'" width="100px" />' : '' ;
  var content = '<div id="iw-container" data-info-id="'+all_markers[info.id].id+'"> ' +
                  '<div class="iw-title">'+ all_markers[info.id].label +'</div>' +
                  '<div class="iw-content">' +
                    '<div class="iw-subTitle">subtitle</div>' +
                    img_src+
                    '<p class="marker_description">'+ all_markers[info.id].description +'</p>' +
                  '</div>' +
                  '<div class="iw-bottom-gradient"></div>' +
                '</div>';

  infowindow.setContent(content);
  infowindow.open(map, info.marker); 
};

* add static/map_lti_inst.js 
function searchAndRecenter(search){
  console.log('search', search);
  gc.geocode(search, function(results, status){
    if (status == google.maps.GeocoderStatus.OK) {
      map.setCenter(results[0].geometry.location);
      var marker = new google.maps.Marker({
          map: map,
          position: results[0].geometry.location
      });
    } else {
      alert("Geocode was not successful for the following reason: " + status);
    }
  });

}

function saveMarker(info){
  if(info.id == undefined || info.id == ''){
    info.id = marker_id(info) ;
  }
  var info_to_save = $.extend({}, info, {});
  delete info_to_save.marker;
  marker_db.child(info.id).set(info_to_save);
}

function delete_marker( id, callback) {
  marker_db.child(id).remove( callback);
}


var initMapInstructor = function(){
  $('#instructor_controls').submit(function(e){
    var search = {
     address: $('#newLocation').val(),
    };
    searchAndRecenter( search );
    e.preventDefault(); 
  });
  $('#marker_editor').change(function(e){

    var m_info = all_markers[$('#selected_marker_id').val()];
    m_info.label = $('#selected_marker_label').val();
    m_info.description = $('#selected_marker_description').val();
    m_info.image = $('#selected_marker_image').val();

    saveMarker( m_info);
    prep_m_list();
    e.preventDefault();
  });
  /*$('#marker_editor').submit(function(e){
    // Save the values from the marker editor to Firebase
    console.log('editor submitted');
    var m_info = all_markers[$('#selected_marker_id').val()];
    m_info.label = $('#selected_marker_label').val();
    m_info.description = $('#selected_marker_description').val();
    m_info.image = $('#selected_marker_image').val();

    saveMarker( m_info);
    prep_m_list();
    e.preventDefault();
  });
  */

  map.addListener('click', function(e) {
    var info = {order: all_markers.length, lat: e.latLng.lat(), lng: e.latLng.lng(), label: '', description:''};

    saveMarker(info)
    //marker_db.push(info);

    var latLng = new google.maps.LatLng(e.latLng.lat(), e.latLng.lng());
    setupMarker(latLng, info)

  });
};

function prep_m_list(){
  $('#marker-list>ul').empty();
  $.each(all_markers, function(idx, mark){
    var el = $('<li data-id="'+ mark.id +'" class="marker-row"><i class="glyphicon glyphicon-trash"></i><i class="glyphicon glyphicon-move"></i> <span class="_label">'+mark.label+'<span></li>');
    $('#marker-list>ul').append(el);
    //el.find('i.glyphicon.glyphicon-trash').click(function(mark.id){ 
    el.find('i.glyphicon.glyphicon-trash').click(function(e){ 
      console.log('delete clicked ' ); 
      console.log(mark.id);
      mark.marker.setMap(null);
      delete all_markers[mark.id];
      delete_marker(mark.id, function(){
        prep_m_list();
      });
    });
    el.find('._label, .glyphicon.glyphicon-move').click(function(e){
     show_info_window( mark );
     setSelectedMarker(mark.marker, mark);
    });
  });
  setListSortable($('#marker-list ul')[0]);
}

function setListSortable(el){
  // var sortable = Sortable.create(el);
  var sortable = new Sortable(el, {
  // dragging started
    onStart: function (/**Event*/evt) {
        evt.oldIndex;  // element index within parent
    },

    // dragging ended
    onEnd: function (/**Event*/evt) {
        console.log($(evt.item).data('id'));
        var id = $(evt.item).data('id');

        all_markers[id].order = evt.newIndex;
        saveMarker(all_markers[id]);
        var items = $(evt.target).find('li');
        for(var x=evt.newIndex+1, l=items.length; x<l; x++){
          id = $(items[x]).data('id');
          all_markers[id].order = x+1;
          saveMarker(all_markers[id]);
        }
        //evt.oldIndex;  // element's old index within parent
        //evt.newIndex;  // element's new index within parent
        //
    },
  });
}

* add static/map_lti_student.js 

* modify templates/layout.html
// Change header
<meta name="viewport" content="width=device-width, initial-scale=1, user-scalable=no">

* add extra_css block
{% block extra_css %}{% endblock %}

* replace main_content block with simply
{% block main_content %}{% endblock %}

* add extra_js block
{% block extra_js %}{% endblock %}

* add templates/mapit_launch.html
{% extends "layout.html" %}

{% block main_content %}
<div class='row'>
  <div class='col-md-6'>
    {% if 'Learner' in session['ext_roles'] %}
      <p>You are a student, this page should load a map that was created by the
      instructor before the course was published.</p>
    {% endif %}

    {% if 'Instructor' in session['ext_roles'] %}
    <p>You are an instructor.</p>

    <form id='instructor_controls'>
      <div class='form-group'>
        <label for='recenterLocation'>Search Location</label>
        <input type='textbox' class='form-control' id='newLocation'
        placeholder='e.g. "Dallas, Texas"'>
      </div>
    </form>
    {% endif %}
    <div id='map'></div>
    
  </div>
  
  <div class='col-md-6'>
    <div id='total'></div>
    <div id='right-panel'>
      <h2>Marks</h2> 
      {% if 'Instructor' in session['ext_roles'] %}
      <form id='marker_editor'>
        <input type='hidden' id='selected_marker_id'>
        <div class='form-group'>
          <label for='marker_label'>Label</label>
          <input type='textbox' class='form-control' name='marker_label'
          id='selected_marker_label'
          placeholder='e.g. Place where Pecos Bill shot his first buffalo.'>
        </div>
        <div class='form-group'>
          <label for='marker_image'>Image</label>
          <input type='textbox' class='form-control' name='image'
          id='selected_marker_image'
          placeholder='e.g. url to image'>
        </div>
        <div class='form-group'>
          <label for='marker_description'>Description</label>
          <textarea rows='4' type='textbox' class='form-control' name='description'
          id='selected_marker_description'
          placeholder='e.g. Description about place where Pecos Bill shot his first buffalo.'>
          </textarea>
        </div>
      </form>
      <div id='marker-list'>
        <ul >
        </ul> 
      </div>
      {% else %}
      <dl>
        <dt>Label</dt>
        <dd id='marker_label'></dd>
        <dt>Description</dt>
        <dd id='marker_description'></dd>
      </dl>
      {% endif %}
    </div>
  </div>
</div>

{% endblock %}

{% block extra_css %}
<style>
  html, body {
    height: 100%;
    margin: 0;
    padding: 0;
  }
  #map {
    width: 100%%;
    height: 500px;
  }

  /* Google Map Styles see
     http://en.marnoto.com/2014/09/5-formas-de-personalizar-infowindow.html */
  #map-canvas {
    margin: 0;
    padding: 0;
    height: 400px;
    max-width: none;
  }
  #map-canvas img {
    max-width: none !important;
  }
  .gm-style-iw {
    width: 350px !important; 
    top: 15px !important;
    left: 0px !important;
    background-color: #fff;
    box-shadow: 0 1px 6px rgba(178, 178, 178, 0.6);
    border: 1px solid rgba(72, 181, 233, 0.6);
    border-radius: 2px 2px 10px 10px;
  }
  #iw-container {
    margin-bottom: 10px;
  }
  #iw-container .iw-title {
    font-family: 'Open Sans Condensed', sans-serif;
    font-size: 22px;
    font-weight: 400;
    padding: 10px;
    background-color: #48b5e9;
    color: white;
    margin: 0;
    border-radius: 2px 2px 0 0;
  }
  #iw-container .iw-content {
    font-size: 13px;
    line-height: 18px;
    font-weight: 400;
    margin-right: 1px;
    padding: 15px 5px 20px 15px;
    max-height: 140px;
    overflow-y: auto;
    overflow-x: hidden;
    width: 350px;
  }
  .iw-content img {
    float: right;
    margin: 0 5px 5px 10px;	
  }
  .iw-subTitle {
    font-size: 16px;
    font-weight: 700;
    padding: 5px 0;
  }
  .iw-bottom-gradient {
    position: absolute;
    width: 326px;
    height: 25px;
    bottom: 10px;
    right: 18px;
    background: linear-gradient(to bottom, rgba(255,255,255,0) 0%, rgba(255,255,255,1) 100%);
    background: -webkit-linear-gradient(top, rgba(255,255,255,0) 0%, rgba(255,255,255,1) 100%);
    background: -moz-linear-gradient(top, rgba(255,255,255,0) 0%, rgba(255,255,255,1) 100%);
    background: -ms-linear-gradient(top, rgba(255,255,255,0) 0%, rgba(255,255,255,1) 100%);
  }

  .marker-row { cursor: pointer; }
  .marker-row i { color: green; }

</style>
{% endblock %}

{% block extra_js %}
<script src="https://cdn.firebase.com/js/client/2.2.1/firebase.js"></script>
<script src="https://maps.googleapis.com/maps/api/js?key={{ G_API_KEY }}"></script>
<script>
var LTI_ENV = { 
  custom_canvas_user_id: '{{ session.custom_canvas_user_id }}', 
  context_id: '{{session.context_id}}' ,
  resource_link_id: '{{session.resource_link_id}}',
  is_instructor: false
};
</script>

<script src="/static/map_lti.js"></script>
{% if 'Instructor' in session['ext_roles'] %}
<script src="/static/map_lti_inst.js"></script>
<script src="//cdnjs.cloudflare.com/ajax/libs/Sortable/1.4.2/Sortable.min.js"></script>
{% endif %}

<script>
var LTI_ENV = { 
  custom_canvas_user_id: '{{ session.custom_canvas_user_id }}', 
  context_id: '{{session.context_id}}' ,
  is_instructor: false
};
$(document).ready(function(){
  initMap();
  {% if 'Instructor' in session['ext_roles'] %}
  LTI_ENV.is_instructor = true;
  initMapInstructor();
  {% else %}
  LTI_ENV.is_instructor = false;
  {% endif %}
});
</script>

{% endblock %}

* add templates/mapit_launch_with_directions.html
{% extends "layout.html" %}

{% block main_content %}
<div class='row'>
  <div class='col-md-6'>
    {% if 'Learner' in session['ext_roles'] %}
      <p>You are a student, this page should load a map that was created by the
      instructor before the course was published.</p>
    {% endif %}

    {% if 'Instructor' in session['ext_roles'] %}
    <p>You are an instructor.</p>

    <form id='instructor_controls'>
      <div class='form-group'>
        <label for='recenterLocation'>Search Location</label>
        <input type='textbox' class='form-control' id='newLocation'
        placeholder='e.g. "Dallas, Texas"'>
      </div>
      <!--
      <div class='form-group'>
        <label for='recenterLocation'>Start Location</label>
        <input type='textbox' class='form-control' id='startLocation'
        placeholder='e.g. "Dallas, Texas"'>
      </div>
      <div class='form-group'>
        <label for='recenterLocation'>End Location</label>
        <input type='textbox' class='form-control' id='endLocation'
        placeholder='e.g. "Dallas, Texas"'>
      </div>
      -->
    </form>
    {% endif %}
    <div id='map'></div>
    
  </div>
  
  <div class='col-md-6'>
    <div id='total'></div>
    <div id='right-panel'>
    
    </div>
  </div>
</div>
{% endblock %}

{% block extra_css %}
<style>
  html, body {
    height: 100%;
    margin: 0;
    padding: 0;
  }
  #map {
    width: 100%%;
    height: 500px;
  }
</style>
{% endblock %}

{% block extra_js %}
<script src="https://cdn.firebase.com/js/client/2.2.1/firebase.js"></script>
<script src="https://maps.googleapis.com/maps/api/js?key={{ G_API_KEY }}"></script>

<script>
var g_api_key='{{ G_API_KEY }}';
var firebase = new Firebase('https://burning-fire-7264.firebaseio.com/'); //#-KGMjngqOsfdYmQVAuOQ|84de6e0176b2809975487d2c428c4965');
var marker_db = firebase.child('markers');
var map;
var gc = new google.maps.Geocoder();

function initMap() {
  map = new google.maps.Map(document.getElementById('map'), {
    zoom: 1,
    center: {lat: 39.57605638518604, lng: -105.9521484375},  // Keystone, Colorado
    zoomControl: false,
    mapTypeControl: false,
    scaleControl: false,
    streetViewControl: false,
    rotateControl: false,
    fullscreenControl: false
  });

  var directionsService = new google.maps.DirectionsService;
  var directionsDisplay = new google.maps.DirectionsRenderer({
    draggable: true,
    map: map,
    panel: document.getElementById('right-panel')
  });

  directionsDisplay.addListener('directions_changed', function() {
    computeTotalDistance(directionsDisplay.getDirections());
  });

  displayRoute('Denver, CO', 'Keystone, CO', directionsService,
      directionsDisplay);

  map.addListener('click', function(e) {
    var info = {lat: e.latLng.lat(), lng: e.latLng.lng(), label: '', description:''};
    marker_db.push(info);

    var latLng = new google.maps.LatLng(e.latLng.lat(), e.latLng.lng());
    setupMarker(latLng, info)

  });
}

marker_db.on("child_added", function(snapshot, prevChildKey) {
  // Get latitude and longitude from Firebase.
  var newPosition = snapshot.val();

  // Create a google.maps.LatLng object for the position of the marker.
  // A LatLng object literal (as above) could be used, but the heatmap
  // in the next step requires a google.maps.LatLng object.
  var latLng = new google.maps.LatLng(newPosition.lat, newPosition.lng);
  setupMarker(latLng, newPosition);
});

function setupMarker(latLng, info){

  var infowindow = new google.maps.InfoWindow({ content: info.description });
  // Place a marker at that location.
  var marker = new google.maps.Marker({
    position: latLng,
    map: map,
    title:'',
  });

  // Add a click handler to the marker so it shows the info window when...clicked
  marker.addListener('click', function(){
    infowindow.open(map, marker); 
  });
}

function displayRoute(origin, destination, service, display) {
  service.route({
    origin: origin,
    destination: destination,
    waypoints: [{location: 'Boulder, CO'}, {location: 'Black Hawk, CO'}],
    travelMode: google.maps.TravelMode.DRIVING,
    avoidTolls: true
  }, function(response, status) {
    if (status === google.maps.DirectionsStatus.OK) {
      display.setDirections(response);
    } else {
      alert('Could not display directions due to: ' + status);
    }
  });
}

function computeTotalDistance(result) {
  var total = 0;
  var myroute = result.routes[0];
  for (var i = 0; i < myroute.legs.length; i++) {
    total += myroute.legs[i].distance.value;
  }
  total = total / 1000;
  document.getElementById('total').innerHTML = total + ' km';
}

function searchAndRecenter(search){
  console.log('search', search);
  gc.geocode(search, function(results, status){
    if (status == google.maps.GeocoderStatus.OK) {
      map.setCenter(results[0].geometry.location);
      var marker = new google.maps.Marker({
          map: map,
          position: results[0].geometry.location
      });
    } else {
      alert("Geocode was not successful for the following reason: " + status);
    }
  });

}


google.maps.event.addDomListener(window, "load", initMap);

$(document).ready(function(){
  $('#instructor_controls').submit(function(e){
    var search = {
     address: $('#newLocation').val(),
    };
    searchAndRecenter( search );
    event.preventDefault(); 
  });
});

</script>

{% endblock %}

* modify templates/xml/config.xml
replace

<blti:launch_url>{{ protocol|default('http') }}://{{ tool.domain }}/lti/launch</blti:launch_url>

with 

<blti:launch_url>{{ tool.url }}</blti:launch_url>


Step 5 Changes
===============

* Add flask jsonify import
from flask import jsonify

* modify first_lti_launch route, add elif for new tool
  elif tool_id == '1':
    return redirect('/lti/yt_watch_for_points')


* add yt_watch_for_points route
@app.route('/lti/yt_watch_for_points')
@lti(error=error, request='session')
def yt_watch_for_points(lti, *args, **kwargs):
  return render_template('yt_watch_for_points.html', video_id=video_id)


* add yt_watch_for_points_submit route
@app.route('/lti/yt_watch_for_points/finished', methods=['POST'])
@lti(error=error, request='session')
def yt_watch_for_points_submit(lti, *args, **kwargs):
  status = 'submitted'
  response = lti.post_grade(request.form.get('score',0))
  print('response', response)
  return jsonify(status=response)

* add yt view tool info to tool dictionary
  },{ 
  'domain' : SERVER_NAME,
  'title' : 'Step 5-Watch Youtube - Get Grade',
  'description' : '''This is the step 5 LTI Tool, with differentiated
  functionality for students and teachers. Teach will add an assignment as
  external tool, and select a youtube video. Students watch the video and get
  points when they finish the video.''',

  'url':'http://{}/lti/launch/{}'.format(SERVER_NAME, 1),
  }]

* Change version in app.py

* Add static/video_watcher.js
// This function creates an <iframe> (and YouTube player)
// after the API code downloads.
var player;
function onYouTubeIframeAPIReady() {
  get_video( function(video){
    LTI_ENV.video = video;
    console.log('got', video);

    $('#video_id').val(video.video_id);
    $('#minimum_percent').val(video.minimum_percent);
    if(LTI_ENV.is_instructor){
      $('#video_description').val(video.description);
    }else{
      $('#video_description').text(video.description);
    }
    player = new YT.Player('player', {
      height: '390',
      width: '640',
      videoId: video.video_id,
      playerVars: {
        rel: 0,
        modestbranding: 1
      },
      events: {
        'onReady': onPlayerReady,
        'onStateChange': onPlayerStateChange
      }
    });
  
  });
}

// The API will call this function when the video player is ready.
var interval;
function onPlayerReady(event) {
  event.target.playVideo();
  checkProgress(function(){
    console.log('setting up interval');
    interval = setInterval(checkProgress, 5000); // check every 10 seconds
  });
}

// The API calls this function when the player's state changes.
// The function indicates that when playing a video (state=1),
// the player should play for six seconds and then stop.
function onPlayerStateChange(event) {
  //console.log(YT.PlayerState);
  if (event.data == YT.PlayerState.ENDED ) {
    console.log('currentTime', player.getCurrentTime());
    console.log('duration', player.getDuration());
    checkProgress();
  }
}

function checkProgress(cb){
  if(typeof(cb) != 'function'){ cb = function(){} };
  if(LTI_ENV.is_instructor){
    if(interval) { window.clearInterval(interval); }
    cb();
    return
  }
  if(player.getDuration() > 0  ){
    // The player has watched at least 90% of the video
    // Send signal that video is finished playing
    // TODO make this take account of the minimum_percent

    var min_duration = LTI_ENV.video.minimum_percent / 100 * player.getDuration();
    var score = player.getCurrentTime() / min_duration; 
    get_current_score(function(current_score){
      var per_progress = Math.floor(current_score * 100);
      $('#you_have_watched').text(per_progress);
      $('#prog_bar').css('width',per_progress+'%').attr('aria-valuenow', per_progress).text(per_progress+'%');
      console.log('updating score to ' + score);
      if(score>=1){
        window.clearInterval(interval);
      }
      if( current_score == false || score > current_score ){
        $.post('/lti/yt_watch_for_points/finished',{score:score}).done( function(res, status){
          scores_db.child(score_id()).set({score:score});
          cb();
        });
      }else{
        cb();
      }
    });
  }else{
    cb();
  }
}

var firebase = new Firebase('https://burning-fire-7264.firebaseio.com/');
var scores_db = firebase.child('scores:'+LTI_ENV.context_id);
function get_current_score(callback){
  var score = scores_db.child(score_id());
  score.once('value', function(snapshot){
    var ret_value = false;
    if(snapshot.exists()){
      ret_value = snapshot.val().score;
    }
    callback(ret_value);
  });
}

function score_id(){
  return LTI_ENV.resource_link_id + '::' + LTI_ENV.custom_canvas_user_id;
}

function get_video(cb){
  var video_ref = scores_db.child('videos').child(LTI_ENV.resource_link_id);
  video_ref.on('value', function(snapshot){
    if (snapshot.exists()){
      cb( snapshot.val())
    }
  });
}

function set_video_id(video_id, description, minimum_percent, cb){
  scores_db.child('videos').child(LTI_ENV.resource_link_id).set({
    video_id:video_id, 
    description:description, 
    minimum_percent:minimum_percent
  },
  cb());
}

* remove navigation elements from templates/layout.html
delete from <nav> to </nav>
or 
comment the sections out

* add templates/yt_watch_for_points.html
{% extends "layout.html" %}

{% block main_content %}
<div class='row'>
  <div class='col-md-12'>
    {% if 'Learner' in session['ext_roles'] %}
    <div class="progress">
      <div id='prog_bar' class="progress-bar" role="progressbar" aria-valuenow="5"
      aria-valuemin="0" aria-valuemax="5" style="width:5%">
        70%
      </div>
    </div>
    <p id='video_description'></p>
    {% else %}
    <form id='video_form' class='form'>
      <div class="form-group">
        <label for="video_id">Video ID</label>
        <input type="textbox" class="form-control" id="video_id" placeholder="Youtube Video ID">
      </div>
      <div class="form-group">
        <label for="video_description">Description</label>
        <textarea rows='3' class="form-control" id="video_description" placeholder="e.g. description"></textarea>
      </div>
      <div class="form-group">
        <label for="minimum_percent">What percentage of the video should be watched for full points?</label>
        <input type="number" max='100' class="form-control" id="minimum_percent" placeholder="" value="100">
      </div>

      <div class="form-group">
        <button type='submit' class='btn btn-default'>Save</button>
      </div>
    </form>
    {% endif %}

  </div>
</div>
<div class='row'>
  <div class='col-md-12'>
    <!-- 1. The <iframe> (and video player) will replace this <div> tag. -->
    <div id="player"></div>
    
    {% if 'Learner' in session['ext_roles'] %}
    <p>You have watched <span id="you_have_watched">...</span>% of 
    this video. Your score is updated in the LMS every couple of seconds.
    </p>
    {% endif %}
  </div>
</div>
{% endblock %}

{% block extra_js %}

<script src="https://www.youtube.com/iframe_api"></script>
<script src="https://cdn.firebase.com/js/client/2.2.1/firebase.js"></script>

<script>
var LTI_ENV = { 
  custom_canvas_user_id: '{{ session.custom_canvas_user_id }}', 
  context_id: '{{session.context_id}}' ,
  resource_link_id: '{{session.resource_link_id}}',
  {% if 'Instructor' in session['ext_roles'] %}
  is_instructor: true
  {% else %}
  is_instructor: false
  {% endif %}
};
</script>
<script src="/static/video_watcher.js"></script>
<script>

{% if 'Instructor' in session['ext_roles'] %}
$(document).ready(function(){
  $('#video_id').change(function(e){
    // change_video_preview
    // get the player, set the video to 
    player.loadVideoById($('#video_id').val());
  });
  $('#video_form').submit(function(e){
    set_video_id(
        $('#video_id').val(), 
        $('#video_description').val(), 
        $('#minimum_percent').val(), 
        function(){ });
    e.preventDefault();
  });
});
{% endif %}
</script>

{% endblock %}


Step 6 Changes
===============

* add render_template_string import
from flask import render_template_string

* add requests and urllib import
import requests
import urllib

* set the preferred URL_SCHEME to https
app.config['PREFERRED_URL_SCHEME'] = 'https'

* Set the SERVER_NAME to the domain name of your c9 app
SERVER_NAME = 'flasktestapp1-kajigga2.c9users.io'

* make improvements to first_lti_launch
replace
    return redirect('/lti/mapit')
with
    return redirect(url_for('mapit', _scheme='https', _external=True))

replace
    return redirect('/lti/yt_watch_for_points')
with
    return redirect(url_for('yt_watch_for_points', _scheme='https', _external=True))

* Add branch for ipsum to first_lti_launch
  elif tool_id == '2':
    return redirect(url_for('baconIpsumChoose', _scheme='https', _external=True))
 
* Add lorem_types dictionary

lorem_types = {
  'regular':{
    'name':'regular',
    'label':'Regular Lorem Ipsum text'
  },
  'with_bacon':{
    'name':'with_bacon',
    'label':'Bacon Ipsum - tasty but not so good looking'
  },
  'random_text':{
    'name':'random_text',
    'label':'Random Text'
  },
  'arresteddevelopment_quotes': {
    'name': 'arresteddevelopment_quotes',
    'label':'Quotes from Arrested Development'
  },
  'doctorwho_quotes':{
    'name':'doctorwho_quotes',
    'label':'Quotes from Dr. Who'
  },
  'dexter_quotes':{
    'name':'dexter_quotes',
    'label':'Quotes from Dexter'
  },
  'futurama_quotes':{
    'name':'futurama_quotes',
    'label':'Quotes from Futurama'
  },
  'holygrail_quotes':{
    'name':'holygrail_quotes',
    'label':'Quotes from Monty Python and the Holy Grail'
  },
  'simpsons_quotes':{
    'name':'simpsons_quotes',
    'label':'Quotes from the Simpsons'
  },
  'starwars_quotes':{
    'name':'starwars_quotes',
    'label':'Quotes from Star Wars'
  }}


* Add baconIpsumFetch route
# Make sure you don't include the @lti decorator on this route. Canvas won't be
# able to request the information otherwise.

@app.route('/lti/baconipsum/fetch')
def baconIpsumFetch(*args,**kwargs):
    num_para = int(request.args.get('num_para',5))
    lorem_type = request.args.get('lorem_type','regular').lower()
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
    if lorem_type == 'with_bacon':
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
    elif lorem_type == 'random_text':
      lorem_url = 'http://randomtext.me/api/lorem/p-{}/5-15/'.format(num_para)

      try:
        paragraphs = requests.get(bacon_url).json()
        # paragraphs = json_decode('%s' % bacon_response)
      except Exception,err:
        print 'err',err

        paragraphs = ['']
      resp['html'] = paragraphs['text_out']
    #elif show in ('arresteddevelopment','doctorwho','dexter','futurama','holygrail','simpsons','starwars'):
    #elif show in ('arresteddevelopment','doctorwho','dexter','futurama','holygrail','simpsons','starwars'):
    elif '_quotes' in lorem_type:
      show = lorem_type.replace('_quotes', '')
      fillerama_url = "http://api.chrisvalleskey.com/fillerama/get.php?count=10&format=json&show=%s" % show
      response = requests.get(fillerama_url).json()
      paragraphs = [x['quote'] for x in response['db']]
      resp['html'] = render_template('show_quotes.html', paragraphs=response['db'], lorem=lorem_types[lorem_type])
    elif lorem_type == 'regular':
      # No bacon wanted, get regular Lorem Ipsum
      options = ['short','headers','decorate','link','ul','ul','dl','bq']
      lorem_url = "http://loripsum.net/api/%d/%s" % (num_para,'/'.join(options))
      paragraphs = requests.get(lorem_url).text
      paragraphs = paragraphs.replace('loripsum.net', 'canvaslms.com')
      resp['html'] = paragraphs

    #return render_template('baconIpsumFetch.html',paragraphs=paragraphs)
    if request.args.get('html','no')=='yes':
      return render_template('baconIpsumFetch.html',dict(paragraphs=paragraphs))
    else:
      return jsonify(resp)

* add baconIpsumChoose route
@app.route('/lti/baconipsum/choose', methods=['GET', 'POST'])
#@lti(error=error, request='session')
def baconIpsumChoose(*args, **kwargs):
  if request.method == 'GET':
    # Prompt the user to select the size of the bacon 
    return render_template('baconIpsumChoose.html', lorem_types=lorem_types)

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
        'url':     url_for('baconIpsumFetch', _external=True, _scheme='https', args=['lkjlkjlk']), 
        'endpoint':'',
        'width':'400',
        'height':'400',
        'embed_type':'oembed',
        },
    'link': { # works
        'url':     url_for('baconIpsumFetch', _external=True, _scheme='https',args=['lkjlkjlk']), 
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
        'return_type':'iframe',
        'embed_type':'iframe',
        }
    }
  
    success_url = session.get('launch_presentation_return_url','')

    #redirect_url = success_url % urllib.urlencode(red_args['oembed'])
    wanted_type = request.form.get('wanted_type','oembed')
    print('wanted_type: ' + wanted_type)
    if wanted_type in red_args.keys():
      #redirect_url = success_url % urllib.urlencode(red_args['img'])
      if wanted_type == 'img':
        height = int(request.args.get('height',100))
        width  = int(request.args.get('width',100))
        red_args['img']['url'] = red_args['img']['url'] % (height,width)
        red_args['img']['height'] = height
        red_args['img']['width']  = width
      elif wanted_type == 'iframe':
        height = request.form.get('iframe_height',100)
        width  = request.form.get('iframe_width',100)
        red_args['iframe']['url'] = request.form.get('iframe_url')
        red_args['iframe']['title'] = request.form.get('iframe_title')
        red_args['iframe']['height'] = height
        red_args['iframe']['width']  = width
        print 'form args', request.form
        print 'red_args[iframe]', red_args['iframe']
      elif wanted_type == 'link':
        pass
      elif wanted_type == 'oembed':
        show = request.form.get('show','none')
        url_for('baconIpsumFetch', _external=True, _scheme='https',args=['lkjlkjlk']) 
        red_args['oembed']['endpoint'] = url_for('baconIpsumFetch', _external=True, _scheme='https',**dict(request.form))
        red_args['oembed']['url'] = red_args['oembed']['endpoint'] #.replace('https','http')

      redirect_url = success_url +"?"+ urllib.urlencode(red_args[wanted_type])
    return redirect(redirect_url)


* modify lti_profile route
replace
  'url':'http://{}/lti/launch/{}'.format(SERVER_NAME, 0),
with
  'url':'https://{}/lti/launch/{}'.format(SERVER_NAME, 0),

* modify tools dictionary
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


* change version
      'version':"0.0.1-step6",

* Add force to https
def _force_https():
  # my local dev is set on debug, but on AWS it's not (obviously)
  # I don't need HTTPS on local, change this to whatever condition you want.
  if not app.debug: 
      from flask import _request_ctx_stack
      if _request_ctx_stack is not None:
          reqctx = _request_ctx_stack.top
          reqctx.url_adapter.url_scheme = 'https'
app.before_request(_force_https)

* add static/lorem_ipsum.js
$(document).ready(function(){ 
    $('button').click(function(){
      $('#wanted_submit_btn').show();
    });

    $('#kitten_btn').click(function(){
      $('#wanted_type').val('img');
      $('#kitten_fields').show();
      $('#lorem_fields, #iframe_fields').hide();
    });
    $('#kitten_fields').change(function(){
      // height/width
      var img_src = 'https://placekitten.com/g/'+ $('#height').val() +'/'+ $('#width').val() ;
      $('#kitten_preview')
        .attr('height', $('#height').val() + 'px')
        .attr('width', $('#width').val() + 'px')
        .attr('src', img_src)
    });
    $('#lorem_btn').click(function(){
      $('#wanted_type').val('oembed');
      $('#lorem_fields').show();
      $('#kitten_fields, #iframe_fields').hide();
    });
    $('#embed_iframe_btn').click(function(){
      $('#wanted_type').val('iframe');
      $('#iframe_fields').show();
      $('#lorem_fields, #kitten_fields').hide();
    });
    $('#random_btn').click(function(){
      $('#wanted_type').val('iframe');
      $('#random_fields').show();
      $('#iframe_fields, lorem_fields, #kitten_fields').hide();
    });
    $('#iframe_fields').change(function(){
      var height = $('#iframe_height').val() == '' ?  $('#iframe_preview').attr('height') : $('#iframe_height').val();
      var width = $('#iframe_width').val() == '' ?  $('#iframe_preview').attr('width') : $('#iframe_width').val();
      $('#iframe_preview')
        .attr('src', $('#iframe_url').val())
        .attr('height', height + 'px')
        .attr('width', width + 'px');
    });
});

* add templates/baconIpsumChoose.html
{% extends 'layout.html'%}
{% block page_title %}Choose your Bacon{% endblock %}

{% block main_content %}
<div class='col-sm-12'>
    <p>What would you like?</p>
    <div class='btn-group' role='group' aria-label=''>
      <button class='btn btn-default' type='button' id='kitten_btn'>Kitten Image</button>
      <button class='btn btn-default' type='button' id='lorem_btn'>Lorem Ipsum</button>
      <button class='btn btn-default' type='button' id='embed_iframe_btn'>Embed iFrame</button>
      <button class='btn btn-default' type='button' id='random_dilbert_btn'>Random Dilbert</button>
    </div>
    <form class='form-vertical' action='{{ url_for("baconIpsumChoose" ) }}' method='POST'>
      <input type='hidden' name='wanted_type' id='wanted_type' value='img'/> 

      <div id='kitten_fields' style='display:none'>
        <div class="form-group">
          <label for="width" class="control-label">Width</label>
          <div class="">
            <input type="number" class="form-control" id="width" name='width' placeholder="width">
          </div>
        </div>
        <div class="form-group">
          <label for="height" class="control-label">Height</label>
          <div class="">
            <input type="number" class="form-control" id="height" name='height' placeholder="height">
          </div>
        </div>
        <img id='kitten_preview' src='https://placekitten.com/g/100/100' height='100px' width='100px' alt='kitten image'/>
      </div>

      <div id='lorem_fields' style='display:none'>
        <div class="form-group">
          
          {% for lorem_type in lorem_types %}
          <div class="radio">
            <label>
              <input type="radio" name="lorem_type" 
                     value="{{lorem_types[lorem_type].name}}">
              {{ lorem_types[lorem_type].label }}
            </label>
          </div>
          {% endfor %}
        </div>

        <div class='form-group'>
          <label for="num_para" class="control-label">number of paragraphs</label>
          <div class=''>
            <select name='num_para' class='form-control'>
              <option value='5'>5</option>
              <option value='4'>4</option>   
              <option value='3'>3</option>    
              <option value='2'>2</option>    
              <option value='1'>1</option>    

            </select>      
          </div>
        </div>
      </div>

      <div id='iframe_fields' style='display:none'>
        <div class="form-group">
          <label for="iframe_title" class="control-label">Title</label>
          <input type="textbox" class="form-control" id="iframe_title"
                 name='iframe_title' placeholder="optional, iframe title" />
        </div>
        <div class="form-group">
          <label for="iframe_width" class="control-label">Width</label>
          <input type="number" class="form-control" id="iframe_width"
          name='iframe_width' placeholder="width" value="640px"/>
        </div>
        <div class="form-group">
          <label for="iframe_height" class="control-label">Height</label>
          <input type="number" class="form-control" id="iframe_height"
          name='iframe_height' placeholder="height" value="200px"/>
        </div>
        <div class="form-group">
          <label for="iframe_url" class="control-label">URL</label>
          <input type="textbox" name="iframe_url" id="iframe_url" 
                 class="form-control" placeholder="src for iframe"/>
        </div>

        <iframe id="iframe_preview" src="" height="200" width="640"></iframe>
      </div>

      <button class='btn btn-primary' type='submit' 
        name='submit' value='submit' id='wanted_submit_btn' style='display:none'>Get Content</button>
    </form>      

</div>

{% endblock %}

{% block extra_js %}
<script type='text/javascript' src='/static/lorem_ipsum.js'></script>
{% endblock %}


* add templates/baconIpsumFetch.html
<div class='ipsum'>
{% for p in paragraphs %}
  <p>{{ p | safe }}</p>
{% endfor %}
</div>


* add templates/show_quotes.html
<h3>{{ lorem.label }}</h3>
{% for p in paragraphs %}
<div class='content-box'>
  <div class='grid-row'>
    <div class='col-xs-1'>
      <img class='avatar' style="width:75px; height: 75px" src="http://loremflickr.com/75/75?randomstuff={{ loop.index }}" width="75px" height="75px"/>
    </div>
    <div class='col-xs-11'>
      <p>{{ p.quote | safe }}</p> 
      <footer class='text-right'><cite title="{{ p.source }}"><em>{{ p.source }}</em></cite></footer>
    </div>
  </div>
</div>
{% endfor %}

* modify templates/xml/config.xml - add editor button piece
      {% if tool.editor_button %}
      <lticm:options name="editor_button">
        <lticm:property name="enabled">true</lticm:property>
        <lticm:property name="icon_url">{{ tool.editor_button.icon_url }}</lticm:property>
        <lticm:property name="selection_width">{{ tool.editor_button.selection_width }}</lticm:property>
        <lticm:property name="selection_height">{{ tool.editor_button.selection_height }}</lticm:property>
      </lticm:options>
      {% endif %}
