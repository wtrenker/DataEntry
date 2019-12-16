from flask import Flask, render_template, flash, request, session, redirect, url_for
from pony.orm import Database, Optional, Required, PrimaryKey, db_session, sql_debug, select
import datetime as dt
from pathlib import Path
#import statistics as st
import os
import pony
import pprint
import logging
from logging.handlers import RotatingFileHandler
from forms import DataEntryForm, SelectReadingForm, EditReadingForm
from functions import decimalAverage
from collections import namedtuple

# App config.
##DEBUG = True
app = Flask(__name__)
app.config.from_object(__name__)
app.config['SECRET_KEY'] = os.urandom(512)

@app.errorhandler(405)
def methodNotAllowed(e):
    f = request.full_path.split('?', 1)[0]
    return render_template('405.jinja2', **locals()), 405

dbFile = "/home/bill/glucose2/glucose.db"
dbPath = Path(dbFile)
db = Database()

class Readings(db.Entity):
    date = PrimaryKey(str) #(dt.datetime)
    average = Optional(float)
    comment = Optional(str)
    hold = Optional(float)

db.bind(provider='sqlite', filename=str(dbPath), create_db=False)
db.generate_mapping(create_tables=False)

@app.route("/", methods=['GET'])
def home():
    flash(dbPath)
    with db_session:
        numberOfHeldReadings = len(Readings.select(lambda c: c.hold is not None))
        if numberOfHeldReadings == 0:
            flash('There are no partial readings.')
        elif numberOfHeldReadings == 1:
            flash('There is one partial reading.')
        else:
            flash(f'There are {numberOfHeldReadings} partial readings.')
    return render_template('Home.jinja2', **locals())

@app.route("/enter", methods=['GET', 'POST'])
def enter():

    flash(dbPath)

    if request.method == 'GET':
        form = DataEntryForm(request.form)
        return render_template('EnterReading.jinja2', **locals())

    elif request.method == 'POST':
        form = DataEntryForm(request.form)
        reqdate = request.form['ddate']
        comment = request.form['annotation']
        morning = request.form['amreading']
        evening = request.form['pmreading']
        if evening == '':
            average = None
            hold = morning
        else:
            average = decimalAverage(morning, evening)
            hold = None
        try:
            with db_session:
                Readings(date = reqdate, average = average, comment = comment, hold = hold)
        # except pony.orm.core.TransactionIntegrityError as e:
        except Exception as e:
            flash(f'ERROR (DataEnbry.py:64): {e}')
        return render_template('EnterReading.jinja2', **locals())

    else:
        return "fall through"

@app.route("/select", methods=['GET'])
def select():

    flash(dbPath)

    with db_session:
        heldReadings = Readings.select(lambda c: c.hold is not None).order_by(1)
        numberOfHeldReadings = len(heldReadings)
        heldReadingsList = list(heldReadings)
        if numberOfHeldReadings > 0:
            heldReadingDates = []
            index = 1
            for heldReading in heldReadingsList:
                heldReadingDates.append((f'D{index}', heldReading.date))
                index += 1
            form = SelectReadingForm()
            form.helddateslist.choices = heldReadingDates
            session['heldDates'] = heldReadingDates
            return render_template('SelectReading.jinja2', **locals())  # form=heldForm)
        else:
            return render_template('NoneHeld.jinja2', **locals())

@app.route("/edit", methods=['POST'])
def edit():

    flash(dbPath)

    form = SelectReadingForm(request.form)
    FormIndex = form.data['helddateslist']
    heldReadingDates = session['heldDates']
    # session.pop('heldDates')
    heldReadingDates = dict(heldReadingDates)
    WorkingDate = heldReadingDates[FormIndex]
    session['WorkingDate'] = WorkingDate
    with db_session:
        reading = Readings[WorkingDate]
        heldReading = namedtuple('heldReading', ['readingDate', 'amreading', 'annotation'])
        hr = heldReading(WorkingDate, reading.hold, reading.comment)
    form = EditReadingForm(obj=hr)
    return render_template('EditReading.jinja2', **locals())

@app.route("/update", methods=['POST'])
def update():
    WorkingDate = session['WorkingDate']
    session.pop('WorkingDate')
    form = EditReadingForm(request.form)
    evening = form.data['pmreading']
    if evening is None:
        return render_template('NoEvening.jinja2', **locals())
    with db_session:
        reading = Readings[WorkingDate]
        morning = reading.hold
        reading.hold = None
        reading.average = decimalAverage(morning, evening)
        reading.comment = form.data['annotation']
    return redirect(url_for('home'))


if __name__ == "__main__":

    # handler = RotatingFileHandler('foo.log', maxBytes=10000, backupCount=1)
    # handler.setLevel(logging.DEBUG)
    # handler.setLevel(logging.INFO)
    # app.logger.addHandler(handler)
    # app.logger.setLevel(logging.DEBUG)
    # l = app.logger.info

    app.debug = True
    app.logger = True

    app.run(host='wtrenker.com', port=7000, debug = True, use_reloader=False)
# use_reloader=False is the key to getting multi-threaded debug working in PyCharm
