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
 
create new file 
----------------
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
