from flask import Flask, render_template, request
import os
import docx2txt
import PyPDF2
from werkzeug.utils import secure_filename

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'pdf', 'docx'}

# Add more career paths and related skills
career_roles = {
    'Data Scientist': ['python', 'pandas', 'numpy', 'machine learning', 'data analysis', 'statistics'],
    'Web Developer': ['html', 'css', 'javascript', 'react', 'angular', 'node', 'bootstrap'],
    'Android Developer': ['android', 'kotlin', 'java', 'xml', 'firebase'],
    'Software Engineer': ['c', 'c++', 'java', 'python', 'algorithms', 'data structures'],
    'Full Stack Developer': ['frontend', 'backend', 'api', 'react', 'node', 'django', 'mongodb', 'express'],
    'Data Analyst': ['excel', 'sql', 'data visualization', 'power bi', 'tableau', 'pandas', 'statistics'],
    '.NET Developer': ['.net', 'c#', 'asp.net', 'entity framework', 'sql server']
}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text(file_path):
    ext = file_path.rsplit('.', 1)[1].lower()
    text = ""
    if ext == 'pdf':
        with open(file_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                if page.extract_text():
                    text += page.extract_text()
    elif ext == 'docx':
        text = docx2txt.process(file_path)
    return text.lower()

def predict_career_and_skills(text):
    skill_scores = {}
    for career, skills in career_roles.items():
        matched_skills = [skill for skill in skills if skill in text]
        score = len(matched_skills) / len(skills) * 100
        skill_scores[career] = round(score, 2)

    best_career = max(skill_scores, key=skill_scores.get)
    if skill_scores[best_career] == 0:
        best_career = "Career path not found. Please update your resume with more relevant skills."
    return best_career, skill_scores

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'resume' not in request.files:
            return "No file part"
        file = request.files['resume']
        if file.filename == '':
            return "No selected file"
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            resume_text = extract_text(file_path)
            best_career, skill_scores = predict_career_and_skills(resume_text)
            return render_template('index.html', prediction=best_career, scores=skill_scores)
    return render_template('index.html')

if __name__ == '__main__':
    if not os.path.exists('uploads'):
        os.makedirs('uploads')
    app.run(debug=True)
