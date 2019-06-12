from flask import Flask, flash, make_response, render_template, request
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = set(('csv'))
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = '/tmp'

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/cardsort/', methods = ['GET', 'POST'])
def cardsort():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part.')
            return render_template('cardsort.html')

        f = requset.files['file']
        if f.filename == '':
            flash('No file part.')
            return render_template('cardsort.html')

        # add troubleshooting messages here. 

        c = CardSort()
        c.import_from_csv(f)
        m = Matrix()
        m.import_from_csv(c.csv())
        m.cluster(request.linkage_method)
        s = StringIO.StringIO()
        csv_writer = csv.writer(s)
        csv_writer.writerows(m.csv())
        output = make_response(s.getvalue())
        output.headers["Content-Disposition"] = "attachment; filename=export.csv"
        output.headers["Content-type"] = "text/csv"
        return output
    elif request.method == 'GET':
        return render_template('cardsort.html')

@app.route('/interactions/', methods = ['GET', 'POST'])
def interactions():
    if request.method == 'POST':
        pass
    return render_template('interactions.html')

@app.route('/matrix/', methods = ['GET', 'POST'])
def matrix():
    if request.method == 'POST':
        pass
    return render_template('matrix.html')

@app.route('/similarity/', methods = ['GET', 'POST'])
def similarity():
    if request.method == 'POST':
        pass
    return render_template('similarity.html')


if __name__ == '__main__':
    app.run()
