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
        dates_dict["date"] = date
        dates_dict["precipitation"] = prcp
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

    temp_data = session.query(measurement.tobs).filter(measurement.date >= year_ago).\
        filter(measurement.station == station).all()

    session.close()

    return jsonify(list(np.ravel(temp_data)))

if __name__ == '__main__':
    app.run(debug=True)