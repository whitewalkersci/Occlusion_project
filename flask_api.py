from flask import Flask, request
from flask_restful import Api, Resource
import cv2
from backend.section_process import ImageProcessor
from backend.process import PillarDetector
from backend.occlusion_process import OcclusionModel
import os 
from pathlib import Path

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
            print(image_path)
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
            print(data)
            specimen_name = data['specimen_name']
        

            sections_image_path = data['sections_image_path']  
            print(sections_image_path)
            occlusion_model = OcclusionModel(occlusion_model_path)
            process_pillar = PillarDetector(pillar_filter_path)

            for sec_id, section_path in enumerate(sections_image_path):
                section_image = cv2.imread(section_path, cv2.IMREAD_GRAYSCALE)
                section_image_copy = sections_image_path.copy()
                patch = process_pillar.process_cont(section_image, sec_id, specimen_name)

                # Detect pillars in the section
                image, pillar_count, all_points = process_pillar.detect_pillars(section_image, patch, sec_id,
                                                                                specimen_name)

                # Find occlusions in the section
                num_negative, num_positive = occlusion_model.occlusion_finder(all_points, section_image, sec_id,
                                                                              specimen_name)

                print(f'Section {4 - sec_id}: Number of pillars: {pillar_count}, Occlusion count: {num_positive}')

                result[f'Section {4 - sec_id}'] = {'Number of pillars': pillar_count, 'Occlusion count': num_positive}

            return result

        except Exception as e:
            import traceback
            traceback.print_exc()
            return {'message': f'Error processing image: {str(e)}'}, 500


# Define the API endpoint
api.add_resource(SectionProcessing, '/process_image')
api.add_resource(CountProcessing,'/process_analysis')

if __name__ == '__main__':
    app.run(debug=True,port=5001)  # Set debug to False in production
