from index import app

application = app.server

"""
wsgi.py created in Digital Ocean droplet Ubuntu 18.04;
wsgi.py provides anchor for uwsgi.ini; 
uwsgi.ini looks for module wsgi.py and executes application variable (app.server) in file;
Alias as application because uwsgi looks for 'application' in designated module variable in uwsgi.ini;
"""

if __name__ == "__main__":
    app.run_server()
