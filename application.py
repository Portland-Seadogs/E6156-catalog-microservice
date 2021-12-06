from flask import Flask, Response, request
from flask_cors import CORS
from application_services.art_catalog_resource import (
    ArtCatalogResource,
    ArtCatalogResourceInvalidFieldException,
    ArtCatalogResourceInvalidDataTypeException,
)
import json
import logging
from http import HTTPStatus
from middleware.security.security import Security
from middleware.Notification.notification import SnsWrapper
import boto3
import os


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()

application = Flask(__name__)
CORS(application)

UNKNOWN_FIELD_MSG = "unknown field in request"
INVALID_DATA_MSG = "invalid data type provided"


@application.before_request
def verify_oauth_token():
    """
    Method to run before all requests; determines if a user has a valid
    Google OAuth2 token and uses the token to discover who the user making the request is.
    The google user and auth token loaded into special flask object called 'g'.
    While g is not appropriate for storing data across requests, it provides a global namespace
    for holding any data you want during a single request.
    """
    if request.method != 'OPTIONS':
        return Security.verify_token(request)
    else:
        return None


@application.after_request
def after_decorator(rsp):
    if request.method == "POST":
        sns_wrapper = SnsWrapper(boto3.client("sns"))

        # create notification object
        topic = os.environ.get("SNSARN", None)
        sns_wrapper.publish_message(topic, request.json)
    return rsp


@application.route("/")
def health_check():
    return "<u>Hello World</u>"


@application.route("/api/catalog", methods=["GET"])
def get_full_catalog():
    print('here')
    res = ArtCatalogResource.retrieve_all_records()
    if res:
        [
            item.update(
                {
                    "links": [
                        {
                            "rel": "catalog_item",
                            "href": f'/api/catalog/{item["item_id"]}',
                        }
                    ]
                }
            )
            for item in res
        ]    
    return Response(
        json.dumps(res), status=HTTPStatus.OK, content_type="application/json"
    )


@application.route("/api/catalog/<int:item_id>", methods=["GET"])
def get_catalog_item(item_id):
    res = ArtCatalogResource.retrieve_single_record(item_id)

    if not res:  # couldn't find anything with that ID
        return Response(
            json.dumps({"item_id": item_id}),
            status=HTTPStatus.NOT_FOUND,
            content_type="application/json",
        )
    else:
        result = (
            {"item": res, "links": [{"rel": "self", "href": f"/api/catalog/{item_id}"}]}
            if res
            else None
        )
        return Response(
            json.dumps(result), status=HTTPStatus.OK, content_type="application/json"
        )


@application.route("/api/catalog", methods=["POST"])
def add_new_catalog_item():
    json_s = None
    status_code = HTTPStatus.INTERNAL_SERVER_ERROR

    try:
        res = ArtCatalogResource.add_new_product(request.get_json())
        json_s = json.dumps({"item_id": res}) if res != 0 else ""
        status_code = HTTPStatus.CREATED
    except ArtCatalogResourceInvalidFieldException:
        json_s = json.dumps({"status": UNKNOWN_FIELD_MSG})
        status_code = HTTPStatus.BAD_REQUEST
    except ArtCatalogResourceInvalidDataTypeException:
        json_s = json.dumps({"status": INVALID_DATA_MSG})
        status_code = HTTPStatus.BAD_REQUEST

    return Response(json_s, status_code, content_type="application/json")


@application.route("/api/catalog/<int:item_id>", methods=["PUT", "POST"])
def update_catalog_item(item_id):
    fields_to_update = request.get_json() if request.get_json() else {}
    json_s = json.dumps({"item_id": item_id, "status": "error"})
    status_code = HTTPStatus.INTERNAL_SERVER_ERROR

    try:
        res = ArtCatalogResource.update_item_by_id(item_id, fields_to_update)
        fields_to_update.update(
            {
                "item_id": item_id,
                "status": "updated",
                "links": [{"rel": "self", "href": f"/api/catalog/{item_id}"}],
            }
        )
        json_s = json.dumps(fields_to_update)
        status_code = HTTPStatus.OK
    except ArtCatalogResourceInvalidFieldException:
        json_s = json.dumps({"item_id": item_id, "status": UNKNOWN_FIELD_MSG})
        status_code = HTTPStatus.BAD_REQUEST
    except ArtCatalogResourceInvalidDataTypeException:
        json_s = json.dumps({"item_id": item_id, "status": INVALID_DATA_MSG})
        status_code = HTTPStatus.BAD_REQUEST

    return Response(json_s, status=status_code, content_type="application/json")


@application.route("/api/catalog/<int:item_id>", methods=["DELETE"])
def delete_catalog_item(item_id):
    res = ArtCatalogResource.delete_item_by_id(item_id)

    if res == 1:
        json_s = json.dumps({"item_id": item_id, "status": "deleted"})
        status_code = (HTTPStatus.OK,)
    elif res == 0:
        json_s = json.dumps({"item_id": item_id})
        status_code = (HTTPStatus.NOT_FOUND,)
    else:
        json_s = json.dumps({"item_id": item_id, "status": "error"})
        status_code = HTTPStatus.INTERNAL_SERVER_ERROR

    return Response(json_s, status=status_code, content_type="application/json")


if __name__ == "__main__":
    application.run(host="0.0.0.0", port=7777)
