import json
from datetime import datetime, timedelta
import base64
import os
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.fernet import Fernet
import random

# User ID
USER_ID = 1

# Generate mock data instead of fetching from API
def generate_mock_data():
    # Dictionary to store all mock data
    all_data = {}
    
    # Current time
    now = datetime.now()
    
    # 1. Generate mock test results
    test_results = []
    for i in range(3):
        test_time = now - timedelta(days=i*2)
        test_results.append({
            'id': i + 1,
            'user_id': USER_ID,
            'timestamp': test_time.isoformat(),
            'data': {
                'score': random.randint(65, 95),
                'duration': random.randint(30, 90),
                'questions_answered': random.randint(20, 50),
                'cheating_score': random.uniform(0, 10),
                'test_id': f"TEST{random.randint(1000, 9999)}"
            }
        })
    all_data['test_results'] = test_results
    print(f"Generated {len(test_results)} mock test results")
    
    # 2. Generate mock tab switches
    tab_switches = []
    for i in range(20):
        switch_time = now - timedelta(minutes=random.randint(1, 200))
        windows = ["Test Window", "Google", "Notes", "Calculator", "Reference Page"]
        from_window = random.choice(windows)
        to_window = random.choice([w for w in windows if w != from_window])
        
        tab_switches.append({
            'id': i + 1,
            'user_id': USER_ID,
            'timestamp': switch_time.isoformat(),
            'from_window': from_window,
            'to_window': to_window
        })
    all_data['tab_switches'] = tab_switches
    print(f"Generated {len(tab_switches)} mock tab switches")
    
    # 3. Generate mock fingerprint changes
    fingerprints = []
    prev_hash = None
    for i in range(5):
        fp_time = now - timedelta(minutes=random.randint(1, 180))
        current_hash = base64.b64encode(os.urandom(32)).decode()[:64]
        
        fingerprints.append({
            'id': i + 1,
            'user_id': USER_ID,
            'timestamp': fp_time.isoformat(),
            'fingerprint_hash': current_hash,
            'active_window': random.choice(windows),
            'previous_hash': prev_hash
        })
        prev_hash = current_hash
    
    all_data['fingerprints'] = fingerprints
    print(f"Generated {len(fingerprints)} mock fingerprint changes")
    
    return all_data

# Encryption configuration
def generate_key(password, salt=None):
    """Generate an encryption key from a password and optional salt."""
    if salt is None:
        salt = os.urandom(16)  # Generate a random salt if not provided
    
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    
    key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
    return key, salt

def encrypt_data(data, password):
    """Encrypt data using a password."""
    # Generate key from password
    key, salt = generate_key(password)
    
    # Create a Fernet object with the key
    fernet = Fernet(key)
    
    # Convert data to JSON string and encode to bytes
    data_bytes = json.dumps(data).encode()
    
    # Encrypt the data
    encrypted_data = fernet.encrypt(data_bytes)
    
    # Return both the encrypted data and the salt (needed for decryption)
    return {
        'encrypted_data': base64.b64encode(encrypted_data).decode(),
        'salt': base64.b64encode(salt).decode()
    }

def decrypt_data(encrypted_package, password):
    """Decrypt data using a password and salt."""
    # Extract encrypted data and salt
    encrypted_data = base64.b64decode(encrypted_package['encrypted_data'])
    salt = base64.b64decode(encrypted_package['salt'])
    
    # Regenerate the key using the same password and salt
    key, _ = generate_key(password, salt)
    
    # Create a Fernet object with the key
    fernet = Fernet(key)
    
    # Decrypt the data
    decrypted_bytes = fernet.decrypt(encrypted_data)
    
    # Convert bytes back to JSON object
    decrypted_data = json.loads(decrypted_bytes.decode())
    
    return decrypted_data

# Function to process and analyze the data
def process_data(data):
    # Extract separate variables for easier access
    test_results = data['test_results']
    tab_switches = data['tab_switches']
    fingerprints = data['fingerprints']
    
    # Get the most recent test result if any
    most_recent_test = None
    if test_results:
        most_recent_test = max(test_results, key=lambda x: datetime.fromisoformat(x['timestamp']))
    
    # Count tab switches
    tab_switch_count = len(tab_switches)
    
    # Count fingerprint changes
    fingerprint_change_count = len(fingerprints)
    
    # Create summary
    summary = {
        'user_id': USER_ID,
        'test_count': len(test_results),
        'tab_switch_count': tab_switch_count,
        'fingerprint_change_count': fingerprint_change_count,
        'most_recent_test_timestamp': most_recent_test['timestamp'] if most_recent_test else None,
        'most_recent_test_id': most_recent_test['id'] if most_recent_test else None
    }
    
    # Return processed data
    return {
        'raw_data': data,
        'summary': summary,
        'test_results': test_results,
        'tab_switches': tab_switches,
        'fingerprints': fingerprints
    }

# Main function to generate mock data, process, and encrypt it
def main(password="secure_password_123"):
    print(f"Generating mock data for user ID: {USER_ID}")
    
    # Generate mock data instead of fetching
    raw_data = generate_mock_data()
    
    # Process data
    processed_data = process_data(raw_data)
    
    # Access the variables
    test_results = processed_data['test_results']
    tab_switches = processed_data['tab_switches']
    fingerprints = processed_data['fingerprints']
    summary = processed_data['summary']
    
    # Print summary
    print("\nData Summary:")
    print(json.dumps(summary, indent=2))
    
    # Encrypt the data
    print("\nEncrypting data...")
    encrypted_package = encrypt_data(processed_data, password)
    
    # Save encrypted data to file
    encrypted_file_path = f'user_{USER_ID}_encrypted_data.json'
    with open(encrypted_file_path, 'w') as f:
        json.dump(encrypted_package, f)
        print(f"Encrypted data saved to {encrypted_file_path}")
    
    # Example of how to decrypt and use the data
    print("\nTest decrypting the data...")
    decrypted_data = decrypt_data(encrypted_package, password)
    print("Decryption successful!")
    
    # Save unencrypted data to file for comparison (in real app, you might not want to do this)
    unencrypted_file_path = f'user_{USER_ID}_data.json'
    with open(unencrypted_file_path, 'w') as f:
        json.dump(processed_data, f, indent=2)
        print(f"Unencrypted data saved to {unencrypted_file_path} for comparison")
    
    return {
        'processed_data': processed_data,
        'test_results': test_results,
        'tab_switches': tab_switches, 
        'fingerprints': fingerprints,
        'encrypted_package': encrypted_package
    }

def load_encrypted_data(file_path, password):
    """Load and decrypt data from an encrypted file."""
    with open(file_path, 'r') as f:
        encrypted_package = json.load(f)
    
    return decrypt_data(encrypted_package, password)

# Example usage
if __name__ == "__main__":
    # Set your encryption password
    encryption_password = "your_secure_password_here"
    
    # Generate, process, and encrypt mock data
    data_package = main(encryption_password)
    
    # Example of how to load the encrypted data later
    print("\nExample: Loading encrypted data from file")
    encrypted_file_path = f'user_{USER_ID}_encrypted_data.json'
    
    try:
        loaded_data = load_encrypted_data(encrypted_file_path, encryption_password)
        print(f"Successfully loaded and decrypted data for user {USER_ID}")
        
        # Now you can access the decrypted data
        print(f"User has {len(loaded_data['test_results'])} test results")
        print(f"First test score: {loaded_data['test_results'][0]['data']['score']}")
        print(f"Tab switches: {len(loaded_data['tab_switches'])}")
        
        # Wrong password test (this should raise an exception)
        try:
            wrong_decrypt = load_encrypted_data(encrypted_file_path, "wrong_password")
            print("This should not execute - wrong password should fail")
        except Exception as e:
            print(f"Expected error with wrong password: {str(e)}")
            
    except Exception as e:
        print(f"Error loading encrypted data: {str(e)}")