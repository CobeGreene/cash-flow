from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import csv
import io
from datetime import datetime
import logging
from typing import Any, Union
from master_csv_manager import MasterCSVManager
from categorizer_manager import CategorizerManager
import json


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)


# Configuration
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['DATA_FOLDER'] = os.path.join(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))), 'data')
app.config['ALLOWED_EXTENSIONS'] = {'csv'}

# Create uploads directory if it doesn't exist
os.makedirs(app.config['DATA_FOLDER'], exist_ok=True)

master_csv_manager = MasterCSVManager(
    os.path.join(
        os.path.abspath(os.path.dirname(__file__)),
        app.config['DATA_FOLDER']
    )
)

categorized_manager = CategorizerManager(master_csv_manager, os.path.join(
    os.path.abspath(os.path.dirname(__file__)),
    app.config['DATA_FOLDER']))


def allowed_file(filename):
    """Check if the file extension is allowed."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower(
           ) in app.config['ALLOWED_EXTENSIONS']


def parse_csv_content(file_content):
    """Parse CSV content and return structured data."""
    try:
        # Decode content if it's bytes
        if isinstance(file_content, bytes):
            file_content = file_content.decode('utf-8')

        # Create a StringIO object to read the CSV
        csv_file = io.StringIO(file_content)
        reader = csv.DictReader(csv_file)

        # Read all rows
        rows: list[dict[Union[str, Any], Union[str, Any]]] = []
        for row in reader:
            rows.append(row)

        return {
            'success': True,
            'row_count': len(rows),
            'columns': list(rows[0].keys()) if rows else [],
            'data': rows,  # Return all rows for master CSV processing
            'preview': rows[:10],  # Return first 10 rows as preview
            'total_rows': len(rows)
        }
    except Exception as e:
        logger.error(f"Error parsing CSV: {str(e)}")
        return {
            'success': False,
            'error': f"Failed to parse CSV: {str(e)}"
        }


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'CSV Upload Server'
    })


@app.route('/transactions', methods=['GET'])
def get_transactions():
    # Read master file rows using the manager
    result = master_csv_manager.read_master_csv_list()
    return jsonify({
        'columns': result['columns'],
        'data': result['rows']
    })

@app.route('/categories', methods=['GET'])
def get_categories():
    result = categorized_manager.get_categories()
    return jsonify({
        'data': result
    })

@app.route('/categories', methods=['POST'])
def update_categories():
    data = json.loads(request.data.decode('utf-8'))
    result = categorized_manager.update_categories(data["changes"])
    return jsonify({
        'data': result
    })

@app.route('/train', methods=['POST'])
def train_transactions():
    categorized_manager.add_train_task()
    return jsonify({
    })

@app.route('/update_transactions_categories', methods=['POST'])
def update_transactions_categories():    
    data = json.loads(request.data.decode('utf-8'))
    master_csv_manager.update_rows_with_categories(data["rows"])
    result = master_csv_manager.read_master_csv_list()
    return jsonify({
        'columns': result['columns'],
        'data': result['rows']
    })

@app.route('/upload', methods=['POST'])
def upload_csv():
    """Upload and process CSV file."""
    try:
        # Check if file is present in request
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No file provided'
            }), 400

        file = request.files['file']

        # Check if file was selected
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No file selected'
            }), 400

        # Check file extension
        if not allowed_file(file.filename):
            return jsonify({
                'success': False,
                'error': 'Invalid file type. Only CSV files are allowed.'
            }), 400

        # Read file content
        file_content = file.read()

        # Parse CSV content
        result = parse_csv_content(file_content)

        if not result['success']:
            return jsonify(result), 400

        # Update master CSV with new data
        print("Adding rows to master file")
        master_result = master_csv_manager.add_rows_to_master_csv(
            result['data'])

        categorized_manager.add_categorized_task(master_result['added_rows'])
        print("Finish adding rows to master file")

        logger.info(
            f"File processed successfully: {file.filename} and added {len(master_result['added_rows'])} rows")

        return jsonify({
            'success': True,
            'message': 'File processed successfully',
            'original_filename': file.filename,
            'upload_time': datetime.now().isoformat(),
            'file_size': len(file_content),
            'csv_data': {
                'success': result['success'],
                'row_count': result['row_count'],
                'columns': result['columns'],
                'data': result['preview'],  # Show preview in response
                'total_rows': result['total_rows']
            },
            'master_csv': {
                'total_rows': master_result['total_rows'],
                'added_rows': len(master_result['added_rows']),
                'duplicate_rows': master_result['duplicate_rows']
            }
        })

    except Exception as e:
        logger.error(f"Error processing upload: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500


@app.errorhandler(413)
def too_large(e):
    """Handle file too large error."""
    return jsonify({
        'success': False,
        'error': 'File too large. Maximum size is 16MB.'
    }), 413


@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors."""
    return jsonify({
        'success': False,
        'error': 'Endpoint not found'
    }), 404


if __name__ == '__main__':
    categorized_manager.add_initialized_task()
    app.run(debug=True, host='0.0.0.0', port=5000)
    print("App Finish")
    categorized_manager.stop()
