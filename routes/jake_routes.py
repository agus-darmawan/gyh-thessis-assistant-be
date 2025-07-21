from flask import Blueprint, request, jsonify, send_from_directory
import random
import os

jake_bp = Blueprint('jake', __name__)

IMAGES_FOLDER = "jake_images"
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png'}

if not os.path.exists(IMAGES_FOLDER):
    os.makedirs(IMAGES_FOLDER)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_existing_image_numbers():
    return sorted([
        int(f.split('.')[0])
        for f in os.listdir(IMAGES_FOLDER)
        if f.endswith('.jpg') and f.split('.')[0].isdigit()
    ])

def get_next_image_number():
    existing = set(get_existing_image_numbers())
    i = 1
    while i in existing:
        i += 1
    return i

@jake_bp.route('/random-jake', methods=['GET'])
def get_random_jake():
    try:
        existing = get_existing_image_numbers()
        if not existing:
            return jsonify({
                'success': False,
                'message': 'No Jake images found in the folder'
            }), 404

        random_number = random.choice(existing)
        filename = f"{random_number}.jpg"

        return jsonify({
            'success': True,
            'image_path': filename,
            'image_number': random_number,
            'message': f'Random Jake image #{random_number}'
        })

    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

@jake_bp.route('/upload-jake', methods=['POST'])
def upload_jake_image():
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'message': 'No file part in the request'}), 400

        file = request.files['file']

        if file.filename == '':
            return jsonify({'success': False, 'message': 'No file selected'}), 400

        if not allowed_file(file.filename):
            return jsonify({
                'success': False,
                'message': f'File type not allowed. Allowed: {", ".join(ALLOWED_EXTENSIONS)}'
            }), 400

        custom_number = request.form.get('number')
        if custom_number:
            try:
                custom_number = int(custom_number)
                if custom_number < 1:
                    return jsonify({'success': False, 'message': 'Number must be 1 or higher'}), 400

                file_path = os.path.join(IMAGES_FOLDER, f"{custom_number}.jpg")
                if os.path.exists(file_path):
                    return jsonify({'success': False, 'message': f'Image #{custom_number} already exists'}), 400

                next_number = custom_number
            except ValueError:
                return jsonify({'success': False, 'message': 'Invalid number format'}), 400
        else:
            next_number = get_next_image_number()

        filename = f"{next_number}.jpg"
        file_path = os.path.join(IMAGES_FOLDER, filename)
        file.save(file_path)

        return jsonify({
            'success': True,
            'message': f'Jake image uploaded as #{next_number}',
            'image_number': next_number,
            'filename': filename,
            'image_path': filename
        }), 201

    except Exception as e:
        return jsonify({'success': False, 'message': f'Upload failed: {str(e)}'}), 500

@jake_bp.route('/upload-multiple', methods=['POST'])
def upload_multiple_images():
    try:
        if 'files' not in request.files:
            return jsonify({'success': False, 'message': 'No files found in request'}), 400

        files = request.files.getlist('files')
        if not files or all(f.filename == '' for f in files):
            return jsonify({'success': False, 'message': 'No files selected'}), 400

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
            try:
                filename = f"{next_number}.jpg"
                file_path = os.path.join(IMAGES_FOLDER, filename)
                file.save(file_path)

                uploaded_files.append({
                    'original_name': file.filename,
                    'saved_as': filename,
                    'image_number': next_number,
                    'image_path': filename
                })
            except Exception as e:
                failed_files.append({
                    'filename': file.filename,
                    'reason': str(e)
                })

        return jsonify({
            'success': True,
            'message': f'Upload completed. {len(uploaded_files)} success, {len(failed_files)} failed',
            'uploaded_files': uploaded_files,
            'failed_files': failed_files
        }), 201

    except Exception as e:
        return jsonify({'success': False, 'message': f'Multiple upload failed: {str(e)}'}), 500

@jake_bp.route('/delete-jake/<int:image_number>', methods=['DELETE'])
def delete_jake_image(image_number):
    try:
        if image_number < 1:
            return jsonify({'success': False, 'message': 'Invalid image number'}), 400

        filename = f"{image_number}.jpg"
        file_path = os.path.join(IMAGES_FOLDER, filename)

        if not os.path.exists(file_path):
            return jsonify({'success': False, 'message': f'Image #{image_number} not found'}), 404

        os.remove(file_path)

        return jsonify({
            'success': True,
            'message': f'Jake image #{image_number} deleted successfully',
            'deleted_number': image_number
        })

    except Exception as e:
        return jsonify({'success': False, 'message': f'Delete failed: {str(e)}'}), 500

@jake_bp.route('/jake-stats', methods=['GET'])
def get_jake_stats():
    try:
        numbers = get_existing_image_numbers()
        return jsonify({
            'success': True,
            'total_images': len(numbers),
            'available_numbers': numbers[:10],
            'message': f'Found {len(numbers)} Jake images'
        })
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

@jake_bp.route('/images/<filename>')
def serve_image(filename):
    return send_from_directory(IMAGES_FOLDER, filename)
