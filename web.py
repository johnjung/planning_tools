import csv
import os
from flask import Flask, flash, make_response, render_template, request
from planning_tools.classes import Matrix
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = set(('csv'))
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = '/tmp'

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'GET':
        return render_template('home.html')
    elif request.method == 'POST':
        f = None
        if 'file' in request.files:
            f = request.files['file']
            if f.filename == '':
                f = None
        if not f:
            os.path.dirname(os.path.abspath(__file__))
            f = open(
                '{0}{1}sample_data{1}fruits_and_vegetables.csv'.format(
                    os.path.dirname(os.path.abspath(__file__)),
                    os.sep
                )
            )
        m = Matrix()
        m.import_from_csv(f)
        m.cluster(request.form['linkage_method'])
        output = make_response(m.csv())
        output.headers["Content-Disposition"] = "attachment; filename=export.csv"
        output.headers["Content-type"] = "text/csv"
        return output


if __name__ == '__main__':
    app.run()
