# Taxonomy Navigator

A web application for navigating and filtering technology and NAICS taxonomies.

## Features

- Technology Taxonomy Browser
- NAICS Code Browser
- Multi-level filtering system
- Login authentication
- AND/OR filter combinations
- Interactive tree view

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/taxonomy-navigator.git
cd taxonomy-navigator
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Start the application:
```bash
python app.py
```

2. Open a web browser and navigate to:
```
http://localhost:8080
```

3. Login with default credentials:
- Username: admin
- Password: admin123

## Development

- The application uses Dash and Flask for the web interface
- Data is stored in JSON files
- Authentication is handled by Flask-Login

## Deployment

The application is configured for deployment on platforms like Render:

1. Set the PORT environment variable
2. Use gunicorn for production:
```bash
gunicorn app:server
```

## Security Notes

For production deployment:
- Change default credentials
- Implement proper user database
- Use password hashing
- Enable HTTPS
- Add rate limiting
- Implement CSRF protection

## License

[Your chosen license] 