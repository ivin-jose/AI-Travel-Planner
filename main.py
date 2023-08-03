from flask import Flask, render_template, request, redirect
from flask_mysqldb import MySQL
from datetime import datetime
import mysql.connector

app = Flask(__name__)

# Mysql DataBase 
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'somethingfishy1234'
app.config['MYSQL_DB'] = 'ai_travel_planner'
mysql = MySQL(app)


# The Secrete key
app.config['SECRET_KEY'] = "is my secret key"


#CURRENT DATE

current_date = datetime.now()

# Print the current date in a specific format
today_date = current_date.strftime("%d-%b-%Y")


#CUSTOME ERROR PAGES

#Invalid pages

@app.errorhandler(404)

def page_not_found(e):
    return render_template('errors/404.html')

#Internal server error

@app.errorhandler(500)

def page_not_found(e):
    return render_template('errors/505.html')



@app.route('/')
def home():
    return render_template('index.html')


@app.route('/login', methods = ['GET', 'POST'])
def login():
    error_message = ''
    if request.method == 'POST':
       email_or_username = request.form.get('loginname')
       password = request.form.get('loginpassword')

       ''' Checking password and username or email'''
       cursor = mysql.connection.cursor()
       query = "SELECT * FROM users WHERE (email = %s OR username = %s) AND password = %s"
       values = (email_or_username, email_or_username, password)
       cursor.execute(query, values)
       result = cursor.fetchall()
       if len(result) > 0:
        return redirect('/')
       else:
        error_message = "Invalid username/email or password"

    return render_template('login.html', error_message=error_message)

@app.route('/signup', methods = ['GET', 'POST'])
def signup():
    username =''
    email = ''
    security_q = ''
    password = ''
    email_exist_msg = ''
    date = today_date
    if request.method == 'POST':
        username = request.form.get('signupname')
        email = request.form.get('signupemail')
        security_q = request.form.get('signupsecuritycode')
        password = request.form.get('signuppassword')

        '''Adding user data to MySQL db'''

        cursor = mysql.connection.cursor()
        checking_username_unique = "SELECT * FROM users WHERE email = %s"
        values = (email,)
        cursor.execute(checking_username_unique, values)
        result = cursor.fetchall()

        if len(result) > 0:
            email_exist_msg = "Email Already Taken"
        else:
            # Insert new user data into the 'users' table
            insert_query = "INSERT INTO users (username, email, security_code, password, date) VALUES (%s, %s, %s, %s, %s)"
            values = (username, email, security_q, password, date)
            cursor.execute(insert_query, values)
            mysql.connection.commit()
            return redirect('/')

    return render_template('signup.html', email_exist_msg = email_exist_msg, username = username, email = email,
                            security_q = security_q, password = password)
