from flask import Flask, render_template, request, jsonify, send_file
import pandas as pd
from datetime import datetime
import os

app = Flask(__name__)

# Create CSV file if it doesn't exist
if not os.path.exists('patients.csv'):
    df = pd.DataFrame(columns=['patient_id', 'name', 'age', 'problems', 'last_visit'])
    df.to_csv('patients.csv', index=False)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/add_patient', methods=['POST'])
def add_patient():
    try:
        data = request.get_json()
        
        # Validate input data
        if not all(key in data for key in ['name', 'age', 'problems']):
            return jsonify({
                'success': False, 
                'message': 'Missing required fields'
            }), 400

        # Read existing data
        df = pd.read_csv('patients.csv')
        
        # Create new patient entry
        new_patient = {
            'patient_id': len(df) + 1,  # Auto-increment ID
            'name': data['name'],
            'age': data['age'],
            'problems': data['problems'],
            'last_visit': datetime.now().strftime('%Y-%m-%d')
        }
        
        # Use concat instead of append (append is deprecated)
        df = pd.concat([df, pd.DataFrame([new_patient])], ignore_index=True)
        df.to_csv('patients.csv', index=False)
        
        return jsonify({
            'success': True,
            'message': f"Patient added successfully! Patient ID: {new_patient['patient_id']}",
            'patient_id': new_patient['patient_id']
        })

    except Exception as e:
        print(f"Error: {str(e)}")  # For debugging
        return jsonify({
            'success': False,
            'message': 'Error adding patient'
        }), 500

@app.route('/get_patient/<int:patient_id>')
def get_patient(patient_id):
    try:
        df = pd.read_csv('patients.csv')
        patient = df[df['patient_id'] == patient_id]
        
        if len(patient) == 0:
            return jsonify({
                'success': False,
                'message': 'Patient not found'
            }), 404
        
        return jsonify({
            'success': True,
            'patient_id': int(patient['patient_id'].values[0]),
            'name': patient['name'].values[0],
            'age': int(patient['age'].values[0]),
            'problems': patient['problems'].values[0],
            'last_visit': patient['last_visit'].values[0]
        })

    except Exception as e:
        print(f"Error: {str(e)}")  # For debugging
        return jsonify({
            'success': False,
            'message': 'Error retrieving patient'
        }), 500

@app.route('/download_csv')
def download_csv():
    try:
        # Read and format the CSV file
        df = pd.read_csv('patients.csv')
        
        # Sort by patient_id for better organization
        df = df.sort_values(by='patient_id')
        
        # Save to a temporary formatted CSV
        temp_csv = 'hospital_patients_data.csv'
        df.to_csv(temp_csv, index=False)
        
        # Send file to client
        return send_file(
            temp_csv,
            mimetype='text/csv',
            as_attachment=True,
            download_name='hospital_patients_data.csv'
        )
    except Exception as e:
        print(f"Download error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Error downloading CSV file'
        }), 500

if __name__ == '__main__':
    app.run(debug=True) 