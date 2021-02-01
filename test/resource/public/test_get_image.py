from test.BaseCase import BaseCase
from unittest.mock import patch
import os


class TestGetImage(BaseCase):

    @patch('resource.public.get_image.IMAGE_FOLDER', os.path.join(os.path.dirname(os.path.realpath(__file__)), "test_get_image"))
    def test_ok(self):

        response = self.application.get('/public/get_image/50')

        self.assertEqual(200, response.status_code)

    def test_ko_missing_file(self):

        response = self.application.get('/public/get_image/50')

        self.assertEqual("500 Image not found", response.status)
