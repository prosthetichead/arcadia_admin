#!flask/bin/python
from arcadia_admin import app, db

##create the database if we need it
db.create_all()

#start the server
app.run(debug=True, host='0.0.0.0')

#clean up after server finished