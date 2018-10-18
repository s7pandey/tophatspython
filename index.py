from flask import Flask, render_template, url_for, request
from flask_mail import Mail, Message

import maine_combined
import montclair_combined
import rhode_combined
import westchester_combined

from multiprocessing.pool import ThreadPool

import boto3

app = Flask(__name__)
mail = Mail(app)
name = "app"
pool = ThreadPool(processes=2)

def email_result(result):
    print(result)
    return 

@app.route("/")
def hello():
    return render_template("index.html", name=name)

@app.route("/values", methods=['POST'])
def values():
    school = request.form["school"]
    term = request.form["term"]
    if school == "Montclair":
        pool.apply_async(target=montclair_combined.scrape_classes, args=[term] callback=email_result)
    elif school == "Rhode":
        pool.apply_async(target=rhode_combined.scrape_classes,args=[term] callback=email_result)
    elif school == "Westchester":
        pool.apply_async(target=westchester_combined.scrape_classes,args=[term], callback=email_result)
    
    return render_template("index.html", name=name)



if __name__ == "__main__":
    app.run()
