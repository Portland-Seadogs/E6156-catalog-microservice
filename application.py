from flask import Flask, Response, request
from flask_cors import CORS
from application_services.art_catalog_resource import ArtCatalogResource
import json
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()

application = app = Flask(__name__)
CORS(app)


@app.route("/")
def health_check():
    return "<u>Hello World</u>"


@app.route("/api/catalog", methods=["GET"])
def get_full_catalog():
    res = ArtCatalogResource.retrieve_all_records()
    rsp = Response(json.dumps(res), status=200, content_type="application/json")
    return rsp


@app.route("/api/catalog/<int:item_id>", methods=["GET"])
def get_catalog_item(item_id):
    res = ArtCatalogResource.retrieve_single_record(item_id)
    rsp = Response(json.dumps(res), status=200, content_type="application/json")
    return rsp


@app.route("/api/catalog", methods=["POST"])
def add_new_catalog_item():
    res = ArtCatalogResource.add_new_product(request.get_json())
    rsp = Response(json.dumps(res), status=201, content_type="application/json")
    return rsp


@app.route("/api/catalog/<int:item_id>", methods=["PUT"])
def update_catalog_item(item_id):
    fields_to_update = request.get_json()
    res = ArtCatalogResource.update_item_by_id(item_id, fields_to_update)

    if res == 1:
        fields_to_update.update({"item_id": item_id, "status": "updated"})
        rsp = Response(
            json.dumps(fields_to_update), status=200, content_type="application/json"
        )
    else:
        rsp = Response(
            json.dumps({"item_id": item_id, "status": "error"}),
            status=500,
            content_type="application/json",
        )
    return rsp


@app.route("/api/catalog/<int:item_id>", methods=["DELETE"])
def delete_catalog_item(item_id):
    res = ArtCatalogResource.delete_item_by_id(item_id)

    if res == 1:
        rsp = Response(
            json.dumps({"item_id": item_id, "status": "deleted"}),
            status=200,
            content_type="application/json",
        )
    else:
        rsp = Response(
            json.dumps({"item_id": item_id, "status": "error"}),
            status=500,
            content_type="application/json",
        )
    return rsp


if __name__ == "__main__":
    application.run(host="0.0.0.0", port=5000)
