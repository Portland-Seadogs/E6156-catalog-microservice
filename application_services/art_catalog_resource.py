from application_services.base_application_resource import BaseApplicationResource
import database_services.rdb_service as d_service


class ArtCatalogResourceInvalidFieldException(BaseException):
    def __init__(self, msg=None):
        self.msg = msg


class ArtCatalogResourceInvalidDataTypeException(BaseException):
    def __init__(self, msg=None):
        self.msg = msg


class ArtCatalogResource(BaseApplicationResource):
    db_schema = "art_catalog"
    table_name = "products"

    expected_types = {
        "artist": [str],
        "title": [str],
        "description": [str],
        "width": [float, int],
        "height": [float, int],
        "price": [float, int],
        "img_url": [str],
        "comments": [str],
    }

    def __init__(self):
        super().__init__()

    def get_links(self, resource_data):
        pass

    @classmethod
    def retrieve_all_records(cls):
        return d_service.fetch_all_records(cls.db_schema, cls.table_name)

    @classmethod
    def retrieve_single_record(cls, record_id):
        return d_service.find_by_template(
            cls.db_schema, cls.table_name, {"item_id": record_id}
        )

    @classmethod
    def add_new_product(cls, item_information):
        if cls.is_valid_input(item_information):
            new_record_id = d_service.create_new_record(
                cls.db_schema, cls.table_name, **item_information
            )
            return new_record_id

    @classmethod
    def update_item_by_id(cls, item_id, updated_information):
        if cls.is_valid_input(updated_information):
            return d_service.update_record(
                cls.db_schema, cls.table_name, "item_id", item_id, **updated_information
            )

    @classmethod
    def delete_item_by_id(cls, record_id):
        return d_service.delete_record_by_key(
            cls.db_schema, cls.table_name, "item_id", record_id
        )

    @classmethod
    def is_valid_input(cls, field_information):
        # pymysql will cast data to fit schema; to prevent this, some explicit checks
        # in application layer are made
        if any(not cls._field_exists(field) for field in field_information.keys()):
            raise ArtCatalogResourceInvalidFieldException()
        if any(
            not cls._valid_d_type(field, value)
            for field, value in field_information.items()
        ):
            raise ArtCatalogResourceInvalidDataTypeException()
        return True

    @classmethod
    def _field_exists(cls, field):
        return field in cls.expected_types.keys()

    @classmethod
    def _valid_d_type(cls, variable, value):
        return type(value) in cls.expected_types[variable]
