from flask import Flask, request, jsonify
from flask_cors import CORS
from proctor_system import ProctorSystem  # Import the ProctorSystem class from your file
from database import db
from models import TabSwitch
from models import Tab  # Add this line
from models import TestResult  # Add this line
from datetime import datetime
from tabswitch import TabSwitchingDetector
from browser import BrowserFingerprintMonitor
from models import Browser  # Add this line
import os

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'tab_switches.db')
db.init_app(app)
CORS(app)  # Enable CORS for all routes

# Create a global instance of ProctorSystem
proctor = ProctorSystem()
fingerprint_monitor = BrowserFingerprintMonitor(
    check_interval=10,
    api_url="http://localhost:5000",
    user_id=1
)

# Create tab tracker instance
tabtrack = TabSwitchingDetector(api_url="http://localhost:5000")

# Setup function to start monitoring
def start_monitoring():
    tabtrack.start_monitoring()
    print("Monitoring started")

def start_fingerprint_monitoring():
    if fingerprint_monitor.start_monitoring():
        print("Browser fingerprint monitoring started")
    else:
        print("Failed to start browser fingerprint monitoring")


# Initialize database and start monitoring
with app.app_context():
    db.create_all()  # Ensure database tables are created
    print("Tables created successfully")
    
    # Start monitoring
    start_monitoring()  # For tab switching
    start_fingerprint_monitoring()  # For browser fingerprints

# Start monitoring directly
start_monitoring()

@app.route('/api/start_baseline', methods=['POST'])
def start_baseline():
    result = proctor.start_baseline_collection()
    return jsonify(result)

@app.route('/api/stop_baseline', methods=['POST'])
def stop_baseline():
    result = proctor.stop_baseline_collection()
    return jsonify(result)

@app.route('/api/start_test', methods=['POST'])
def start_test():
    proctor.start_test()
    return jsonify({"status": "success", "message": "Test started"})

# @app.route('/api/end_test', methods=['POST'])
# def end_test():
#     # Stop tab switch monitoring when test ends
#     tabtrack.stop_monitoring()
#     print("Tab switch monitoring stopped")
    
#     # Get test results
#     results = proctor.end_test()
#     return jsonify(results)

@app.route('/api/end_test', methods=['POST'])
def end_test():
    try:
        # Hardcode user_id to 1
        user_id = 1
        
        # Stop tab switch monitoring when test ends
        tabtrack.stop_monitoring()
        print("Tab switch monitoring stopped")
        
        # Get test results
        results = proctor.end_test()
        
        # Store results in database with timestamp
        new_result = TestResult(
            user_id=user_id,
            timestamp=datetime.now(),
            data=results
        )
        
        db.session.add(new_result)
        db.session.commit()
        
        print(f"Test results stored in database with ID: {new_result.id}")
        
        # Add the database ID to the results
        results['db_record_id'] = new_result.id
        
        return jsonify(results)
    except Exception as e:
        db.session.rollback()
        print(f"Error saving test results: {str(e)}")
        return jsonify({"error": f"Error saving test results: {str(e)}"}), 500
@app.route('/api/test_results', methods=['GET'])
def get_test_results():
    try:
        # Check if user_id is provided as a query parameter
        user_id = request.args.get('user_id', type=int)
        
        if user_id:
            # Get test results for specific user
            results = TestResult.query.filter_by(user_id=user_id).all()
            if not results:
                return jsonify({"message": f"No test results found for user {user_id}"}), 404
        else:
            # Get all test results
            results = TestResult.query.all()
            if not results:
                return jsonify({"message": "No test results found"}), 404
        
        # Format results
        formatted_results = []
        for result in results:
            formatted_results.append({
                'id': result.id,
                'user_id': result.user_id,
                'timestamp': result.timestamp.isoformat(),
                'data': result.data
            })
        
        return jsonify({
            'count': len(formatted_results),
            'results': formatted_results
        })
        
    except Exception as e:
        print(f"Error retrieving test results: {str(e)}")
        return jsonify({"error": f"Error retrieving test results: {str(e)}"}), 500
# New API to track tab switches
# @app.route('/api/tab_switch', methods=['POST'])
# def tab_switch():
#     data = request.json
#     new_switch = TabSwitch(
#         timestamp=datetime.now(),
#         from_window=data['from_window'],
#         to_window=data['to_window']
#     )
#     db.session.add(new_switch)
#     db.session.commit()
#     return jsonify({"message": "Tab switch recorded"}), 201

# @app.route('/api/get_tab_switches', methods=['GET'])
# def get_tab_switches():
#     switches = TabSwitch.query.all()
#     return jsonify([{
#         "id": s.id,
#         "timestamp": s.timestamp.isoformat(),
#         "from_window": s.from_window,
#         "to_window": s.to_window
#     } for s in switches])
# New API endpoint to record tab switches in the Tab table
@app.route('/api/tab', methods=['POST'])
def record_tab():
    data = request.json
    new_tab = Tab(
        user_id=data.get('user_id', 1),  # Default to 1 if not provided
        timestamp=datetime.now(),
        from_window=data['from_window'],
        to_window=data['to_window']
    )
    db.session.add(new_tab)
    db.session.commit()
    return jsonify({"message": "Tab switch recorded in Tab table"}), 201

# Update the get_tab_switches endpoint to query from Tab
@app.route('/api/get_tabs', methods=['GET'])
def get_tabs():
    tabs = Tab.query.all()
    return jsonify([{
        "id": t.id,
        "user_id": t.user_id,
        "timestamp": t.timestamp.isoformat(),
        "from_window": t.from_window,
        "to_window": t.to_window
    } for t in tabs])

# Optional: Get tabs for a specific user
@app.route('/api/get_user_tabs/<int:user_id>', methods=['GET'])
def get_user_tabs(user_id):
    tabs = Tab.query.filter_by(user_id=user_id).all()
    return jsonify([{
        "id": t.id,
        "user_id": t.user_id,
        "timestamp": t.timestamp.isoformat(),
        "from_window": t.from_window,
        "to_window": t.to_window
    } for t in tabs])
@app.route('/api/test_results/<int:result_id>', methods=['GET'])
def get_test_result(result_id):
    try:
        result = TestResult.query.get(result_id)
        
        if not result:
            return jsonify({"message": f"Test result with ID {result_id} not found"}), 404
        
        formatted_result = {
            'id': result.id,
            'user_id': result.user_id,
            'timestamp': result.timestamp.isoformat(),
            'data': result.data
        }
        
        return jsonify(formatted_result)
        
    except Exception as e:
        print(f"Error retrieving test result: {str(e)}")
        return jsonify({"error": f"Error retrieving test result: {str(e)}"}), 500
# @app.route('/api/fingerprint_change', methods=['POST'])
# def fingerprint_change():
#     data = request.json
    
#     # Create a new Browser record
#     new_fingerprint = Browser(
#         user_id=data.get('user_id', 1),  # Default to 1 if not provided
#         timestamp=datetime.now(),
#         fingerprint_hash=data['new_fingerprint']['hash'],
#         active_window=data['active_window'],
#         previous_hash=data['previous_fingerprint']['hash']
#     )
    
#     db.session.add(new_fingerprint)
#     db.session.commit()
    
#     return jsonify({"message": "Browser fingerprint change recorded"}), 201

# @app.route('/api/get_fingerprints', methods=['GET'])
# def get_fingerprints():
#     fingerprints = Browser.query.all()
#     return jsonify([{
#         "id": f.id,
#         "user_id": f.user_id,
#         "timestamp": f.timestamp.isoformat(),
#         "fingerprint_hash": f.fingerprint_hash,
#         "active_window": f.active_window,
#         "previous_hash": f.previous_hash
#     } for f in fingerprints])
@app.route('/api/fingerprint_change', methods=['POST'])
def fingerprint_change():
    data = request.json
    
    # Parse the timestamp if it's a string
    timestamp = data.get('timestamp')
    if isinstance(timestamp, str):
        timestamp = datetime.fromisoformat(timestamp)
    else:
        timestamp = datetime.now()
    
    # Create a new Browser record
    new_fingerprint = Browser(
        user_id=data.get('user_id', 1),  # Default to 1 if not provided
        timestamp=timestamp,
        fingerprint_hash=data.get('fingerprint_hash'),
        active_window=data.get('active_window'),
        previous_hash=data.get('previous_hash')
    )
    
    db.session.add(new_fingerprint)
    db.session.commit()
    
    return jsonify({"message": "Browser fingerprint change recorded"}), 201

@app.route('/api/get_fingerprints', methods=['GET'])
def get_fingerprints():
    fingerprints = Browser.query.all()
    return jsonify([{
        "id": f.id,
        "user_id": f.user_id,
        "timestamp": f.timestamp.isoformat(),
        "fingerprint_hash": f.fingerprint_hash,
        "active_window": f.active_window,
        "previous_hash": f.previous_hash
    } for f in fingerprints])

@app.route('/api/get_user_fingerprints/<int:user_id>', methods=['GET'])
def get_user_fingerprints(user_id):
    fingerprints = Browser.query.filter_by(user_id=user_id).all()
    return jsonify([{
        "id": f.id,
        "user_id": f.user_id,
        "timestamp": f.timestamp.isoformat(),
        "fingerprint_hash": f.fingerprint_hash,
        "active_window": f.active_window,
        "previous_hash": f.previous_hash
    } for f in fingerprints])

@app.route('/api/check_db', methods=['GET'])
def check_db():
    from sqlalchemy import inspect
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    return jsonify({"tables": tables})

if __name__ == '__main__':
    app.run(debug=True, port=5000)