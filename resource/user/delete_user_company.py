from flask_restful import Resource
from flask import request
from flask_jwt_extended import jwt_required
from decorator.verify_payload import verify_payload
from decorator.verify_admin_access import verify_admin_access
from decorator.catch_exception import catch_exception
from decorator.log_request import log_request
from exception.object_not_found import ObjectNotFound


class DeleteUserCompany(Resource):

    def __init__(self, db):
        self.db = db

    @log_request
    @verify_payload([
        {'field': 'user', 'type': int},
        {'field': 'company', 'type': int},
    ])
    @jwt_required
    @verify_admin_access
    @catch_exception
    def post(self):
        input_data = request.get_json()

        row = {
            "user_id": input_data["user"],
            "company_id": input_data["company"],
        }

        rights = self.db.get(self.db.tables["UserCompanyAssignment"], row)

        if len(rights) > 0:
            self.db.delete(self.db.tables["UserCompanyAssignment"], row)
        else:
            raise ObjectNotFound

        return "", "200 "
