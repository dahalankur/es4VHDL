from flask import Flask, render_template, request

app = Flask(__name__, template_folder='templates')

@app.route("/")
def index():
    return render_template('index.html') 

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404
