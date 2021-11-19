from flask import request
from application import app
from middleware.Notification.notification import SnsWrapper
import boto3
import os


@app.after_request
def after_decorator(rsp):
    if request.method == "POST":
        sns_wrapper = SnsWrapper(boto3.client('sns'))

        # create notification object
        topic = os.environ.get("SNSARN", None)
        sns_wrapper.publish_message(topic, request.json)
    return rsp
