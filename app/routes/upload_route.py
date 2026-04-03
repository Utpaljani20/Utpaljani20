from flask import Flask,render_template,request,redirect,url_for,Response,Blueprint,flash
from flask_sqlalchemy import SQLAlchemy
import os
from werkzeug.utils import secure_filename 
from app.models import Scan,db
from flask_login import login_required, current_user
from xhtml2pdf import pisa
from io import BytesIO
from flask import make_response,render_template,send_file
import tensorflow as tf
import numpy as np
from tensorflow.keras.preprocessing import image
from tensorflow.keras.models import load_model
import pytz 
from datetime import datetime
IST=pytz.timezone('Asia/Kolkata')

upload = Blueprint("upload",__name__)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, 'model', 'skinbuzz_pro_vision.keras')

model = load_model(MODEL_PATH)

classes = {
    0: 'Actinic keratoses', 1: 'Basal cell carcinoma', 
    2: 'Benign keratosis', 3: 'Dermatofibroma', 
    4: 'Melanocytic nevi', 5: 'Vascular lesions', 
    6: 'Melanoma (Cancer)'
}


def get_ai_prediction(filepath):
    img = image.load_img(filepath, target_size=(128, 128))
    img_array = image.img_to_array(img) / 255.0
    img_array = np.expand_dims(img_array, axis=0)


    prediction = model.predict(img_array)
    pred_idx = np.argmax(prediction)
    confidence = float(np.max(prediction))

    return classes[pred_idx], confidence

@upload.route("/")
def index():
    return render_template("index.html")

@upload.route("/contact")
def contact():
    return render_template("contact.html")
@upload.route("/sampark",methods=["POST","GET"])
def sampark():
    if request.method == 'POST':
        email=request.form.get("email")
        message=request.form.get("message")
        flash("You are Message is Recieved", "success")
        return redirect(url_for("upload.index"))
    return redirect(url_for("upload.contact"))



@upload.route("/upload-page")
@login_required
def upload_page():
    return render_template("upload.html")
allow_type={"jpeg","png","jpg","webp"}
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allow_type

@upload.route("/predict",methods=["POST","GET"])
@login_required
def predict():
    if request.method == 'POST':
        name=request.form.get("name")
        age=request.form.get("age")
        gender=request.form.get("gender")
        file=request.files.get('file')
        if file and allowed_file(file.filename):

            filename = secure_filename(file.filename)
            filepath=os.path.join('app/static/uploads',filename)
            file.save(filepath)
            res,conf=get_ai_prediction(filepath)

            # Save scan details to database
            new_scan = Scan(
                user_id=current_user.id,
                name=name,
                age=age,
                gender=gender,
                image_filename=filename,
                result=res,
                Confidence=conf,
                created_at=datetime.now(IST)
            )
            db.session.add(new_scan)
            db.session.commit()
            return render_template("result.html",name=name,result=res,confidence=conf,filename=filename,age=age,gender=gender,scan_id=new_scan.id)
        else:
            flash("Please Insert in JPG,PNG or JPEG Format!", "danger")
            return redirect(url_for("upload.upload_page"))
    return redirect(url_for("upload.index"))

@upload.route("/download-report/<int:scan_id>")
@login_required
def download_report(scan_id):
    # 1. Database se scan ki details lo
    scan = Scan.query.get_or_404(scan_id)

    base_dir=os.path.dirname(os.path.abspath(__file__))
    logo_path=os.path.join('app/static/img/logo-removebg-preview.png')
    # 2. PDF ke liye HTML render karo
    # Hum ek alag chota HTML file use karenge report ke liye
    html_content = render_template('report.html', scan=scan,logo_path=logo_path)
    
    # 3. PDF Generate karne ka logic
    pdf_buffer = BytesIO()
    pisa_status = pisa.CreatePDF(html_content, dest=pdf_buffer)
    
    if pisa_status.err:
        return "There is Error in Making PDF!", 500
    
    pdf_buffer.seek(0)
    
    # 4. User ko file download karwao
    return send_file(
        pdf_buffer,
        as_attachment=True,
        download_name=f"SkinBuzz_Report_{scan.id}.pdf",
        mimetype='application/pdf'
    )

