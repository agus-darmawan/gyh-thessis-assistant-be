from flask import Blueprint, request, jsonify
from sqlalchemy import and_, or_, func, desc, asc
from models.nailstudio import NailStudio
from extensions import db
from datetime import datetime

nailstudio_bp = Blueprint('nailstudio', __name__)

@nailstudio_bp.route('/nail-studios', methods=['GET'])
def get_nail_studios():
    """Get all nail studios with filtering and search"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        search = request.args.get('search', '').strip()
        desa = request.args.get('desa', '').strip()
        survey_status = request.args.get('survey_status', '').strip()
        rating_min = request.args.get('rating_min', 0, type=float)
        sort_by = request.args.get('sort_by', 'nama') 
        sort_order = request.args.get('sort_order', 'asc') 
        open_today = request.args.get('open_today', '').strip()
        
        query = NailStudio.query
        filters = []
        
        if search:
            search_filter = or_(
                NailStudio.nama.ilike(f'%{search}%'),
                NailStudio.alamat.ilike(f'%{search}%'),
                NailStudio.desa.ilike(f'%{search}%'),
                NailStudio.description.ilike(f'%{search}%')
            )
            filters.append(search_filter)
        
        if desa:
            filters.append(NailStudio.desa.ilike(f'%{desa}%'))
        
        if survey_status.lower() in ['true', 'false']:
            filters.append(NailStudio.surveyStatus == (survey_status.lower() == 'true'))
        
        if rating_min > 0:
            filters.append(NailStudio.rating >= rating_min)
        
        if filters:
            query = query.filter(and_(*filters))
        
        if sort_by == 'rating':
            query = query.order_by(desc(NailStudio.rating) if sort_order == 'desc' else asc(NailStudio.rating))
        elif sort_by == 'created_at':
            query = query.order_by(desc(NailStudio.createdAt) if sort_order == 'desc' else asc(NailStudio.createdAt))
        else:  
            query = query.order_by(desc(NailStudio.nama) if sort_order == 'desc' else asc(NailStudio.nama))
        
        paginated = query.paginate(page=page, per_page=per_page, error_out=False)
        
        studios = []
        for studio in paginated.items:
            studio_data = studio.to_dict()
            
            if open_today.lower() == 'true' and not studio_data['isOpenToday']:
                continue
            elif open_today.lower() == 'false' and studio_data['isOpenToday']:
                continue
            
            studios.append(studio_data)
        
        desa_options = db.session.query(NailStudio.desa).distinct().filter(
            NailStudio.desa.isnot(None),
            NailStudio.desa != ''
        ).all()
        desa_list = [d[0] for d in desa_options if d[0]]
        
        return jsonify({
            'success': True,
            'data': studios,
            'pagination': {
                'page': paginated.page,
                'per_page': paginated.per_page,
                'total': paginated.total,
                'pages': paginated.pages,
                'has_next': paginated.has_next,
                'has_prev': paginated.has_prev
            },
            'filters': {
                'desa_options': sorted(desa_list),
                'applied_filters': {
                    'search': search,
                    'desa': desa,
                    'survey_status': survey_status,
                    'rating_min': rating_min,
                    'open_today': open_today,
                    'sort_by': sort_by,
                    'sort_order': sort_order
                }
            },
            'message': f'Found {len(studios)} nail studios'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error fetching nail studios: {str(e)}'
        }), 500

@nailstudio_bp.route('/nail-studios/<studio_id>', methods=['GET'])
def get_nail_studio(studio_id):
    """Get single nail studio by ID"""
    try:
        studio = NailStudio.query.get(studio_id)
        if not studio:
            return jsonify({
                'success': False,
                'message': 'Nail studio not found'
            }), 404
        
        return jsonify({
            'success': True,
            'data': studio.to_dict(),
            'schedule': studio.get_week_schedule(),
            'message': f'Nail studio {studio.nama} retrieved successfully'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error fetching nail studio: {str(e)}'
        }), 500

@nailstudio_bp.route('/nail-studios', methods=['POST'])
def create_nail_studio():
    """Create new nail studio"""
    try:
        data = request.get_json()
        
        if not data or not data.get('nama'):
            return jsonify({
                'success': False,
                'message': 'Nama is required'
            }), 400
        
        studio = NailStudio(
            nama=data.get('nama'),
            alamat=data.get('alamat'),
            desa=data.get('desa'),
            noTelp=data.get('noTelp'),
            instagram=data.get('instagram'),
            whatsapp=data.get('whatsapp'),
            rating=float(data.get('rating', 0.0)),
            totalReviews=int(data.get('totalReviews', 0)),
            description=data.get('description'),
            photoUrl=data.get('photoUrl'),
            instagramEmbed=data.get('instagramEmbed'),
            mapsEmbed=data.get('mapsEmbed'),
            latitude=float(data.get('latitude')) if data.get('latitude') is not None else None,
            longitude=float(data.get('longitude')) if data.get('longitude') is not None else None,
            operatingHours=data.get('operatingHours', {}),
            surveyStatus=bool(data.get('surveyStatus', False))
        )
        
        db.session.add(studio)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': studio.to_dict(),
            'message': f'Nail studio {studio.nama} created successfully'
        }), 201
        
    except ValueError as ve:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Invalid data format: {str(ve)}'
        }), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error creating nail studio: {str(e)}'
        }), 500

@nailstudio_bp.route('/nail-studios/<studio_id>', methods=['PUT'])
def update_nail_studio(studio_id):
    """Update nail studio"""
    try:
        studio = NailStudio.query.get(studio_id)
        if not studio:
            return jsonify({
                'success': False,
                'message': 'Nail studio not found'
            }), 404
        
        data = request.get_json()
        
        if 'nama' in data:
            studio.nama = data['nama']
        if 'alamat' in data:
            studio.alamat = data['alamat']
        if 'desa' in data:
            studio.desa = data['desa']
        if 'noTelp' in data:
            studio.noTelp = data['noTelp']
        if 'instagram' in data:
            studio.instagram = data['instagram']
        if 'whatsapp' in data:
            studio.whatsapp = data['whatsapp']
        if 'rating' in data:
            studio.rating = float(data['rating'])
        if 'totalReviews' in data:
            studio.totalReviews = int(data['totalReviews'])
        if 'description' in data:
            studio.description = data['description']
        if 'photoUrl' in data:
            studio.photoUrl = data['photoUrl']
        if 'instagramEmbed' in data:
            studio.instagramEmbed = data['instagramEmbed']
        if 'mapsEmbed' in data:
            studio.mapsEmbed = data['mapsEmbed']
        if 'latitude' in data:
            studio.latitude = float(data['latitude']) if data['latitude'] is not None else None
        if 'longitude' in data:
            studio.longitude = float(data['longitude']) if data['longitude'] is not None else None
        if 'operatingHours' in data:
            studio.operatingHours = data['operatingHours']
        if 'surveyStatus' in data:
            studio.surveyStatus = bool(data['surveyStatus'])
        
        studio.updatedAt = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': studio.to_dict(),
            'message': f'Nail studio {studio.nama} updated successfully'
        })
        
    except ValueError as ve:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Invalid data format: {str(ve)}'
        }), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error updating nail studio: {str(e)}'
        }), 500

@nailstudio_bp.route('/nail-studios/<studio_id>/survey-status', methods=['PATCH'])
def update_survey_status(studio_id):
    """Update survey status only"""
    try:
        studio = NailStudio.query.get(studio_id)
        if not studio:
            return jsonify({
                'success': False,
                'message': 'Nail studio not found'
            }), 404
        
        data = request.get_json()
        survey_status = data.get('surveyStatus')
        
        if survey_status is None:
            return jsonify({
                'success': False,
                'message': 'surveyStatus is required'
            }), 400
        
        studio.surveyStatus = bool(survey_status)
        studio.updatedAt = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': {
                'id': studio.id,
                'nama': studio.nama,
                'surveyStatus': studio.surveyStatus
            },
            'message': f'Survey status updated to {studio.surveyStatus}'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error updating survey status: {str(e)}'
        }), 500

@nailstudio_bp.route('/nail-studios/<studio_id>', methods=['DELETE'])
def delete_nail_studio(studio_id):
    """Delete nail studio"""
    try:
        studio = NailStudio.query.get(studio_id)
        if not studio:
            return jsonify({
                'success': False,
                'message': 'Nail studio not found'
            }), 404
        
        studio_name = studio.nama
        db.session.delete(studio)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Nail studio {studio_name} deleted successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error deleting nail studio: {str(e)}'
        }), 500

@nailstudio_bp.route('/nail-studios/stats', methods=['GET'])
def get_stats():
    """Get nail studios statistics"""
    try:
        total_studios = NailStudio.query.count()
        surveyed_studios = NailStudio.query.filter(NailStudio.surveyStatus == True).count()
        
        open_today_count = 0
        studios = NailStudio.query.all()
        for studio in studios:
            if studio.is_open_today():
                open_today_count += 1
        
        avg_rating = db.session.query(func.avg(NailStudio.rating)).scalar() or 0
        
        desa_stats = db.session.query(
            NailStudio.desa,
            func.count(NailStudio.id).label('count')
        ).group_by(NailStudio.desa).filter(
            NailStudio.desa.isnot(None),
            NailStudio.desa != ''
        ).all()
        
        return jsonify({
            'success': True,
            'stats': {
                'total_studios': total_studios,
                'surveyed_studios': surveyed_studios,
                'unsurveyed_studios': total_studios - surveyed_studios,
                'open_today': open_today_count,
                'average_rating': round(avg_rating, 2),
                'desa_distribution': [{'desa': d[0], 'count': d[1]} for d in desa_stats]
            },
            'message': 'Statistics retrieved successfully'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error fetching statistics: {str(e)}'
        }), 500