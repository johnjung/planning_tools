import os
import random
import sqlite3
import sys

from flask import Flask, flash, jsonify, render_template, request
from planning_tools.classes import Matrix

app = Flask(__name__)

# Display the current state of the matrix on the homepage. (look at this part
# on a projector.)
@app.route('/')
def home():
    return render_template('home.html')

# Display the interface for comparing two elements (look at this part on
# smartphones.)
@app.route('/compare', methods=['GET', 'POST'])
def compare():
    conn = sqlite3.connect(
        os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            'insightmatrix.db'
        )
    )
    cur = conn.cursor()

    def all_comparisons_present():
        label_count = len(Label.query.all())
        comparison_count = len(Comparison.query.all())
        max_comparison_count = sum([i + 1 for i in range(label_count)])
        return comparison_count == max_comparison_count

    def comparison_present(label_one, label_two):
        for c in Comparison.query.all():
            sys.stdout.write(c) 
            if c.label_one.label == request.form.get('label_one') and \
                c.label_two.label == request.form.get('label_two'):
                return True
            if c.label_one.label == request.form.get('label_two') and \
                c.label_two.label == request.form.get('label_one'):
                return True
        return False
 
    if request.method == 'POST':
        if not comparison_present(
            request.form.get('label_one'),
            request.form.get('label_two')
        ):
            db.session.add(
                Comparison(
                    label_one_id=request.form.get('label_one'),
                    label_two_id=request.form.get('label_two'),
                    comparison=int(request.form.get('comparison'))
                )
            )
            db.session.commit()

    if all_comparisons_present():
        return render_template('compare_no_more_comparisons.html')
    else:
        m = Matrix()
        cur.execute('SELECT label FROM label;')
        labels = [row[0] for row in cur.fetchall()]

        # m.import_labels(labels, labels)

        # build up a set of all possible comparisons.
        comparisons = set()
        for label_one in labels:
            for label_two in labels:
                comparisons.add((label_one, label_two))

        # remove the comparisons that are present in the database.
        for c in Comparison.query.all():
            sys.stdout.write(c.label_one.label)
            comparisons.discard((c.label_one.label, c.label_two.label))

        # select two remaining elements at random.
        comparisons = list(comparisons)
        random.shuffle(comparisons)
        label_one, label_two = comparisons[0]
            
        return render_template(
            'compare.html',
            label_one=label_one,
            label_two=label_two
        )

@app.route('/json')
def json():
    """Get JSON data to render the matrix: e.g., 
    {
        "comparisons": [
            {"label_one": "apples", "label_two": "apples", "comparison": 3},
            {"label_one": "oranges", "label_two": "oranges", "comparison": 3},
            {"label_one": "bananas", "label_two": "bananas", "comparison": 3}
        ],
        "labels": ["apples", "oranges", "bananas"],
    }
    """
    m = Matrix()
    # m.import_labels([l.label for l in Label.query.all()])

    labels = []
    comparisons = []

    # m.import_data(comparisons)
    # how processor-intensive is this? do I need a timestamp for the last time
    # this happened?
    # m.cluster()

    return jsonify({
        'comparisons': comparisons,
        'labels': labels
    })

# Reset the matrix.
@app.route('/reset')
def reset():
    labels = ['peppers', 'cucumbers', 'celery', 'tomatoes', 'onions',
        'spinach', 'lettuce', 'limes', 'lemons', 'pineapples', 'oranges',
        'grapefruit', 'potatoes', 'cabbage', 'squash', 'corn', 'peas', 'beans',
        'carrots', 'broccoli', 'avocados', 'bananas', 'apples', 'pears',
        'peaches', 'strawberries', 'raspberries', 'grapes', 'figs',
        'cherries']

    conn = sqlite3.connect(
        os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            'insightmatrix.db'
        )
    )
    c = conn.cursor()
    c.execute("DROP TABLE IF EXISTS test;")
    c.execute("""CREATE TABLE test (
                     id INTEGER NOT NULL, 
                     PRIMARY KEY (id)
                 );""")
    c.execute("DROP TABLE IF EXISTS label;")
    c.execute("""CREATE TABLE label (
                     id INTEGER NOT NULL, 
                     label VARCHAR(250) NOT NULL, 
                     test_id INTEGER NOT NULL, 
                     PRIMARY KEY (id), 
                     FOREIGN KEY(test_id) REFERENCES test (id)
                 );""")
    c.execute("DROP TABLE IF EXISTS comparison;")
    c.execute("""CREATE TABLE comparison (
                     id INTEGER NOT NULL, 
                     label_one_id INTEGER NOT NULL, 
                     label_two_id INTEGER NOT NULL, 
                     comparison INTEGER NOT NULL, 
                     PRIMARY KEY (id), 
                     FOREIGN KEY(label_one_id) REFERENCES label (id), 
                     FOREIGN KEY(label_two_id) REFERENCES label (id)
                 );""")
    conn.commit()
    c.execute("INSERT INTO test (id) VALUES (?);", (1,))
    conn.commit()
    for l in labels:
        c.execute("INSERT INTO label (id, label, test_id) VALUES (?, ?, ?);", (None, l, 1))
    conn.commit()

    for l in labels:
        c.execute("INSERT INTO comparison (id, label_one_id, label_two_id, comparison) SELECT NULL, id, id, 3 FROM label WHERE label='{}';".format(l))
    conn.commit()

    conn.close()
    return render_template('reset.html')


if __name__ == '__main__':
    app.run()
