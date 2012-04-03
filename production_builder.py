import subprocess, os, signal
import asset_cook

f = open("../logs/django-server.pid")
pid = f.read()
f.close()

try:
    os.kill(int(pid), signal.SIGTERM)
    print "Django killed"
except OSError as err:
    print err
    
subprocess.check_call(["python", "manage.py", "runfcgi", "method=prefork", "maxchildren=10", "maxspare=5", "minspare=2", "maxrequests=200", 
                       "socket=/srv/django-projects/groupspy/logs/django-server.sock", "pidfile=/srv/django-projects/groupspy/logs/django-server.pid", "umask=777" ])
subprocess.check_call(["chmod", "777", "../logs/django-server.sock"])
print "Django restarted"

asset_cook.process_templates("main_spy/templates/", "main_spy/static")
print "Assets baked"