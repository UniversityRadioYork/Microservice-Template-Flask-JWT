from waitress import serve
from flask import Flask, render_template, redirect, session, request
import os, requests, json, sys, secrets, re, jwt
from datetime import datetime
import urllib3

#Imports ENV variables

# port to run the app on, defaults to 6339
port = os.environ.get('PORT', 6339)

#url to redirect to when using jwt auth
scheduler_url = os.environ.get('SCHEDULER_URL', f"http://127.0.0.1:{port}/")

#key used for myradio jwt auth
myradio_key = os.environ.get('MYRADIO_SIGNING_KEY', "dev")

#key used to validate myradio api requests. This is the only thing you will need to edit for development.
myradio_api = os.environ.get('MYRADIO_API_KEY', "change_me")

#I'm not sure if this does anything but i'm scared to delete it
log_location = os.environ.get('LOG_LOCATION', "/logs/")

#url of the myradio api, change this if you want to test with the myradio dev instance (you don't)
myradio_url = os.environ.get('MYRADIO_URL', "https://www.ury.org.uk/api/v2/")

# Dev mode enables some debugging and other niceties
dev_mode = os.environ.get('DEV_MODE', "True")

#creates an app
class Config:
    PREFERRED_URL_SCHEME = 'https'

app = Flask(__name__)
app.config.from_object(Config())

#just logs some stuff
unix_timestamp = (datetime.now() - datetime(1970, 1, 1)).total_seconds()
print("Starting at " + str(unix_timestamp) , file=sys.stderr)
print("live on " + scheduler_url, file=sys.stderr)

#important for session stuff
app = Flask(__name__)
app.secret_key = secrets.token_urlsafe(16)

#formats api key a little
myradio_apikey = "api_key="+myradio_api

def auth_route():
    return redirect("https://ury.org.uk/myradio/MyRadio/jwt?redirectto="+scheduler_url+"auth/", code=302)

def verifyKey(key):
    pattern = re.compile('^[ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789]+$')
    return re.search(pattern, key)

#lets you in if you are comp officer or have "edit banner" permission or if the app is in dev mode
def verifySession(session):
    if myradio_key == "dev":
        return True
    if ('name' in session and 'uid' in session):
        api_url = myradio_url + "/user/"+str(session["uid"])+"/permissions?" + myradio_apikey
        response = requests.get(api_url)
        officer = json.loads(response.text)
        if 221 in officer["payload"] or 234 in officer["payload"]:
            return True
    return False

#either redirects the user to myradio to signing (see auth) or renders a flask-wtf form or stores the values from a submitted form
@app.route("/", methods=['GET'])
def index():
    if verifySession(session):
        return render_template('/index.html', title='Microservice Template')
    else:
        return auth_route()

#uses a jwt to authenticate the user then redirects them back to index
@app.route('/auth/', methods=['GET'])
def auth( ):
    args = request.args
    userinfo = jwt.decode(args['jwt'], myradio_key, algorithms=["HS256"])
    session['name'] = userinfo['name']
    session['uid'] = userinfo['uid']
    return redirect(scheduler_url, code=302)

@app.route('/logout/', methods=['GET'])
def logout():
    session.pop('name', None)
    session.pop('uid', None)
    return render_template('/loggedout.html', title='Logged Out')

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 6339))
    print("Starting server on port " + str(port), file=sys.stderr)
    if dev_mode == "True":
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        print("Running in dev mode", file=sys.stderr)
        app.run(debug=True, port=port)
    else:
        serve(app, host='0.0.0.0',port=port)
