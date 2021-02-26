import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt

from flask import Flask, jsonify

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

Base = automap_base()

Base.prepare(engine, reflect=True)

measurement = Base.classes.measurement
station = Base.classes.station

app = Flask(__name__)

@app.route("/")
def welcome():
    """List all available api routes"""
    return(
        f"Available Routes:<br/>"
        f"Precipitation: /api/v1.0/precipitation<br/>"
        f"Stations: /api/v1.0/stations<br/>"
        f"Temperatures: /api/v1.0/tobs<br/>"
        f"Temperature stat start date (yyyy-mm-dd): /api/v1.0/yyyy-mm-dd<br/>"
        f"Temperature stat from start to end dates(yyyy-mm-dd): /api/v1.0/yyyy-mm-dd/yyyy-mm-dd"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    
    results = session.query(measurement.date, measurement.prcp).all()

    session.close()

    all_dates = []
    for date, prcp in results:
        dates_dict = {}
        dates_dict[date] = prcp
        all_dates.append(dates_dict)

    return jsonify(all_dates)

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)

    results = session.query(station.station).all()

    session.close()

    all_stations = list(np.ravel(results))

    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def mostActive():
    session = Session(engine)

    year_ago = dt.date(2017,8,23) - dt.timedelta(days=365)
    station = measurement.station
    count = func.count(measurement.station)

    most_active = session.query(station).group_by(station).order_by(count.desc()).first()

    station = most_active[0]

    results = session.query(measurement.date, measurement.tobs).filter(measurement.date >= year_ago).\
        filter(measurement.station == station).all()

    session.close()

    temp_data = []

    for date, tobs in results:
        new_dict = {}
        new_dict[date] = tobs
        temp_data.append(new_dict)

    return jsonify(temp_data)

@app.route("/api/v1.0/<start>")
def startTemperatures(start):

    session = Session(engine)

    results = session.query(
        func.min(measurement.tobs),\
        func.max(measurement.tobs),\
        func.avg(measurement.tobs)).filter(measurement.date >= start).all()
    
    session.close()

    temp_analysis = []

    for min, max, avg in results:
        temp_dict = {}
        temp_dict["Min"] = min
        temp_dict["Max"] = max
        temp_dict["Avg"] = avg
        temp_analysis.append(temp_dict)

    return jsonify(temp_analysis)

@app.route("/api/v1.0/<start>/<end>")
def endTemperatures(start, end):

    session = Session(engine)

    results = session.query(
        func.min(measurement.tobs),
        func.max(measurement.tobs),
        func.avg(measurement.tobs)).filter(measurement.date >= start).filter(measurement.date <= end).all()
    
    session.close()

    temp_analysis = []

    for min, max, avg in results:
        temp_dict = {}
        temp_dict["Min"] = min
        temp_dict["Max"] = max
        temp_dict["Avg"] = avg
        temp_analysis.append(temp_dict)

    return jsonify(temp_analysis)

if __name__ == '__main__':
    app.run(debug=True)