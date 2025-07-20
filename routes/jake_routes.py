# routes/jake_routes.py - Jake Image API Routes
from flask import Blueprint, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
import random
import os
from config import Config

jake_bp = Blueprint('jake', __name__)

IMAGES_FOLDER = Config.JAKE_IMAGES_FOLDER
MAX_IMAGE_NUMBER = Config.MAX_IMAGE_NUMBER
ALLOWED_EXTENSIONS = Config.ALLOWED_EXTENSIONS

if not os.path.exists(IMAGES_FOLDER):
    os.makedirs(IMAGES_FOLDER)

def allowed_file(filename):
    """Check if file has allowed extension"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_next_image_number():
    """Find the next available image number"""
    for i in range(1, MAX_IMAGE_NUMBER + 1):
        image_path = os.path.join(IMAGES_FOLDER, f"{i}.jpg")
        if not os.path.exists(image_path):
            return i
    return None

@jake_bp.route('/random-jake', methods=['GET'])
def get_random_jake():
    """Get a random Jake image number and return the URL"""
    try:
        random_number = random.randint(1, MAX_IMAGE_NUMBER)
        image_filename = f"{random_number}.jpg"
        image_path = os.path.join(IMAGES_FOLDER, image_filename)
        
        if os.path.exists(image_path):
            image_url = f"https://gyh-api.agus-darmawan.com/images/{image_filename}"
            return jsonify({
                'success': True,
                'image_url': image_url,
                'image_number': random_number,
                'message': f'Random Jake image #{random_number}'
            })
        else:
            available_images = []
            for i in range(1, MAX_IMAGE_NUMBER + 1):
                if os.path.exists(os.path.join(IMAGES_FOLDER, f"{i}.jpg")):
                    available_images.append(i)
            
            if available_images:
                random_number = random.choice(available_images)
                image_filename = f"{random_number}.jpg"
                image_url = f"https://gyh-api.agus-darmawan.com/images/{image_filename}"
                return jsonify({
                    'success': True,
                    'image_url': image_url,
                    'image_number': random_number,
                    'message': f'Random Jake image #{random_number}'
                })
            else:
                return jsonify({
                    'success': False,
                    'message': 'No Jake images found in the folder'
                }), 404
                
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500

@jake_bp.route('/upload-jake', methods=['POST'])
def upload_jake_image():
    """Upload a new Jake image"""
    try:
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'message': 'No file part in the request'
            }), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({
                'success': False,
                'message': 'No file selected'
            }), 400
        
        if not allowed_file(file.filename):
            return jsonify({
                'success': False,
                'message': f'File type not allowed. Allowed types: {", ".join(ALLOWED_EXTENSIONS)}'
            }), 400
        
        next_number = get_next_image_number()
        if next_number is None:
            return jsonify({
                'success': False,
                'message': f'Maximum number of images ({MAX_IMAGE_NUMBER}) reached'
            }), 400
        
        custom_number = request.form.get('number')
        if custom_number:
            try:
                custom_number = int(custom_number)
                if 1 <= custom_number <= MAX_IMAGE_NUMBER:
                    custom_path = os.path.join(IMAGES_FOLDER, f"{custom_number}.jpg")
                    if os.path.exists(custom_path):
                        return jsonify({
                            'success': False,
                            'message': f'Image number {custom_number} already exists'
                        }), 400
                    next_number = custom_number
                else:
                    return jsonify({
                        'success': False,
                        'message': f'Number must be between 1 and {MAX_IMAGE_NUMBER}'
                    }), 400
            except ValueError:
                return jsonify({
                    'success': False,
                    'message': 'Invalid number format'
                }), 400
        
        filename = f"{next_number}.jpg"
        file_path = os.path.join(IMAGES_FOLDER, filename)
        file.save(file_path)
        
        return jsonify({
            'success': True,
            'message': f'Jake image uploaded successfully as #{next_number}',
            'image_number': next_number,
            'filename': filename,
            'image_url': f"https://gyh-api.agus-darmawan.com/images/{filename}"
        }), 201
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Upload failed: {str(e)}'
        }), 500

@jake_bp.route('/upload-multiple', methods=['POST'])
def upload_multiple_images():
    """Upload multiple Jake images at once"""
    try:
        if 'files' not in request.files:
            return jsonify({
                'success': False,
                'message': 'No files found in request'
            }), 400
        
        files = request.files.getlist('files')
        if not files or all(f.filename == '' for f in files):
            return jsonify({
                'success': False,
                'message': 'No files selected'
            }), 400
        
        uploaded_files = []
        failed_files = []
        
        for file in files:
            if file.filename == '':
                continue
                
            if not allowed_file(file.filename):
                failed_files.append({
                    'filename': file.filename,
                    'reason': 'File type not allowed'
                })
                continue
            
            next_number = get_next_image_number()
            if next_number is None:
                failed_files.append({
                    'filename': file.filename,
                    'reason': 'Maximum images reached'
                })
                continue
            
            try:
                filename = f"{next_number}.jpg"
                file_path = os.path.join(IMAGES_FOLDER, filename)
                file.save(file_path)
                
                uploaded_files.append({
                    'original_name': file.filename,
                    'saved_as': filename,
                    'image_number': next_number,
                    'image_url': f"https://gyh-api.agus-darmawan.com/images/{filename}"
                })
                
            except Exception as e:
                failed_files.append({
                    'filename': file.filename,
                    'reason': str(e)
                })
        
        return jsonify({
            'success': True,
            'message': f'Upload completed. {len(uploaded_files)} successful, {len(failed_files)} failed',
            'uploaded_files': uploaded_files,
            'failed_files': failed_files,
            'total_uploaded': len(uploaded_files),
            'total_failed': len(failed_files)
        }), 201
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Multiple upload failed: {str(e)}'
        }), 500

@jake_bp.route('/delete-jake/<int:image_number>', methods=['DELETE'])
def delete_jake_image(image_number):
    """Delete a specific Jake image"""
    try:
        if not (1 <= image_number <= MAX_IMAGE_NUMBER):
            return jsonify({
                'success': False,
                'message': f'Image number must be between 1 and {MAX_IMAGE_NUMBER}'
            }), 400
        
        filename = f"{image_number}.jpg"
        file_path = os.path.join(IMAGES_FOLDER, filename)
        
        if not os.path.exists(file_path):
            return jsonify({
                'success': False,
                'message': f'Image #{image_number} not found'
            }), 404
        
        os.remove(file_path)
        
        return jsonify({
            'success': True,
            'message': f'Jake image #{image_number} deleted successfully',
            'deleted_number': image_number
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Delete failed: {str(e)}'
        }), 500

@jake_bp.route('/jake-stats', methods=['GET'])
def get_jake_stats():
    """Get statistics about available Jake images"""
    try:
        available_images = []
        for i in range(1, MAX_IMAGE_NUMBER + 1):
            if os.path.exists(os.path.join(IMAGES_FOLDER, f"{i}.jpg")):
                available_images.append(i)
        
        return jsonify({
            'success': True,
            'total_images': len(available_images),
            'max_possible': MAX_IMAGE_NUMBER,
            'available_numbers': available_images[:10],  # Show first 10 as preview
            'message': f'Found {len(available_images)} Jake images'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500

@jake_bp.route('/images/<filename>')
def serve_image(filename):
    """Serve images from the jake_images folder"""
    return send_from_directory(IMAGES_FOLDER, filename)