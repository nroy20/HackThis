import json
import os
import requests
import geopy
from flask import Flask, render_template, request, jsonify, abort, session, redirect, url_for
from flask_cors import CORS
from functools import wraps
from models import Student, Business, setup_db
#from geopy.geocoders import GoogleV3
from os import environ as env
from werkzeug.exceptions import HTTPException
from dotenv import load_dotenv, find_dotenv
from authlib.integrations.flask_client import OAuth
from six.moves.urllib.parse import urlencode
#from uszipcode import SearchEngine


def get_student_id_from_auth_id():
    profile = session['profile']
    user_id = profile['user_id']
    if not user_id:
        abort(403)
    student = Student.query.filter_by(auth_id=user_id).one_or_none()
    if not student:
        abort(404)
    return student.id

def get_business_id_from_auth_id():
    business_profile = session['business_profile']
    user_id = business_profile['user_id']
    if not user_id:
        abort(403)
    business = Business.query.filter_by(auth_id=user_id).one_or_none()
    if not business:
        abort(404)
    return business.id

def create_app(test_config=None):
    app = Flask(__name__, static_folder="templates/stylesheets")
    setup_db(app)
    oauth = OAuth(app)
    app.secret_key = "temp key"

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization, true')
        response.headers.add('Access-Control-Allow-Methods', 'GET, POST, DELETE, PATCH')
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        return response

    auth0 = oauth.register(
        'auth0',
        client_id='yzDykpaQCAi0qMfaYnbD3pwH6nQiRgSs',
        client_secret='T5ggzfkhmQMFIDj2TeHnpu75Gqn8n2UEcABKIRImMkq0N8czZ0SYFO7jYbIiTPC-',
        api_base_url='https://hackthistest.us.auth0.com',
        access_token_url='https://hackthistest.us.auth0.com/oauth/token',
        authorize_url='https://hackthistest.us.auth0.com/authorize',
        client_kwargs={
            'scope': 'openid profile email',
        },
    )

    
    @app.route('/login')
    def login():
        return auth0.authorize_redirect(redirect_uri='https://community-cafe.herokuapp.com/login-results')

    @app.route('/signup')
    def signup():
        return auth0.authorize_redirect(redirect_uri='https://community-cafe.herokuapp.com/signup-results')

    @app.route('/login_business')
    def business_login():
        return auth0.authorize_redirect(redirect_uri='https://community-cafe.herokuapp.com/login-results-business')

    @app.route('/signup_business')
    def business_signup():
        return auth0.authorize_redirect(redirect_uri='https://community-cafe.herokuapp.com/signup-results-business')

    @app.route('/login-results')
    def login_handling():
        # Handles response from token endpoint
        auth0.authorize_access_token()
        resp = auth0.get('userinfo')
        userinfo = resp.json()

        # Store the user information in flask session.
        session['jwt_payload'] = userinfo
        session['profile'] = {
            'user_id': userinfo['sub'],
            'name': userinfo['name'],
            'picture': userinfo['picture']
        }
        return redirect('/dashboard/display')

    @app.route('/signup-results')
    def signup_handling():
        # Handles response from token endpoint
        auth0.authorize_access_token()
        resp = auth0.get('userinfo')
        userinfo = resp.json()

        # Store the user information in flask session.
        session['jwt_payload'] = userinfo
        session['profile'] = {
            'user_id': userinfo['sub'],
            'name': userinfo['name'],
            'picture': userinfo['picture']
        }
        return redirect('/profile/student/create')

    @app.route('/login-results-business')
    def business_login_handling():
        # Handles response from token endpoint
        auth0.authorize_access_token()
        resp = auth0.get('userinfo')
        userinfo = resp.json()

        # Store the user information in flask session.
        session['jwt_payload'] = userinfo
        session['business_profile'] = {
            'user_id': userinfo['sub'],
            'name': userinfo['name'],
            'picture': userinfo['picture']
        }
        return redirect('/profile/business/display')

    @app.route('/signup-results-business')
    def business_signup_handling():
        # Handles response from token endpoint
        auth0.authorize_access_token()
        resp = auth0.get('userinfo')
        userinfo = resp.json()

        # Store the user information in flask session.
        session['business_jwt_payload'] = userinfo
        session['business_profile'] = {
            'user_id': userinfo['sub'],
            'name': userinfo['name'],
            'picture': userinfo['picture']
        }
        return redirect('/profile/business/create')


    def requires_auth(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if 'profile' not in session:
            # Redirect to Login page here
                return redirect('/login')
            return f(*args, **kwargs)

        return decorated

    def requires_business_auth(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if 'business_profile' not in session:
            # Redirect to Login page here
                return redirect('/login_business')
            return f(*args, **kwargs)

        return decorated

    @app.route('/logout')
    def logout():
        # Clear session stored data
        session.clear()
        # Redirect user to logout endpoint
        params = {'returnTo': url_for('index', _external=True), 'client_id': 'yzDykpaQCAi0qMfaYnbD3pwH6nQiRgSs'}
        return redirect(auth0.api_base_url + '/v2/logout?' + urlencode(params))
    #______________________________student endpoints___________________________________

    @app.route('/dashboard/display', methods=['GET'])
    @requires_auth
    def display_student_dashboard():
        student_id = get_student_id_from_auth_id()
        student = Student.query.get(student_id)
        student_name = student.name
        return render_template('student_dashboard.html', student_id=student_id, student_name=student_name)
    @app.route('/dashboard', methods=['GET'])
    @requires_auth
    def get_student_dashboard():
        student_id = get_student_id_from_auth_id()
        if student_id == 0:
            abort(400)

        student = Student.query.get(student_id)
        if not student:
            abort(404)

        student_zip_code = student.zip_code

        recommended_businesses = Business.query.filter_by(zip_code=student_zip_code).all()
        if not recommended_businesses:
            abort(404)

        data = []
        for business in recommended_businesses:
            data.append(business.name)
        '''
        student_zip_code = student.zip_code
        search = SearchEngine(simple_zipcode=True)
        zipcode = search.by_zipcode(student_zip_code)
        zipcode_json = zipcode.to_json()
        student_lat = zipcode_json["lat"]
        student_long = zipcode_json["long"]

        all_businesses = Business.query.filter(Business.address != None).all()
        businesses_in_zip_code = []
        #geolocator = geocode.GoogleV3(api_key='APIKEY')

        for business in all_businesses:
            if (business.zip_code == student.zip_code):
                #location = geolocator.geocode(business.address, timeout=15)
                #g = geocoder.google(business.address)
                #businesses_in_zip_code.append({
                    'id': business.id,
                    'name': business.name,
                    'latitude': g.latlng[0],
                    'longitude': g.latlng[1]
                })
        '''
        return jsonify({
            'success': True,
            'id': student_id,
            'name': student.name,
            'business_names': student.business_names,
            'recommended_count': len(recommended_businesses),
            'recommended': data
            #'student_lat': student_lat,
            #'student_long': student_long, 
            #'businesses_in_zip_code': businesses_in_zip_code
        }), 200
    
    @app.route('/profile/student/create', methods=['GET', 'POST'])
    @requires_auth
    def create_student_profile():
        if request.method == 'GET':
            return render_template('new_student_form.html', userinfo=session['profile'])

        body = request.get_json()
        try:
            name = body.get('name')
            email = body.get('email')
            zip_code = body.get('zip_code')
            interests = body.get('interests')
            qualifications = body.get('qualifications')
            auth_id = body.get('auth_id')

            student = Student(
                name=name,
                email=email,
                zip_code=zip_code,
                interests=interests,
                qualifications=qualifications,
                auth_id=auth_id
            )

            if not student:
                abort(404)

            student.insert()

            return jsonify({
                'success': True,
                'name': student.name,
                'email': student.email,
                'zip_code': student.zip_code,
                'interests': student.interests,
                'qualifications': student.qualifications,
                'auth_id': student.auth_id
            }), 200
        except:
            abort(422)
    @app.route('/profile/student/display', methods=['GET'])
    @requires_auth
    def display_student_profile():
        student_id = get_student_id_from_auth_id()
        return render_template('my_profile.html', student_id=student_id)
    @app.route('/profile/student', methods=['GET'])
    @requires_auth
    def get_student_profile():
        student_id = get_student_id_from_auth_id()
        if student_id == 0:
            abort(400)

        student = Student.query.get(student_id)
        if not student:
            abort(404)

        return jsonify({
            'success': True,
            'id': student_id,
            'name': student.name,
            'email': student.email,
            'zip_code': student.zip_code,
            'interests': student.interests,
            'qualifications': student.qualifications,
            'business_names': student.business_names
        }), 200
    @app.route('/profile/student/edit', methods=['GET', 'PATCH'])
    @requires_auth
    def update_student_profile():
        student_id = get_student_id_from_auth_id()
        if request.method == 'GET':
            return render_template('update_student_form.html', student_id=student_id)

        if student_id == 0:
            abort(400)

        student = Student.query.get(student_id)

        if not student:
            abort(404)

        body = request.get_json()

        try:
            name = body.get('name')
            email = body.get('email')
            zip_code = body.get('zip_code')
            interests = body.get('interests')
            qualifications = body.get('qualifications')

            if name:
                student.name = name
            if email:
                student.email = email
            if zip_code:
                student.zip_code = zip_code
            if interests:
                student_interests = interests
            if qualifications:
                student.qualifications = qualifications

            if not student:
                abort(404)

            student.update()

            return jsonify({
                'success': True,
                'name': student.name,
                'email': student.email,
                'zip_code': student.zip_code,
                'interests': student.interests,
                'qualifications': student.qualifications
            }), 200
        except:
            abort(422)
        
    @app.route('/profile/student', methods=['DELETE'])
    @requires_auth
    def delete_student_profile():
        student_id = get_student_id_from_auth_id()
        if student_id == 0:
            abort(400)

        student = Student.query.get(student_id)
        if not student:
            abort(404)

        student.delete()

        return jsonify({
            'success': True,
            'id': student_id
        }), 200

    @app.route('/student/search', methods=['GET','POST'])
    @requires_auth
    def search_businesses():
        if request.method == 'GET':
            return render_template("search.html")

        body = request.get_json()
        search_term = body.get('search_term')
        
        businesses = Business.query.filter(Business.name.ilike('%{}%'.format(search_term))).all()
        
        if len(businesses) == 0:
            abort(404)

        data=[]
        for business in businesses:
            data.append({
                "id": business.id,
                "name": business.name,
                "skills": business.skills
            })

        return jsonify({
            'success': True,
            'count': len(businesses),
            'data': data
        })

    @app.route('/profile/business/<int:business_id>/display', methods=['GET'])
    @requires_auth
    def display_business_profile_student_view(business_id):
        return render_template('business_profile_student_view.html', business_id=business_id)
    @app.route('/profile/business/<int:business_id>', methods=['GET'])
    @requires_auth
    def get_business_profile_student_view(business_id):
        if business_id == 0:
            abort(400)

        business = Business.query.get(business_id)
        if not business:
            abort(404)

        return jsonify({
            'success': True,
            'id': business.id,
            'name': business.name,
            'email': business.email,
            'zip_code': business.zip_code,
            'goals': business.goals,
            'website': business.website,
            'address': business.address,
            'description': business.description,
            'skills': business.skills
        }), 200
        
    @app.route('/student/login', methods=['GET'])
    def login_buttons():
        return render_template('student_login.html')


    #for testing purposes
    '''
    @app.route('/listallstudents', methods=['GET'])
    def listemall():
        students = Student.query.all()
        data = []
        for student in students:
            data.append({
                "id": student.id
            })
        return jsonify({
            'success': True,
            'data': data
        })
    '''
    #_____________________________business endpoints__________________________________

    @app.route('/profile/business/create', methods=['GET','POST'])
    @requires_business_auth
    def create_business_profile():
        if request.method == 'GET':
            return render_template('new_business_form.html', userinfo=session['business_profile'])

        body = request.get_json()
        try:
            name = body.get('name')
            email = body.get('email')
            zip_code = body.get('zip_code')
            goals = body.get('goals')
            website = body.get('website')
            address = body.get('address')
            description = body.get('description')
            skills = body.get('skills'),
            auth_id = body.get('auth_id')

            business = Business(
                name=name,
                email=email,
                zip_code=zip_code,
                goals=goals,
                website=website,
                address=address,
                description=description,
                skills=skills,
                auth_id=auth_id
            )

            if not business:
                abort(404)

            business.insert()

            return jsonify({
                'success': True,
                'name': business.name,
                'email': business.email,
                'zip_code': business.zip_code,
                'goals': business.goals,
                'website': business.website,
                'address': business.address,
                'description': business.description,
                'skills': business.skills,
                'auth_id': business.auth_id
            }), 200
        except:
            abort(422)
    @app.route('/profile/business/display', methods=['GET'])
    @requires_business_auth
    def display_business_profile():
        business_id = get_business_id_from_auth_id()
        return render_template('business_profile_business_view.html', business_id=business_id)
    @app.route('/profile/business', methods=['GET'])
    @requires_business_auth
    def get_business_profile():
        business_id = get_business_id_from_auth_id()
        if business_id == 0:
            abort(400)

        business = Business.query.get(business_id)
        if not business:
            abort(404)

        return jsonify({
            'success': True,
            'id': business.id,
            'name': business.name,
            'email': business.email,
            'zip_code': business.zip_code,
            'goals': business.goals,
            'website': business.website,
            'address': business.address,
            'description': business.description,
            'skills': business.skills
        }), 200

    @app.route('/profile/business/edit', methods=['GET','PATCH'])
    @requires_business_auth
    def update_business_profile():
        business_id = get_business_id_from_auth_id()
        if request.method == 'GET':
            return render_template('update_business_form.html', business_id=business_id)

        if business_id == 0:
            abort(400)

        business = Business.query.get(business_id)

        if not business:
            abort(404)

        body = request.get_json()

        try:
            name = body.get('name')
            email = body.get('email')
            zip_code = body.get('zip_code')
            goals = body.get('goals')
            website = body.get('website')
            address = body.get('address')
            description = body.get('description')
            skills = body.get('skills')

            if name:
                business.name = name
            if email:
                business.email = email
            if zip_code:
                business.zip_code = zip_code
            if goals:
                business.goals = goals
            if website:
                business.website = website
            if address:
                business.address = address
            if description:
                business.description = description
            if skills:
                business.skills = skills

            if not business:
                abort(404)

            business.update()

            return jsonify({
                'success': True,
                'id': business.id,
                'name': business.name,
                'email': business.email,
                'zip_code': business.zip_code,
                'goals': business.goals,
                'website': business.website,
                'address': business.address,
                'description': business.description,
                'skills': business.skills
            }), 200
        except:
            abort(422)
        
    @app.route('/profile/business', methods=['DELETE'])
    @requires_business_auth
    def delete_business_profile():
        business_id = get_business_id_from_auth_id()
        if business_id == 0:
            abort(400)

        business = Business.query.get(business_id)
        if not business:
            abort(404)

        business.delete()

        return jsonify({
            'success': True,
            'id': business_id
        }), 200

    @app.route('/business/search', methods=['GET','POST'])
    @requires_business_auth
    def search_students():
        if request.method == 'GET':
            return render_template('search_business.html')

        body = request.get_json()
        search_term = body.get('search_term')

        students = Student.query.filter(Student.name.ilike('%{}%'.format(search_term))).all()
        
        if len(students) == 0:
            abort(404)

        data=[]
        for student in students:
            data.append({
                "id": student.id,
                "name": student.name,
                "interests": student.interests
            })

        return jsonify({
            'success': True,
            'count': len(students),
            'data': data
        })
    @app.route('/profile/student/<int:student_id>/display', methods=['GET'])
    @requires_business_auth
    def display_student_profile_business_view(student_id):
        return render_template('student_profile_business_view.html', student_id=student_id)
    @app.route('/profile/student/<int:student_id>', methods=['GET'])
    @requires_business_auth
    def get_student_profile_business_view(student_id):
        if student_id == 0:
            abort(400)

        student = Student.query.get(student_id)
        if not student:
            abort(404)

        return jsonify({
            'success': True,
            'id': student_id,
            'name': student.name,
            'email': student.email,
            'zip_code': student.zip_code,
            'interests': student.interests,
            'qualifications': student.qualifications
        }), 200

    @app.route('/business/login', methods=['GET'])
    def business_login_buttons():
        return render_template('business_login.html')

    #___________________________endpoints for everyone!________________________________

    @app.route('/')
    def index():
        return render_template('home.html'), 200
        
    #_______________________________error handlers____________________________________

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
                        "success": False, 
                        "error": 422,
                        "message": "unprocessable"
                        }), 422

    @app.errorhandler(404)
    def resource_not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "resource not found - PLEASE REFRESH PAGE"
        }), 404

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "bad request"
        }), 400

    @app.errorhandler(403)
    def bad_login(error):
        return jsonify({
            "success": False,
            "error": 403,
            "message": "bad login"
        }), 403

        

    return app

app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)



