from flask import Flask, render_template, url_for
import boto3

app = Flask(__name__)

name = "Flask-app"

@app.route("/")
def hello():
    return render_template("index.html", name=name)

if __name__ == "__main__":
    app.run()
