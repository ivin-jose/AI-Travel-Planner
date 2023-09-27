from flask import Flask, render_template, request, redirect, session
from flask_mysqldb import MySQL
from datetime import datetime
import mysql.connector
import os
from os.path import realpath, dirname, join

app = Flask(__name__)


# Mysql DataBase 
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'somethingfishy1234'
app.config['MYSQL_DB'] = 'ai_travel_planner'
mysql = MySQL(app)


# The Secrete key
app.config['SECRET_KEY'] = "is my secret key"

# Set the path to your static/images/avatar directory

USER_AVATAR_UPLOAD_FOLDER = 'static/images/users/avatar'
BLOG_IMAGES = 'static/images/blog'

app.config['USER_AVATAR_UPLOAD_FOLDER'] = USER_AVATAR_UPLOAD_FOLDER
app.config['BLOG_IMAGES'] = BLOG_IMAGES

#CURRENT DATE

current_date = datetime.now()

# Print the current date in a specific format
today_date = current_date.strftime("%d-%b-%Y")


#CUSTOME ERROR PAGES

#Invalid pages

@app.errorhandler(404)

def page_not_found(e):
    return render_template('errors/404-error.html')

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
       query = "SELECT user_id, username FROM users WHERE (email = %s OR username = %s) AND password = %s"
       values = (email_or_username, email_or_username, password)
       cursor.execute(query, values)
       result = cursor.fetchall()
       
       if len(result) > 0:
        session['userid'] = result[0][0]
        session['username'] = result[0][1]
        return redirect('/')
       else:
        error_message = "Invalid username/email or password"

    return render_template('login.html', error_message=error_message)

@app.route('/signup', methods = ['GET', 'POST'])
def signup():
    username =''
    email = ''
    password = ''
    email_exist_msg = ''
    date = today_date
    profile_pic = "./static/images/default-avatar-profile.jpg"
    if request.method == 'POST':
        username = request.form.get('signupname')
        email = request.form.get('signupemail')
        password = request.form.get('signuppassword')
        country = request.form.get('country')

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
            insert_query = "INSERT INTO users (username, email, password, date, profile_pic, country) VALUES (%s, %s, %s, %s, %s, %s)"
            values = (username, email, password, date, profile_pic, country)
            cursor.execute(insert_query, values)
            mysql.connection.commit()

            cursor = mysql.connection.cursor()
            query = "SELECT user_id, username FROM users WHERE (email = %s OR username = %s) AND password = %s"
            values = (email, username, password)
            cursor.execute(query, values)
            result = cursor.fetchall()
            if len(result) > 0:
                session['userid'] = result[0][0]
                session['username'] = result[0][1]
                return redirect('/')


            return redirect('/login')

    return render_template('signup.html', email_exist_msg = email_exist_msg, username = username, email = email,
                         password = password)

''' User Session logout '''

@app.route('/logout')
def logout():
    session.pop('userid', None)  # Remove the user_id from the session
    session.pop('username', None)
    return redirect('/')


''' User Profile '''
@app.route('/userprofile', methods = ['GET', 'POST'])
def userprofile():
    cursor = mysql.connection.cursor()
    query = "SELECT * FROM users WHERE user_id = %s"
    values = (str(session['userid']),)
    cursor.execute(query, values)
    result = cursor.fetchall()

    return render_template('userprofile.html', data = result)

''' Edit User Profile '''
@app.route('/user_edit_profile', methods = ['GET', 'POST'])
def user_edit_profile():
    cursor = mysql.connection.cursor()
    query = "SELECT * FROM users WHERE user_id = %s"
    values = (str(session['userid']),)
    cursor.execute(query, values)
    result = cursor.fetchall()

    if request.method == 'POST':
        update_username = request.form.get('update-username')
        update_email = request.form.get('update-email')
        update_bio = request.form.get('update-bio')

        cursor = mysql.connection.cursor()
        query = "UPDATE users SET username = %s, email = %s, bio = %s WHERE user_id = %s"
        values = (update_username, update_email, update_bio, str(session['userid']))
        cursor.execute(query, values)
        mysql.connection.commit()

        cursor = mysql.connection.cursor()
        query = "SELECT * FROM users WHERE user_id = %s"
        values = (str(session['userid']),)
        cursor.execute(query, values)
        result = cursor.fetchall()
        return render_template('userprofile.html', data = result)

    return render_template('profile_edit.html', data = result)

''' Changing User Profile Image '''
@app.route('/user_edit_avatar', methods = ['GET', 'POST'])
def user_edit_avatar():
    if request.method == 'POST':
        userid = session['userid']
        file = request.files['file']
        path = '../static/images/users/avatar'
        file_path = (path + '/' + file.filename)
        data = 'file.read()'

        cursor = mysql.connection.cursor()
        query = "UPDATE users SET profile_pic = %s WHERE user_id = %s"
        values = (file_path, str(session['userid']))
        cursor.execute(query, values)
        mysql.connection.commit()

        cursor = mysql.connection.cursor()
        query = "SELECT * FROM users WHERE user_id = %s"
        values = (str(session['userid']),)
        cursor.execute(query, values)
        result = cursor.fetchall()

        # To move image to folder
        file.save(os.path.join(os.path.abspath(os.path.dirname(realpath(__file__))),app.config['USER_AVATAR_UPLOAD_FOLDER'], file.filename))
        return render_template('profile_edit.html', data = result)


''' Change Password '''

@app.route('/change_password', methods = ['GET', 'POST'])
def change_password():
    return render_template('change_password.html')

''' Changing password inserting to db '''
@app.route('/change_password2', methods = ['GET', 'POST'])
def change_password2():
    ans = ''
    current_password = request.form.get('oldPassword')
    newpassword = request.form.get('confirmPassword')
    cursor = mysql.connection.cursor()
    
    checking_password = "SELECT password FROM users WHERE username = %s AND user_id = %s"
    values = (session['username'], str(session['userid']))
    cursor.execute(checking_password, values)
    result = cursor.fetchall()
    ans = result[0][0]

    if ans != current_password:
        password_error_msg = "Wrong Password"
    else:
        cursor = mysql.connection.cursor()
        query = "UPDATE users SET password = %s WHERE user_id = %s"
        values = (newpassword, str(session['userid']))
        cursor.execute(query, values)
        mysql.connection.commit()

        cursor = mysql.connection.cursor()
        query = "SELECT * FROM users WHERE user_id = %s"
        values = (str(session['userid']),)
        cursor.execute(query, values)
        result = cursor.fetchall()
        return render_template('userprofile.html', data = result)

    return render_template('change_password.html', data = result, error_message = password_error_msg)

''' Blog Home Page '''

@app.route('/blog_home', methods=['POST', 'GET'])
def blog_home(): 
    cursor = mysql.connection.cursor()
    query = '''SELECT blog.blogid, blog.date, blog.heading, SUBSTRING_INDEX(blog.content, ' ', 50) AS truncated_content, users.profile_pic, users.username, CONCAT_WS(', ',
        CASE WHEN blog.adventure = 1 THEN 'adventure' ELSE NULL END,
        CASE WHEN blog.business = 1 THEN 'business trips' ELSE NULL END,
        CASE WHEN blog.solo = 1 THEN 'solo trip' ELSE NULL END,
        CASE WHEN blog.cruise = 1 THEN 'cruise' ELSE NULL END,
        CASE WHEN blog.honeymoon = 1 THEN 'honeymoon' ELSE NULL END,
        CASE WHEN blog.nature = 1 THEN 'nature' ELSE NULL END,
        CASE WHEN blog.vacation = 1 THEN 'vacation' ELSE NULL END
    ) AS categories,
    blog_images.image
    FROM 
    blog
    JOIN users ON blog.userid = users.user_id
    LEFT JOIN blog_images ON blog.blogid = blog_images.blog_id  -- Add this LEFT JOIN
    WHERE 
    blog.adventure = 1 OR
    blog.business = 1 OR
    blog.solo = 1 OR
    blog.cruise = 1 OR
    blog.honeymoon = 1 OR
    blog.nature = 1 OR
    blog.vacation = 1
    ORDER BY RAND() LIMIT 10'''

    cursor.execute(query)
    blog_result = cursor.fetchall()

    # Latest 3 Blogs

    cursor = mysql.connection.cursor()
    
    query = '''SELECT blog.blogid, blog.heading, blog.date, blog_images.image
               FROM blog
               JOIN blog_images ON blog.blogid = blog_images.blog_id
               ORDER BY blog.date DESC
               LIMIT 3'''
    
    cursor.execute(query)
    latest_blog= cursor.fetchall()

    return render_template('blog_home.html', blog_data=blog_result, latest_blog=latest_blog)

# Blog Single Page

@app.route('/blog_single/<int:blog_id>', methods=['POST', 'GET'])
def blog_single(blog_id):
    cursor = mysql.connection.cursor()
    query = '''SELECT blog.blogid, blog.date, blog.heading, blog.content, users.profile_pic, users.username, CONCAT_WS(', ',
        CASE WHEN blog.adventure = 1 THEN 'adventure' ELSE NULL END,
        CASE WHEN blog.business = 1 THEN 'business trips' ELSE NULL END,
        CASE WHEN blog.solo = 1 THEN 'solo trip' ELSE NULL END,
        CASE WHEN blog.cruise = 1 THEN 'cruise' ELSE NULL END,
        CASE WHEN blog.honeymoon = 1 THEN 'honeymoon' ELSE NULL END,
        CASE WHEN blog.nature = 1 THEN 'nature' ELSE NULL END,
        CASE WHEN blog.vacation = 1 THEN 'vacation' ELSE NULL END
    ) AS categories,
    blog_images.image
    FROM 
    blog
    JOIN users ON blog.userid = users.user_id
    LEFT JOIN blog_images ON blog.blogid = blog_images.blog_id  -- Add this LEFT JOIN
    WHERE
    blog.blogid = %s
    ORDER BY RAND() LIMIT 10'''

    cursor.execute(query, (blog_id,))
    blog_result = cursor.fetchall()

    # Latest 3 Blogs

    cursor = mysql.connection.cursor()
    
    query = '''SELECT blog.blogid, blog.heading, blog.date, blog_images.image
               FROM blog
               JOIN blog_images ON blog.blogid = blog_images.blog_id
               ORDER BY blog.date DESC
               LIMIT 3'''
    cursor.execute(query)
    latest_blog= cursor.fetchall()

    query = '''
           SELECT blog.blogid, blog.heading, blog.date, blog_images.image
           FROM blog
           JOIN blog_images ON blog.blogid = blog_images.blog_id
           ORDER BY RAND()
           LIMIT 2
        '''
    cursor.execute(query)
    related_blog= cursor.fetchall()

    return render_template('blog_single.html', blog_data=blog_result, latest_blog=latest_blog, related_blog=related_blog)

@app.route('/blog_categories/<categorie>', methods=['POST', 'GET'])
def blog_categories(categorie):
    cursor = mysql.connection.cursor()
    
    # Create a list of category columns to check based on the 'categorie' parameter
    category_columns = {
        'adventure': 'blog.adventure',
        'business': 'blog.business',
        'solo': 'blog.solo',
        'cruise': 'blog.cruise',
        'honeymoon': 'blog.honeymoon',
        'nature': 'blog.nature',
        'vacation': 'blog.vacation'
    }
    
    # Get the category column for the selected category
    category_column = category_columns.get(categorie, None)
    
    if category_column:
        # Build the SQL query dynamically to filter by the selected category
        query = f'''SELECT blog.blogid, blog.date, blog.heading, SUBSTRING_INDEX(blog.content, ' ', 50) AS truncated_content, users.profile_pic, users.username, CONCAT_WS(', ',
            CASE WHEN blog.adventure = 1 THEN 'adventure' ELSE NULL END,
            CASE WHEN blog.business = 1 THEN 'business trips' ELSE NULL END,
            CASE WHEN blog.solo = 1 THEN 'solo trip' ELSE NULL END,
            CASE WHEN blog.cruise = 1 THEN 'cruise' ELSE NULL END,
            CASE WHEN blog.honeymoon = 1 THEN 'honeymoon' ELSE NULL END,
            CASE WHEN blog.nature = 1 THEN 'nature' ELSE NULL END,
            CASE WHEN blog.vacation = 1 THEN 'vacation' ELSE NULL END
        ) AS categories,
        blog_images.image
        FROM 
        blog
        JOIN users ON blog.userid = users.user_id
        LEFT JOIN blog_images ON blog.blogid = blog_images.blog_id
        WHERE
        {category_column} = 1
        ORDER BY RAND() LIMIT 10'''
        
        cursor.execute(query)
        blog_result = cursor.fetchall()

        # Latest 3 Blogs

        cursor = mysql.connection.cursor()
        
        query = '''SELECT blog.blogid, blog.heading, blog.date, blog_images.image
                   FROM blog
                   JOIN blog_images ON blog.blogid = blog_images.blog_id
                   ORDER BY blog.date DESC
                   LIMIT 3'''
        
        cursor.execute(query)
        latest_blog= cursor.fetchall()

        return render_template('blog_home.html', blog_data=blog_result, latest_blog=latest_blog)
    else:
        # Handle the case where an invalid category is provided in the URL
        return redirect('/blog_home')

# Blog Content Uploading 

@app.route('/blog_upload', methods=['POST', 'GET'])
def blog_upload():
    if request.method == 'POST':
        cursor = mysql.connection.cursor()
        
        # Insert blog content
        heading = request.form.get('blog_heading')
        content = request.form.get('blog_content')
        adventure = request.form.get('adventure')
        business = request.form.get('business-trips')
        solo = request.form.get('solo-trip')
        cruise = request.form.get('cruises')
        honeymoon = request.form.get('honeymoon')
        vacation = request.form.get('vacations')
        nature = request.form.get('nature')

        insert_blog_query = "INSERT INTO blog (userid, date, heading, content, adventure, business, solo, cruise, honeymoon, nature, vacation) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        blog_values = (session['userid'], today_date, heading, content, adventure, business, solo, cruise, honeymoon, nature, vacation)
        cursor.execute(insert_blog_query, blog_values)
        mysql.connection.commit()

        # Get the generated blog_id
        blog_id = cursor.lastrowid
        
        # Insert images associated with the blog
        files = request.files.getlist('images')
        for file in files:
            path = '../static/images/blog'
            file_path = (path + '/' + file.filename)
            file.save(os.path.join(os.path.abspath(os.path.dirname(realpath(__file__))), app.config['BLOG_IMAGES'], file.filename))
            
            insert_image_query = "INSERT INTO blog_images (blog_id, user_id, image) VALUES (%s, %s, %s)"
            image_values = (blog_id, session['userid'], file_path)
            cursor.execute(insert_image_query, image_values)
            mysql.connection.commit()
        
        cursor.close()

    cursor = mysql.connection.cursor()
    query = "SELECT * FROM users WHERE user_id = %s"
    values = (str(session['userid']),)
    cursor.execute(query, values)
    result = cursor.fetchall()

    return render_template('blog_upload.html', data=result)




#---------------------------------------------------------
#---------------------------------------------------------
#---------------------------------------------------------
#---------------------------------------------------------

''' CHECK THE ADMIN LOGIN SESSION '''


@app.route('/admin_dashboard', methods=['GET', 'POST'])
def admin_dashboard():
    if 'admin_name' in session and 'adminid' in session:
        cursor = mysql.connection.cursor()
        query = "SELECT * FROM admin"
        cursor.execute(query)
        admins = cursor.fetchall()
        return render_template('admin/dashboard.html', admins = admins)
    else:
        return redirect('admin')


''' Admin Login and session creation '''

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    error_message = ''

    if request.method == 'POST':
        adminname = request.form.get('adminname')
        password = request.form.get('adminpassword')

        # Checking password and admin name 
        cursor = mysql.connection.cursor()
        query = "SELECT adminid, name FROM admin WHERE name = %s AND password = %s"
        values = (adminname, password)
        cursor.execute(query, values)
        result = cursor.fetchall()

        # fetching admin name 
        cursor = mysql.connection.cursor()
        query = "SELECT * FROM admin"
        cursor.execute(query)
        admins = cursor.fetchall()

        if len(result) > 0:
            session['adminid'] = result[0][0]
            session['admin_name'] = result[0][1]
            return render_template('admin/dashboard.html', admins = admins)
        else:
            error_message = "Invalid credentials"

    return render_template('admin/admin_login.html', error_message=error_message)


''' Add admin name and passwords to db '''

@app.route('/add_admin', methods=['GET', 'POST'])
def add_admin():
 if request.method == 'POST':
    adminname = request.form.get('admin_name')
    password = request.form.get('admin_password')
    cursor = mysql.connection.cursor()

    # Check if admin already exists
    query = "SELECT * FROM admin WHERE name = %s"
    cursor.execute(query, (adminname,))
    admin = cursor.fetchone()

    # Fetch all admins again after adding the new one
    query = "SELECT * FROM admin"
    cursor.execute(query)
    admins = cursor.fetchall()
    if admin:
        status_message = "Admin already exists."
        return render_template('admin/dashboard.html',admins = admins, add_status_message=status_message)

    # Insert the new admin into the database
    insert_query = "INSERT INTO admin (name, password) VALUES (%s, %s)"
    cursor.execute(insert_query, (adminname, password))
    mysql.connection.commit()

    status_message = "Admin added successfully."
    # Fetch all admins again after adding the new one
    query = "SELECT * FROM admin"
    cursor.execute(query)
    admins = cursor.fetchall()
    
    return render_template('admin/dashboard.html', admins=admins, add_status_message=status_message)
 else:
    return redirect('admin')

''' Delete admins '''

@app.route('/delete_admin/<int:aid>', methods=['GET', 'POST'])
def delete_admin(aid):
    cursor = mysql.connection.cursor()
    delete_query = "DELETE FROM admin WHERE adminid = %s"
    delete_val = (aid,)
    cursor.execute(delete_query, delete_val)
    mysql.connection.commit()
    status_message = "Admin Deleted!!"

    # fetching admin name 
    cursor = mysql.connection.cursor()
    query = "SELECT * FROM admin"
    cursor.execute(query)
    admins = cursor.fetchall()
    return render_template('admin/dashboard.html', admins = admins, dlt_status_message=status_message)

''' Session Logout Admins '''

@app.route('/admin_logout')
def admin_logout():
   session['adminid'] = None
   session['admin_name'] = None
   return redirect('admin')

@app.route('/admin_blog')
def admin_blog():
   return render_template('admin/admin_blog.html')

