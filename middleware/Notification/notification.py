import json
import time
import boto3
from botocore.exceptions import ClientError


class SnsWrapper:
    """Encapsulates Amazon SNS topic and subscription functions."""

    def __init__(self, sns_resource):
        """
        :param sns_resource: A Boto3 Amazon SNS resource.
        """
        self.sns_resource = sns_resource

    def list_topics(self):
        """
        Lists topics for the current account.

        :return: An iterator that yields the topics.
        """

        try:
            topics_iter = self.sns_resource.list_topics()
        except ClientError:
            print("Couldn't get topics.")
            raise
        else:
            return topics_iter

    # @classmethod
    def publish_message(self, topic, message):
        """
        Publishes a message, with attributes, to a topic. Subscriptions can be filtered
        based on message attributes so that a subscription receives messages only
        when specified attributes are present.

        :param topic: The topic to publish to.
        :param message: The message to publish.
        :param attributes: The key-value attributes to attach to the message. Values
                           must be either `str` or `bytes`.
        :return: The ID of the message.
        """
        try:
            rsp = self.sns_resource.publish(
                TargetArn=topic,
                Message=json.dumps({"default": json.dumps(message)}),
                MessageStructure="json",
            )
            print("Published message with attributes %s to topic %s.", message, topic)
        except Exception as e:
            print(f"Could not publish message: {e}")
            return
