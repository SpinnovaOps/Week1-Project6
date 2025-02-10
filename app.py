from flask import Flask
from routes.main import main_bp  # Import Blueprint

app = Flask(__name__)
app.config['SECRET_KEY'] = "supersecretkey"
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB limit

# Register Blueprint
app.register_blueprint(main_bp)

if __name__ == '__main__':
    app.run(debug=True)
