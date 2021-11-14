from flask import Flask, render_template, request, flash
from flask.wrappers import Request
import pyrebase
from flask_sqlalchemy import SQLAlchemy
import json
import requests
import csv
import io
from pathlib import Path



app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///pending_details.db"
app.config['SECRET_KEY'] = 'mysecret'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class User(db.Model):
    email = db.Column(db.String(120), unique=True, nullable=False, primary_key=True)
    password = db.Column(db.String(120), nullable = False)
    
dbfile=Path(r'/pending_details.db')
if not dbfile.exists():
    db.create_all()

config = {
    'apiKey': "AIzaSyAkTRKdJ9IdhAhDBvF200bpM_D6VUYC5Tg",
    'authDomain': "messageapp-67fc1.firebaseapp.com",
    'databaseURL': "https://messageapp-67fc1-default-rtdb.firebaseio.com",
    'projectId': "messageapp-67fc1",
    'storageBucket': "messageapp-67fc1.appspot.com",
    'messagingSenderId': "253214828846",
    'appId': "1:253214828846:web:b84582bc6d106e351732bf",
    'measurementId': "G-JMBJS6NT9F"
}

firebase = pyrebase.initialize_app(config)
with open('users.csv','a+') as userr:
    pass
auth = firebase.auth()
def register(email,password):
    # with open('users.csv','r') as userr:
    #     reader=csv.reader(userr,delimiter=',',lineterminator="\n")
    #     for row in reader:
    #         if row[0]==email:
    #             return 
    #     with open('users.csv','a+') as userw:
    #         writer=csv.writer(userw,delimiter=',',lineterminator="\n")
    #         writer.writerow([email,password])
    
    data = User(email=email,password=password)
    db.session.add(data)
    db.session.commit()
    
    
    
@app.route("/")
def mainPage():
    return render_template("index.html")

@app.route("/adminLogin", methods=['GET', 'POST'])
def adminLogin():
    try:
        if request.method == 'POST':
            data=[]
            email = request.form['a_email']
            password = request.form['a_pass']
            auth.sign_in_with_email_and_password(email, password)
            # with open('users.csv','r') as userr:
            #     reader=csv.reader(userr,delimiter=',',lineterminator="\n")
            #     for row in reader:
            #         data.append(row)
            data=User.query.all()
            print(type(data))
            return render_template("admin.html",data=data)
        return render_template("adminLogin.html")
    except:
        return render_template("adminLogin.html")

@app.route("/adduser", methods=['GET', 'POST'])
def adduser():
    
        if request.method == 'GET':
            email=request.args.get('user')
            print(email)
            data=(User.query.filter_by(email=email))
            new_user = auth.create_user_with_email_and_password(email, data[0].password)
            auth.send_email_verification(new_user['idToken'])
            data.delete()
            db.session.commit()
            return render_template("adminLogin.html")
    
    
 
@app.route("/deluser", methods=['GET', 'POST'])
def deluser():
    try:
        if request.method == 'GET':
            email=request.args.get('user')
            print(email)
            data=(User.query.filter_by(email=email))           
            data.delete()
            db.session.commit()
            return render_template("adminLogin.html")
    except:
        return render_template("adminLogin.html")
    
@app.route("/authenticateSingleSender", methods=['GET', 'POST'])
def singleAuthenticator():
    try:
        if request.method == 'POST':
            email = request.form['s_email']
            password = request.form['s_pass']
            register(email,password)
            # new_user = auth.create_user_with_email_and_password(email, password)
            # auth.send_email_verification(new_user['idToken'])
            return render_template('index.html')
    except:
        if request.method == 'POST':
            email = request.form['l_email']
            password = request.form['l_pass']
            auth.sign_in_with_email_and_password(email, password)
            return render_template('single_sender.html')
    return render_template('authSingle.html')

@app.route("/authenticateBulkSender", methods=['GET', 'POST'])
def bulkAuthenticator():
    try:
        if request.method == 'POST':
            email = request.form['s_email']
            password = request.form['s_pass']
            register(email,password)
            # new_user = auth.create_user_with_email_and_password(email, password)
            # auth.send_email_verification(new_user['idToken'])
            return render_template('index.html')
    except:
        if request.method == 'POST':
            email = request.form['l_email']
            password = request.form['l_pass']
            auth.sign_in_with_email_and_password(email, password)
            return render_template('bulk_sender.html')
    return render_template('authBulk.html')
@app.route("/singleMessageSender", methods=['GET','POST'])
def singleMessageSender():
    try:
        if request.method == 'POST':
            mobileNumber =  request.form['mobile']
            message = request.form['message']
            url = f'http://API2.SEND99.COM/api/SendSMS?api_id=API353738097601&api_password=XR9c2k1P8J&sms_type=P&encoding=T&sender_id=SMSInfo&phonenumber={mobileNumber}&textmessage={message}'
            print (url)
            response = requests.get(url)
            print (response)
            flash("Message Sent!")
    except Exception as e :
        print (e)
    return render_template('single_sender.html')
@app.route("/bulkMessageSender", methods=['GET', 'POST'])
def bulkMessageSender():
    if request.method == 'POST':
        try:
            message=request.form['message']
            f = request.files['file']
            if not f:
                print("No file")
            else:
                if ".csv" in f.filename:
                    stream = io.StringIO(f.stream.read().decode("UTF8"), newline=None)
                    reader=csv.reader(stream)
                    mobileNumber=""
                    for row in reader:
                        if row[0].isnumeric() :
                            mobileNumber+=row[0]+","
                    mobileNumber=mobileNumber[:-1]
                    print(mobileNumber)
                    url=f"http://API2.SEND99.COM/api/SendSMSMulti?api_id=API363273267078&api_password=na1HzZFn5t&sms_type=P&encoding=T&sender_id=INFOS&phonenumber={mobileNumber}&textmessage={message}&uid="
                    response = requests.get(url)
                    print (response.json())
                    flash("Message Sent!")
        except:
            pass
        return render_template('bulk_sender.html')
if __name__ == "__main__":
    app.run(debug=True)

 