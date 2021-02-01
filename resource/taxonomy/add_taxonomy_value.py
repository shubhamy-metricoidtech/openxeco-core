from flask_restful import Resource
from flask import request
from flask_jwt_extended import jwt_required
from sqlalchemy.exc import IntegrityError
from utils.verify_payload import verify_payload
from exception.object_already_existing import ObjectAlreadyExisting
from utils.log_request import log_request
from utils.catch_exception import catch_exception


class AddTaxonomyValue(Resource):

    db = None

    def __init__(self, db):
        self.db = db

    @log_request
    @catch_exception
    @verify_payload(format=[
        {'field': 'category', 'type': str},
        {'field': 'value', 'type': str}
    ])
    @jwt_required
    def post(self):
        input_data = request.get_json()

        if len(self.db.get(self.db.tables["TaxonomyCategory"], {"name": input_data["category"]})) == 0:
            return "", "422 the provided category does not exist"

        try:
            self.db.insert(
                {"name": input_data["value"], "category": input_data["category"]},
                self.db.tables["TaxonomyValue"]
            )
        except IntegrityError as e:
            self.db.session.rollback()
            if "Duplicate entry" in str(e):
                raise ObjectAlreadyExisting
            else:
                raise e

        return "", "200 "
