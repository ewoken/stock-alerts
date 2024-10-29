import os
from pymongo.mongo_client import MongoClient

def get_database():
    MONGO_URI = os.getenv("MONGO_URI")
    mongo = MongoClient(MONGO_URI)
    db = mongo['stock-alerts-app']
    return db

def get_all_alerts(db):
    return db['stock-alerts'].find({}).to_list(None)

def has_already_notif_today(db, alert_id):
    return db['notifications'].find_one({ 'alert_id': alert_id }) is not None

def save_notification(db, alert_id):
    db['notifications'].insert_one({ 'alert_id': alert_id })

def delete_all_notifications(db):
    db['notifications'].delete_many({})