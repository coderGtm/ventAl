import firebase_admin
from firebase_admin import credentials
from firebase_admin import db as rtdb
from firebase_admin import storage as cloud_storage
import os

# Fetch the service account key JSON file contents
service_account_file = str(os.path.join(os.path.dirname(__file__), 'service-account-key.json'))
firebase_cred = credentials.Certificate(service_account_file)
# Initialize the app with a service account
try:
    firebase_admin.initialize_app(firebase_cred, {
        'databaseURL': 'https://vental-event-albums-default-rtdb.asia-southeast1.firebasedatabase.app/',
        'storageBucket': 'vental-event-albums.appspot.com',
        'databaseAuthVariableOverride': {
            'uid': 'service-worker'
        }
    })
    
except:
    pass
finally:
    # Create a reference to the database service
    ref = rtdb.reference('users')
    cloud_bucket = cloud_storage.bucket()
    print("Firebase initialized")