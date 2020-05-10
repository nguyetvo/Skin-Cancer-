#Skin Cancer Model Version 1.0.3
import os
from flask import Flask, request, jsonify, render_template, url_for
from werkzeug.utils import secure_filename
import numpy as np
import keras
from keras.preprocessing import image
from keras import backend as K
# please keep this import below. needed for db connection
from flask_sqlalchemy import SQLAlchemy

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

application = Flask(__name__)
application.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# please do not remove. connection to aws database instance
# # application.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://meghana95:awsMySQLmeg95@aaeybycoop6ulm.cfsmu6vnshf2.us-east-2.rds.amazonaws.com:3306/aaeybycoop6ulm'
# db = SQLAlchemy(application)

model = None
graph = None


def load_model():
    global model
    global graph
    model = keras.models.load_model('static/models/sklesion_img.h5')
    graph = K.get_session().graph


def predict(image_path):
    K.clear_session()
    model = keras.models.load_model('static/models/sklesion_img.h5')
    print()
    image_size = (200, 200)
    img = image.load_img(image_path, target_size=image_size)
    x = image.img_to_array(img)
    x = np.expand_dims(x, axis=0)
    predictions = list(model.predict(x)[0])
    return predictions


dx = ['akiec', 'bcc', 'bkl', 'df', 'mel', 'nv', 'vasc']
diagnoses = ["Bowen's Disease", "Basal Cell Carcinoma", "Benign Keratosis-like Lesion",
             "Dermatofibroma", "Melanoma", "Melanocytic Nevi", "Vascular Lesions"]
urls = ['https://www.webmd.com/cancer/what-is-bowens-disease#1',
        'https://www.webmd.com/melanoma-skin-cancer/basal-cell-carcinoma#1',
        'https://www.webmd.com/skin-problems-and-treatments/keratosis-pilaris#1',
        'https://www.webmd.com/skin-problems-and-treatments/picture-of-dermatofibroma',
        'https://www.webmd.com/melanoma-skin-cancer/default.htm',
        'https://emedicine.medscape.com/article/1058445-overview',
        'https://www.webmd.com/skin-problems-and-treatments/picture-of-vascular-malformations-hand']


def predictdx(predictions):
    """Read in list of confidence and return tuple of diagnosis and confidence"""
    ibest = predictions.index(max(predictions))
    x = diagnoses[ibest]
    y = '{:.0%}'.format(predictions[ibest])
    z = urls[ibest]
    return x, y, z


@application.route('/', methods=['GET', 'POST'])
def upload_file():

    data = {"success": False}
    diagnosis = None
    confidence = None
    info = print(url_for('upload_file'))

    if request.method == 'POST':
        print(request)

        if request.files.get('file'):
            file = request.files['file']

            filename = file.filename

            filepath = os.path.join(application.config['UPLOAD_FOLDER'], filename)

            file.save(filepath)

            image_size = (200, 200)
            predictions = predict(filepath)
            # jsonify([int(p) for p in predictions])
            # results = [int(p) for p in predictions]

            diagnosis, confidence, info = predictdx(predictions)

            return render_template("home.html", diagnosis=diagnosis, confidence=confidence, info=info)

    return render_template("home.html", diagnosis=diagnosis, confidence=confidence, info=info)



@application.route('/analysis')
def analysis():
    return render_template("analysis.html")

#if __name__ == '__main__':
#    application.run(debug=True)
if __name__ == '__main__':  
    port = int(os.getenv('PORT', 5000))
    print("Starting app on port %d" % port)
app.run(debug=False, port=port, host='0.0.0.0')
