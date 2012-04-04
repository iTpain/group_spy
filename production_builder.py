import subprocess, os, signal
import asset_cook

f = open("../logs/django-server.pid")
pid = f.read()
f.close()

subprocess.check_call(["git", "pull", "github", "master"])
subprocess.check_call(["git", "pull", "github", "master"], cwd='/srv/django-projects/jsage/')
subprocess.check_call(["git", "pull", "github", "master"], cwd='/srv/django-projects/js_external/')
print "repos fetched"

try:
    os.kill(int(pid), signal.SIGTERM)
    print "Django killed"
except OSError as err:
    print err

try:
    subprocess.check_call(["screen", "-X", "kill"])
except:
    print "failed to kill scanner"
print "scanner killed"

asset_cook.process_templates("main_spy/templates/", "main_spy/production_templates/", "main_spy/static")
print "Assets baked"

subprocess.check_call(["python", "manage.py", "runfcgi", "method=prefork", "maxchildren=10", "maxspare=5", "minspare=2", "maxrequests=200", 
                       "socket=/srv/django-projects/groupspy/logs/django-server.sock", "pidfile=/srv/django-projects/groupspy/logs/django-server.pid", "umask=777" ])
subprocess.check_call(["chmod", "777", "../logs/django-server.sock"])
print "Django restarted"

subprocess.check_call(["screen", "-S", "group_spy_scanner", "-d", "-m", "python", "test.py"])
print "scanner restarted"
