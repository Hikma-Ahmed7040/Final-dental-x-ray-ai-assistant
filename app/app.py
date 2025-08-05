import gradio as gr
from PIL import Image
from fpdf import FPDF
import tempfile
import os
from datetime import datetime 

# Function to simulate detection and generate a PDF
def dummy_detect_and_generate_pdf(img, patient_id):
    if not patient_id.strip():
        raise gr.Error("❗ Patient ID is required to generate the report.")

    # Generate a temporary file path (not opened as a file)
    temp_img_path = os.path.join(tempfile.gettempdir(), f"{patient_id.strip().replace(' ', '_')}_xray.png")
    img.save(temp_img_path)  # Save PIL image directly to this path

    # Create PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, txt="Dental X-ray Analysis Report", ln=True, align='C')
    pdf.cell(200, 10, txt=f"Patient ID: {patient_id}", ln=True)
    pdf.cell(200, 10, txt=f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True)
    pdf.cell(200, 10, txt="Detected Issues: [Crown - Fillings, Caries]", ln=True)

    # Insert the image (now saved and openable)
    pdf.image(temp_img_path, x=10, y=50, w=80)

    # Save PDF
    pdf_filename = f"{patient_id.strip().replace(' ', '_')}_report.pdf"
    pdf_path = os.path.join(tempfile.gettempdir(), pdf_filename)  
    pdf.output(pdf_path)

    return img, pdf_path

# Gradio interface
demo = gr.Interface(
    fn=dummy_detect_and_generate_pdf,
    inputs=[
        gr.Image(type="pil", label="Upload Dental X-ray"),
        gr.Textbox(label="Patient ID (e.g., 12345 or P-001)")
    ],
    outputs=[
        gr.Image(label="X-ray with Detection (Prediction)"),
        gr.File(label="Download Report (PDF)")
    ],
    title="🦷 Dental X-ray Detection",
    description="Upload a dental X-ray image to receive a detection and a downloadable PDF report."
)

demo.launch(share=True)
