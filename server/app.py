from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import csv
import io
from datetime import datetime
import logging
import queue
from typing import Any, Union, cast
import threading
import sys
from transformers import pipeline
# Master CSV manager import and setup
from master_csv_manager import MasterCSVManager

sys.path.append("../categorized_transactions")

import constants

classifer = pipeline("text-classification",
                     model="../categorized_transactions/my_model")


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Configure queue
categorized_queue = queue.Queue()




class CategorizedTask:
    def __init__(self, rows: list[dict[Union[str, Any], Union[str, Any]]]):
        self.rows = rows

    def doWork(self):
        print("Start work on categorizing")
        for row in self.rows:
            type_result = classifer(row['Name'])
            type_label = None
            if type_result and isinstance(type_result, list):
                first_result = type_result[0]
                if isinstance(first_result, dict) and 'label' in first_result:
                    type_label = first_result['label']
            category = constants.type_to_category.get(type_label, "Unknown")
            row['Category'] = category
            row['Sub Category'] = type_label if type_label else "Unknown"
        master_csv_manager.update_rows_with_categories(updated_rows=self.rows)
        print("Finish work on categorizing")


def categorized_consumer(queue: queue.Queue):
    print('Consumer: Running')
    while True:
        # Get a unit of work
        item = queue.get()
        # Check for stop
        if item is None:
            break
        # Perform work
        categorized_task = cast(CategorizedTask, item)
        categorized_task.doWork()
        queue.task_done()
    # All done
    print('Consumer: Done')


# Configuration
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))), 'data')
app.config['ALLOWED_EXTENSIONS'] = {'csv'}

# Create uploads directory if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

master_csv_manager = MasterCSVManager(
    os.path.join(
        os.path.abspath(os.path.dirname(__file__)),
        app.config['UPLOAD_FOLDER'],
        'master_transactions.csv'
    )
)



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
    result = master_csv_manager.read_master_csv()
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
        master_result = master_csv_manager.add_rows_to_master_csv(result['data'])
        categorized_queue.put(CategorizedTask(master_result['added_rows']), block=False)
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
    consumer = threading.Thread(
        target=categorized_consumer, args=(categorized_queue,))
    consumer.start()
    app.run(debug=True, host='0.0.0.0', port=5000)
    print("App Finish")
    categorized_queue.join()
    categorized_queue.put(None)
    consumer.join()
    categorized_queue.join()
