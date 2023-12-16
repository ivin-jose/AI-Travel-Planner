from flask import Flask, render_template, request, redirect, session, url_for, flash
from flask_mysqldb import MySQL
from datetime import datetime
import mysql.connector
import os
from os.path import realpath, dirname, join
from flask_paginate import Pagination

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
BLOG_UPLOAD_IMAGES = 'static/images/blog'
TOUR_PACKAGE_IMAGES = 'static/images/tour_packages'

app.config['USER_AVATAR_UPLOAD_FOLDER'] = USER_AVATAR_UPLOAD_FOLDER
app.config['BLOG_IMAGES'] = BLOG_IMAGES
app.config['BLOG_UPLOAD_IMAGES'] = BLOG_UPLOAD_IMAGES
app.config['TOUR_PACKAGE_IMAGES'] = TOUR_PACKAGE_IMAGES

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


# Direct to home page
@app.route('/sepwrite.com')
def home():
    return render_template('index.html')

# if home 
@app.route('/user.settings')
def user_settings():
    cursor = mysql.connection.cursor()
    query = "SELECT * FROM users WHERE user_id = %s"
    values = (str(session['userid']),)
    cursor.execute(query, values)
    result = cursor.fetchall()
    return render_template('user_settings.html', data = result)

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
    profile_pic = "../static/images/default-avatar-profile.jpg"
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

@app.route('/user-logout')
def user_logout():
    return render_template('user_delete.html')

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

    cursor = mysql.connection.cursor()
    query = '''SELECT blog.blogid, blog.heading, blog_images.image
                FROM blog AS blog
                INNER JOIN blog_images AS blog_images ON blog.blogid = blog_images.blog_id
                WHERE blog.userid = %s LIMIT 4
            '''
    cursor.execute(query, (str(session['userid']),))
    profile_blgos = cursor.fetchall()

    return render_template('userprofile.html', data = result, profile_blgos=profile_blgos)

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
    page = request.args.get('page', type=int, default=1)
    per_page = 8  # Number of blogs per page

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
    ORDER BY RAND()
    LIMIT %s OFFSET %s
    '''

    offset = (page - 1) * per_page
    cursor.execute(query, (per_page, offset))
    blog_result = cursor.fetchall()

    # Count total blogs for pagination
    cursor.execute('''SELECT COUNT(*) FROM blog
                      WHERE adventure = 1 OR
                      business = 1 OR
                      solo = 1 OR
                      cruise = 1 OR
                      honeymoon = 1 OR
                      nature = 1 OR
                      vacation = 1''')
    total_blogs = cursor.fetchone()[0]

    pagination = Pagination(page=page, total=total_blogs, per_page=per_page, css_framework='bootstrap4')

    # Latest 3 Blogs
    cursor = mysql.connection.cursor()
    query = '''SELECT blog.blogid, blog.heading, blog.date, blog_images.image
               FROM blog
               JOIN blog_images ON blog.blogid = blog_images.blog_id
               ORDER BY blog.date ASC
               LIMIT 3'''
    
    cursor.execute(query)
    latest_blog = cursor.fetchall()

    # fetching fact
    cursor = mysql.connection.cursor()
    query = "SELECT * FROM facts ORDER BY RAND() LIMIT 1"
    cursor.execute(query)
    facts = cursor.fetchall()

    return render_template('blog_home.html', blog_data=blog_result, latest_blog=latest_blog, facts=facts, pagination=pagination)

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
               ORDER BY blog.date ASC
               LIMIT 3'''
    cursor.execute(query)
    latest_blog= cursor.fetchall()

    # Related Blogs

    query = '''
           SELECT blog.blogid, blog.heading, blog.date, blog_images.image
           FROM blog
           JOIN blog_images ON blog.blogid = blog_images.blog_id
           ORDER BY RAND()
           LIMIT 2
        '''
    cursor.execute(query)
    related_blog= cursor.fetchall()

    # Fetching Comments

    cursor = mysql.connection.cursor()
    query = """
            SELECT blog_comment.comment, blog_comment.userid, blog_comment.date, users.profile_pic, users.username
            FROM blog_comment AS blog_comment
            JOIN users AS users ON blog_comment.userid = users.user_id
            WHERE blog_comment.blogid = %s
            """
    cursor.execute(query, (blog_id,))
    comments = cursor.fetchall()
    # Get the number of comments
    num_comments = len(comments)

    # fetching fact
    cursor = mysql.connection.cursor()
    query = "SELECT * FROM facts ORDER BY RAND() LIMIT 1"
    cursor.execute(query)
    facts = cursor.fetchall()

    cursor.close()



    return render_template('blog_single.html', blog_data=blog_result, latest_blog=latest_blog, related_blog=related_blog, comments=comments, num_comments=num_comments, facts=facts)

''' Blog Categories '''

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
                   ORDER BY blog.date ASC
                   LIMIT 3'''
        cursor.execute(query)
        latest_blog = cursor.fetchall()

        # Fetching fact
        cursor = mysql.connection.cursor()
        query = "SELECT * FROM facts ORDER BY RAND() LIMIT 1"
        cursor.execute(query)
        facts = cursor.fetchall()

        # Pagination for the blog results
        page = request.args.get('page', type=int, default=1)
        per_page = 8
        offset = (page - 1) * per_page
        total = len(blog_result)

        blog_result = blog_result[offset:offset + per_page]

        pagination = Pagination(page=page, total=total, per_page=per_page, css_framework='bootstrap4')

        return render_template('blog_home.html', blog_data=blog_result, latest_blog=latest_blog, facts=facts, pagination=pagination)
    else:
        # Handle the case where an invalid category is provided in the URL
        return redirect('/blog_home')


# Blog Content Uploading 

@app.route('/blog_upload', methods=['POST', 'GET'])
def blog_upload():
    if request.method == 'POST':
        var = ""
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
        try:
            # Insert images associated with the blog
            files = request.files.getlist('images')
            inserted_image_paths = []  # Store the paths of all inserted images

            cursor = mysql.connection.cursor()

            for file in files:
                path = '../static/images/blog'
                file_path = (path + '/' + file.filename)
                file.save(os.path.join(os.path.abspath(os.path.dirname(realpath(__file__)), app.config['BLOG_UPLOAD_IMAGES'], file.filename)))

                insert_image_query = "INSERT INTO blog_images (blog_id, user_id, image) VALUES (%s, %s, %s)"
                image_values = (blog_id, session['userid'], file_path)
                cursor.execute(insert_image_query, image_values)
                inserted_image_paths.append(file_path)  # Store the path in the list

            mysql.connection.commit()
            cursor.close()

            return redirect('/profile_blogs')
        except Exception as e:
            # Handle the exception (e.g., log or return an error message)
            return "Error: " + str(e)




    cursor = mysql.connection.cursor()
    query = "SELECT * FROM users WHERE user_id = %s"
    values = (str(session['userid']),)
    cursor.execute(query, values)
    result = cursor.fetchall()

    return render_template('blog_upload.html', data=result)

''' Blog Comments Uploading '''

@app.route('/blog_upload_comment', methods=['GET', 'POST'])
def blog_upload_comment():
    blog_id = request.form.get("blog_id")
    if request.method == 'POST':
        comment = request.form.get("blog_comment")
        blog_id = request.form.get("blog_id")
        user_id = request.form.get("user_id")

        if 'userid' not in session:
            return render_template('login.html')
        else:
            cursor = mysql.connection.cursor()
            query = "INSERT INTO blog_comment (blogid, userid, comment, date) VALUES(%s, %s, %s, %s)"
            values = (blog_id, session['userid'], comment, today_date)
            cursor.execute(query, values)
            mysql.connection.commit()
            cursor.close()

    return redirect(url_for('blog_single', blog_id=blog_id))

''' Blog Search '''

@app.route('/blog_search', methods=['POST', 'GET'])
def blog_search():
    search_error = ""
    pagination = ""
    if request.method == 'POST':
        search = request.form.get("blog_search_content")
        cursor = mysql.connection.cursor()
        query = f'''
        SELECT blog.blogid, blog.date, blog.heading, SUBSTRING_INDEX(blog.content, ' ', 50) AS truncated_content, users.profile_pic, users.username, CONCAT_WS(', ',
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
        (blog.adventure = 1 OR
        blog.business = 1 OR
        blog.solo = 1 OR
        blog.cruise = 1 OR
        blog.honeymoon = 1 OR
        blog.nature = 1 OR
        blog.vacation = 1)
        AND
        (blog.heading LIKE %s OR blog.content LIKE %s)
        ORDER BY RAND() LIMIT 10
        '''

        cursor.execute(query, ('%' + search + '%', '%' + search + '%'))
        blog_result = cursor.fetchall()
        facts2 = None
        if not blog_result:
            search_error = "Can't Find anything!!"
            cursor = mysql.connection.cursor()
            query = "SELECT * FROM facts ORDER BY RAND() LIMIT 1"
            cursor.execute(query)
            facts2 = cursor.fetchall()

        # Pagination for the search results
        page = request.args.get('page', type=int, default=1)
        per_page = 8
        offset = (page - 1) * per_page
        total = len(blog_result)

        blog_result = blog_result[offset:offset + per_page]

        pagination = Pagination(page=page, total=total, per_page=per_page, css_framework='bootstrap4')

        # Latest 3 Blogs
        cursor = mysql.connection.cursor()
        query = '''SELECT blog.blogid, blog.heading, blog.date, blog_images.image
                   FROM blog
                   JOIN blog_images ON blog.blogid = blog_images.blog_id
                   ORDER BY blog.date ASC
                   LIMIT 3'''
        cursor.execute(query)
        latest_blog = cursor.fetchall()

        # Fetching fact
        cursor = mysql.connection.cursor()
        query = "SELECT * FROM facts ORDER BY RAND() LIMIT 1"
        cursor.execute(query)
        facts = cursor.fetchall()

        return render_template('blog_home.html', blog_data=blog_result, latest_blog=latest_blog, facts=facts, facts2=facts2, search_error=search_error, pagination=pagination)

    return render_template('blog_home.html', pagination=pagination)  # Render the template without search results for GET requests

''' Blogs on profile page '''
from flask_paginate import Pagination

@app.route('/profile_blogs', methods=['POST', 'GET'])
def profile_blogs():
    search_error = ""
    cursor = mysql.connection.cursor()
    query = f'''
    SELECT blog.blogid, blog.date, blog.heading, SUBSTRING_INDEX(blog.content, ' ', 50) AS truncated_content, users.profile_pic, users.username, CONCAT_WS(', ',
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
    (blog.adventure = 1 OR
    blog.business = 1 OR
    blog.solo = 1 OR
    blog.cruise = 1 OR
    blog.honeymoon = 1 OR
    blog.nature = 1 OR
    blog.vacation = 1)
    AND
    (blog.userid = %s)
    ORDER BY RAND() LIMIT 10
    '''
    values = (str(session['userid']),)
    cursor.execute(query, values)
    blog_result = cursor.fetchall()
    facts2 = None
    if not blog_result:
        search_error = "Can't Find anything!!"
        cursor = mysql.connection.cursor()
        query = "SELECT * FROM facts ORDER BY RAND() LIMIT 1"
        cursor.execute(query)
        facts2 = cursor.fetchall()

    # Pagination for the blog results
    page = request.args.get('page', type=int, default=1)
    per_page = 8
    offset = (page - 1) * per_page
    total = len(blog_result)

    blog_result = blog_result[offset:offset + per_page]

    pagination = Pagination(page=page, total=total, per_page=per_page, css_framework='bootstrap4')

    # Latest 3 Blogs
    cursor = mysql.connection.cursor()
    query = '''SELECT blog.blogid, blog.heading, blog.date, blog_images.image
               FROM blog
               JOIN blog_images ON blog.blogid = blog_images.blog_id
               WHERE userid = %s
               ORDER BY blog.date DESC
               LIMIT 3'''
    
    cursor.execute(query, (str(session['userid']),))
    latest_blog= cursor.fetchall()

    # fetching fact
    cursor = mysql.connection.cursor()
    query = "SELECT * FROM facts ORDER BY RAND() LIMIT 1"
    cursor.execute(query)
    facts = cursor.fetchall()

    return render_template('blog_user_personal.html', blog_data=blog_result, latest_blog=latest_blog, facts=facts, facts2=facts2, search_error=search_error, pagination=pagination)

''' Blogs Edit on profile page '''
@app.route('/edit_blog/<int:blog_id>', methods=['POST', 'GET'])
def edit_blog(blog_id):
    cursor = mysql.connection.cursor()
    query = "SELECT * FROM users WHERE user_id = %s"
    values = (str(session['userid']),)
    cursor.execute(query, values)
    result = cursor.fetchall()

    cursor = mysql.connection.cursor()
    query = "SELECT * FROM blog WHERE blogid = %s"
    values = (blog_id,)
    cursor.execute(query, values)
    blog_result = cursor.fetchall()

    cursor = mysql.connection.cursor()
    query = "SELECT * FROM blog_images WHERE blog_id = %s"
    values = (blog_id,)
    cursor.execute(query, values)
    blog_image = cursor.fetchall()
    return render_template("blog_edit.html", data=result, blog_result = blog_result, blog_image=blog_image)

''' Upload Updated Blogs '''
@app.route('/upload_updated_blogs', methods=['POST', 'GET'])
def upload_updated_blogs():
    var = ''
    if request.method == 'POST':
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
        blog_id = request.form.get('blogid')

        cursor = mysql.connection.cursor()
        update_blog_query = '''UPDATE blog SET userid = %s, heading = %s, content = %s, adventure = %s, business = %s, solo = %s,
                            cruise = %s, honeymoon = %s, nature = %s, vacation = %s WHERE blogid = %s'''
        update_blog_values = (session['userid'], heading, content, adventure, business, solo, cruise, honeymoon, nature, vacation, blog_id)


        # Execute the UPDATE query
        cursor.execute(update_blog_query, update_blog_values)
        mysql.connection.commit()
        
        try:
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
        except:
            var = "nothing"

    cursor = mysql.connection.cursor()
    query = "SELECT * FROM users WHERE user_id = %s"
    values = (str(session['userid']),)
    cursor.execute(query, values)
    result = cursor.fetchall()

    cursor = mysql.connection.cursor()
    query = "SELECT * FROM blog_images WHERE blog_id = %s"
    values = (blog_id,)
    cursor.execute(query, values)
    blog_image = cursor.fetchall()

    return redirect('/profile_blogs')

''' Delete Blogs'''

@app.route('/delete_blog/<int:bid>', methods=['GET', 'POST'])
def delete_blog(bid):
    cursor = mysql.connection.cursor()
    delete_query = "DELETE FROM blog WHERE blogid = %s"
    delete_val = (bid,)
    cursor.execute(delete_query, delete_val)
    mysql.connection.commit()

    delete_img = "DELETE FROM blog_images WHERE blog_id = %s"
    delete_val = (bid,)
    cursor.execute(delete_query, delete_val)
    mysql.connection.commit()
    return redirect('/profile_blogs')

''' Delete Blog Images '''

@app.route('/delete_blog_img/<int:bid>', methods=['GET', 'POST'])
def delete_blog_img(bid):
    cursor = mysql.connection.cursor()
    delete_img = "DELETE FROM blog_images WHERE blog_id = %s"
    delete_val = (bid,)
    cursor.execute(delete_img, delete_val)
    mysql.connection.commit()
    return redirect(url_for('edit_blog', blog_id=bid))


# Company Tour packages

@app.route('/sepwrite.com/tour-packages')
def tour_packages():
    flash = None
    if 'username' in session:
        # SQL query to select Tour Packages
        query = """ SELECT tp.*, pi.image_path
                    FROM tour_packages tp
                    LEFT JOIN (
                        SELECT package_id, MIN(image_path) AS image_path
                        FROM package_images
                        GROUP BY package_id
                    ) pi ON tp.package_id = pi.package_id;
                """
        # Execute the query and retrieve the data
        cursor = mysql.connection.cursor()
        cursor.execute(query)
        tour_packages_data = cursor.fetchall()
        # Close the cursor and database connection if necessary
        cursor.close()
        return render_template('tour_packages.html', tour_packages_data=tour_packages_data)
    else:
        return redirect('/login')


# Tour Package Details
@app.route('/sepwrite.com/tour-packages-details/<package_id>', methods=['POST', 'GET'])
def tour_package_details(package_id):
    pro_id = None
    if 'username' in session:
        # SELECTING TOUR PACKAGE
        query1 ="""
            SELECT tp.*, pi.image_path
            FROM tour_packages tp
            LEFT JOIN (
                SELECT package_id, MIN(image_path) AS image_path
                FROM package_images
                GROUP BY package_id
            ) pi ON tp.package_id = pi.package_id
            WHERE tp.package_id = %s; -- Specify the table for package_id
        """
        # Execute the query and retrieve the data
        cursor = mysql.connection.cursor()
        cursor.execute(query1, (package_id,))
        tour_packages_data = cursor.fetchall()

        for pro_id in tour_packages_data:
            pro_id = pro_id[1]

        query4 = "SELECT * FROM pro_users WHERE pro_usersid = %s"
        # Execute the query and retrieve the data
        cursor = mysql.connection.cursor()
        cursor.execute(query4, (pro_id,))
        pro_user_details = cursor.fetchall()

         # SELECTING TOUR PACKAGE
        query2 = "SELECT * FROM package_day_programme WHERE package_id = %s"
        # Execute the query and retrieve the data
        cursor = mysql.connection.cursor()
        cursor.execute(query2, (package_id,))
        tour_packages_day = cursor.fetchall()

         # SELECTING TOUR PACKAGE
        query3 = "SELECT * FROM package_images WHERE package_id = %s"
        # Execute the query and retrieve the data
        cursor = mysql.connection.cursor()
        cursor.execute(query3, (package_id,))
        tour_packages_image = cursor.fetchall()

        return render_template('tour_package_details.html', tour_packages_data=tour_packages_data,
            tour_packages_day=tour_packages_day, tour_packages_image=tour_packages_image, pro_user_details=pro_user_details)
    else:
        return redirect('/login')

# Saving packages
@app.route('/sepwrite.com/tour-packages-saving/<package_id>', methods=['POST', 'GET'])
def tour_package_saving(package_id):
    query1 ="""
        SELECT tp.*, pi.image_path
        FROM tour_packages tp
        LEFT JOIN (
            SELECT package_id, MIN(image_path) AS image_path
            FROM package_images
            GROUP BY package_id
        ) pi ON tp.package_id = pi.package_id
        WHERE tp.package_id = %s; -- Specify the table for package_id
    """
    # Execute the query and retrieve the data
    cursor = mysql.connection.cursor()
    cursor.execute(query1, (package_id,))
    tour_packages_data = cursor.fetchall()

    for pro_id in tour_packages_data:
        pro_id = pro_id[1]

    query4 = "SELECT * FROM pro_users WHERE pro_usersid = %s"
    # Execute the query and retrieve the data
    cursor = mysql.connection.cursor()
    cursor.execute(query4, (pro_id,))
    pro_user_details = cursor.fetchall()

     # SELECTING TOUR PACKAGE
    query2 = "SELECT * FROM package_day_programme WHERE package_id = %s"
    # Execute the query and retrieve the data
    cursor = mysql.connection.cursor()
    cursor.execute(query2, (package_id,))
    tour_packages_day = cursor.fetchall()

     # SELECTING TOUR PACKAGE
    query3 = "SELECT * FROM package_images WHERE package_id = %s"
    # Execute the query and retrieve the data
    cursor = mysql.connection.cursor()
    cursor.execute(query3, (package_id,))
    tour_packages_image = cursor.fetchall()    
    cursor = mysql.connection.cursor()
    # Inserting the saved package
    try:
        # Define the SQL query to insert data into the table
        query = "SELECT * FROM saved_packages WHERE package_id = %s AND user_id = %s"
        # Execute the query with the actual values
        cursor.execute(query, (package_id, session['userid']))
        # Commit the transaction to save the changes to the database
        saved_packages_data = cursor.fetchall()

        if saved_packages_data:
            flash = "Already Saved..!"
            return render_template('tour_package_details.html', tour_packages_data=tour_packages_data,
                tour_packages_day=tour_packages_day, tour_packages_image=tour_packages_image, pro_user_details=pro_user_details, flash=flash)
        else:
            # Define the SQL query to insert data into the table
            query = "INSERT INTO saved_packages (package_id, user_id) VALUES (%s, %s)"
            # Execute the query with the actual values
            cursor.execute(query, (package_id, session['userid']))
            # Commit the transaction to save the changes to the database
            flash = "Saved Succefully.."
            mysql.connection.commit()
            return render_template('tour_package_details.html', tour_packages_data=tour_packages_data,
                tour_packages_day=tour_packages_day, tour_packages_image=tour_packages_image, pro_user_details=pro_user_details, flash=flash)
    except:
        flash = "Something Wrong..!!"
    return render_template('tour_package_details.html', tour_packages_data=tour_packages_data,
            tour_packages_day=tour_packages_day, tour_packages_image=tour_packages_image, pro_user_details=pro_user_details)

# Deleting Saving packages
@app.route('/sepwrite.com/tour-packages-remove/<package_id>', methods=['POST', 'GET'])
def tour_package_saved_dlt(package_id):
    if 'username' in session:
        # SQL query to select Tour Packages
        query = """ SELECT tp.*, pi.image_path
        FROM tour_packages tp
        LEFT JOIN (
            SELECT package_id, MIN(image_path) AS image_path
            FROM package_images
            GROUP BY package_id
        ) pi ON tp.package_id = pi.package_id
        WHERE tp.package_id IN (
            SELECT DISTINCT  package_id
            FROM saved_packages
            WHERE user_id = %s
        );
        """
        # Execute the query and retrieve the data
        cursor = mysql.connection.cursor()
        cursor.execute(query, (str(session['userid']),))
        tour_packages_data = cursor.fetchall()
        # Close the cursor and database connection if necessary
    try:
        # Define the SQL query to insert data into the table
        query = "DELETE FROM saved_packages WHERE package_id = %s"
        # Execute the query with the actual values
        cursor.execute(query, (package_id))
        # Commit the transaction to save the changes to the database
        mysql.connection.commit()
        delt_flash = "Unsaved...."
        return render_template('saved_packages.html', tour_packages_data=tour_packages_data, delt_flash=delt_flash)
    except:
        delt_flash = "Something Wrong.."
        return render_template('saved_packages.html', tour_packages_data=tour_packages_data, delt_flash=delt_flash)

# user_tour_package_booking
@app.route('/sepwrite.com/tour-packages-booking', methods=['POST', 'GET'])
def user_tour_package_booking():
    if request.method == 'POST':
        view = 0
        package_status = 2
        package_status_view = 1
        provider = request.form.get('pro_id')
        num_people = request.form.get('days')
        package_id = request.form.get('package_id')
        name = request.form.get('username')
        user_identity_document = request.form.get('user_identity_document')
        phone = request.form.get('phone')

        cursor = mysql.connection.cursor()
        query = "INSERT INTO package_bookings (user_id, package_id, viewed, package_provider_id, package_status, package_status_view) VALUES (%s, %s, %s, %s, %s, %s)"
        cursor.execute(query, (session['userid'], package_id, view, provider, package_status, package_status_view))
        mysql.connection.commit()

        # Get the generated Package Id
        booking_id = cursor.lastrowid

        # Adding travel lead
        insert_query = "INSERT INTO package_booked_travalers (booking_id, name, identity_document, phone) VALUES (%s, %s, %s, %s)"
        cursor.execute(insert_query, (booking_id, name, user_identity_document, phone))
        mysql.connection.commit()

        travalers = []

        for i in range(1, int(num_people) + 1):
            person_name = request.form.get(f'personname{i}')
            person_id_document = request.form.get(f'person_id_{i}')
            travalers.append((person_name, person_id_document))
        try:
            # Assuming you have established a database connection and obtained a cursor object
            insert_query = "INSERT INTO package_booked_travalers (booking_id, name, identity_document) VALUES (%s, %s, %s)"
            
            for person_name, person_id_document in travalers:
                cursor.execute(insert_query, (booking_id, person_name, person_id_document))

            # Commit the changes to the database
            mysql.connection.commit()
            flash = "Request Submitted..!"

        except Exception as e:
            # Handle any exceptions that may occur during the database operations
            # You should add appropriate error handling and logging here
            print("An error occurred:", e)
        except Exception as e:
            mysql.connection.rollback()
            return f"Error: {str(e)}"
        query = """SELECT pb.*, tp.tourname
        FROM package_bookings pb
        INNER JOIN tour_packages tp ON pb.package_id = tp.package_id
        WHERE user_id = %s;
        """
        cursor.execute(query, (session['userid'],))
        tour_bookings = cursor.fetchall()
        cursor.close();

    return render_template('user_bookings.html', flash = flash, tour_bookings=tour_bookings)


# User saved Tour packages

@app.route('/sepwrite.com/saved-tour-packages')
def saved_packages():
    flash = None
    if 'username' in session:
        # SQL query to select Tour Packages
        query = """ SELECT tp.*, pi.image_path
                    FROM tour_packages tp
                    LEFT JOIN (
                        SELECT package_id, MIN(image_path) AS image_path
                        FROM package_images
                        GROUP BY package_id
                    ) pi ON tp.package_id = pi.package_id
                    WHERE tp.package_id IN (
                        SELECT DISTINCT  package_id
                        FROM saved_packages
                        WHERE user_id = %s
                    );
                """
        # Execute the query and retrieve the data
        cursor = mysql.connection.cursor()
        cursor.execute(query, (str(session['userid']),))
        tour_packages_data = cursor.fetchall()
        # Close the cursor and database connection if necessary
        cursor.close()
        return render_template('saved_packages.html', tour_packages_data=tour_packages_data)
    else:
        return redirect('/login')

# User package searching 

@app.route('/sepwrite.com/packages/searching', methods=['POST', 'GET'])
def user_package_searching():
    if request.method == 'POST':
        search_value = request.form.get('search_value')
        # SQL query to select Tour Packages
        search_value = request.form.get('search_value')

        # SQL query to select Tour Packages with a search condition
        query = """ 
            SELECT tp.*, pi.image_path
            FROM tour_packages tp
            LEFT JOIN (
                SELECT package_id, MIN(image_path) AS image_path
                FROM package_images
                GROUP BY package_id
            ) pi ON tp.package_id = pi.package_id
            WHERE tp.tourname LIKE %s OR tp.country LIKE %s OR tp.territory LIKE %s OR tp.price LIKE %s OR tp.description LIKE %s
        """

        # Execute the query and retrieve the data
        cursor = mysql.connection.cursor()
        cursor.execute(query, ('%' + search_value + '%', '%' + search_value + '%', '%' + search_value + '%', '%' + search_value + '%', '%' + search_value + '%'))

        # Fetch the result
        tour_packages_data = cursor.fetchall()
        # Close the cursor and database connection if necessary
        cursor.close()
    return render_template('tour_packages.html', tour_packages_data=tour_packages_data)

# User Bookings 

@app.route('/sepwrite.com/user-bookings', methods=['POST', 'GET'])
def user_bookings():
    cursor = mysql.connection.cursor()
    query = """SELECT pb.*, tp.tourname
        FROM package_bookings pb
        INNER JOIN tour_packages tp ON pb.package_id = tp.package_id
        WHERE user_id = %s;
    """
    cursor.execute(query, (session['userid'],))
    tour_bookings = cursor.fetchall()

    query_1 = """SELECT * FROM cancelled_bookings WHERE user_id = %s"""
    cursor.execute(query_1, (session['userid'],))
    cancelled_bookings = cursor.fetchall()
    cursor.close()

    return render_template('user_bookings.html', tour_bookings=tour_bookings, cancelled_bookings=cancelled_bookings)  


# user booking Details

@app.route('/sepwrite.com/tour-packages-booking-details/<booking_id>', methods=['POST', 'GET'])
def user_booking_details(booking_id):
    cursor = mysql.connection.cursor()
    query = """SELECT tour_packages.*, package_bookings.package_status
            FROM tour_packages
            JOIN package_bookings ON tour_packages.package_id = package_bookings.package_id
            WHERE package_bookings.booked_id = %s;
    """
    cursor.execute(query, (booking_id,))
    booking_details = cursor.fetchall()

    if booking_details:
        for row in booking_details:
            tour_provider_id = row[1]
        query = """ SELECT * FROM pro_users WHERE pro_usersid = %s """
        cursor.execute(query, (tour_provider_id,))
        provider_details = cursor.fetchall()

    query1 = "SELECT * FROM package_booked_travalers WHERE booking_id = %s"
    cursor.execute(query1, (booking_id,))
    booking_persons = cursor.fetchall()

    return render_template('user_booking_details.html', booking_details=booking_details, booking_persons=booking_persons, bookingid=booking_id, provider_details=provider_details)

# Canceling the tour package by user
@app.route('/sepwrite.com/user-booking-cancel/<booking_id>/<package_name>/<provider_id>', methods=['POST', 'GET'])
def user_booking_cancel(booking_id, package_name, provider_id):
    pro_view = "0"
    try:
        # Create a new cursor for the delete queries
        delete_cursor = mysql.connection.cursor()

        # Delete from package_bookings table
        try:
            delete_query_1 = "DELETE FROM package_bookings WHERE booked_id = %s"
            delete_cursor.execute(delete_query_1, (booking_id,))
        except:
            flash = "e1"
        try:
            # Delete from accepted_bookings table
            delete_query_2 = "DELETE FROM accepted_bookings WHERE booking_id = %s"
            delete_cursor.execute(delete_query_2, (booking_id,))
        except:
            flash = "e2"
        try:
            # Delete from package_booked_travalers table
            delete_query_3 = "DELETE FROM package_booked_travalers WHERE booking_id = %s"
            delete_cursor.execute(delete_query_3, (booking_id,))
        except:
            flash = "e3"
        try:
            # Delete from package_booking table
            delete_query_4 = "DELETE FROM package_booking WHERE booked_id = %s"
            delete_cursor.execute(delete_query_4, (booking_id,))
        except:
            flash = "e4"
        try:
            # Delete from rejected_booking table
            delete_query_5 = "DELETE FROM rejected_booking WHERE booking_id = %s"
            delete_cursor.execute(delete_query_5, (booking_id,))
        except:
            flash = "e5"

        # Commit the changes
        mysql.connection.commit()
        delete_cursor.close()

        # Create a cursor for the first query
        cursor = mysql.connection.cursor()

        # Fetch tour bookings
        query = """SELECT pb.*, tp.tourname
            FROM package_bookings pb
            INNER JOIN tour_packages tp ON pb.package_id = tp.package_id
            WHERE user_id = %s;
        """
        cursor.execute(query, (session['userid'],))
        tour_bookings = cursor.fetchall()

        #Inserting  the data into cancelled table 

        cancelled_date = today_date

        # Checking the canclation lready done or not

        select_query ="SELECT * FROM cancelled_bookings WHERE booking_id = %s"
        cursor.execute(select_query, (booking_id,))
        checking_booking = cursor.fetchall()

        if checking_booking:
            flash_message = "Already Cancelled.."
        else:
            query_inserting = """
                INSERT INTO cancelled_bookings (booking_id, user_id, provider_id, pro_view, package_name, cancelled_date)
                VALUES (%s, %s, %s, %s, %s, %s);
            """
            # Execute the query with the specified values
            cursor.execute(query_inserting, (str(booking_id), str(session['userid']), str(provider_id), pro_view, str(package_name), cancelled_date))

            # Commit the changes
            mysql.connection.commit()
            cursor.close()
            flash_message = "Booking Cancelled..!!"

    except Exception as e:
        print(f"Error: {e}")
        flash_message = "Something went wrong."


    return render_template('user_bookings.html', tour_bookings=tour_bookings, flash=flash_message)


      
#---------------------------------------------------------
#---------------------------------------------------------
#---------------------------------------------------------
#---------------------------------------------------------
#---------------------------------------------------------
#---------------------------------------------------------
#---------------------------------------------------------
#---------------------------------------------------------


# Business Pro Account home page

@app.route('/sepwrite.com/account.pro')
def pro_account():
    if 'prousercompany' in session:
        cursor = mysql.connection.cursor()

        # Unwatched Notofications
        query = """
            SELECT tour_packages.tourname, package_bookings.booked_id FROM tour_packages
                JOIN package_bookings  ON tour_packages.package_id = package_bookings.package_id
                WHERE package_bookings.viewed = 0 AND package_bookings.package_provider_id = %s;   """
        cursor.execute(query, str(session['proid']))
        unwatched = cursor.fetchall()

        # SQL query to select Tour Packages
        query = """ SELECT tp.*, pi.image_path
                    FROM tour_packages tp
                    LEFT JOIN (
                        SELECT package_id, MIN(image_path) AS image_path
                        FROM package_images
                        GROUP BY package_id
                    ) pi ON tp.package_id = pi.package_id;
                """
        # Execute the query and retrieve the data
        cursor.execute(query)
        tour_packages_data = cursor.fetchall()
        # Close the cursor and database connection if necessary
        cursor.close()
        return render_template('pro/home.html', unwatched=unwatched, tour_packages_data=tour_packages_data)
    return render_template('pro/section.html')

# New notification mark as read
@app.route('/sepwrite.com/account.pro/mark-us-read/<booking_id>')
def booking_mark_as_read(booking_id):
    cursor = mysql.connection.cursor()
    query = "UPDATE package_bookings SET viewed = 1 WHERE package_provider_id = %s AND booked_id = %s"
    cursor.execute(query, (str(session['proid']), booking_id))
    mysql.connection.commit()
    return redirect(url_for('pro_account'))

# Company Logout Page
@app.route('/sepwrite.com/account.pro/logout-section')
def pro_logout_section():
    if 'prousercompany' in session:
        cursor = mysql.connection.cursor()
        query = "SELECT COUNT(*) AS total_count FROM ai_travel_planner.package_bookings WHERE viewed = 0 AND package_provider_id=%s;"
        cursor.execute(query, str(session['proid']))
        result = cursor.fetchone()

        query2 = "SELECT COUNT(*) AS total_count2 FROM ai_travel_planner.cancelled_bookings WHERE pro_view = 0 AND provider_id = %s;"
        cursor.execute(query2, (str(session['proid']),))
        result2 = cursor.fetchone()


        return render_template('pro/logout.html', noti_count=result, noti_count1=result2)
    else:
        return redirect('pro.login')
    
# Company Logout 
@app.route('/sepwrite.com/account.pro/logout')
def pro_logout():
    if 'prousercompany' in session:
        session.pop('prousercompany', None)  # Remove the user_id from the session
        session.pop('proid', None)
        return redirect('/sepwrite.com/account.pro')
    else:
        return redirect('pro.login')

# Company Tour packages

@app.route('/sepwrite.com/account.pro/tour-packages')
def pro_tour_packages():
    if 'prousercompany' in session:
        # SQL query to select Tour Packages
        query = """ SELECT tp.*, pi.image_path
                    FROM tour_packages tp
                    LEFT JOIN (
                        SELECT package_id, MIN(image_path) AS image_path
                        FROM package_images
                        GROUP BY package_id
                    ) pi ON tp.package_id = pi.package_id;
                """

        # Execute the query and retrieve the data
        cursor = mysql.connection.cursor()
        cursor.execute(query)
        tour_packages_data = cursor.fetchall()
        # Close the cursor and database connection if necessary
        cursor.close()

        return render_template('pro/tour_packages.html', tour_packages_data=tour_packages_data)
    else:
        return redirect('pro.login')

# password changing page

@app.route('/sepwrite.com/account.pro/password-changing', methods=['GET', 'POST'])
def pro_password_change():
    if 'prousercompany' in session:
       cursor = mysql.connection.cursor()
       query1 = "SELECT COUNT(*) AS total_count FROM ai_travel_planner.package_bookings WHERE viewed = 0 AND package_provider_id = %s;"
       cursor.execute(query1, (str(session['proid']),))
       result1 = cursor.fetchone()

       query2 = "SELECT COUNT(*) AS total_count2 FROM ai_travel_planner.cancelled_bookings WHERE pro_view = 0 AND provider_id = %s;"
       cursor.execute(query2, (str(session['proid']),))
       result2 = cursor.fetchone()

       return render_template('pro/pro_change_password.html', noti_count=result1, noti_count1=result2)
    else:
        return redirect('pro.login')

# password changing action page

@app.route('/sepwrite.com/account.pro/password-changing_form', methods=['GET', 'POST'])
def pro_password_change2():
    if 'prousercompany' in session:
        ans = ''
        current_password = request.form.get('oldPassword')
        newpassword = request.form.get('confirmPassword')
        cursor = mysql.connection.cursor()
        
        checking_password = "SELECT password FROM pro_users WHERE company = %s AND pro_usersid = %s"
        values = (session['prousercompany'], str(session['proid']))
        cursor.execute(checking_password, values)
        result = cursor.fetchall()
        ans = result[0][0]

        if ans != current_password:
            password_error_msg = "Wrong Password"
        else:
            cursor = mysql.connection.cursor()
            query = "UPDATE pro_users SET password = %s WHERE pro_usersid = %s"
            values = (newpassword, str(session['proid']))
            cursor.execute(query, values)
            mysql.connection.commit()

            cursor = mysql.connection.cursor()
            query = "SELECT * FROM pro_users WHERE pro_usersid = %s"
            values = (str(session['proid']),)
            cursor.execute(query, values)
            result = cursor.fetchall()
            flash = "Password Changed"
            return render_template('pro/pro_change_password.html', flash=flash)
        return render_template('pro/pro_change_password.html', error_message=password_error_msg)
    else:
        return redirect('pro.login')

# company login

@app.route('/sepwrite.com/account.pro/login', methods = ['GET', 'POST'])
def pro_login():
    error_message = ''
    if request.method == 'POST':
       email_or_username = request.form.get('prologinname')
       password = request.form.get('prologinpassword')

       ''' Checking password and username or email'''
       cursor = mysql.connection.cursor()
       query = "SELECT pro_usersid, userid, company FROM pro_users WHERE (email = %s OR company = %s) AND password = %s"
       values = (email_or_username, email_or_username, password)
       cursor.execute(query, values)
       result = cursor.fetchall()
       
       if len(result) > 0:
        session['proid'] = result[0][0]
        session['prouserid'] = result[0][1]
        session['prousercompany'] = result[0][2]
        return redirect('/sepwrite.com/account.pro')
       else:
        error_message = "Invalid username/email or password"

    return render_template('pro/pro_login.html', error_message=error_message)

# Notifications 

@app.route('/sepwrite.com/account.pro/notifcations')
def pro_notifications():
    if 'prousercompany' in session:
        cursor = mysql.connection.cursor()

        # Unwatched Notofications
        query = """
                SELECT tour_packages.tourname, package_bookings.booked_id FROM tour_packages
                JOIN package_bookings  ON tour_packages.package_id = package_bookings.package_id
                WHERE package_bookings.viewed = 0 AND package_bookings.package_provider_id = %s; 
        """
        cursor.execute(query, str(session['proid']))
        unwatched = cursor.fetchall()

        # end

        # watched Notifications
        cursor = mysql.connection.cursor()
        cursor.close()
        cursor = mysql.connection.cursor()
        query1 = """
                SELECT tour_packages.tourname, package_bookings.booked_id FROM tour_packages
                JOIN package_bookings  ON tour_packages.package_id = package_bookings.package_id
                WHERE package_bookings.viewed = 1 AND package_bookings.package_provider_id = %s;  
        """
        cursor.execute(query1, str(session['proid']))
        watched = cursor.fetchall()

        #cancelled Notifications
        query2 = """
                SELECT * FROM cancelled_bookings WHERE pro_view = 1 AND provider_id = %s; 
        """
        cursor.execute(query2, str(session['proid']))
        cancel_watched = cursor.fetchall()

        query2 = """
                SELECT * FROM cancelled_bookings WHERE pro_view = 0 AND provider_id = %s; 
        """
        cursor.execute(query2, str(session['proid']))
        cancel_unwatched = cursor.fetchall()

        query = "UPDATE package_bookings SET viewed = 1 WHERE package_provider_id = %s"
        cursor.execute(query, str(session['proid']))
        mysql.connection.commit()

        query = "UPDATE cancelled_bookings SET pro_view = 1 WHERE provider_id = %s"
        cursor.execute(query, str(session['proid']))
        mysql.connection.commit()

        return render_template('pro/pro_notifications.html', unwatched=unwatched, watched=watched, cancel_watched=cancel_watched,cancel_unwatched=cancel_unwatched)
    else:
        return redirect('pro.login')

# Pro Settings

@app.route('/sepwrite.com/account.pro/company-settings', methods=['GET', 'POST'])
def pro_settings():
    flash = None
    if 'prousercompany' in session:
        cursor = mysql.connection.cursor()
        query = "SELECT COUNT(*) AS total_count FROM ai_travel_planner.package_bookings WHERE viewed = 0 AND package_provider_id = %s;"
        cursor.execute(query, str(session['proid']))
        noti_result = cursor.fetchone()

        query2 = "SELECT COUNT(*) AS total_count2 FROM ai_travel_planner.cancelled_bookings WHERE pro_view = 0 AND provider_id = %s;"
        cursor.execute(query2, (str(session['proid']),))
        result2 = cursor.fetchone()

        email_error = ""
        cursor = mysql.connection.cursor()
        
        # Helper function to check if an email is already taken
        def is_email_taken(email, current_user_id):
            query = "SELECT COUNT(*) FROM pro_users WHERE email = %s AND pro_usersid != %s"
            cursor.execute(query, (email, current_user_id))
            count = cursor.fetchone()[0]
            return count > 0

        # Updating if form submitted
        if request.method == 'POST':
            # Retrieve form data
            companyname = request.form.get("companyname")
            phone = request.form.get("phone")
            state = request.form.get("state")
            territory = request.form.get("territory")
            pin = request.form.get("pin")
            address = request.form.get("address")
            email = request.form.get("email")
            about = request.form.get("bio")

            # Check if the email is already taken by another user
            if is_email_taken(email, session['proid']):
                email_error = "Email is already taken by another user."
                query = "SELECT * FROM pro_users WHERE pro_usersid = %s"
                cursor.execute(query, str(session['proid']))
                result = cursor.fetchall()
                return render_template('pro/pro_settings.html', data=result, email_error=email_error)
            else:
                # UPDATE query
                update_query = """
                    UPDATE pro_users
                    SET company = %s, email = %s, state = %s, territory = %s, pin = %s, phone = %s, address = %s, about = %s
                    WHERE pro_usersid = %s
                """
                # Define the values to update
                update_values = (companyname, email, state, territory, pin, phone, address, about, str(session['proid']))
                # Execute the UPDATE query
                cursor.execute(update_query, update_values)
                mysql.connection.commit()
                flash = "Updated Succefully"

        # Execute a SQL query to fetch data from the pro_users table
        query = "SELECT * FROM pro_users WHERE pro_usersid = %s"
        cursor.execute(query, str(session['proid']))
        # Fetch all rows of data from the result set
        result = cursor.fetchall()

        cursor.close()

        return render_template('pro/pro_settings.html', data=result, email_error=email_error, flash=flash, noti_count=noti_result, noti_count1=result2)
    else:
        return redirect('/sepwrite.com/account.pro/login')  # Use the redirect function here

# Adding Packages images to database

@app.route('/sepwrite.com/account.pro/tour-packages/add-form', methods=['POST', 'GET'])
def adding_tourpackages():
    cursor = mysql.connection.cursor()
    if request.method == 'POST':      
        tourname = request.form.get('tourname')
        num_days = request.form.get('num_days')
        price = request.form.get('price')
        from_date = request.form.get('from_date')
        to_date = request.form.get('to_date')
        description = request.form.get('description')

        # here, inserting query to tourpackages table

        try:
            # Insert the data into the "tour_packages" table
            insert_query = "INSERT INTO tour_packages (pro_id, tourname, num_days, price, from_date, to_date, description) VALUES (%s, %s, %s, %s, %s, %s, %s)"
            values = (session['proid'], tourname, num_days, price, from_date, to_date, description)
            cursor.execute(insert_query, values)

            # Commit the changes to the database
            mysql.connection.commit()
        except Exception as e:
            # Handle the exception (e.g., log or return an error message)
            print("Error:", str(e))
            mysql.connection.rollback()

        # Get the generated Package Id
        package_id = cursor.lastrowid

        # Retrieve day program data based on the number of days

        day_programs = [request.form.get(f'day_program_{i}') for i in range(1, int(num_days) + 1)]

        ''' Here, Inserting code for day_programes to db'''

        try:
            # Iterate through day programs and insert them into the "day_pro" table
            for day, program_text in enumerate(day_programs, start=1):
                insert_query = "INSERT INTO package_day_programme (pro_id, package_id, day, programme) VALUES (%s, %s, %s, %s)"
                cursor.execute(insert_query, (session['proid'], package_id, f"day {day}", program_text))

            # Commit the changes to the database
            mysql.connection.commit()


        except Exception as e:
            mysql.connection.rollback()
            return f"Error: {str(e)}"

        '''Here Inserting images to db'''

        try:
            # Insert images associated with the blog
            files = request.files.getlist('images')
            inserted_image_paths = []  # Store the paths of all inserted images
            for file in files:
                path = 'images/tour_packages'
                file_path = (path + '/' + file.filename)
                file.save(os.path.join(os.path.abspath(os.path.dirname(realpath(__file__))), app.config['TOUR_PACKAGE_IMAGES'], file.filename))
                inserted_image_paths.append(file_path) # Store the path in the list

            cursor = mysql.connection.cursor()
            for image_path in inserted_image_paths:
                insert_image_query = "INSERT INTO package_images (pro_id, package_id, image_path) VALUES (%s, %s, %s)"
                image_values = (session['proid'], package_id, image_path)
                cursor.execute(insert_image_query, image_values)

            mysql.connection.commit()
            cursor.close()
            flash = "New Package Added"
            return redirect('/sepwrite.com/account.pro/tour-packages', flash=flash)
        except:
            var = "nothing"
            return render_template('pro/tour-packages-adding-form.html')
    return render_template('pro/tour-packages-adding-form.html')

## Tour Edit Package Details
@app.route('/sepwrite.com/account.pro/pro-tour-packages-edit/<package_id>', methods=['POST', 'GET'])
def pro_tour_package_edit(package_id):
    if 'prousercompany' in session:
        # SELECTING TOUR PACKAGE
        query1 = """
        SELECT tp.*, pi.image_path
            FROM tour_packages tp
            LEFT JOIN (
                SELECT package_id, MIN(image_path) AS image_path
                FROM package_images
                GROUP BY package_id
            ) pi ON tp.package_id = pi.package_id
            WHERE tp.package_id = %s;
            """
        # Execute the query and retrieve the data
        cursor = mysql.connection.cursor()
        cursor.execute(query1, package_id)
        tour_packages_data = cursor.fetchall()

         # SELECTING TOUR PACKAGE
        query2 = "SELECT * FROM package_day_programme WHERE package_id = %s"
        # Execute the query and retrieve the data
        cursor = mysql.connection.cursor()
        cursor.execute(query2, package_id)
        tour_packages_day = cursor.fetchall()

         # SELECTING TOUR PACKAGE
        query3 = "SELECT * FROM package_images WHERE package_id = %s"
        # Execute the query and retrieve the data
        cursor = mysql.connection.cursor()
        cursor.execute(query3, package_id)
        tour_packages_image = cursor.fetchall()

        return render_template('pro/tour_package_edit_form.html', tour_packages_data=tour_packages_data,
            tour_packages_day=tour_packages_day, tour_packages_image=tour_packages_image)
    else:
        return render_template('pro/login')


# Tour Package Details
@app.route('/sepwrite.com/account.pro/pro-tour-packages-details/<package_id>', methods=['POST', 'GET'])
def pro_tour_package_details(package_id):
    if 'prousercompany' in session:
        # SELECTING TOUR PACKAGE
        query1 = """SELECT tp.*, pi.image_path
            FROM tour_packages tp
            LEFT JOIN (
                SELECT package_id, MIN(image_path) AS image_path
                FROM package_images
                GROUP BY package_id
            ) pi ON tp.package_id = pi.package_id
            WHERE tp.package_id = %s;"""
        # Execute the query and retrieve the data
        cursor = mysql.connection.cursor()
        cursor.execute(query1, package_id)
        tour_packages_data = cursor.fetchall()

         # SELECTING TOUR PACKAGE
        query2 = "SELECT * FROM package_day_programme WHERE package_id = %s"
        # Execute the query and retrieve the data
        cursor = mysql.connection.cursor()
        cursor.execute(query2, package_id)
        tour_packages_day = cursor.fetchall()

         # SELECTING TOUR PACKAGE
        query3 = "SELECT * FROM package_images WHERE package_id = %s"
        # Execute the query and retrieve the data
        cursor = mysql.connection.cursor()
        cursor.execute(query3, package_id)
        tour_packages_image = cursor.fetchall()

        return render_template('pro/tour_package_details.html', tour_packages_data=tour_packages_data,
            tour_packages_day=tour_packages_day, tour_packages_image=tour_packages_image)
    else:
        return render_template('pro/login')


# Remove Tour Packages Details
@app.route('/sepwrite.com/account.pro/remove-package/<package_id>')
def remove_package(package_id):
    cursor = mysql.connection.cursor()
    query = """
        DELETE FROM tour_packages
        WHERE package_id = %s;
    """
    cursor.execute(query, (package_id,))
    mysql.connection.commit()
    return redirect('/sepwrite.com/account.pro/notifcations')



# View Package Order Details
@app.route('/sepwrite.com/account.pro/tour-packages-booking-details/<booking_id>', methods=['POST', 'GET'])
def pro_tour_booking_details(booking_id):
    cursor = mysql.connection.cursor()
    query = """SELECT tour_packages.*, package_bookings.package_status
            FROM tour_packages
            JOIN package_bookings ON tour_packages.package_id = package_bookings.package_id
            WHERE package_bookings.booked_id = %s;
    """
    cursor.execute(query, (booking_id,))
    booking_details = cursor.fetchall()

    query1 = "SELECT * FROM package_booked_travalers WHERE booking_id = %s"
    cursor.execute(query1, (booking_id,))
    booking_persons = cursor.fetchall()

    return render_template('pro/booking_details.html', booking_details=booking_details, booking_persons=booking_persons, bookingid=booking_id)

# Accepting Package Booking request
@app.route('/sepwrite.com/account.pro/package-accepting/<booking_id>', methods=['POST', 'GET'])
def pro_tour_booking_accept(booking_id):
    cursor = mysql.connection.cursor()
    try:
        query = "UPDATE package_bookings SET package_status = 1,  package_status_view = 0 WHERE booked_id = %s;"
        cursor.execute(query, (booking_id,))
        mysql.connection.commit()

        flash = "Request Accepted"
    except Exception as e:
        flash = "Something Wrong.."

    query = """SELECT tour_packages.*, package_bookings.package_status
            FROM tour_packages
            JOIN package_bookings ON tour_packages.package_id = package_bookings.package_id
            WHERE package_bookings.booked_id = %s;
    """
    cursor.execute(query, (booking_id,))
    booking_details = cursor.fetchall()

    query1 = "SELECT * FROM package_booked_travalers WHERE booking_id = %s"
    cursor.execute(query1, (booking_id,))
    booking_persons = cursor.fetchall()

    return render_template('pro/booking_details.html', flash=flash, booking_details=booking_details, booking_persons=booking_persons, bookingid=booking_id)

# Reject Package Order Request
@app.route('/sepwrite.com/account.pro/package-rejecting/<booking_id>', methods=['POST', 'GET'])
def pro_tour_booking_reject(booking_id):
    cursor = mysql.connection.cursor()
    try:
        query = "UPDATE package_bookings SET package_status = 0, package_status_view = 0 WHERE booked_id = %s;"
        cursor.execute(query, (booking_id,))
        mysql.connection.commit()

        flash = "Request Rejected"
    except Exception as e:
        flash = "Something Wrong.."

    query = """SELECT tour_packages.*, package_bookings.package_status
            FROM tour_packages
            JOIN package_bookings ON tour_packages.package_id = package_bookings.package_id
            WHERE package_bookings.booked_id = %s;
    """
    cursor.execute(query, (booking_id,))
    booking_details = cursor.fetchall()

    query1 = "SELECT * FROM package_booked_travalers WHERE booking_id = %s"
    cursor.execute(query1, (booking_id,))
    booking_persons = cursor.fetchall()


    return render_template('pro/booking_details.html', flash=flash, booking_details=booking_details, booking_persons=booking_persons, bookingid=booking_id)

#View all Bookings 

@app.route('/sepwrite.com/account.pro/bookings')
def bookings():
    cursor = mysql.connection.cursor()
    query = """SELECT pb.*, tp.tourname
        FROM package_bookings pb
        INNER JOIN tour_packages tp ON pb.package_id = tp.package_id
        WHERE pb.package_provider_id = %s AND package_status = %s;
    """
    cursor.execute(query, (session['proid'], 1))
    accepted = cursor.fetchall()
    # Rejected Details
    query = """SELECT pb.*, tp.tourname
        FROM package_bookings pb
        INNER JOIN tour_packages tp ON pb.package_id = tp.package_id
        WHERE pb.package_provider_id = %s AND package_status = %s;
    """
    cursor.execute(query, (session['proid'], 0))
    rejected = cursor.fetchall()
    # Pending Details
    query = """SELECT pb.*, tp.tourname
        FROM package_bookings pb
        INNER JOIN tour_packages tp ON pb.package_id = tp.package_id
        WHERE pb.package_provider_id = %s AND package_status = %s;
    """
    cursor.execute(query, (session['proid'], 2))
    pending = cursor.fetchall()
    
    query = """SELECT pb.*, tp.tourname
        FROM package_bookings pb
        INNER JOIN tour_packages tp ON pb.package_id = tp.package_id
        WHERE pb.package_provider_id = %s;
    """
    cursor.execute(query, (session['proid'],))
    all_d = cursor.fetchall()

    return render_template('pro/bookings.html', rejected=rejected, accepted=accepted, pending=pending, all = all_d)


#---------------------------------------------------------
#---------------------------------------------------------
#---------------------------------------------------------
#---------------------------------------------------------
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


''' Facts Page '''

@app.route('/admin_facts', methods=['GET', 'POST'])
def admin_facts():
    cursor = mysql.connection.cursor()
    query = "SELECT * FROM facts"
    cursor.execute(query)
    facts = cursor.fetchall()
    return render_template('admin/admin_facts.html', facts=facts)

@app.route('/add_facts', methods=['GET', 'POST'])
def add_facts():
    if request.method == 'POST':
        facts = request.form.get('facts')

        # Insert the new admin into the database
        cursor = mysql.connection.cursor()
        insert_query = "INSERT INTO facts (adminid, fact) VALUES (%s, %s)"
        cursor.execute(insert_query, (str(session['adminid']), facts))
        mysql.connection.commit()

        query = "SELECT * FROM facts"
        cursor.execute(query)
        facts = cursor.fetchall()

        status_message = "Facts added successfully."

    return render_template('admin/admin_facts.html', add_status_message=status_message, facts=facts)

@app.route('/delete_fact/<int:fid>', methods=['GET', 'POST'])
def delete_fact(fid):
    cursor = mysql.connection.cursor()
    delete_query = "DELETE FROM facts WHERE facts_id = %s"
    delete_val = (fid,)
    cursor.execute(delete_query, delete_val)
    mysql.connection.commit()
    status_message = "Facts Deleted!!"

    # fetching facts 
    cursor = mysql.connection.cursor()
    query = "SELECT * FROM facts"
    cursor.execute(query)
    facts = cursor.fetchall()

    return render_template('admin/admin_facts.html', facts = facts, dlt_status_message=status_message)

    

