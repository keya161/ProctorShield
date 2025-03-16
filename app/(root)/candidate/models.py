from database import db
from datetime import datetime
import json

class TabSwitch(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, nullable=False)
    from_window = db.Column(db.String(255), nullable=False)
    to_window = db.Column(db.String(255), nullable=False)

class Tab(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)
    from_window = db.Column(db.String(255), nullable=False)
    to_window = db.Column(db.String(255), nullable=False)

class Browser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.now)
    fingerprint_hash = db.Column(db.String(64), nullable=False)  # SHA-256 hash is 64 characters
    active_window = db.Column(db.String(255))  # Store the active window when fingerprint changed
    previous_hash = db.Column(db.String(64))  # Store the previous hash to track changes

class TestResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.now)
    _data = db.Column('data', db.Text, nullable=True)  # Storing JSON as text

    @property
    def data(self):
        if self._data:
            return json.loads(self._data)
        return {}

    @data.setter
    def data(self, value):
        self._data = json.dumps(value) if value else None