"""
This file creates your application.
"""
import os
from flask import Flask, render_template, request, redirect, url_for, session
app = Flask(__name__)
app.debug = True

@app.route('/')
def index():
    # "index.html" is a file found in the "templates" folder. It is mostly regular
    # HTML with some special templating syntax mixed in. The templating
    # language is called Jinja.
    return render_template('index.html')

@app.route('/hello_world')
def hello_world():
    return 'Hello World!'

# I like to make certain values available on any page that is rendered without
# explicitly naming them when a template is rendered.
@app.context_processor
def inject_app_info():
  return {
      'version':"0.0.1",
      'project_name':'LTI Starter'
      }

if __name__ == '__main__':
  ''' IP and PORT are two environmental variables configured in Cloud9. They
  can change occasionally without warning so the application must be able to
  dynamically detect the change on each startup.'''

  app.run(host=os.getenv('IP','0.0.0.0'),port=os.getenv('PORT',5000))    
