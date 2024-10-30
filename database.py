import os
from pymongo.mongo_client import MongoClient


class Database:
    def __init__(self):
        MONGO_URI = os.getenv("MONGO_URI")
        self.mongo = MongoClient(MONGO_URI)
        self.db = self.mongo['stock-alerts-app']

    def get_all_alerts(self):
        return self.db['stock-alerts'].find({}).to_list(None)

    def has_already_notif_today(self, alert_id):
        return self.db['notifications'].find_one({ 'alert_id': alert_id }) is not None

    def save_notification(self, alert_id):
        self.db['notifications'].insert_one({ 'alert_id': alert_id })

    def delete_all_notifications(self):
        self.db['notifications'].delete_many({})

    def save_aggregates(self, aggregates):
        self.db['aggregates'].insert_many(aggregates)

    def get_all_aggregates(self):
        return self.db['aggregates'].find({}).to_list(None)

    def delete_all_aggregates(self):
        self.db['aggregates'].delete_many({})

    def raw(self):
        return self.db