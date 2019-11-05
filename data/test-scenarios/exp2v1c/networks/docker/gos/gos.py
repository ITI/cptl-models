from typing import List, Dict
from flask import Flask
import mysql.connector
import json

app = Flask(__name__)

def booking_entries() -> List[Dict]:
    config = {
        'user': 'GOS',
        'password': 'GOS',
        'host': 'crowley-gos-db',
        'port': 3306,
        'database': 'crowley'
    }
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM gos')
    results = [ {'id': containerId, 'line': line, 'booking':booking } for (containerId, transactionType, line, booking) in cursor]
    cursor.close()
    connection.close()

    return results

@app.route('/')
def index() -> str:
    return json.dumps({'bookings': booking_entries()})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
    
                 
