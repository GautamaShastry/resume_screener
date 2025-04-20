from flask import Flask, request, jsonify
from sentence_transformers import SentenceTransformer, util
import fitz  # PyMuPDF for PDFs
import docx
import os
import spacy
import torch
import tempfile

app = Flask(__name__)

# Load models once
model = SentenceTransformer('all-MiniLM-L6-v2')
nlp = spacy.load("en_core_web_sm")

def extract_text_from_file(file_stream, filename):
    """Extract text from uploaded file."""
    ext = filename.lower()
    if ext.endswith('.pdf'):
        pdf = fitz.open(stream=file_stream.read(), filetype="pdf")
        text = ""
        for page in pdf:
            text += page.get_text()
        return text
    elif ext.endswith('.docx'):
        doc = docx.Document(file_stream)
        return "\n".join([para.text for para in doc.paragraphs])
    else:
        raise ValueError("Unsupported file format. Only PDF or DOCX allowed.")

def extract_keywords(text):
    """Extract nouns and proper nouns as keywords."""
    doc = nlp(text)
    return {token.lemma_.lower() for token in doc if token.is_alpha and not token.is_stop and token.pos_ in ['NOUN', 'PROPN']}

@app.route('/api/analyze', methods=['POST'])
def analyze_resume():
    try:
        file = request.files.get('file')
        job_text = request.form.get('jobDescriptionText', '')

        if not file or not job_text:
            return jsonify({'error': 'File and Job Description Text are required.'}), 400

        # Extract text directly
        resume_text = extract_text_from_file(file.stream, file.filename)

        # Embed the texts
        resume_embedding = model.encode(resume_text, convert_to_tensor=True)
        job_embedding = model.encode(job_text, convert_to_tensor=True)

        # Calculate cosine similarity
        similarity = util.cos_sim(resume_embedding, job_embedding).item()

        # Match accuracy
        accuracy = round(similarity * 100, 2)

        # Extract strengths and weaknesses
        resume_keywords = extract_keywords(resume_text)
        job_keywords = extract_keywords(job_text)

        strengths = resume_keywords.intersection(job_keywords)
        weaknesses = job_keywords.difference(resume_keywords)

        return jsonify({
            "matchScore": accuracy,
            "skills": ", ".join(list(resume_keywords)[:10]) or "N/A",
            "strengths": ", ".join(list(strengths)[:10]) or "N/A",
            "weaknesses": ", ".join(list(weaknesses)[:10]) or "N/A",
            "accuracy": accuracy
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6000)
