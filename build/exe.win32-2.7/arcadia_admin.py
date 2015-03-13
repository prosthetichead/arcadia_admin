#!flask/bin/python
from arcadia_admin import app, db
from cherrypy import wsgiserver

db.create_all()

# app.run(debug=True, host='0.0.0.0')


d = wsgiserver.WSGIPathInfoDispatcher({'/': app})
server = wsgiserver.CherryPyWSGIServer(('0.0.0.0', 8080), d)

if __name__ == '__main__':
	try:
		server.start()
	except KeyboardInterrupt:
		server.stop()