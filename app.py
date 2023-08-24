# Flask:Python Framework for web development,other examples include django
# Modules:Python files containing python functions(lowercase) and classes(uppercase)
# flask is an external python module that we need to install by "pip" command
# python (app.py)- Backend application
# folder templates- used to hold all the html files (Front End)
# static folder -used to hold resources e.g images,js,css....
# class Flask-used to create the flask application
# decorators (@)-it injects functionality to an object variable
# variable="Erick"
# @variable="Erick"
# flask is a single file application framework where different functionalities have been separated by routes
# cursor-a function to allow a connectionto executesql codes on python files
# sessions-->Identify logged in users on the system e.g username,emails
# session hijacking -->Attackers can access your session then impersonates you on the system
from flask import Flask,render_template,request,redirect,session
import pymysql
connection=pymysql.connect(host='localhost',user='root',password='',database='misoji')
print("Successful database connection")

app=Flask(__name__)
app.secret_key='kdfuinvsaugdrgohrg-rgjrg83477438998237fbbfdb2130'
# Default Home route
@app.route('/product')
def product():
    connection=pymysql.connect(host='localhost',user='root',password='',database='misoji')
    
    # phone
    cursor_phone=connection.cursor()
    sql_phone='select*from stickers'
    cursor_phone.execute(sql_phone)

    data=cursor_phone.fetchall()

    return render_template('product.html',phone=data)

@app.route('/single/<stickerset_id>')
def single(stickerset_id):
    connection=pymysql.connect(host='localhost',user='root',password='',database='misoji')
    print("Successful database connection")

    cursor_single=connection.cursor()
    sql_single='select * from stickers where stickerset_id=%s'
    # Formatting options(%s)-Place the value during sql execution
    cursor_single.execute(sql_single,stickerset_id)

    data=cursor_single.fetchone()
    print(data)

    

# similar products basedon category-data[4]
    cursor_similar=connection.cursor()
    sql_similar='select * from stickers '
    cursor_similar.execute(sql_similar)
    similar =cursor_similar.fetchall()
    return render_template('single.html',similar_products=similar,single=data)

# Specifying the route,will implement both methods
# before registration->we 'GET' The registration
# After registration->we 'POST' the form data

@app.route('/register',methods=['POST','GET'])
def register():
    if request.method== 'POST':
        username =request.form["username"]
        email=request.form["email"]
        phone=request.form["phone"]
        password1=request.form["password1"]
        password2=request.form["password2"]

        # server form validation
        # check that at least password exceeds 8 characters
        # name="Antony" len(name)-->6

        if len(password1)<= 8:
            return render_template('register.html',error ='Password must be at least 8 characters')
        elif password1!=password2:
            return render_template('register.html',error='Passwords do not match')
        else:
            connection=pymysql.connect(host='localhost',user='root',password='',database='misoji')
            print("Successful database connection")

            cursor_register=connection.cursor()
            sql_register='insert into users (username,email,phone,password) values (%s,%s,%s,%s)'
            cursor_register.execute(sql_register,(username,email,phone,password1))

            # commit:ensures that database has been updated with the new record
            connection.commit()
            # sms application
            from sms import send_sms
            send_sms(phone,f'Thank You for registering,your username is {username} and your password is {password1}')

            return render_template('register.html',success='Registered Successfully')

    else:
        return render_template('register.html')
    
# POST-->sending information from the client to the server
# GET-->receiving info (htmls) from the server to the client

@app.route('/login',methods=['POST','GET'])
def login():
    if request.method=='POST':
        username=request.form["username"]
        password=request.form["password"]

        connection=pymysql.connect(host='localhost',user='root',password='',database='misoji')
        print("Successful database connection")
        cursor_login=connection.cursor()
        sql_login='select * from users where username=%s and password=%s'
        cursor_login.execute(sql_login,(username,password))

        # rowcount: returns the number of records on a table then returns a numeric value

        if cursor_login.rowcount==0:
            return render_template('login.html',error='Invalid username or password,Try again!!!')
        else:
            # access
            session['key']= username
            return redirect('/')
    else:
        return render_template('login.html')


@app.route('/logout')
def logout():
    if 'key' in session:
        session.clear()
        return redirect('/')
    return render_template('login.html')


import requests
import datetime
import base64
from requests.auth import HTTPBasicAuth

@app.route('/mpesa', methods=['POST', 'GET'])
def mpesa_payment():
    if request.method == 'POST':
        phone = str(request.form['phone'])
        amount = str(request.form['amount'])
        # GENERATING THE ACCESS TOKEN
        # create an account on safaricom daraja
        consumer_key = "GTWADFxIpUfDoNikNGqq1C3023evM6UH"
        consumer_secret = "amFbAoUByPV2rM5A"

        api_URL = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"  # AUTH URL
        r = requests.get(api_URL, auth=HTTPBasicAuth(consumer_key, consumer_secret))

        data = r.json()
        access_token = "Bearer" + ' ' + data['access_token']

        #  GETTING THE PASSWORD
        timestamp = datetime.datetime.today().strftime('%Y%m%d%H%M%S')
        passkey = 'bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919'
        business_short_code = "174379"
        data = business_short_code + passkey + timestamp
        encoded = base64.b64encode(data.encode())
        password = encoded.decode('utf-8')

        # BODY OR PAYLOAD
        payload = {
            "BusinessShortCode": "174379",
            "Password": "{}".format(password),
            "Timestamp": "{}".format(timestamp),
            "TransactionType": "CustomerPayBillOnline",
            "Amount": amount,  # use 1 when testing
            "PartyA": phone,  # change to your number
            "PartyB": "174379",
            "PhoneNumber": phone,
            "CallBackURL": "https://modcom.co.ke/job/confirmation.php",
            "AccountReference": "account",
            "TransactionDesc": "account"
        }

        # POPULAING THE HTTP HEADER
        headers = {
            "Authorization": access_token,
            "Content-Type": "application/json"
        }

        url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"  # C2B URL

        response = requests.post(url, json=payload, headers=headers)
        print(response.text)
        return '<h3>Please Complete Payment in Your Phone and we will deliver in minutes</h3>' \
               '<a href="/" class="btn btn-dark btn-sm">Back to Products</a>'
    else:
        return render_template('single.html')


@app.route('/vendor', methods=['POST','GET'])
def vendor():
    if request.method == 'POST':
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        county = request.form['county']
        email = request.form['email']
        password3 = request.form['password3']
        password4 = request.form['password4']

        if len(password3)<= 8:
            return render_template('vendor.html',error ='Password must be at least 8 characters')
        elif password3!=password4:
            return render_template('vendor.html',error='Passwords do not match')
        else:
            connection=pymysql.connect(host='localhost',user='root',password='',database='misoji')
            print("Successful database connection")
        

        cursor_vendor=connection.cursor()
        sql_vendor='insert into vendors (firstname,lastname,county,email,password) values (%s,%s,%s,%s,%s)'
        cursor_vendor.execute(sql_vendor,(firstname,lastname,county,email,password3))

        connection.commit()
        return render_template('vendor.html',success='Registered Successfully')

    else:
        return render_template('vendor.html')
    
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/aboutus')
def aboutus():
    return render_template('aboutus.html')

@app.route('/realitytv')
def realitytv():
    return render_template('realitytv.html')
app.run(debug = True)
# end
# flask-->django
# front (html,css,javascript)-->
# React/AngularJS/VueJS
# MySQL/PostGreSQL,SQLite

# web hosting
# call backs