import os
from flask import Flask, request, jsonify, render_template
from werkzeug.utils import secure_filename
import numpy as np
import keras
from keras.preprocessing import image
from keras import backend as K


UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

model = None
graph = None


def load_model():
    global model
    global graph
    model = keras.models.load_model('static/models/sklesion_img.h5')
    graph = K.get_session().graph


dx = ['akiec', 'bcc', 'bkl', 'df', 'mel', 'nv', 'vasc']


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


@app.route('/', methods=['GET', 'POST'])
def upload_file():

    data = {"success": False}
    results = None

    if request.method == 'POST':
        print(request)

        if request.files.get('file'):
            file = request.files['file']

            filename = file.filename

            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)

            file.save(filepath)

            image_size = (200, 200)
            predictions = predict(filepath)
            # jsonify([int(p) for p in predictions])
            results = [int(p) for p in predictions]

            return render_template("home.html", results=results)
    # return '''
    # <!doctype html>
    # <title>Upload new File</title>
    # <h1>Upload new File</h1>
    # <form method=post enctype=multipart/form-data>
      # <p><input type=file name=file>
         # <input type=submit value=Upload>
    # </form>
    # '''

    return render_template("home.html", results=results)


#if __name__ == '__main__':
#    app.run(debug=True)
if __name__ == '__main__':  
	port = int(os.getenv('PORT', 5000))
	print("Starting app on port %d" % port)
app.run(debug=False, port=port, host='0.0.0.0')