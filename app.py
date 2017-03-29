import os
import random
import time
import subprocess
import redis
import cloudinary
import json
import uuid
import cloudinary.uploader
import io

from flask import Flask, request, render_template, session, flash, redirect, url_for, jsonify
from celery import Celery


app = Flask(__name__)
app.config['SECRET_KEY'] = 'top-secret!'

# Celery configuration
app.config['CELERY_BROKER_URL'] = 'redis://:devpassword@redis:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://:devpassword@redis:6379/0'


app.config['UPLOAD_FOLDER'] = './uploads/'


# Initialize Celery
celery = Celery(app.name, backend=app.config['CELERY_RESULT_BACKEND'], broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

cloudinary.config( 
  cloud_name = "[]", 
  api_key = "[]", 
  api_secret = "[]" 
)

from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage


def convert_pdf_to_txt(path):
    rsrcmgr = PDFResourceManager()
    retstr = io.StringIO()
    codec = 'utf-8'
    laparams = LAParams()
    device = TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
    fp = open(path, 'rb')
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    password = ""
    maxpages = 0
    caching = True
    pagenos=set()

    for page in PDFPage.get_pages(fp, pagenos, maxpages=maxpages, password=password,caching=caching, check_extractable=True):
        interpreter.process_page(page)

    text = retstr.getvalue()

    fp.close()
    device.close()
    retstr.close()
    return text


@celery.task(bind=True)
def convert_ocr(self, filename, newDir, uniqueId):
    ocr_filename = (filename.replace(".pdf","") + "_ocr.pdf")
    cmd = ['ocrmypdf', '--tesseract-pagesegmode','3', '-s', '-c', '-l', 'por', os.path.join(newDir, filename), os.path.join(newDir, ocr_filename)]
    print(cmd)
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    output = process.communicate()[0]
    print(output)
    process.wait()
    r = redis.client.StrictRedis(host='redis', port=6379, db=0, password='devpassword')
    upload_json = cloudinary.uploader.upload(os.path.join(newDir, ocr_filename), public_id = uniqueId+"/"+filename.replace(".pdf",""))
    upload_json["name"] = filename
    upload_json["text"] = convert_pdf_to_txt(os.path.join(newDir, ocr_filename))
    message = { "route": "update_file", "task_id": self.request.id, "data": upload_json }
    r.publish('pubsub', json.dumps(message))
    return message


@app.route('/upload', methods=['POST'])
def upload():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file:
            uniqueId = str(uuid.uuid4())
            uploadDir = os.path.dirname(app.config['UPLOAD_FOLDER'])
            newDir = uploadDir + "/" + uniqueId
            if not os.path.exists(newDir):
                os.makedirs(newDir)
            file.save(os.path.join(newDir, file.filename))
            task = convert_ocr.apply_async([file.filename, newDir, uniqueId])
            return jsonify({ 'task_id': task.id }), 202

@app.route('/status/<task_id>')
def taskstatus(task_id):
    task = convert_ocr.AsyncResult(task_id)
    if task.state == 'PENDING':
        response = {
            'state': 'pending'
        }
    elif task.state != 'FAILURE':
        response = {
            'state': 'completed',
        }
        response['result'] = task.info
    else:
        response = {
            'state': task.state,
            'status': str(task.info)
        }
    return jsonify(response)

@app.errorhandler(500)
def internal_server_error(error):
    print(error)
    return jsonify({ 'error': ':/' }), 500


if __name__ == '__main__':
    app.run(debug=True)


