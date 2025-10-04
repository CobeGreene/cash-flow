# CSV Upload Server

A Python Flask server that accepts CSV file uploads, processes them, and provides API endpoints for file management.

## Features

- ✅ CSV file upload with validation
- ✅ File size limit (16MB max)
- ✅ CSV parsing and data preview
- ✅ Secure filename handling
- ✅ File listing and management
- ✅ Health check endpoint
- ✅ Comprehensive error handling
- ✅ Logging

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the server:**
   ```bash
   python app.py
   ```

The server will start on `http://localhost:5000`

## API Endpoints

### Health Check
- **GET** `/health`
- Returns server status and timestamp

### Upload CSV File
- **POST** `/upload`
- **Content-Type:** `multipart/form-data`
- **Body:** Form data with `file` field containing CSV file

**Response:**
```json
{
  "success": true,
  "message": "File uploaded and processed successfully",
  "filename": "20231201_143022_sample.csv",
  "file_path": "uploads/20231201_143022_sample.csv",
  "upload_time": "2023-12-01T14:30:22.123456",
  "file_size": 1024,
  "csv_data": {
    "success": true,
    "row_count": 100,
    "columns": ["name", "email", "age"],
    "data": [...],
    "total_rows": 100
  }
}
```

### List Uploaded Files
- **GET** `/files`
- Returns list of all uploaded CSV files

**Response:**
```json
{
  "success": true,
  "files": [
    {
      "filename": "20231201_143022_sample.csv",
      "size": 1024,
      "upload_time": "2023-12-01T14:30:22.123456"
    }
  ],
  "total_files": 1
}
```

## Usage Examples

### Using curl to upload a CSV file:
```bash
curl -X POST -F "file=@your_file.csv" http://localhost:5000/upload
```

### Using Python requests:
```python
import requests

url = 'http://localhost:5000/upload'
files = {'file': open('your_file.csv', 'rb')}
response = requests.post(url, files=files)
print(response.json())
```

### Health check:
```bash
curl http://localhost:5000/health
```

### List files:
```bash
curl http://localhost:5000/files
```

## File Storage

Uploaded files are stored in the `uploads/` directory with timestamped filenames to prevent conflicts.

## Error Handling

The server handles various error scenarios:
- File too large (>16MB)
- Invalid file type (non-CSV)
- Malformed CSV files
- Missing files in request
- Server errors

All errors return appropriate HTTP status codes and JSON error messages.

## Configuration

You can modify the following settings in `app.py`:
- `MAX_CONTENT_LENGTH`: Maximum file size (default: 16MB)
- `UPLOAD_FOLDER`: Directory for storing files (default: 'uploads')
- `ALLOWED_EXTENSIONS`: Allowed file extensions (default: {'csv'})

## Developing

Create a conada workspace, activate, and run

```  sh
pip install -r requirements.txt
```

Then run with

``` sh
python app.py
```

## Building Binary

Clean the previous build

``` sh
python -m PyInstaller --clean app.py
```

Build the exe (note this is not working at the moment)


``` sh
python -m PyInstaller app.spec
``` 

## Notes

I originally did the following command to create the spec. It hit a recursion limit and recommend to
use the spec. 

``` sh
python -m PyInstaller --onefile app.py
```