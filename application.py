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

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()

application = app = Flask(__name__)
CORS(app)

UNKNOWN_FIELD_MSG = "unknown field in request"
INVALID_DATA_MSG = "invalid data type provided"


@app.route("/")
def health_check():
    return "<u>Hello World</u>"


@app.route("/api/catalog", methods=["GET"])
def get_full_catalog():
    res = ArtCatalogResource.retrieve_all_records()
    return Response(
        json.dumps(res), status=HTTPStatus.OK, content_type="application/json"
    )


@app.route("/api/catalog/<int:item_id>", methods=["GET"])
def get_catalog_item(item_id):
    res = ArtCatalogResource.retrieve_single_record(item_id)

    if not res:  # couldn't find anything with that ID
        return Response(
            json.dumps({"item_id": item_id}),
            status=HTTPStatus.NOT_FOUND,
            content_type="application/json",
        )
    else:
        return Response(
            json.dumps(res), status=HTTPStatus.OK, content_type="application/json"
        )


@app.route("/api/catalog", methods=["POST"])
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


@app.route("/api/catalog/<int:item_id>", methods=["PUT", "POST"])
def update_catalog_item(item_id):
    fields_to_update = request.get_json()
    json_s = json.dumps({"item_id": item_id, "status": "error"})
    status_code = HTTPStatus.INTERNAL_SERVER_ERROR

    try:
        res = ArtCatalogResource.update_item_by_id(item_id, fields_to_update)
        fields_to_update.update({"item_id": item_id, "status": "updated"})
        json_s = json.dumps(fields_to_update)
        status_code = HTTPStatus.OK
    except ArtCatalogResourceInvalidFieldException:
        json_s = json.dumps({"item_id": item_id, "status": UNKNOWN_FIELD_MSG})
        status_code = HTTPStatus.BAD_REQUEST
    except ArtCatalogResourceInvalidDataTypeException:
        json_s = json.dumps({"item_id": item_id, "status": INVALID_DATA_MSG})
        status_code = HTTPStatus.BAD_REQUEST

    return Response(json_s, status=status_code, content_type="application/json")


@app.route("/api/catalog/<int:item_id>", methods=["DELETE"])
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
    application.run(host="0.0.0.0", port=5000)
