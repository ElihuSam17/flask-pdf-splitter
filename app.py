from flask import Flask, request, send_file, render_template
import os
import pandas as pd
from PyPDF2 import PdfReader, PdfWriter
import zipfile

temp_folder = "temp_output"
os.makedirs(temp_folder, exist_ok=True)

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process_pdf():
    course_name = request.form['course_name']
    pdf_file = request.files['pdf_file']
    excel_file = request.files['excel_file']
    
    if not pdf_file or not excel_file or not course_name:
        return "Faltan archivos o el nombre del curso", 400
    
    pdf_path = os.path.join(temp_folder, "input.pdf")
    excel_path = os.path.join(temp_folder, "input.xlsx")
    pdf_file.save(pdf_path)
    excel_file.save(excel_path)
    
    df = pd.read_excel(excel_path)
    names = df["Nombres"].tolist()
    
    pdf_reader = PdfReader(pdf_path)
    output_zip_name = f"{course_name}_constancias.zip"
    output_zip_path = os.path.join(temp_folder, output_zip_name)
    
    with zipfile.ZipFile(output_zip_path, 'w') as zipf:
        for i, name in enumerate(names):
            if i >= len(pdf_reader.pages):
                break
            
            pdf_writer = PdfWriter()
            pdf_writer.add_page(pdf_reader.pages[i])
            output_pdf_path = os.path.join(temp_folder, f"{course_name}-{name}.pdf")
            
            with open(output_pdf_path, "wb") as output_pdf:
                pdf_writer.write(output_pdf)
            
            zipf.write(output_pdf_path, os.path.basename(output_pdf_path))
            os.remove(output_pdf_path)
    
    return send_file(output_zip_path, as_attachment=True)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
