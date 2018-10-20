import datetime
import os
from flask import Flask, render_template, url_for, request, make_response
from flask_mail import Mail, Message

import pandas as pd

import maine_combined
import montclair_combined
import rhode_combined
import westchester_combined

from multiprocessing.pool import ThreadPool

import boto3

app = Flask(__name__)

app.config.update(dict(
    DEBUG = True,
    # email server
    MAIL_SERVER = 'smtp.googlemail.com',
    MAIL_PORT = 465,
    MAIL_USE_TLS = False,
    MAIL_USE_SSL = True,
    MAIL_USERNAME = 'shashwat.pandey.com@gmail.com',
    MAIL_PASSWORD = 'wioholdczxanrxpm',

    # administrator list
    ADMINS = ['shashwat.pandey.com@gmail.com']
))
schools = {
    "Montclair": [montclair_combined.scrape_classes, montclair_combined.scrape_profs], 
    "Rhode": [rhode_combined.scrape_classes, rhode_combined.scrape_profs],
    "Westchester": [westchester_combined.scrape_classes, westchester_combined.scrape_profs]
    }
mail = Mail(app)
name = "app"
pool = ThreadPool(processes=2)

def run_school(school, term, args={}, frame=None):
    pool.apply_async(schools[school][0], args=[term, args, frame], callback=get_profs)

def run_profs(school, frame):
    pool.apply_async(schools[school][1], args=[args, frame], callback=email_result)

def get_profs(result):
    args = result[1]
    if not args["finished"]:
        run_school(args["school"], args["term"], args, result)
        return
    frame = pd.DataFrame(result[0])
    run_profs(args["school"], frame)

def email_result(result):
    frame = pd.DataFrame(result[0])
    name = args["school"]+'_'+args["term"].replace(" ","_")+'.xlsx'
    frame.to_excel('./temp/'+name)
    with app.app_context():
        msg = Message(subject=name, sender="shashwat.pandey.com@gmail.com", recipients=["shashwat.pandey.com@gmail.com"])
        with open('./temp/'+name, 'rb') as fp:
            msg.attach(name+'.xlsx', "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", fp.read())
        mail.send(msg)
    os.remove('./temp/'+name)
    return 

@app.route("/")
def hello():
    return render_template("index.html", name=name)

@app.route("/values", methods=['POST'])
def values():
    school = request.form["school"]
    term = request.form["term"]
    response = make_response(render_template("index.html", name=name))
    response.set_cookie(school+"_"+term.replace(" ","_"), str(datetime.datetime.now()), expires=datetime.datetime.now() + datetime.timedelta(days=3))
    run_school(school,term)
    
    return response



if __name__ == "__main__":
    app.run()
