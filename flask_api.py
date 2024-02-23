from flask import Flask, request
from flask_restful import Api, Resource
import cv2
from backend.section_process import ImageProcessor
from backend.process import PillarDetector
from backend.occlusion_process import OcclusionModel
import os 
from pathlib import Path
import sqlite3


app = Flask(__name__)
api = Api(app)


class SectionProcessing(Resource):
    def post(self):
        try:
            # Get the image path from the request JSON
            data = request.get_json()
            image_path = data.get('image_path')
            if not image_path:
                return {'message': 'No image path provided'}, 400

            # Check if the image path has the correct format and naming template
            image_filename = os.path.basename(image_path)
            if not image_filename.endswith(".tif"):
                return {'message': 'Invalid image path. Image filename should start with "Specimen_" and have a .tif extension'}, 400

            # Process the image
            model_section_path = os.path.join('models', 'section.onnx')
            image_processor = ImageProcessor(model_section_path)

            specimen_name = image_filename.split('.')[0]  # Using the filename directly since we've already validated it
            image, crops = image_processor.get_sections(image_path, specimen_name)

            # Perform any further processing or return the results as needed

            return {'message': 'Image processed successfully','specimen_name':specimen_name, 'sections_image_path': crops}, 200
        except Exception as e:
            import traceback
            traceback.print_exc()
            return {'message': f'Error processing image: {str(e)}'}, 500

class CountProcessing(Resource):
    def post(self):
        try:
            data = request.get_json()
            occlusion_model_path = os.path.join('models', 'occlusion.onnx')
            pillar_filter_path = os.path.join('models', 'pillar_filter.onnx')
            result = {}
    
            specimen_name = data['specimen_name']
        

            sections_image_path = data['sections_image_path']  

            occlusion_model = OcclusionModel(occlusion_model_path)
            process_pillar = PillarDetector(pillar_filter_path)

            for sec_id, section_path in enumerate(sections_image_path):
                section_image = cv2.imread(section_path, cv2.IMREAD_GRAYSCALE)
                section_image_copy = sections_image_path.copy()
                patch = process_pillar.process_cont(section_image, sec_id, specimen_name)

                # Detect pillars in the section
                image, pillar_count, all_points, plotted_image_path = process_pillar.detect_pillars(section_image, patch, sec_id,
                                                                                specimen_name)

                # Find occlusions in the section
                num_negative, num_positive = occlusion_model.occlusion_finder(all_points, section_image, sec_id,
                                                                              specimen_name)

                print(f'Section{4 - sec_id}: Number_of_pillars: {pillar_count}, Occlusion_count: {num_positive}')

                result[f'Section{4 - sec_id}'] = {'Number_of_pillars': pillar_count, 
                                                  'Occlusion_count': num_positive,
                                                  'Unindentified': 0,
                                                  'Non_occlusion':0 ,
                                                  'Plotted_path':plotted_image_path}
                
            result['Total_occlusion_count'] = 0
            result['Occlusion_index'] = 0

            return result , 200

        except Exception as e:
            import traceback
            traceback.print_exc()
            return {'message': f'Error processing image: {str(e)}'}, 500
        



# Function to create a new database connection
def get_db():
    # Check if the database file exists
    if not os.path.exists('database.db'):
        # If the database file doesn't exist, create it
        conn = sqlite3.connect('database.db')
        # Create the users table
        conn.execute('''
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        ''')
        conn.commit()
        conn.close()

    return sqlite3.connect('database.db')

class Login(Resource):
    def post(self):
        try:
            # Get username and password from request JSON
            data = request.get_json()
            username = data.get('username')
            password = data.get('password')

            # Create a new database connection and cursor within the current thread
            with get_db() as conn:
                cur = conn.cursor()

                # Query the database to check if the user exists
                cur.execute("SELECT * FROM users WHERE username = ?", (username,))
                user = cur.fetchone()

                if user:
                    # Check if the provided password matches the password in the database
                    if password == user[2]:  # Assuming password is stored in the third column
                        return {'message': 'Login successful'}, 200
                    else:
                        return {'message': 'Invalid username or password'}, 401
                else:
                    return {'message': 'User does not exist. Please create a new user.'}, 404
        except Exception as e:
            return {'message': f'Error logging in: {str(e)}'}, 500

class CreateUser(Resource):
    def post(self):
        try:
            # Get username and password from request JSON
            data = request.get_json()
            username = data.get('username')
            password = data.get('password')

            # Create a new database connection and cursor within the current thread
            with get_db() as conn:
                cur = conn.cursor()

                # Check if the username already exists in the database
                cur.execute("SELECT * FROM users WHERE username = ?", (username,))
                existing_user = cur.fetchone()

                if existing_user:
                    return {'message': 'Username already exists. Please choose a different username.'}, 400
                else:
                    # Insert the new user into the database
                    cur.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
                    conn.commit()
                    return {'message': 'User created successfully'}, 201
        except Exception as e:
            return {'message': f'Error creating user: {str(e)}'}, 500

# Add the Login and CreateUser resources to the API
api.add_resource(Login, '/login')
api.add_resource(CreateUser, '/create_user')

# Define the API endpoint
api.add_resource(SectionProcessing, '/process_image')
api.add_resource(CountProcessing,'/process_analysis')

if __name__ == '__main__':
    app.run(debug=True,port=5001)  # Set debug to False in production
