import gradio as gr
from PIL import Image
from fpdf import FPDF
import tempfile
import os
from datetime import datetime
from ultralytics import YOLO
import plotly.graph_objects as go
import numpy as np
from collections import Counter

# 1️⃣ Load your trained YOLOv8 model
model = YOLO(r"C:\Users\User\OneDrive\Desktop\FinalDentalAssistantModel\runs\detect\train2\weights\best.pt")

# 2️⃣ Function: Detection + PDF generation
def detect_and_generate_pdf(img, patient_id):
    if not patient_id.strip():
        raise gr.Error("❗ Patient ID is required to generate the report.")

    # Run YOLO inference
    results = model(img)

    # Extract boxes, labels, conf
    boxes = results[0].boxes.xyxy.cpu().numpy()
    classes = results[0].boxes.cls.cpu().numpy().astype(int)
    confs = results[0].boxes.conf.cpu().numpy()
    names = results[0].names

    # Convert image to numpy for Plotly
    img_np = np.array(img)

    # Create Plotly figure
    fig = go.Figure()
    fig.add_trace(go.Image(z=img_np))

    # Color map for unique classes
    colors = {}
    palette = [
        "#FF0000", "#00FF00", "#0000FF", "#FFA500", "#800080",
        "#00FFFF", "#FFC0CB", "#A52A2A", "#808000", "#008080"
    ]

    for i, (box, cls_id, conf) in enumerate(zip(boxes, classes, confs)):
        label = names[cls_id]
        if cls_id not in colors:
            colors[cls_id] = palette[len(colors) % len(palette)]

        x1, y1, x2, y2 = box

        # Draw transparent rectangle for bounding box
        fig.add_shape(
            type="rect",
            x0=x1, y0=y1, x1=x2, y1=y2,
            line=dict(color=colors[cls_id], width=2),
            fillcolor="rgba(0,0,0,0)"
        )

        # Add invisible scatter for hover tooltip
        fig.add_trace(go.Scatter(
            x=[x1, x2],
            y=[y1, y2],
            mode="markers",
            marker_opacity=0,
            hoverinfo="text",
            text=[f"{label} ({conf:.2f})"] * 2
        ))

    fig.update_xaxes(showticklabels=False).update_yaxes(showticklabels=False)
    fig.update_layout(margin=dict(l=0, r=0, t=0, b=0), dragmode=False)

    # Save annotated image for PDF
    annotated_img_path = os.path.join(tempfile.gettempdir(), f"{patient_id}_pred.png")
    results[0].save(filename=annotated_img_path)
    annotated_img = Image.open(annotated_img_path)

    # Create PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, txt="Dental X-ray Analysis Report", ln=True, align='C')
    pdf.cell(200, 10, txt=f"Patient ID: {patient_id}", ln=True)
    pdf.cell(200, 10, txt=f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True)

    # Count detections per class
    label_counts = Counter([names[c] for c in classes])
    if label_counts:
        issues_summary = ", ".join(
            [f"{count} {label}{'s' if count > 1 else ''}" for label, count in label_counts.items()]
        )
    else:
        issues_summary = "None"

    pdf.cell(200, 10, txt=f"Detected Issues: {issues_summary}", ln=True)

    # Insert annotated image into PDF
    pdf.image(annotated_img_path, x=10, y=50, w=80)

    # Save PDF to temp path
    pdf_filename = f"{patient_id}_report.pdf"
    pdf_path = os.path.join(tempfile.gettempdir(), pdf_filename)
    pdf.output(pdf_path)

    # Return interactive plot + PDF file
    return fig, pdf_path

# 3️⃣ Gradio interface
demo = gr.Interface(
    fn=detect_and_generate_pdf,
    inputs=[
        gr.Image(type="pil", label="Upload Dental X-ray"),
        gr.Textbox(label="Patient ID (e.g., 12345 or P-001)")
    ],
    outputs=[
        gr.Plot(label=" Detection Result"),
        gr.File(label="Download Report (PDF)")
    ],
    title="🦷 Dental X-ray Detection",
    description="Upload a dental X-ray to get hover-enabled YOLO detection and a PDF report."
)

# 4️⃣ Launch app
demo.launch(share=True)
