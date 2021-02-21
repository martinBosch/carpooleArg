import os
from flask_socketio import SocketIO
from pymongo import MongoClient

from repositories.aco_configurations_repository import AcoConfigurationsRepository
from repositories.trips_repository import TripsRepository

socketIO = SocketIO(cors_allowed_origins='*')

mongo_uri = os.environ.get("MONGO_URI")
mono_client = MongoClient(mongo_uri)
trips_repository = TripsRepository(mono_client)
aco_configurations_repository = AcoConfigurationsRepository(mono_client)
