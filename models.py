from app import db
from datetime import datetime
import uuid

class SearchHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    phone_number = db.Column(db.String(20), nullable=False)
    country_code = db.Column(db.String(50), nullable=False)
    carrier = db.Column(db.String(100))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    address = db.Column(db.String(255))
    search_time = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<SearchHistory {self.phone_number} ({self.search_time})>'

class TrackingLink(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tracking_id = db.Column(db.String(36), unique=True, default=lambda: str(uuid.uuid4()))
    phone_number = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_expired = db.Column(db.Boolean, default=False)
    
    def __repr__(self):
        return f"<TrackingLink {self.tracking_id} - {self.phone_number}>"

class TrackedLocation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tracking_id = db.Column(db.String(36), nullable=False)
    ip_address = db.Column(db.String(45), nullable=True)
    user_agent = db.Column(db.String(255), nullable=True)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    altitude = db.Column(db.Float, nullable=True)
    accuracy = db.Column(db.Float, nullable=True)
    address = db.Column(db.String(255), nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    platform = db.Column(db.String(50), nullable=True)
    
    # Campos adicionais de dispositivo
    device_model = db.Column(db.String(100), nullable=True)
    browser_name = db.Column(db.String(50), nullable=True)
    browser_version = db.Column(db.String(50), nullable=True)
    os_name = db.Column(db.String(50), nullable=True)
    os_version = db.Column(db.String(50), nullable=True)
    screen_size = db.Column(db.String(30), nullable=True)
    connection_type = db.Column(db.String(30), nullable=True)
    device_fingerprint = db.Column(db.String(100), nullable=True)
    isp = db.Column(db.String(100), nullable=True)
    timezone = db.Column(db.String(50), nullable=True)
    language = db.Column(db.String(20), nullable=True)
    device_type = db.Column(db.String(20), nullable=True)
    battery_level = db.Column(db.Float, nullable=True)
    
    # Armazenar dados de dispositivo avançados como JSON
    device_info_json = db.Column(db.Text, nullable=True)
    
    def __repr__(self):
        return f"<TrackedLocation {self.tracking_id} - {self.timestamp}>"
