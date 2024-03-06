from flask import Flask, request
from flask_restful import Api, Resource
import cv2
from backend.section_process import ImageProcessor
from backend.process import PillarDetector
from backend.occlusion_process import OcclusionModel
import os 
from pathlib import Path
import sqlite3
import json 
from datetime import datetime

# datetime object containing current date and time
now = datetime.now()

app = Flask(__name__)
api = Api(app)

def update_json_file(filename, key, new_dict):
    try:
        with open(filename, 'r') as file:
            data = json.load(file)
    except FileNotFoundError:
        data = {}
        
    if key in data:
        if isinstance(data[key], list):
            data[key].append(new_dict)
        else:
            data[key] = [data[key], new_dict]
    else:
        data[key] = new_dict

    with open(filename, 'w') as file:
        json.dump(data, file, indent=4)

class SectionProcessing(Resource):
    def post(self):
        try:
            data = request.get_json()
            image_path = data.get('image_path')
            if not image_path:
                return {'message': 'No image path provided'}, 400

            image_filename = os.path.basename(image_path)
            if not image_filename.endswith(".tif"):
                return {'message': 'Invalid image path. Image filename should start with "Specimen_" and have a .tif extension'}, 400

            model_section_path = os.path.join(os.getcwd(),'models', 'section.onnx')
            image_processor = ImageProcessor(model_section_path)

            specimen_name = image_filename.split('.')[0]
            image, crops = image_processor.get_sections(image_path, specimen_name)

            return {'message': 'Image processed successfully','specimen_name':specimen_name, 'sections_image_path': crops}, 200
        except Exception as e:
            import traceback
            traceback.print_exc()
            return {'message': f'Error processing image: {str(e)}'}, 500

class CountProcessing(Resource):
    def post(self):
        try:        
            data = request.get_json()
            occlusion_model_path = os.path.join(os.getcwd(),'models', 'occlusion.onnx')
            pillar_filter_path = os.path.join(os.getcwd(),'models', 'pillar_filter.onnx')
            database_filename = os.path.join(os.getcwd(),'database', 'final_databases.json')

            result = {}

            if not os.path.exists(database_filename):
                with open(database_filename, 'w') as file:
                    json.dump({}, file)
    
            specimen_name = data['specimen_name']
        
            sections_image_path = data['sections_image_path']  
            result[specimen_name]= {}

            occlusion_model = OcclusionModel(occlusion_model_path)
            process_pillar = PillarDetector(pillar_filter_path)

            for sec_id, section_path in enumerate(sections_image_path):
                section_image = cv2.imread(section_path, cv2.IMREAD_GRAYSCALE)
                section_image_copy = sections_image_path.copy()
                patch = process_pillar.process_cont(section_image, sec_id, specimen_name)

                image, pillar_count, all_points, plotted_image_path = process_pillar.detect_pillars(section_image, patch, sec_id,
                                                                                specimen_name)

                num_negative, num_positive = occlusion_model.occlusion_finder(all_points, section_image, sec_id,
                                                                              specimen_name)

                print(f'Section{4 - sec_id}: Number_of_pillars: {pillar_count}, Occlusion_count: {num_positive}')

                result[specimen_name][f'Section{4 - sec_id}'] = {'Number_of_pillars': pillar_count, 
                                                  'Occlusion_count': num_positive,
                                                  'Unindentified': 0,
                                                  'Non_occlusion':0 ,
                                                  'Plotted_path':plotted_image_path}
                
            result[specimen_name]['Total_occlusion_count'] = 0
            result[specimen_name]['Occlusion_index'] = 0
            result[specimen_name]['Date_time'] = now.strftime("%d/%m/%Y-%H:%M:%S")

            with open(database_filename, 'r') as file:
                data = json.load(file)
                total_elements = sum(len(value) if isinstance(value, list) else 1 for value in data.values())

            data[total_elements+1] = result
    
            with open(database_filename, 'w') as file:
                json.dump(data, file, indent=4)

            return result , 200
        except Exception as e:
            import traceback
            traceback.print_exc()
            return {'message': f'Error processing image: {str(e)}'}, 500
        
class HistoryPage(Resource):
    def get(self):
        try:
            database_json_path = os.path.join(os.getcwd(),'database', 'final_databases.json')
            with open(database_json_path, 'r') as file:
                data_from_file = json.load(file)    
                final_res = []
                
            for key, value in data_from_file.items():
                print("Key:", key)
                for specimen_key, specimen_value in value.items():
                    final_res.append({'project_name':specimen_key,'Date_time':value[specimen_key]['Date_time'],'project_id':key,'Occlusion_folder_path':os.path.join(os.getcwd(),'database',specimen_key)})
 
            return final_res , 200
        except Exception as e:
            return {'message': f'Error reading {str(e)}'}, 500
        
class ViewResult(Resource):
    def post(self):
        try:
            data = request.get_json()
            project_key = data['project_key']
            specimen_name = data['Specimen_name']
            print(project_key)

            return {os.path.join(os.getcwd(),'database',specimen_name,'occlusion_images','cell')} , 200
        except:
            return {'message': f'Error reading {str(e)}'}, 500

def get_db():
    if not os.path.exists('database.db'):
        conn = sqlite3.connect('database.db')
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

class ResultShow(Resource):
    def post(self):
        try:
            data = request.get_json()
            project_key = data['project_key']
            print(project_key)
            
            database_json_path = os.path.join(os.getcwd(),'database', 'final_databases.json')
            with open(database_json_path, 'r') as file:
                data_from_file = json.load(file)
 
                
            for key, value in data_from_file.items():
                if str(key) == str(project_key):
                    for specimen_key, specimen_value in value.items():
                        final_res={'project_name':specimen_key,
                                        'Date_time':value[specimen_key]['Date_time'],
                                        'Total_occlusion_count':value[specimen_key]['Total_occlusion_count'],
                                        'Occlusion_index':value[specimen_key]['Occlusion_index'],
                                        'Section1':value[specimen_key]['Section1'],
                                        'Section2':value[specimen_key]['Section2'],
                                        'Section3':value[specimen_key]['Section3'],
                                        'Section4':value[specimen_key]['Section4'],
                                        'Section1_image': os.path.join(os.getcwd(),'database', specimen_key ,'sections_images','1.png'),
                                        'Section2_image': os.path.join(os.getcwd(),'database',specimen_key ,'sections_images','2.png'),
                                        'Section3_image': os.path.join(os.getcwd(),'database',specimen_key ,'sections_images','3.png'),
                                        'Section4_image': os.path.join(os.getcwd(),'database',specimen_key ,'sections_images','4.png'),
                                        }
                        return final_res , 200
 
            return 'No data in database' , 200
        except Exception as e:
            return {'message': f'Error reading {str(e)}'}, 500
        

class Login(Resource):
    def post(self):
        try:
            data = request.get_json()
            username = data.get('username')
            password = data.get('password')

            with get_db() as conn:
                cur = conn.cursor()

                cur.execute("SELECT * FROM users WHERE username = ?", (username,))
                user = cur.fetchone()

                if user:
                    if password == user[2]:
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
            data = request.get_json()
            username = data.get('username')
            password = data.get('password')

            with get_db() as conn:
                cur = conn.cursor()

                cur.execute("SELECT * FROM users WHERE username = ?", (username,))
                existing_user = cur.fetchone()

                if existing_user:
                    return {'message': 'Username already exists. Please choose a different username.'}, 400
                else:
                    cur.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
                    conn.commit()
                    return {'message': 'User created successfully'}, 201
        except Exception as e:
            return {'message': f'Error creating user: {str(e)}'}, 500

api.add_resource(Login, '/login')
api.add_resource(CreateUser, '/create_user')

api.add_resource(SectionProcessing, '/process_image')
api.add_resource(CountProcessing,'/process_analysis')
api.add_resource(HistoryPage, '/history')
api.add_resource(ResultShow, '/result')

if __name__ == '__main__':
    app.run(debug=True,port=5000)
