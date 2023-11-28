# Import the dependencies.

import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///hawaii.sqlite")

Base = automap_base()

#reflect db schema
Base.prepare(autoload_with = engine)

#save references

Station = Base.classes.station
Measurement = Base.classes.measurement

with Session(engine) as session:

    #################################################
    # Flask Setup
    #################################################
    app = Flask(__name__)

    # Variables
    m_date = Measurement.date
    m_prcp = Measurement.prcp
    s_station = Station.station
    m_id = Measurement.id
    m_station = Measurement.station
    m_tobs = Measurement.tobs
    
    # Find the most recent date in the data set.
    most_recent = session.query(m_date).\
        order_by(m_date.desc()).\
        first()

    one_year_ago = dt.date.fromisoformat(most_recent[0]) - dt.timedelta(days=365)

    # Find the most active station in the data set.
    count_id = func.count(m_id)
    most_active = session.query(m_station, count_id).\
        group_by(m_station).\
        order_by(count_id.desc()).\
        first()[0]

    #################################################
    # Flask Routes
    #################################################
    @app.route("/")
    def welcome():
        """List all available routes."""
        return (
            f"Hi, welcome. <br/>"
            f"<br/>"
            f"Available Routes:<br/>"
            f"/api/v1.0/precipitation<br/>"
            f"/api/v1.0/stations<br/>"
            f"/api/v1.0/tobs<br/>"
            f"/api/v1.0/start_date<br/>"
            f"/api/v1.0/start_date/end_date<br/>"
            f"<br/>"
            f"For start_date and end_date: <br/>"
            f"* use format yyyy-mm-dd<br/>"
            f"* enter dates in the interval [2010-01-01, 2017-08-23]<br/>"
        )


    @app.route("/api/v1.0/precipitation")
    def precipitation():

        precipitation_1yr = session.query(m_date, m_prcp).\
            filter(m_date >= one_year_ago).\
            all()

        """Only returns the jsonified precipitation data for the last year in the database"""
        precipitation_1yr_d = dict(precipitation_1yr)

        return jsonify(precipitation_1yr_d)


    @app.route("/api/v1.0/stations")
    def stations():
        """ Returns a JSON list of stations in the dataset """
    
        station_tl = session.query(s_station).\
            all()

        station_l = list(np.ravel(station_tl))

        return jsonify(station_l)


    @app.route("/api/v1.0/tobs")
    def tobs():
        """  jsonified data for the most active station (USC00519281) """
    
        tobs_1yr = session.query(m_date, m_tobs).\
            filter(m_station == most_active).\
            filter(m_date >= one_year_ago).\
            all()

        return jsonify([temp for date, temp in tobs_1yr])


    def def_dates(start, end = "2017-08-23"):
        """Returns the min, max, and average temperatures calculated from the given start date to the end of the dataset  """

        start_to_end = session.query(func.min(m_tobs), func.max(m_tobs), func.avg(m_tobs)).\
            filter(m_date >= start).\
            filter(m_date <= end).\
            all()

        return jsonify(list(np.ravel(start_to_end)))


    @app.route("/api/v1.0/<start>")
    def one_date(start):
        """Returns the min, max, and average temperatures calculated from the given start date to the end of the dataset"""

        return def_dates(start)


    @app.route("/api/v1.0/<start>/<end>")
    def two_dates(start, end):
        """ Returns the min, max, and average temperatures calculated from the given start date to the given end date"""

        return def_dates(start, end)

if __name__ == '__main__':
    app.run(debug=False)