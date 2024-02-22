from flask import Flask, render_template, request, redirect, session, url_for, flash, jsonify
import requests
from flask_mysqldb import MySQL
from datetime import datetime
import mysql.connector
import os
from os.path import realpath, dirname, join
from flask_paginate import Pagination
from datetime import date

from werkzeug.utils import secure_filename
import json
import numpy as np
import pandas as pd
import PIL
import tensorflow as tf
import tensorflow_hub as hub
from geopy.geocoders import Nominatim
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
# 12-AUG-2021
today_date = current_date.strftime("%d-%b-%Y")


# Convert the string to a datetime object

# Format the datetime object as a string in the desired format
# 2024-01-26
package_date = current_date.strftime("%Y-%m-%d")

#API KEYS

API_KEY = 'c95354cf6bmsha1d0c084d95867cp1ef7b7jsn022524b64ff9'
API_KEY_OFFICIAL = 'ffb1f70549msh4f6afa984fb4d18p133e17jsne63de69dbc36'
API_KEY_IVIBCA = '55a774adc9msh7d2f9d5bc900644p135f9djsn1bea14d5c060'
GPT_API_KEY = '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'

# Asian Landmark Searching y images

upload = 'C:/Flask Projects/Ai_trip_planner/static/upload_images'
app.config['UPLOAD'] = upload

#CUSTOME ERROR PAGES

#Invalid pages

@app.errorhandler(404)

def page_not_found(e):
    return render_template('errors/404-error.html')

#Internal server error

@app.errorhandler(500)

def page_not_found(e):
    return render_template('errors/505.html')

# CHAT BOT
@app.route("/chat2", methods=['GET', 'POST'])
def chat2():
    data = ""
    ins = 0
    response = ""
    dta = ""
    msg = ""
    if request.method == 'POST':
        # Process the POST request
        message = request.form.get('msg')

        url = "https://chatgpt4-ai-chatbot.p.rapidapi.com/ask"

        payload = { "query": message }
        headers = {
            "content-type": "application/json",
            "X-RapidAPI-Key": API_KEY_OFFICIAL,
            "X-RapidAPI-Host": "chatgpt4-ai-chatbot.p.rapidapi.com"
        }

        response = requests.post(url, json=payload, headers=headers)
        print(response)
        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            ins = 1
            data = response.json()
            print(data)

            if 'response' in data:
                ins = 2
                data = data['response']
                return render_template('index-03.html', dta = data, rp = response, ins=ins, msg = message)

    return render_template('index-03.html', dta = data, rp = response, ins=ins)

@app.route("/chat", methods=['GET', 'POST'])
def chat():
    data = ""
    if request.method == 'POST':
        # Process the POST request
        message = request.form.get('message')

        message = ' " '+ message + ' ?" ' + "This question is not related to tourism, places, hotels, food spots, toursm activites then you only reply i'm ready to give data about tourism please ask about tourism activites"

        url = "https://open-ai21.p.rapidapi.com/conversationgpt35"

        payload = {
            "messages": [
                {
                    "role": "user",
                    "content": message
                }
            ],
            "web_access": False,
            "system_prompt": "",
            "temperature": 0.9,
            "top_k": 5,
            "top_p": 0.9,
            "max_tokens": 256
        }
        headers = {
            "content-type": "application/json",
            "X-RapidAPI-Key": API_KEY_OFFICIAL,
            "X-RapidAPI-Host": "open-ai21.p.rapidapi.com"
        }

        response = requests.post(url, json=payload, headers=headers)

        print(response.json())

    return (response.json())

# END CHATBOT

#TIME TABLE

@app.route('/TripOrganizer.com/plantrip', methods=['POST', 'GET'])
def plantrip():
    tripplann_msg = ''
    plan = ''
    trip_plan_related_searches = ''
    trip_plan_related_images = ''
    if request.method == 'POST':
        start_date = request.form.get('departDate')
        end_date = request.form.get('endDate')
        days = request.form.get('days')
        location = request.form.get('destination')
        var = start_date 
        try:
            url = "https://ai-trip-planner.p.rapidapi.com/"

            querystring = {"days": days, "destination": location}

            headers = {
            "X-RapidAPI-Key": API_KEY_IVIBCA,
            "X-RapidAPI-Host": "ai-trip-planner.p.rapidapi.com"
            }

            response = requests.get(url, headers=headers, params=querystring)
            data = response.json()
            plan = data.get('plan', [])  # Get the 'plan' list from the response JSON
            try:
                url = "https://image-search-api2.p.rapidapi.com/image-search"
                querystring = {"q": location, "imgc":"hd"}
                headers = {
                "X-RapidAPI-Key": API_KEY,
                "X-RapidAPI-Host": "image-search-api2.p.rapidapi.com"
                }
                response = requests.get(url, headers=headers, params=querystring)
                data = response.json()
                related_searches = []
                images = []

                if response.status_code == 200:
                    related_searches = []
                    images = []
                    if "related_searches" in data:
                        trip_plan_related_searches = data["related_searches"]

                    if "images" in data:
                        trip_plan_related_images = data["images"]
                else:
                    return "Request failed with status code:", response.status_code
            except:
                msg2 = "Related images not accesed"
        except:
            tripplann_msg = "Not getting"
                    
    return render_template('tour_time_table_view.html', plan = plan, no_days = days,
                         msg3 = tripplann_msg, location = location, var=var,
                         trip_plan_related_searches=trip_plan_related_searches,
                         trip_plan_related_images=trip_plan_related_images)

#END TIME TABLE
# IMAGE SEARCH
@app.route('/TripOrganizer/search_image', methods=['POST', 'GET'])
def search_image():
    msg = ""
    msg2 = ''
    image_to_search = './static/upload_images/place.jpg'
    image_loaction_address = ''
    image_lat_lon = ''
    related_searches = ''
    images = ''
    name_place = ''
    try:
        if request.method == 'POST':
            image = request.files['image']
            filename = secure_filename(image.filename)
            new_filename = 'place.jpg'
            image.save(os.path.join(app.config['UPLOAD'], new_filename))
            
            try:
                model_url = 'https://tfhub.dev/google/on_device_vision/classifier/landmarks_classifier_asia_V1/1'
                labels = "C:/Flask Projects/Ai_trip_planner/try.csv"

                img_shape = (321, 321)
                classifier = tf.keras.Sequential([hub.KerasLayer(model_url, input_shape=img_shape+(3,), output_key="predictions:logits")])
                df = pd.read_csv(labels)
                labels = dict(zip(df.id, df.name))


                img = PIL.Image.open("C:/Flask Projects/Ai_trip_planner/static/upload_images/place.jpg")
                img = img.resize(img_shape)
                img = np.array(img)/255.0
                img = img[np.newaxis]
                result = classifier.predict(img)

                name_place = labels[np.argmax(result)]
                print(labels[np.argmax(result)])

                try:
                    url = "https://image-search-api2.p.rapidapi.com/image-search"
                    querystring = {"q": name_place, "imgc":"hd"}
                    headers = {
                    "X-RapidAPI-Key": API_KEY,
                    "X-RapidAPI-Host": "image-search-api2.p.rapidapi.com"
                    }
                    response = requests.get(url, headers=headers, params=querystring)
                    data = response.json()
                    related_searches = []
                    images = []

                    if response.status_code == 200:
                        related_searches = []
                        images = []

                        if "related_searches" in data:
                            related_searches = data["related_searches"]

                        if "images" in data:
                            images = data["images"]

                    else:
                        return "Request failed with status code:", response.status_code
                except Exception as e:
                    msg2 = f"Related images not accessed. Error: {str(e)}"

                try:
                    address = name_place
                    geolocator = Nominatim(user_agent="Your_name")
                    location = geolocator.geocode(address, language="en")
                    image_loaction_address = (location.address)
                    image_lat_lon = (location.latitude, location.longitude)
                except:
                    msg2 = "Address not Available"
            except:
                msg2 = "Something error in fetching datas!"
    except:
        msg = "Image uploading failed!!"
    return render_template('image_search.html', msg=msg, img=image_to_search, msg2=msg2,
                             image_loaction_address=image_loaction_address,
                             image_lat_lon = image_lat_lon,
                             place_name = name_place, related_searches=related_searches,
                             images=images)

# HOME MAIN SEARCH

@app.route('/TripOrganizer/search_city', methods=['POST', 'GET'])
def search_city():
    city_to_search = ''
    city_state_country = ''
    search_related_images = ''
    search_related_searches = ''
    try:
        if request.method == 'POST':
            city_to_search = request.form.get('search_text')

            cursor = mysql.connection.cursor()
            query = "SELECT * FROM tour_packages WHERE tourname LIKE %s OR country LIKE %s OR territory LIKE %s ORDER BY RAND() LIMIT 4;"
            search_param = '%' + city_to_search + '%';  # Adding wildcards to search for partial matches
            cursor.execute(query, (search_param, search_param, search_param))
            related_tours = cursor.fetchall()


            url = "https://travel-advisor.p.rapidapi.com/locations/v2/auto-complete"
            querystring = {
                "query": city_to_search,
                "lang": "en_US",
                "units": "km"
            }
            headers = {
                "X-RapidAPI-Key": API_KEY_OFFICIAL,
                "X-RapidAPI-Host": "travel-advisor.p.rapidapi.com"
            }
            response = requests.get(url, headers=headers, params=querystring)
            data = response.json()
            state_country_info = ''
            if 'data' in data and 'Typeahead_autocomplete' in data['data']:
                results = data['data']['Typeahead_autocomplete']['results']
                printed_locations = set()
                for result in results:
                    if result.get('__typename') == 'Typeahead_LocationItem':
                        state_country_info = result['detailsV2']['names']['longOnlyHierarchyTypeaheadV2']
                        if state_country_info not in printed_locations:
                            city_state_country = state_country_info
                            printed_locations.add(state_country_info)
                        else:
                            city_state_country = ('Invalid response format')
                        break
            else:
                city_state_country = ('No data available for the city')
            try:
                url = "https://image-search-api2.p.rapidapi.com/image-search"
                querystring = {"q": city_to_search, "imgc": "hd"}
                headers = {
                    "X-RapidAPI-Key": API_KEY,
                    "X-RapidAPI-Host": "image-search-api2.p.rapidapi.com"
                }
                response = requests.get(url, headers=headers, params=querystring)
                data = response.json()
                related_searches = []
                images = []
                if response.status_code == 200:
                    related_searches = []
                    images = []
                    if "related_searches" in data:
                        search_related_searches = data["related_searches"]
                    if "images" in data:
                        search_related_images = data["images"]
                else:
                    return "Request failed with status code:", response.status_code
            except:
                msg2 = "Related images not accesed"
    except Exception as e:
        city_state_country = ('Error occurred while fetching data:', str(e))
    
    return jsonify({
        "city": city_to_search,
        "city_state_country": city_state_country,
        "search_related_images": search_related_images,
        "search_related_searches": search_related_searches,
        "related_tours" : related_tours
    })

    # END OF HOME MAIN SEARCH

# Direct to home page
@app.route('/TripOrganizer.com', methods=['POST', 'GET'])
def home():
    session['todate'] = package_date
    main_s_result = ""
    search_element = ""
    notification = ""
    booking_notifications = ""
    if request.method == 'POST':
        search_element = request.form.get("search_text")
        if search_element == 'ivin':
            main_s_result = {'name':ivin}
            return ({'result': main_s_result})
        else:
            main_s_result = search_element
            return ({'result': main_s_result})

    if 'userid' in session:
        notification = "Root"
        cursor = mysql.connection.cursor()
        query = "SELECT * FROM package_bookings WHERE user_id = %s AND (user_view_status IS NULL OR user_view_status != 1) AND package_status != 2"
        values = (str(session['userid']),)
        cursor.execute(query, values)
        booking_notifications = cursor.fetchall()
    else:
        notification = "login to get notifcations"

    # Packages
    cursor = mysql.connection.cursor()
    query = """ SELECT tp.*, pi.image_path,
        COALESCE(SUM(pr.ratings), 0) / COUNT(pr.package_id) * 5 AS average_rating_percentage
        FROM tour_packages tp
        LEFT JOIN (
            SELECT package_id, MIN(image_path) AS image_path
            FROM package_images
            GROUP BY package_id
        ) pi ON tp.package_id = pi.package_id
        LEFT JOIN package_reviews pr ON tp.package_id = pr.package_id
        WHERE tp.package_id = tp.package_id
        GROUP BY tp.package_id
        ORDER BY RAND()
        LIMIT 6;
    """
    cursor.execute(query)
    tour_packages_data = cursor.fetchall()

    #blogs in home
    query1 = '''SELECT blog.blogid, blog.date, blog.heading, blog.content, users.profile_pic, users.username, CONCAT_WS(', ',
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
    ORDER BY RAND() LIMIT 3'''

    cursor.execute(query1)
    blog_result = cursor.fetchall()

    return render_template('index.html', booking_notifications=booking_notifications, notification=notification, tour_packages_data=tour_packages_data, blog_result=blog_result)

@app.route('/TripOrganizer.com/tour-planner')
def tour_planner():
    return render_template('tour_planner.html')

# user booking Details on notification bar

@app.route('/TripOrganizer.com/tour-packages-booking-details-noti/<booking_id>', methods=['POST', 'GET'])
def user_booking_details_not(booking_id):
    provider_details = ""
    cursor = mysql.connection.cursor()

    # updating the row to viewd by user 

    update_query = "UPDATE package_bookings SET user_view_status = 1 WHERE booked_id = %s"
    cursor.execute(update_query, (booking_id,))
    mysql.connection.commit()

    #selecting the details of booking

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



# if home 
@app.route('/TripOrganizer.com/user.settings')
def user_settings():
    cursor = mysql.connection.cursor()
    query = "SELECT * FROM users WHERE user_id = %s"
    values = (str(session['userid']),)
    cursor.execute(query, values)
    result = cursor.fetchall()
    return render_template('user_settings.html', data = result)

@app.route('/TripOrganizer.com/login', methods = ['GET', 'POST'])
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
        return redirect('/TripOrganizer.com')
       else:
        error_message = "Invalid username/email or password"

    return render_template('login.html', error_message=error_message)

@app.route('/TripOrganizer.com/signup', methods = ['GET', 'POST'])
def signup():
    username =''
    email = ''
    password = ''
    email_exist_msg = ''
    username_exist_msg = ''
    date = today_date
    profile_pic = "../static/images/default-avatar-profile.jpg"
    if request.method == 'POST':
        username = request.form.get('signupname')
        email = request.form.get('signupemail')
        password = request.form.get('signuppassword')
        country = request.form.get('country')

        '''Adding user data to MySQL db'''

        cursor = mysql.connection.cursor()
        checking_email_unique = "SELECT * FROM users WHERE email = %s"
        values = (email,)
        cursor.execute(checking_email_unique, values)
        result = cursor.fetchall()

        cursor = mysql.connection.cursor()
        checking_username_unique = "SELECT * FROM users WHERE username = %s"
        values1 = (username,)
        cursor.execute(checking_username_unique, values1)
        result1 = cursor.fetchall()

        if len(result) > 0:
            email_exist_msg = "Email Already Taken"
        elif len(result1) > 0:
            username_exist_msg = "User Name Already In Use"
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
                return redirect('/TripOrganizer.com')


            return redirect('TripOrganizer.com/login')

    return render_template('signup.html', email_exist_msg=email_exist_msg, username=username, email=email,
                         password=password, username_exist_msg=username_exist_msg)

''' User Session logout '''

@app.route('/TripOrganizer.com/user-logout')
def user_logout():
    return render_template('user_delete.html')

@app.route('/logout')
def logout():
    session.pop('userid', None)  # Remove the user_id from the session
    session.pop('username', None)
    return redirect('/TripOrganizer.com')



''' User Profile '''
@app.route('/TripOrganizer/userprofile', methods = ['GET', 'POST'])
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
                file_path = os.path.join(path, file.filename)
                file.save(os.path.join(os.path.abspath(os.path.dirname(__file__)), app.config['BLOG_UPLOAD_IMAGES'], file.filename))


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

@app.route('/TripOrganizer.com/tour-packages')
def tour_packages():
    flash = None
    # SQL query to select Tour Packages
    query = """ SELECT tp.*, pi.image_path,
           COALESCE(SUM(pr.ratings), 0) / COUNT(pr.package_id) * 5 AS average_rating_percentage
    FROM tour_packages tp
    LEFT JOIN (
        SELECT package_id, MIN(image_path) AS image_path
        FROM package_images
        GROUP BY package_id
    ) pi ON tp.package_id = pi.package_id
    LEFT JOIN package_reviews pr ON tp.package_id = pr.package_id
    WHERE tp.package_id = tp.package_id
    GROUP BY tp.package_id;
    """
    # Execute the query and retrieve the data
    cursor = mysql.connection.cursor()
    cursor.execute(query)
    tour_packages_data = cursor.fetchall()

    # Close the cursor and database connection if necessary
    cursor.close()
    return render_template('tour_packages.html', tour_packages_data=tour_packages_data)


# Tour Package Details
@app.route('/TripOrganizer.com/tour-packages-details/<package_id>', methods=['POST', 'GET'])
def tour_package_details(package_id):
    pro_id = None
    session['todate'] = package_date
    if 'username' in session:
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
        cursor.execute(query1, (str(package_id),))
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

        # SQL query to check user is attended the package
        select_query = "SELECT * FROM package_bookings WHERE user_id = %s AND package_id = %s AND attendance = 1"
        select_values = (session['userid'], package_id)
        # Execute the query
        cursor.execute(select_query, select_values)
        user_attendance = cursor.fetchall()

        #selecting reviews to display
        review_select = """SELECT pr.*, u.username, u.profile_pic
                FROM package_reviews pr
                JOIN users u ON pr.user_id = u.user_id
                WHERE pr.package_id = %s;
        """
        cursor.execute(review_select, (package_id,))
        package_reviews = cursor.fetchall()

        # checking the user travaled or not

        review_select = """SELECT * FROM package_bookings WHERE user_id = %s AND package_id = %s AND attendance = %s;
        """
        cursor.execute(review_select, (session['userid'], package_id, 1))
        user_travaled = cursor.fetchall()

        # Execute the query
        cursor = mysql.connection.cursor()
        avg_rating = "SELECT AVG(ratings) AS average_rating, COUNT(ratings) AS rating_count FROM package_reviews WHERE package_id = %s"
        cursor.execute(avg_rating, (package_id,))
        average_rating = cursor.fetchall()


        return render_template('tour_package_details.html', tour_packages_data=tour_packages_data, user_attendance=user_attendance, user_travaled=user_travaled,
            tour_packages_day=tour_packages_day, tour_packages_image=tour_packages_image, pro_user_details=pro_user_details, package_reviews=package_reviews, average_rating=average_rating)
    else:
        return redirect('/TripOrganizer.com/login')

# Saving packages
@app.route('/TripOrganizer.com/tour-packages-saving/<package_id>', methods=['POST', 'GET'])
def tour_package_saving(package_id):
    session['todate'] = package_date
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

    # SQL query to check user is attended the package
    select_query = "SELECT * FROM package_bookings WHERE user_id = %s AND package_id = %s AND attendance = 1"
    select_values = (session['userid'], package_id)
    # Execute the query
    cursor.execute(select_query, select_values)
    user_attendance = cursor.fetchall()

    # selecting package reviews

    review_select = """SELECT pr.*, u.username, u.profile_pic
            FROM package_reviews pr
            JOIN users u ON pr.user_id = u.user_id
            WHERE pr.package_id = %s;
    """
    cursor.execute(review_select, (package_id,))
    package_reviews = cursor.fetchall()

    # checking the user travaled or not

    review_select = """SELECT * FROM package_bookings WHERE user_id = %s AND package_id = %s AND attendance = %s;
    """
    cursor.execute(review_select, (session['userid'], package_id, 1))
    user_travaled = cursor.fetchall()

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
            return render_template('tour_package_details.html', tour_packages_data=tour_packages_data, user_attendance=user_attendance, user_travaled=user_travaled,
                tour_packages_day=tour_packages_day, tour_packages_image=tour_packages_image, pro_user_details=pro_user_details, flash=flash, package_reviews=package_reviews)
        else:
            # Define the SQL query to insert data into the table
            query = "INSERT INTO saved_packages (package_id, user_id) VALUES (%s, %s)"
            # Execute the query with the actual values
            cursor.execute(query, (package_id, session['userid']))
            # Commit the transaction to save the changes to the database
            flash = "Saved Succefully.."
            mysql.connection.commit()
            return render_template('tour_package_details.html', tour_packages_data=tour_packages_data, user_attendance=user_attendance, user_travaled=user_travaled,
                tour_packages_day=tour_packages_day, tour_packages_image=tour_packages_image, pro_user_details=pro_user_details, flash=flash, package_reviews=package_reviews)
    except:
        flash = "Something Wrong..!!"
    return render_template('tour_package_details.html', tour_packages_data=tour_packages_data, user_attendance=user_attendance, package_reviews=package_reviews,
            tour_packages_day=tour_packages_day, tour_packages_image=tour_packages_image, pro_user_details=pro_user_details, user_travaled=user_travaled)

# Deleting Saving packages
@app.route('/TripOrganizer.com/tour-packages-remove/<package_id>', methods=['POST', 'GET'])
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

# user package booking payament 
@app.route('/TripOrganizer.com/tour-packages-booking-payment', methods=['POST', 'GET'])
def tour_package_booking_payment():
    price = 0.0
    package_name = "Not Available"
    if request.method == 'POST':
        if request.method == 'POST':
            provider = request.form.get('pro_id')
            num_people = request.form.get('days')
            package_id = request.form.get('package_id')
            name = request.form.get('username')
            user_identity_document = request.form.get('user_identity_document')
            phone = request.form.get('phone')
            price = request.form.get('price')
            package_name = request.form.get('package_name')

            session['booking_form_provider'] = provider
            session['booking_form_num_people'] = num_people
            session['booking_form_package_id'] = package_id
            session['booking_form_name'] = name
            session['booking_form_user_identity_document'] = user_identity_document
            session['booking_form_phone'] = phone

    return render_template('tour_package_payment.html', package_price=price, package_name=package_name)

# user_tour_package_booking
@app.route('/TripOrganizer.com/tour-packages-booking', methods=['POST', 'GET'])
def user_tour_package_booking():
    session['todate'] = ""
    session['todate'] = package_date
    view = 0
    package_status = 2
    package_status_view = 1
    provider = session['booking_form_provider']
    num_people = session['booking_form_num_people']
    package_id = session['booking_form_package_id']
    name = session['booking_form_name']
    user_identity_document = session['booking_form_user_identity_document']
    phone = session['booking_form_phone']
    date = today_date

    cursor = mysql.connection.cursor()
    query = "INSERT INTO package_bookings (user_id, package_id, viewed, package_provider_id, package_status, package_status_view, date) VALUES (%s, %s, %s, %s, %s, %s, %s)"
    cursor.execute(query, (session['userid'], package_id, view, provider, package_status, package_status_view, date))
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
    query = """SELECT pb.*, tp.tourname, tp.from_date
            FROM package_bookings pb
            INNER JOIN tour_packages tp ON pb.package_id = tp.package_id
            WHERE pb.user_id = %s
            ORDER BY pb.booked_id DESC;
    """
    cursor.execute(query, (session['userid'],))
    tour_bookings = cursor.fetchall()
    cursor.close();

    session['booking_form_provider'] = ""
    session['booking_form_num_people'] = ""
    session['booking_form_package_id'] = ""
    session['booking_form_name'] = ""
    session['booking_form_user_identity_document'] = ""
    session['booking_form_phone'] = ""

    return render_template('user_bookings.html', flash = flash, tour_bookings=tour_bookings)


# User saved Tour packages

@app.route('/TripOrganizer.com/user-saved-tour-packages')
def saved_packages():
    session['todate'] = package_date
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
        return redirect('/TripOrganizer.com/login')

        # User package searching 


@app.route('/TripOrganizer.com/packages/searching', methods=['POST', 'GET'])
def user_package_searching():
    if request.method == 'POST':
        session['todate'] = package_date
        search_value = request.form.get('search_value')
        # SQL query to select Tour Packages
        search_value = request.form.get('search_value')

        # SQL query to select Tour Packages with a search condition
        query = """ 
           SELECT tp.*, pi.image_path,
        COALESCE((SELECT AVG(ratings) FROM package_reviews pr WHERE pr.package_id = tp.package_id), 0) AS average_rating
        FROM tour_packages tp
        LEFT JOIN (
            SELECT package_id, MIN(image_path) AS image_path
            FROM package_images
            GROUP BY package_id
        ) pi ON tp.package_id = pi.package_id
        WHERE tp.tourname LIKE %s OR tp.country LIKE %s OR tp.territory LIKE %s OR tp.price LIKE %s OR tp.description LIKE %s;
        """

        # Execute the query and retrieve the data
        cursor = mysql.connection.cursor()
        cursor.execute(query, ('%' + search_value + '%', '%' + search_value + '%', '%' + search_value + '%', '%' + search_value + '%', '%' + search_value + '%'))

        # Fetch the result
        tour_packages_data = cursor.fetchall()
        # Close the cursor and database connection if necessary
        cursor.close()
        rating_true = True
    return render_template('tour_packages.html', tour_packages_data=tour_packages_data, rating_true=rating_true)

@app.route('/TripOrganizer.com/packages/package-searching-home-form', methods=['POST', 'GET'])
def package_search_on_home_form():
    if request.method == 'POST':
        session['todate'] = package_date
        destination = request.form.get('destination_p')
        depart_date = request.form.get('departDate_p')
        days = request.form.get('days_p')

        # Use the correct format for 'depart_date'
        user_date = datetime.strptime(depart_date, "%Y-%m-%d")
        
        # 'user_date' is already in the correct format, so no need to convert it again
        db_date_format = user_date.strftime("%Y-%m-%d")

        # Rest of your code

        query = """ 
           SELECT tp.*, pi.image_path,
        COALESCE((SELECT AVG(ratings) FROM package_reviews pr WHERE pr.package_id = tp.package_id), 0) AS average_rating
        FROM tour_packages tp
        LEFT JOIN (
            SELECT package_id, MIN(image_path) AS image_path
            FROM package_images
            GROUP BY package_id
        ) pi ON tp.package_id = pi.package_id
        WHERE (tp.tourname LIKE %s OR tp.country LIKE %s OR tp.territory LIKE %s OR tp.description LIKE %s)
        AND (tp.num_days <= %s OR tp.from_date >= %s);
        """

        # Execute the query and retrieve the data
        cursor = mysql.connection.cursor()
        cursor.execute(query, (
            '%' + destination + '%', '%' + destination + '%', '%' + destination + '%', '%' + destination + '%',
            days, db_date_format))

        # Fetch the result
        tour_packages_data = cursor.fetchall()
        # Close the cursor and database connection if necessary
        cursor.close()
        rating_true = True
    return render_template('tour_packages.html', tour_packages_data=tour_packages_data, rating_true=rating_true)







# 3searching the package
@app.route('/TripOrganizer.com/packages/searching-on-home/<search_value>', methods=['POST', 'GET'])
def user_package_searching_onhome(search_value):
    session['todate'] = package_date
    # SQL query to select Tour Packages with a search condition
    query = """ 
       SELECT tp.*, pi.image_path,
    COALESCE((SELECT AVG(ratings) FROM package_reviews pr WHERE pr.package_id = tp.package_id), 0) AS average_rating
    FROM tour_packages tp
    LEFT JOIN (
        SELECT package_id, MIN(image_path) AS image_path
        FROM package_images
        GROUP BY package_id
    ) pi ON tp.package_id = pi.package_id
    WHERE tp.tourname LIKE %s OR tp.country LIKE %s OR tp.territory LIKE %s OR tp.price LIKE %s OR tp.description LIKE %s;
    """

    # Execute the query and retrieve the data
    cursor = mysql.connection.cursor()
    cursor.execute(query, ('%' + search_value + '%', '%' + search_value + '%', '%' + search_value + '%', '%' + search_value + '%', '%' + search_value + '%'))

    # Fetch the result
    tour_packages_data = cursor.fetchall()
    # Close the cursor and database connection if necessary
    cursor.close()
    rating_true = True
    return render_template('tour_packages.html', tour_packages_data=tour_packages_data, rating_true=rating_true)

# User Bookings 

@app.route('/TripOrganizer.com/user-bookings', methods=['POST', 'GET'])
def user_bookings():
    session['todate'] = ""
    session['todate'] = package_date
    cursor = mysql.connection.cursor()
    query = """SELECT pb.*, tp.tourname, tp.from_date
            FROM package_bookings pb
            INNER JOIN tour_packages tp ON pb.package_id = tp.package_id
            WHERE pb.user_id = %s
            ORDER BY pb.booked_id DESC;
    """
    cursor.execute(query, (session['userid'],))
    tour_bookings = cursor.fetchall()

    query_1 = """SELECT * FROM cancelled_bookings WHERE user_id = %s"""
    cursor.execute(query_1, (session['userid'],))
    cancelled_bookings = cursor.fetchall()
    cursor.close()

    return render_template('user_bookings.html', tour_bookings=tour_bookings, cancelled_bookings=cancelled_bookings)  


# user booking Details

@app.route('/TripOrganizer.com/tour-packages-booking-details/<booking_id>', methods=['POST', 'GET'])
def user_booking_details(booking_id):
    provider_details = ""
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
@app.route('/TripOrganizer.com/user-booking-cancel/<booking_id>/<package_name>/<provider_id>', methods=['POST', 'GET'])
def user_booking_cancel(booking_id, package_name, provider_id):
    session['todate'] = ""
    session['todate'] = package_date
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
        query = """SELECT pb.*, tp.tourname, tp.from_date
            FROM package_bookings pb
            INNER JOIN tour_packages tp ON pb.package_id = tp.package_id
            WHERE pb.user_id = %s
            ORDER BY pb.booked_id DESC;
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

# Review adding to the form
@app.route('/TripOrganizer.com/package-review-adding/', methods=['POST', 'GET'])
def review_adding():
    if 'username' in session:
        cursor = mysql.connection.cursor()
        if request.method == "POST":
            review = request.form.get("review")
            rating = request.form.get("rating")
            package_id=request.form.get("package_id")
            if rating == "":
                rating = 0

            query_select = """
                SELECT * FROM package_reviews WHERE user_id = %s AND package_id = %s
            """
            cursor.execute(query_select, (session['userid'], package_id))
            package_review = cursor.fetchall()

            if package_review:
                if  review != "":
                    query_updating = """
                        UPDATE package_reviews
                        SET review = %s, ratings = %s
                        WHERE user_id = %s AND package_id = %s;
                    """
                    query_values_update = (review, rating, session['userid'], package_id)
                    cursor.execute(query_updating, query_values_update)
                    mysql.connection.commit()
                else:
                    query_updating = """
                        UPDATE package_reviews
                        SET ratings = %s
                        WHERE user_id = %s AND package_id = %s;
                    """
                    query_values_update = (rating, session['userid'], package_id)
                    cursor.execute(query_updating, query_values_update)
                    mysql.connection.commit()
            else:
                query_inserting = """
                INSERT INTO package_reviews (user_id, package_id, review, ratings)
                VALUES (%s, %s, %s, %s);
                """
                query_values = (session['userid'], package_id, review, rating)
                cursor.execute(query_inserting, query_values)
                mysql.connection.commit()

        return redirect(url_for('tour_package_details', package_id=package_id))


# Review adding to the form
@app.route('/TripOrganizer.com/package-review-deleting/<review_id>/<package_id>', methods=['POST', 'GET'])
def review_deleting(review_id, package_id):
    cursor = mysql.connection.cursor()
    # SQL query to delete rows from travalers_attendance table
    delete_query = "DELETE FROM package_reviews WHERE review_id = %s"
    delete_values = (review_id,)
    cursor.execute(delete_query, delete_values)
    mysql.connection.commit()
    return redirect(url_for('tour_package_details', package_id=package_id))



      
#---------------------------------------------------------
#---------------------------------------------------------
#---------------------------------------------------------
#---------------------------------------------------------
#---------------------------------------------------------
#---------------------------------------------------------
#---------------------------------------------------------
#---------------------------------------------------------


# Business Pro Account home page

@app.route('/TripOrganizer.com/account.pro')
def pro_account():
    session['todate'] = package_date
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
        query = """SELECT tp.*, pi.image_path
           FROM tour_packages tp
           LEFT JOIN (
               SELECT DISTINCT package_id, MIN(image_path) AS image_path
               FROM package_images
               GROUP BY package_id
           ) pi ON tp.package_id = pi.package_id
           WHERE tp.pro_id = %s;"""

        # Execute the query and retrieve the data
        cursor.execute(query, (session['proid'],))
        tour_packages_data = cursor.fetchall()
        # Close the cursor and database connection if necessary
        cursor.close()

        cursor = mysql.connection.cursor()
        current_date = date.today()

        # Execute the SQL query to select tourname where from_date is equal to the current date
        query = "SELECT * FROM tour_packages WHERE from_date = %s AND pro_id = %s"
        cursor.execute(query, (current_date, str(session['proid'])))

        # Fetch the results
        matching_tournames = cursor.fetchall()

        cursor = mysql.connection.cursor()
        query1 = "SELECT COUNT(*) AS total_count FROM ai_travel_planner.package_bookings WHERE viewed = 0 AND package_provider_id = %s;"
        cursor.execute(query1, (str(session['proid']),))
        result1 = cursor.fetchone()

        query2 = "SELECT COUNT(*) AS total_count2 FROM ai_travel_planner.cancelled_bookings WHERE pro_view = 0 AND provider_id = %s;"
        cursor.execute(query2, (str(session['proid']),))
        result2 = cursor.fetchone()

        query = """ SELECT tp.*, pi.image_path
           FROM tour_packages tp
           LEFT JOIN (
               SELECT DISTINCT package_id, MIN(image_path) AS image_path
               FROM package_images
               GROUP BY package_id
           ) pi ON tp.package_id = pi.package_id
           WHERE tp.pro_id = %s
           AND tp.from_date < %s;
                """
        # Execute the query and retrieve the data
        cursor = mysql.connection.cursor()
        cursor.execute(query, (str(session['proid']), package_date))
        tour_packages_data_out_dated = cursor.fetchall()

        # Close the cursor and connection
        cursor.close()
        return render_template('pro/home.html', unwatched=unwatched, tour_packages_data=tour_packages_data, current_date=current_date,
         matching_tournames=matching_tournames, noti_count=result1, noti_count1=result2, tour_packages_data_out_dated=tour_packages_data_out_dated)
    return render_template('pro/section.html')

# Current day tour list of users
@app.route('/TripOrganizer.com/account.pro/travalers-list/<package_id>')
def travalers_list(package_id):
    cursor = mysql.connection.cursor()
    query = """ SELECT pb.user_id, pb.booked_id, pbt.travaler_id, pbt.*, pb.attendance
FROM package_bookings pb
JOIN package_booked_travalers pbt ON pb.booked_id = pbt.booking_id
WHERE pb.package_id = %s;


            """
    cursor.execute(query, (package_id,))

    travalers_list = cursor.fetchall()
    return render_template('pro/travalers_list.html', travalers_list=travalers_list, package_id=package_id)


# company login
@app.route('/TripOrganizer.com/account.pro/login', methods = ['GET', 'POST'])
def pro_login():
    session['today_date'] = today_date
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
        return redirect('/TripOrganizer.com/account.pro')
       else:
        error_message = "Invalid username/email or password"
    return render_template('pro/pro_login.html', error_message=error_message)

# Company Signup
@app.route('/TripOrganizer.com/account.pro/sign-up', methods = ['GET', 'POST'])
def pro_signup():
    error_message = ""
    prousername =''
    email = ''
    password = ''
    email_exist_msg = ''
    username_exist_msg = ''
    profile_pic = ""
    company = ''
    country = ''
    state = ''
    territory = ''
    address = ''
    phone = ''
    bio = ''
    pin = ''
    date = today_date
    if request.method == 'POST':
        company = request.form.get('signupname')
        email = request.form.get('signupemail')
        password = request.form.get('signuppassword')
        country = request.form.get('country')

        state = request.form.get('state')
        territory = request.form.get('territory')
        address = request.form.get('address')
        phone = request.form.get('phone')
        bio = request.form.get('bio')
        pin = request.form.get('pin')

        '''Adding user data to MySQL db'''

        cursor = mysql.connection.cursor()
        checking_email_unique = "SELECT * FROM pro_users WHERE email = %s"
        values = (email,)
        cursor.execute(checking_email_unique, values)
        result = cursor.fetchall()

        cursor = mysql.connection.cursor()
        checking_username_unique = "SELECT * FROM pro_users WHERE company = %s"
        values1 = (company,)
        cursor.execute(checking_username_unique, values1)
        result1 = cursor.fetchall()

        if len(result) > 0:
            email_exist_msg = "Email Already Taken"
        elif len(result1) > 0:
            username_exist_msg = "User Name Already In Use"
        else:
            # Insert new user data into the 'users' table
            insert_query = "INSERT INTO pro_users (company, email, country, state, territory, pin, phone, password, address, date) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
            values = (company, email, country, state, territory, pin, phone, password, address, date)
            cursor.execute(insert_query, values)
            mysql.connection.commit()

            cursor = mysql.connection.cursor()
            query = "SELECT pro_usersid, company FROM pro_users WHERE (email = %s OR company = %s) AND password = %s"
            values = (email, company, password)
            cursor.execute(query, values)
            result = cursor.fetchall()
            if len(result) > 0:
                session['userid'] = result[0][0]
                session['company'] = result[0][1]
                return redirect('/TripOrganizer.com/account.pro')

    return render_template('pro/pro_signup.html',email_exist_msg=email_exist_msg, username_exist_msg=username_exist_msg, email=email, company=company,
                            country=country,
                            state = state,
                            territory = territory,
                            address = address,
                            phone = phone,
                            bio = bio)


# Travaler attendance
@app.route('/TripOrganizer.com/account.pro/travaler-attendance/<travaler_id>/<user_id>/<booking_id>/<package_id>')
def travaler_attendance(travaler_id, user_id, booking_id, package_id):
    cursor = mysql.connection.cursor()

    # SQL query to insert values into travelers_attendance table
    insert_query = "INSERT INTO travalers_attendance (user_id, booking_id, package_id, travaler_id) VALUES (%s, %s, %s, %s)"
    insert_values = (user_id, booking_id, package_id, travaler_id)
    cursor.execute(insert_query, insert_values)
    mysql.connection.commit()

    # SQL query to update the attendance column to 1
    update_query = "UPDATE package_bookings SET attendance = 1 WHERE user_id = %s"
    update_values = (user_id,)
    cursor.execute(update_query, update_values)
    mysql.connection.commit()

    # SQL query to update the attendance column to 1 in travaler table
    update_query = "UPDATE package_booked_travalers SET attendance = 1 WHERE travaler_id = %s"
    update_values = (travaler_id,)
    cursor.execute(update_query, update_values)
    mysql.connection.commit()

    query = """ SELECT pb.user_id, pb.booked_id, pbt.travaler_id, pbt.*, pb.attendance
                FROM package_bookings pb
                JOIN package_booked_travalers pbt ON pb.booked_id = pbt.booking_id
                WHERE pb.package_id = %s;
            """
    cursor.execute(query, (package_id,))

    travalers_list = cursor.fetchall()
    return render_template('pro/travalers_list.html', travalers_list=travalers_list,package_id=package_id)

# REmmove travelr form list of travalers
@app.route('/TripOrganizer.com/account.pro/travaler-attendance-remove/<travaler_id>/<user_id>/<booking_id>/<package_id>')
def travaler_attendance_remove(travaler_id, user_id, booking_id, package_id):
    cursor = mysql.connection.cursor()

    # SQL query to delete rows from travalers_attendance table
    delete_query = "DELETE FROM travalers_attendance WHERE travaler_id = %s"
    delete_values = (travaler_id,)
    cursor.execute(delete_query, delete_values)
    mysql.connection.commit()

    # SQL query to update the attendance column to 0 in travaler table
    update_query = "UPDATE package_booked_travalers SET attendance = 0 WHERE travaler_id = %s"
    update_values = (travaler_id,)
    cursor.execute(update_query, update_values)
    mysql.connection.commit()

    # SQL query to update the attendance column to 0
    update_query = "UPDATE package_bookings SET attendance = 0 WHERE user_id = %s"
    update_values = (user_id,)
    cursor.execute(update_query, update_values)
    mysql.connection.commit()

    
    cursor = mysql.connection.cursor()

    query = """ SELECT pb.user_id, pb.booked_id, pbt.travaler_id, pbt.*, pb.attendance
                FROM package_bookings pb
                JOIN package_booked_travalers pbt ON pb.booked_id = pbt.booking_id
                WHERE pb.package_id = %s;
            """
    cursor.execute(query, (package_id,))

    travalers_list = cursor.fetchall()
    return render_template('pro/travalers_list.html', travalers_list=travalers_list,package_id=package_id)



# New notification mark as read
@app.route('/TripOrganizer.com/account.pro/mark-us-read/<booking_id>')
def booking_mark_as_read(booking_id):
    cursor = mysql.connection.cursor()
    query = "UPDATE package_bookings SET viewed = 1 WHERE package_provider_id = %s AND booked_id = %s"
    cursor.execute(query, (str(session['proid']), booking_id))
    mysql.connection.commit()
    return redirect(url_for('pro_account'))

# Company Logout Page
@app.route('/TripOrganizer.com/account.pro/logout-section')
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
@app.route('/TripOrganizer.com/account.pro/logout')
def pro_logout():
    if 'prousercompany' in session:
        session.pop('prousercompany', None)  # Remove the user_id from the session
        session.pop('proid', None)
        return redirect('/TripOrganizer.com/account.pro')
    else:
        return redirect('pro.login')

# Company Tour packages

@app.route('/TripOrganizer.com/account.pro/tour-packages')
def pro_tour_packages():
    if 'prousercompany' in session:
        # SQL query to select Tour Packages
        query = """SELECT tp.*, pi.image_path, AVG(pr.ratings) AS average_rating
        FROM tour_packages tp
        LEFT JOIN (
            SELECT package_id, MIN(image_path) AS image_path
            FROM package_images
            GROUP BY package_id
        ) pi ON tp.package_id = pi.package_id
        LEFT JOIN package_reviews pr ON tp.package_id = pr.package_id
        WHERE tp.pro_id = %s
        GROUP BY tp.package_id;

        """

        # Execute the query and retrieve the data
        cursor = mysql.connection.cursor()
        cursor.execute(query, (str(session['proid']),))
        tour_packages_data = cursor.fetchall()        
        # Close the cursor and database connection if necessary
        cursor.close()

        return render_template('pro/tour_packages.html', tour_packages_data=tour_packages_data)
    else:
        return redirect('pro.login')

# password changing page

@app.route('/TripOrganizer.com/account.pro/password-changing', methods=['GET', 'POST'])
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

@app.route('/TripOrganizer.com/account.pro/password-changing_form', methods=['GET', 'POST'])
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


        query1 = "SELECT COUNT(*) AS total_count FROM ai_travel_planner.package_bookings WHERE viewed = 0 AND package_provider_id = %s;"
        cursor.execute(query1, (str(session['proid']),))
        result1 = cursor.fetchone()

        query2 = "SELECT COUNT(*) AS total_count2 FROM ai_travel_planner.cancelled_bookings WHERE pro_view = 0 AND provider_id = %s;"
        cursor.execute(query2, (str(session['proid']),))
        result2 = cursor.fetchone()

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

            return render_template('pro/pro_change_password.html', flash=flash, noti_count1=result2, noti_count=result1)
        return render_template('pro/pro_change_password.html', error_message=password_error_msg, noti_count1=result2, noti_count=result1)
    else:
        return redirect('pro.login')



# Notifications 

@app.route('/TripOrganizer.com/account.pro/notifcations')
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

@app.route('/TripOrganizer.com/account.pro/company-settings', methods=['GET', 'POST'])
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
        return redirect('/TripOrganizer.com/account.pro/login')  # Use the redirect function here

# Adding Packages images to database

@app.route('/TripOrganizer.com/account.pro/tour-packages/add-form', methods=['POST', 'GET'])
def adding_tourpackages():
    cursor = mysql.connection.cursor()
    if request.method == 'POST':      
        tourname = request.form.get('tourname')
        num_days = request.form.get('days')
        price = request.form.get('price')
        from_date = request.form.get('from_date')
        to_date = request.form.get('to_date')
        description = request.form.get('description')
        country = request.form.get('country')
        territory = request.form.get('region')

        # here, inserting query to tourpackages table

        try:
            # Insert the data into the "tour_packages" table
            insert_query = "INSERT INTO tour_packages (pro_id, tourname, num_days, price, from_date, to_date, description, country, territory) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
            values = (session['proid'], tourname, num_days, price, from_date, to_date, description, country, territory)
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
            return redirect('/TripOrganizer.com/account.pro/tour-packages', flash=flash)
        except:
            var = "nothing"
            return render_template('pro/tour-packages-adding-form.html')
    return render_template('pro/tour-packages-adding-form.html')

#EDITING AND UPDATING TOURPACKAGES BY TOUR OPERATOR

@app.route('/TripOrganizer.com/account.pro/tour-packages/edit-form', methods=['POST', 'GET'])
def pro_editing_tourpackages():
    cursor = mysql.connection.cursor()
    if request.method == 'POST':
        package_id = request.form.get('package_id')     
        tourname = request.form.get('tourname')
        num_days = request.form.get('days')
        price = request.form.get('price')
        from_date = request.form.get('from_date')
        to_date = request.form.get('to_date')
        description = request.form.get('description')

        # here, updating query to tourpackages table
        try:
            # Update the data in the "tour_packages" table
            update_query = "UPDATE tour_packages SET tourname = %s, num_days = %s, price = %s, from_date = %s, to_date = %s, description = %s WHERE pro_id = %s AND package_id = %s"
            values = (tourname, num_days, price, from_date, to_date, description, session['proid'], package_id)
            cursor.execute(update_query, values)

            # Commit the changes to the database
            mysql.connection.commit()
        except Exception as e:
            # Handle the exception (e.g., log or return an error message)
            print("Error:", str(e))
            mysql.connection.rollback()
            flash = "Error updating tour package"
            return redirect('/TripOrganizer.com/account.pro/tour-packages')

        # Retrieve day program data based on the number of days
        day_programs = [request.form.get(f'day_program_{i}') for i in range(1, int(num_days) + 1)]


        '''Here Updating images to db'''
    return redirect('/TripOrganizer.com/account.pro/tour-packages')


    return render_template('pro/tour-packages-adding-form.html')


## Tour Edit Package Details
@app.route('/TripOrganizer.com/account.pro/pro-tour-packages-edit/<package_id>', methods=['POST', 'GET'])
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
        cursor.execute(query1, (package_id,))
        tour_packages_data = cursor.fetchall()

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

        return render_template('pro/tour_package_edit_form.html', tour_packages_data=tour_packages_data,
            tour_packages_day=tour_packages_day, tour_packages_image=tour_packages_image)
    else:
        return render_template('pro/login')


# Tour Package Details
@app.route('/TripOrganizer.com/account.pro/pro-tour-packages-details/<package_id>', methods=['POST', 'GET'])
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
        cursor.execute(query1, (package_id,))
        tour_packages_data = cursor.fetchall()

        # SELECTING TOUR PACKAGE
        query2 = "SELECT * FROM package_day_programme WHERE package_id = %s"
        # Execute the query and retrieve the data
        cursor = mysql.connection.cursor()
        cursor.execute(query2, (package_id,))
        tour_packages_day = cursor.fetchall()

        # SELECTING TOUR PACKAGE IMAGES
        query3 = "SELECT * FROM package_images WHERE package_id = %s"
        # Execute the query and retrieve the data
        cursor = mysql.connection.cursor()
        cursor.execute(query3, (package_id,))
        tour_packages_image = cursor.fetchall()

        #selecting reviews to display
        review_select = """SELECT pr.*, u.username, u.profile_pic
                FROM package_reviews pr
                JOIN users u ON pr.user_id = u.user_id
                WHERE pr.package_id = %s;
        """
        cursor.execute(review_select, (package_id,))
        package_reviews = cursor.fetchall()

        # Execute the query
        cursor = mysql.connection.cursor()
        avg_rating = "SELECT AVG(ratings) AS average_rating FROM package_reviews WHERE package_id = %s"
        cursor.execute(avg_rating, (package_id,))
        # Fetch the result
        average_rating = cursor.fetchall()

        return render_template('pro/tour_package_details.html', tour_packages_data=tour_packages_data,
            tour_packages_day=tour_packages_day, tour_packages_image=tour_packages_image, package_reviews=package_reviews, average_rating=average_rating)
    else:
        return render_template('pro/section.html')


# Remove Tour Packages Details
@app.route('/TripOrganizer.com/account.pro/remove-package/<package_id>')
def remove_package(package_id):
    cursor = mysql.connection.cursor()
    try:

        query = """
            DELETE FROM tour_packages
            WHERE package_id = %s;
        """
        cursor.execute(query, (package_id,))
        mysql.connection.commit()

        # delete package from images

        query = """
            DELETE FROM package_images
            WHERE package_id = %s;
        """
        cursor.execute(query, (package_id,))
        mysql.connection.commit()

        # delete package from reviews

        query = """
            DELETE FROM package_reviews
            WHERE package_id = %s;
        """
        cursor.execute(query, (package_id,))
        mysql.connection.commit()

        # delete package from bookings

        query = """
            DELETE FROM package_bookings
            WHERE package_id = %s;
        """
        cursor.execute(query, (package_id,))
        mysql.connection.commit()

        # delete package from day prgrammes

        query = """
            DELETE FROM package_day_programme
            WHERE package_id = %s;
        """
        cursor.execute(query, (package_id,))
        mysql.connection.commit()

        # Delete package from saved packages

        query = """
            DELETE FROM saved_packages
            WHERE package_id = %s;
        """
        cursor.execute(query, (package_id,))
        mysql.connection.commit()

        flash = "Package deleted.."
    except:
        flash = " Something error"
    query = """SELECT tp.*, pi.image_path, AVG(pr.ratings) AS average_rating
        FROM tour_packages tp
        LEFT JOIN (
            SELECT package_id, MIN(image_path) AS image_path
            FROM package_images
            GROUP BY package_id
        ) pi ON tp.package_id = pi.package_id
        LEFT JOIN package_reviews pr ON tp.package_id = pr.package_id
        WHERE tp.pro_id = %s
        GROUP BY tp.package_id;

    """

    # Execute the query and retrieve the data
    cursor = mysql.connection.cursor()
    cursor.execute(query, (str(session['proid']),))
    tour_packages_data = cursor.fetchall()        
    # Close the cursor and database connection if necessary
    cursor.close()

    return render_template('pro/tour_packages.html', tour_packages_data=tour_packages_data, flash=flash)



# View Package Order Details
@app.route('/TripOrganizer.com/account.pro/tour-packages-booking-details/<booking_id>', methods=['POST', 'GET'])
def pro_tour_booking_details(booking_id):
    session['todate'] = package_date
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
@app.route('/TripOrganizer.com/account.pro/package-accepting/<booking_id>', methods=['POST', 'GET'])
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
@app.route('/TripOrganizer.com/account.pro/package-rejecting/<booking_id>', methods=['POST', 'GET'])
def pro_tour_booking_reject(booking_id):
    session['todate'] = package_date
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

@app.route('/TripOrganizer.com/account.pro/bookings')
def bookings():
    session['todate'] = package_date
    # Assuming session['today_date'] is a string in the format '12-AUG-2021'
    today_date_str = today_date
    session['today_date'] = datetime.strptime(today_date_str, '%d-%b-%Y')
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


# Provider account and datas deletion

@app.route('/TripOrganizer.com/account.pro/provider_deletion')
def provider_deletion():
    # Create a cursor
    cursor = conn.cursor()

    # Delete from pro_users table
    delete_query_pro_users = "DELETE FROM pro_users WHERE provider_id = %s"
    cursor.execute(delete_query_pro_users, (str(session['proid']),))

    # Delete from package_bookings table
    delete_query_package_bookings = "DELETE FROM package_bookings WHERE provider_id = %s"
    cursor.execute(delete_query_package_bookings, (str(session['proid']),))

    # Delete from cancelled_bookings table
    delete_query_cancelled_bookings = "DELETE FROM cancelled_bookings WHERE provider_id = %s"
    cursor.execute(delete_query_cancelled_bookings, (str(session['proid']),))

    # Delete from package_bookings table (assuming this is a different table from the first one)
    delete_query_another_package_bookings = "DELETE FROM another_package_bookings WHERE provider_id = %s"
    cursor.execute(delete_query_another_package_bookings, (str(session['proid']),))

    # Delete from tour_packages table
    delete_query_tour_packages = "DELETE FROM tour_packages WHERE provider_id = %s"
    cursor.execute(delete_query_tour_packages, (str(session['proid']),))

    # Commit the changes
    conn.commit()

    # Close the cursor and connection
    cursor.close()
    conn.close()
    if 'prousercompany' in session:
        session.pop('prousercompany', None)  # Remove the user_id from the session
        session.pop('proid', None)
        return redirect('/TripOrganizer.com/account.pro')
    else:
        return redirect('pro.login')
    return redirect('pro.login')

# Provider contact us page

@app.route('/TripOrganizer.com/account.pro/contact-us')
def contactus():
    return render_template('pro/contactus.html')

@app.route('/TripOrganizer.com/account.pro/provider-search', methods=['POST', 'GET'])
def provider_searching():
    if 'prousercompany' in session:
        if request.method == 'POST':
            search_value = request.form.get('search_value')
            cursor = mysql.connection.cursor()
            query = """SELECT pb.*, tp.tourname
                FROM package_bookings pb
                INNER JOIN tour_packages tp ON pb.package_id = tp.package_id
                WHERE pb.package_provider_id = %s
                AND pb.booked_id = %s;
            """
            cursor.execute(query, (session['proid'], search_value))
            all_d = cursor.fetchall()
            cursor.close()

        return render_template('pro/search_results.html', bookings=all_d, se=all_d)
    else:
        return redirect('pro.login')
#---------------------------------------------------------
#---------------------------------------------------------
#---------------------------------------------------------
#---------------------------------------------------------
#---------------------------------------------------------
#---------------------------------------------------------
#---------------------------------------------------------
#---------------------------------------------------------

''' CHECK THE ADMIN LOGIN SESSION '''


@app.route('/TripOrganizeradmins.com', methods=['GET', 'POST'])
def admin_dashboard():
    if 'admin_name' in session and 'adminid' in session:
        cursor = mysql.connection.cursor()
        query = "SELECT * FROM admin"
        cursor.execute(query)
        admins = cursor.fetchall()
        return render_template('admin/dashboard.html', admins = admins)
    else:
        return redirect('/TripOrganizeradmins.com/admin')


''' Admin Login and session creation '''

@app.route('/TripOrganizeradmins.com/admin', methods=['GET', 'POST'])
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

@app.route('/TripOrganizeradmins.com/add_admin', methods=['GET', 'POST'])
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

@app.route('/TripOrganizeradmins.com/delete_admin/<int:aid>', methods=['GET', 'POST'])
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

@app.route('/TripOrganizeradmins.com/admin_logout')
def admin_logout():
   session['adminid'] = None
   session['admin_name'] = None
   return redirect('admin')

# ________________________________________________________#

''' Facts Page '''

@app.route('/TripOrganizer.com.com/admin_facts', methods=['GET', 'POST'])
def admin_facts():
    cursor = mysql.connection.cursor()
    query = "SELECT * FROM facts"
    cursor.execute(query)
    facts = cursor.fetchall()
    return render_template('admin/admin_facts.html', facts=facts)

# Adding new facts
@app.route('/TripOrganizeradmins.com/add_facts', methods=['GET', 'POST'])
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

#Deletion of facts

@app.route('/TripOrganizeradmins.com/delete_fact/<int:fid>', methods=['GET', 'POST'])
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

# ________________________________________________________#

@app.route('/TripOrganizeradmins.com/users_admin')
def users_admin():
    cursor = mysql.connection.cursor()
    query = "SELECT * FROM users"
    cursor.execute(query)
    users = cursor.fetchall()
    return render_template('admin/admin_users.html', users=users)

# Searching of user
@app.route('/TripOrganizeradmins.com/users_admin', methods=['POST', 'GET'])
def search_user():
    if request.method == 'POST':
        search_value = request.form.get('search_value')
        cursor = mysql.connection.cursor()
        query = "SELECT * FROM users WHERE user_id LIKE %s OR email LIKE %s OR username LIKE %s"
        cursor.execute(query, (f'%{search_value}%', f'%{search_value}%', f'%{search_value}%'))
        users = cursor.fetchall()
        return render_template('admin/admin_users.html', users=users)
#Deletion of user

@app.route('/TripOrganizeradmins.com/delete_user/<int:userid>', methods=['GET', 'POST'])
def delete_user(userid):
    cursor = mysql.connection.cursor()
    delete_query = "DELETE FROM users WHERE user_id = %s"
    delete_val = (userid,)
    cursor.execute(delete_query, delete_val)
    mysql.connection.commit()
    status_message = "User Deleted!!"

    # fetching facts 
    cursor = mysql.connection.cursor()
    query = "SELECT * FROM users"
    cursor.execute(query)
    users = cursor.fetchall()

    return render_template('admin/admin_users.html', users = users, dlt_status_message=status_message)


# Provider details
@app.route('/TripOrganizeradmins.com/admin-providers')
def admin_providers():
    cursor = mysql.connection.cursor()
    query = "SELECT * FROM pro_users"
    cursor.execute(query)
    pro_users = cursor.fetchall()
    return render_template('admin/admin_pro_users.html', pro_users = pro_users)

#Deletion of user

@app.route('/TripOrganizeradmins.com/delete_pro_user/<int:prouserid>', methods=['GET', 'POST'])
def delete_pro_user(prouserid):
    cursor = mysql.connection.cursor()
    delete_query = "DELETE FROM pro_users WHERE pro_usersid = %s"
    delete_val = (prouserid,)
    cursor.execute(delete_query, delete_val)
    mysql.connection.commit()
    status_message = "Provider Deleted!!"

    # fetching facts 
    cursor = mysql.connection.cursor()
    query = "SELECT * FROM pro_users"
    cursor.execute(query)
    pro_users = cursor.fetchall()

    return render_template('admin/admin_users.html', pro_users = pro_users, dlt_status_message=status_message)


# Searching of user
@app.route('/TripOrganizeradmins.com/pro_users_admin', methods=['POST', 'GET'])
def search_pro_user():
    if request.method == 'POST':
        search_value = request.form.get('search_value')
        cursor = mysql.connection.cursor()
        query = "SELECT * FROM pro_users WHERE CONCAT(company, email, country, state) LIKE %s"
        cursor.execute(query, (f'%{search_value}%',))
        pro_users = cursor.fetchall()
        return render_template('admin/admin_pro_users.html', pro_users=pro_users)


# ________________________________________________________#

#blogs
@app.route('/TripOrganizeradmins.com/admin-blogs')
def blogs_admin():
    cursor = mysql.connection.cursor()
    query = "SELECT * FROM blog"
    cursor.execute(query)
    blogs = cursor.fetchall()
    return render_template('admin/admin_blog.html', blogs=blogs)

# Deletion of blog
@app.route('/TripOrganizeradmins.com/delete_blog/<int:blog_id>', methods=['GET', 'POST'])
def admin_delete_blog(blog_id):
    cursor = mysql.connection.cursor()
    delete_query = "DELETE FROM blog WHERE blogid = %s"
    delete_val = (blog_id,)
    cursor.execute(delete_query, delete_val)
    mysql.connection.commit()
    status_message = "Blog Deleted!!"

    # Fetching blogs after deletion
    cursor = mysql.connection.cursor()
    query = "SELECT * FROM blog"
    cursor.execute(query)
    blogs = cursor.fetchall()

    return render_template('admin/admin_blog.html', blogs=blogs, dlt_status_message=status_message)

# Searching for blogs
@app.route('/TripOrganizeradmins.com/blogs_admin', methods=['POST', 'GET'])
def search_admin_blog():
    if request.method == 'POST':
        search_value = request.form.get('search_value')
        cursor = mysql.connection.cursor()
        query = "SELECT * FROM blog WHERE heading LIKE %s OR content LIKE %s OR userid LIKE %s OR blogid LIKE %s"
        cursor.execute(query, (f'%{search_value}%', f'%{search_value}%', f'%{search_value}%', f'%{search_value}%'))
        blogs = cursor.fetchall()
        return render_template('admin/admin_blog.html', blogs=blogs)

# details of blogs
@app.route('/TripOrganizeradmins.com/blog-details/<int:blog_id>', methods=['GET', 'POST'])
def admin_blog_details(blog_id):
    cursor = mysql.connection.cursor()
    query = "SELECT * FROM blog_comment WHERE blogid = %s"
    cursor.execute(query, (blog_id,))
    blog_comments = cursor.fetchall()

    cursor = mysql.connection.cursor()
    query = "SELECT * FROM blog_images WHERE blog_id = %s"
    cursor.execute(query, (blog_id,))
    blog_images = cursor.fetchall()

    return render_template('admin/blog_details.html', blog_images=blog_images, blog_comments=blog_comments, blog_id=blog_id)
   
# Deletion of blog images
@app.route('/TripOrganizeradmins.com/delete_blog_images/<int:image_id>', methods=['GET', 'POST'])
def admin_delete_blog_images(image_id):
    cursor = mysql.connection.cursor()
    delete_query = "DELETE FROM blog_images WHERE blog_image_id = %s"
    delete_val = (image_id,)
    cursor.execute(delete_query, delete_val)
    mysql.connection.commit()
    status_message = "Blog Image Deleted!!"

    # Fetching blogs after deletion

    cursor = mysql.connection.cursor()
    query = "SELECT * FROM blog"
    cursor.execute(query)
    blogs = cursor.fetchall()

    return render_template('admin/admin_blog.html', blogs=blogs, dlt_status_message=status_message)

# Deletion of blog comment
@app.route('/TripOrganizeradmins.com/delete_blog_comment/<int:comment_id>', methods=['GET', 'POST'])
def admin_delete_blog_comment(comment_id):
    cursor = mysql.connection.cursor()
    delete_query = "DELETE FROM blog_comment WHERE commentid = %s"
    delete_val = (comment_id,)
    cursor.execute(delete_query, delete_val)
    mysql.connection.commit()
    status_message = "Blog Comment Deleted!!"

    # Fetching blog  after deletion
    cursor = mysql.connection.cursor()
    query = "SELECT * FROM blog"
    cursor.execute(query)
    blogs = cursor.fetchall()
    return render_template('admin/admin_blog.html', blogs=blogs, dlt_status_message=status_message)


@app.route('/TripOrganizeradmins.com/search-blogs-comments-admin', methods=['POST', 'GET'])
def search_admin_blog_comment():
    if request.method == 'POST':
        search_value = request.form.get('search_value')
        blog_id = request.form.get('blog_id')
        cursor = mysql.connection.cursor()
        query = "SELECT * FROM blog_comment WHERE (comment LIKE %s OR userid LIKE %s OR blogid LIKE %s) AND blogid = %s"
        cursor.execute(query, (f'%{search_value}%', f'%{search_value}%', f'%{search_value}%', blog_id))
        blog_comments = cursor.fetchall()
        return render_template('admin/blog_details.html', blog_comments=blog_comments,blog_id=blog_id)

# ________________________________________________________#

#Packages
@app.route('/TripOrganizeradmins.com/packages_admin')
def packages_admin():
    cursor = mysql.connection.cursor()
    query = "SELECT * FROM tour_packages"
    cursor.execute(query)
    packages = cursor.fetchall()
    return render_template('admin/admin_packages.html',packages=packages)

# Details of Packages
@app.route('/TripOrganizeradmins.com/packages-details/<int:package_id>', methods=['GET', 'POST'])
def admin_package_details(package_id):
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
    cursor.execute(query1, (package_id,))
    tour_packages_data = cursor.fetchall()

    # SELECTING TOUR PACKAGE
    query2 = "SELECT * FROM package_day_programme WHERE package_id = %s"
    # Execute the query and retrieve the data
    cursor = mysql.connection.cursor()
    cursor.execute(query2, (package_id,))
    tour_packages_day = cursor.fetchall()

    # SELECTING TOUR PACKAGE IMAGES
    query3 = "SELECT * FROM package_images WHERE package_id = %s"
    # Execute the query and retrieve the data
    cursor = mysql.connection.cursor()
    cursor.execute(query3, (package_id,))
    tour_packages_image = cursor.fetchall()

    #selecting reviews to display
    review_select = """SELECT pr.*, u.username, u.profile_pic
            FROM package_reviews pr
            JOIN users u ON pr.user_id = u.user_id
            WHERE pr.package_id = %s;
    """
    cursor.execute(review_select, (package_id,))
    package_reviews = cursor.fetchall()

    return render_template('admin/admin_packages_details.html', tour_packages_data=tour_packages_data,
            tour_packages_day=tour_packages_day, tour_packages_image=tour_packages_image, package_reviews=package_reviews, package_id=package_id)
 
# Search packages
@app.route('/TripOrganizeradmins.com/packages_admin', methods=['POST', 'GET'])
def search_admin_packages():
    if request.method == 'POST':
        search_value = request.form.get('search_value')
        cursor = mysql.connection.cursor()
        query = "SELECT * FROM tour_packages WHERE tourname LIKE %s OR description LIKE %s OR package_id LIKE %s"
        cursor.execute(query, (f'%{search_value}%', f'%{search_value}%', f'%{search_value}%'))
        packages = cursor.fetchall()
        return render_template('admin/admin_packages.html', packages=packages)

# Deletion of package image
@app.route('/TripOrganizeradmins.com/delete_package_image/<int:image_id>/<int:package_id>', methods=['GET', 'POST'])
def admin_delete_package_image(image_id, package_id):
    cursor = mysql.connection.cursor()
    delete_query = "DELETE FROM package_images WHERE package_image_id = %s"
    delete_val = (image_id,)
    cursor.execute(delete_query, delete_val)
    mysql.connection.commit()
    status_message = "Package Image Deleted!!"

    return redirect(url_for('admin_package_details', package_id=package_id))

# Deletion of package review
@app.route('/TripOrganizeradmins.com/delete_package_review/<int:review_id>/<int:package_id>', methods=['GET', 'POST'])
def admin_delete_package_review(review_id, package_id):
    cursor = mysql.connection.cursor()
    delete_query = "DELETE FROM package_review WHERE review_id = %s"
    delete_val = (review_id,)
    cursor.execute(delete_query, delete_val)
    mysql.connection.commit()
    status_message = "Package Review Deleted!!"

    return redirect(url_for('admin_package_details', package_id=package_id))

@app.route('/TripOrganizeradmins.com/search-package-review-admin', methods=['POST', 'GET'])
def search_admin_package_review():
    if request.method == 'POST':
        search_value = request.form.get('search_value')
        package_id = request.form.get('package_id')
        cursor = mysql.connection.cursor()
        query = "SELECT * FROM package_reviews WHERE (review LIKE %s OR user_id LIKE %s) AND package_id = %s"
        cursor.execute(query, (f'%{search_value}%', f'%{search_value}%', package_id))
        package_reviews = cursor.fetchall()
        return render_template('admin/admin_packages_details.html', package_reviews=package_reviews,package_id=package_id)

@app.route('/TripOrganizeradmins.com/remove-package-admin/<int:package_id>', methods=['POST', 'GET'])
def admin_remove_package(package_id):
    cursor = mysql.connection.cursor()
    query = """
        DELETE FROM tour_packages
        WHERE package_id = %s;
    """
    cursor.execute(query, (package_id,))
    mysql.connection.commit()

    # delete package from images

    query = """
        DELETE FROM package_images
        WHERE package_id = %s;
    """
    cursor.execute(query, (package_id,))
    mysql.connection.commit()

    # delete package from reviews

    query = """
        DELETE FROM package_reviews
        WHERE package_id = %s;
    """
    cursor.execute(query, (package_id,))
    mysql.connection.commit()

    # delete package from bookings

    query = """
        DELETE FROM package_bookings
        WHERE package_id = %s;
    """
    cursor.execute(query, (package_id,))
    mysql.connection.commit()

    # delete package from day prgrammes

    query = """
        DELETE FROM package_day_programme
        WHERE package_id = %s;
    """
    cursor.execute(query, (package_id,))
    mysql.connection.commit()

    # Delete package from saved packages

    query = """
        DELETE FROM saved_packages
        WHERE package_id = %s;
    """
    cursor.execute(query, (package_id,))
    mysql.connection.commit()

    dlt_status_message = "Package deleted"
    query = "SELECT * FROM tour_packages"
    cursor.execute(query)
    packages = cursor.fetchall()
    return render_template('admin/admin_packages.html',packages=packages, dlt_status_message=dlt_status_message)

# ________________________________________________________#

@app.route('/TripOrganizeradmins.com/bookings_admin')
def bookings_admin():
    cursor = mysql.connection.cursor()
    query = "SELECT * FROM package_bookings"
    cursor.execute(query)
    bookings = cursor.fetchall()
    return render_template('admin/admin_bookings.html', bookings=bookings)

@app.route('/TripOrganizeradmins.com/bookings_admin-details/<int:booking_id>/<int:package_id>')
def admin_booking_details(booking_id, package_id):
    cursor = mysql.connection.cursor()
    query = "SELECT * FROM package_booked_travalers WHERE booking_id = %s"
    cursor.execute(query, (booking_id,))
    booking_details = cursor.fetchall()

    # selecting package_details

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
    cursor.execute(query1, (package_id,))
    tour_packages_data = cursor.fetchall()

    # SELECTING TOUR PACKAGE
    query2 = "SELECT * FROM package_day_programme WHERE package_id = %s"
    # Execute the query and retrieve the data
    cursor = mysql.connection.cursor()
    cursor.execute(query2, (package_id,))
    tour_packages_day = cursor.fetchall()

    # SELECTING TOUR PACKAGE IMAGES
    query3 = "SELECT * FROM package_images WHERE package_id = %s"
    # Execute the query and retrieve the data
    cursor = mysql.connection.cursor()
    cursor.execute(query3, (package_id,))
    tour_packages_image = cursor.fetchall()

    return render_template('admin/admin_booking_details.html', tour_packages_image=tour_packages_image, booking_details=booking_details
        , tour_packages_day=tour_packages_day, tour_packages_data=tour_packages_data)

    
# Canceling the tour package by user
@app.route('/TripOrganizeradmins.com/admin-user-booking-cancel/<booking_id>/<package_name>/<provider_id>', methods=['POST', 'GET'])
def admin_booking_cancel(booking_id, package_name, provider_id):
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
            dlt_status_message = "Booking Cancelled..!!"
        cursor = mysql.connection.cursor()
        query = "SELECT * FROM package_bookings"
        cursor.execute(query)
        bookings = cursor.fetchall()
        

    except Exception as e:
        print(f"Error: {e}")
        flash_message = "Something went wrong."
    return render_template('admin/admin_bookings.html', bookings=bookings, error_message="")



# Search bookings
@app.route('/TripOrganizeradmins.com/bookings_admin', methods=['POST', 'GET'])
def search_admin_bookings():
    if request.method == 'POST':
        search_value = request.form.get('search_value')
        cursor = mysql.connection.cursor()
        query = "SELECT * FROM package_bookings WHERE booked_id LIKE %s OR package_id LIKE %s OR package_provider_id LIKE %s"
        cursor.execute(query, (f'%{search_value}%', f'%{search_value}%', f'%{search_value}%'))
        bookings = cursor.fetchall()
        return render_template('admin/admin_bookings.html', bookings=bookings)
     