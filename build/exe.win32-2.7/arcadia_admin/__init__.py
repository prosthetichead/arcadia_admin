import os
import re
import sys
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from arcadia_admin import theGameDB
from jinja2 import evalcontextfilter, Markup, escape


def find_data_file(filename):
    if getattr(sys, 'frozen', False):
        # The application is frozen
        datadir = os.path.dirname(sys.executable)
        datadir = os.path.join(datadir, 'arcadia_admin')
    else:
        # The application is not frozen
        datadir = os.path.dirname(__file__)
        
    return os.path.join(datadir, filename)


template_path = find_data_file('templates')


app = Flask(__name__, template_folder=template_path)

# custom filter for JinJa2 taken from here http://flask.pocoo.org/snippets/28/
# replaces \n with <p> and <br>
_paragraph_re = re.compile(r'(?:\r\n|\r|\n){2,}')
@app.template_filter()
@evalcontextfilter
def nl2br(eval_ctx, value):
    result = u'\n\n'.join(u'<p>%s</p>' % p.replace('\n', '<br>\n') \
        for p in _paragraph_re.split(escape(value)))
    if eval_ctx.autoescape:
        result = Markup(result)
    return result

app.config.from_object('config')
db = SQLAlchemy(app)
theGameDB.refresh_platform_choices() ## one off load of the platforms from gamedb

# initialization done, load up the  the modules
from arcadia_admin import views, models

