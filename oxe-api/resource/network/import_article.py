from flask_apispec import MethodResource
from flask_apispec import use_kwargs, doc
from flask_jwt_extended import fresh_jwt_required
from flask_restful import Resource
from webargs import fields
import json
import traceback
import base64

from decorator.catch_exception import catch_exception
from decorator.log_request import log_request
from decorator.verify_admin_access import verify_admin_access
from exception.object_not_found import ObjectNotFound
from utils import request
from urllib.error import HTTPError
from resource.media.add_image import AddImage


class ImportArticle(MethodResource, Resource):

    db = None

    def __init__(self, db):
        self.db = db

    @log_request
    @doc(tags=['network'],
         description='Import an article from a network node',
         responses={
             "200": {},
             "422.a": {"description": "Object not found: Network node"},
             "500": {"description": "Error while fetching the network node article"},
         })
    @use_kwargs({
        'network_node_id': fields.Int(),
        'article_id': fields.Int(),
        'sync_global': fields.Bool(required=False, missing=False),
        'sync_content': fields.Bool(required=False, missing=False),
    })
    @fresh_jwt_required
    @verify_admin_access
    @catch_exception
    def post(self, **kwargs):

        # Fetch the node information

        try:
            node = self.db.get_by_id(kwargs["network_node_id"], self.db.tables["NetworkNode"])
        except Exception:
            raise ObjectNotFound("Network node")

        # Fetch the article data from the node

        article_image = None

        try:
            article = request.get_request(f"{node.api_endpoint}/public/get_public_article/{kwargs['article_id']}")
            article = json.loads(article)

            if article["image"] is not None:
                article_image = request \
                    .get_request(f"{node.api_endpoint}/public/get_public_image/{article['image']}")

            try:
                article_content = request \
                    .get_request(f"{node.api_endpoint}/public/get_public_article_content/{kwargs['article_id']}")
                article_content = json.loads(article_content)["content"]
            except HTTPError:
                article_content = []
        except Exception:
            traceback.print_exc()
            return "", "500 Error while fetching the network node article"

        # Create the article locally

        if article_image is not None:
            article_image_response = self.create_image(article_image)
            if article_image_response[1].startswith("200"):
                article_image = article_image_response[0]
            else:
                return article_image_response
        article = self.create_article(article, article_image, **kwargs)
        article_version = self.create_article_version(article)
        self.create_article_content(article_content, article_version)

        # Terminate the import

        self.db.session.commit()

        return "", "200 "

    def create_image(self, image):
        add_image = AddImage(self.db)
        return add_image.add_image(image=base64.b64encode(image).decode('utf-8'))

    def create_article(self, article, article_image, **kwargs):

        del article["id"]
        article = {
            **article,
            **{
                "sync_node": kwargs["network_node_id"],
                "sync_id": kwargs["article_id"],
                "sync_global": kwargs["sync_global"],
                "sync_content": kwargs["sync_content"],
                "sync_status": "OK",
                "is_created_by_admin": True,
                "image": article_image["id"] if article_image is not None else None,
            },
        }

        return self.db.insert(article, self.db.tables["Article"], commit=False, flush=True)

    def create_article_version(self, article):

        article_version = {
            "name": "Generated by synchronization",
            "is_main": 1,
            "article_id": article.id,
        }

        return self.db.insert(article_version, self.db.tables["ArticleVersion"], commit=False, flush=True)

    def create_article_content(self, article_content, article_version):

        boxes = list()

        for b in article_content:
            boxes.append({
                "position": b["position"],
                "type": b["type"],
                "content": b["content"],
                "article_version_id": article_version.id,
            })

        self.db.insert(boxes, self.db.tables["ArticleBox"], commit=False, flush=True)
