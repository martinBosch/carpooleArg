import os
from flask_socketio import SocketIO
from pymongo import MongoClient
from repositories.trips_repository import TripsRepository

socketIO = SocketIO(cors_allowed_origins='*')

mongo_uri = os.environ.get("MONGO_URI")
trips_repository = TripsRepository(MongoClient(mongo_uri))
