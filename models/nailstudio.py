from extensions import db
from datetime import datetime, time
from sqlalchemy.dialects.postgresql import ARRAY
import pytz

class NailStudio(db.Model):
    __tablename__ = 'nail_studios'
    
    id = db.Column(db.String(50), primary_key=True, default=lambda: f"ns_{datetime.now().strftime('%Y%m%d%H%M%S')}")
    nama = db.Column(db.String(255), nullable=False, index=True)
    alamat = db.Column(db.Text)
    desa = db.Column(db.String(100), index=True) 
    
    noTelp = db.Column(db.String(20))
    instagram = db.Column(db.String(100))
    whatsapp = db.Column(db.String(20))
    
    rating = db.Column(db.Float, default=0.0, index=True)
    totalReviews = db.Column(db.Integer, default=0)
    
    description = db.Column(db.Text)
    photoUrl = db.Column(db.Text)
    
    instagramEmbed = db.Column(db.Text)
    mapsEmbed = db.Column(db.Text)
    
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    
    operatingHours = db.Column(db.JSON, default={})
    
    surveyStatus = db.Column(db.Boolean, default=False, index=True)
    
    createdAt = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updatedAt = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<NailStudio {self.nama}>'
    
    def to_dict(self, include_today_status=True):
        """Convert model to dictionary with optional today's opening status"""
        data = {
            'id': self.id,
            'nama': self.nama,
            'alamat': self.alamat,
            'desa': self.desa,
            'noTelp': self.noTelp,
            'instagram': self.instagram,
            'whatsapp': self.whatsapp,
            'rating': self.rating,
            'totalReviews': self.totalReviews,
            'description': self.description,
            'photoUrl': self.photoUrl,
            'instagramEmbed': self.instagramEmbed,
            'mapsEmbed': self.mapsEmbed,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'operatingHours': self.operatingHours or {},
            'surveyStatus': self.surveyStatus,
            'createdAt': self.createdAt.isoformat() if self.createdAt else None,
            'updatedAt': self.updatedAt.isoformat() if self.updatedAt else None,
        }
        
        if include_today_status:
            data['isOpenToday'] = self.is_open_today()
            data['todayHours'] = self.get_today_hours()
        
        return data
    
    def is_open_today(self):
        """Check if nail studio is open today"""
        if not self.operatingHours:
            return False
        
        jakarta_tz = pytz.timezone('Asia/Jakarta')
        now = datetime.now(jakarta_tz)
        day_name = now.strftime('%A').lower() 
        
        day_schedule = self.operatingHours.get(day_name, {})
        return day_schedule.get('isOpen', False)
    
    def get_today_hours(self):
        """Get today's operating hours"""
        if not self.operatingHours:
            return None
        
        jakarta_tz = pytz.timezone('Asia/Jakarta')
        now = datetime.now(jakarta_tz)
        day_name = now.strftime('%A').lower()
        
        day_schedule = self.operatingHours.get(day_name, {})
        if day_schedule.get('isOpen', False):
            return {
                'openTime': day_schedule.get('openTime'),
                'closeTime': day_schedule.get('closeTime'),
                'isOpen': True
            }
        return {'isOpen': False}
    
    def get_week_schedule(self):
        """Get full week schedule in readable format"""
        days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        day_names = ['Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat', 'Sabtu', 'Minggu']
        
        schedule = {}
        for i, day in enumerate(days):
            day_data = self.operatingHours.get(day, {'isOpen': False})
            if day_data.get('isOpen', False):
                schedule[day_names[i]] = f"{day_data.get('openTime', '')} - {day_data.get('closeTime', '')}"
            else:
                schedule[day_names[i]] = 'Tutup'
        
        return schedule