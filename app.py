from flask import Flask, render_template, request, jsonify, abort, session
from flask_cors import CORS
from functools import wraps
from models import Student, Business, setup_db
import json
import os
import requests

def create_app(test_config=None):
    app = Flask(__name__)
    setup_db(app)
    app.secret_key = "temp key"

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization, true')
        response.headers.add('Access-Control-Allow-Methods', 'GET, POST, DELETE, PATCH')
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        return response

    #______________________________student endpoints___________________________________

    @app.route('/dashboard/student/<int:student_id>/display', methods=['GET'])
    def display_student_dashboard(student_id):
        return render_template('student_dashboard.html')
    @app.route('/dashboard/student/<int:student_id>', methods=['GET'])
    def get_student_dashboard(student_id):
        if student_id == 0:
            abort(400)

        student = Student.query.get(student_id)
        if not student:
            abort(404)

        return jsonify({
            'success': True,
            'id': student_id,
            'name': student.name,
            'zip_code': student.zip_code
        }), 200

    @app.route('/profile/student/create', methods=['GET', 'POST'])
    def create_student_profile():
        if request.method == 'GET':
            return render_template('new_student_form.html')

        body = request.get_json()
        try:
            name = body.get('name')
            email = body.get('email')
            zip_code = body.get('zip_code')
            interests = body.get('interests')
            qualifications = body.get('qualifications')

            student = Student(
                name=name,
                email=email,
                zip_code=zip_code,
                interests=interests,
                qualifications=qualifications
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
                'qualifications': student.qualifications
            }), 200
        except:
            abort(422)
    @app.route('/profile/student/<int:student_id>/display', methods=['GET'])
    def display_student_profile(student_id):
        return render_template('my_profile.html')
    @app.route('/profile/student/<int:student_id>', methods=['GET'])
    def get_student_profile(student_id):
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

    @app.route('/profile/student/<int:student_id>/edit', methods=['GET', 'PATCH'])
    def update_student_profile(student_id):
        if request.method == 'GET':
            return render_template('update_student_form.html')

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
        
    @app.route('/profile/student/<int:student_id>', methods=['GET', 'DELETE'])
    def delete_student_profile(student_id):
        if request.method == 'GET':
            return render_template('home.html')
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
        
    #_____________________________business endpoints__________________________________

    @app.route('/profile/business/create', methods=['GET','POST'])
    def create_business_profile():
        if request.method == 'GET':
            return render_template('new_business_form.html')

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

            business = Business(
                name=name,
                email=email,
                zip_code=zip_code,
                goals=goals,
                website=website,
                address=address,
                description=description,
                skills=skills
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
                'skills': business.skills
            }), 200
        except:
            abort(422)
    @app.route('/profile/business/<int:business_id>/display', methods=['GET'])
    def display_business_profile(business_id):
        return render_template('business_profile_business_view.html')
    @app.route('/profile/business/<int:business_id>', methods=['GET'])
    def get_business_profile():
        if business_id == 0:
            abort(400)

        business = Business.query.get(business_id)
        if not business:
            abort(404)

        return jsonify({
            'success': True,
            'id': business,
            'name': business.name,
            'email': business.email,
            'zip_code': business.zip_code,
            'goals': business.goals,
            'website': business.website,
            'address': business.address,
            'description': business.description,
            'skills': business.skills
        }), 200

    @app.route('/profile/business/<int:business_id>', methods=['GET','PATCH'])
    def update_business_profile(business_id):
        if request.method == 'GET':
            return render_template('update_business_form.html')

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
                business.interests= interests
            if website:
                business.qualifications = qualifications
            if address:
                business.address = address
            if description:
                business.description = description
            if skills:
                business.skills = skills

            if not student:
                abort(404)

            student.update()

            return jsonify({
                'success': True,
                'id': business,
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
        
    @app.route('/profile/business/<int:business_id>', methods=['DELETE'])
    def delete_business_profile(business_id):
        if request.method == 'GET':
            return render_template('home.html')
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
    def search_students():
        if request.method == 'GET':
            return render_template('search.html')
        search_term = request.form.get('search_term')
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
            "message": "resource not found"
        }), 404

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "bad request"
        }), 400
    '''
    @app.errorhandler(AuthError)
    def error_auth(ex):
        response = jsonify(ex.error)
        response.status_code = ex.status_code
        return response
    '''

    return app

app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)



