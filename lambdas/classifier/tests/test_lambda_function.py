import base64
import json
import os
from unittest import TestCase

from clip import clip

test_model = "/tmp/model/ViT-B-32.pt"


class TestLambda(TestCase):
    def setUp(self):
        os.environ["MODEL_PATH"] = test_model
        if not os.path.exists(test_model):
            clip.load("ViT-B/32", download_root=test_model)
        with open('game_stream_440x248.jpeg', 'rb') as file:
            self.test_image_game_stream = base64.b64encode(file.read()).decode('utf-8')
        with open('underwear_not_nude-440x248.jpeg', 'rb') as file:
            self.test_image_lingerie = base64.b64encode(file.read()).decode('utf-8')
        with open('religious-440x248.jpeg', 'rb') as file:
            self.test_image_religious = base64.b64encode(file.read()).decode('utf-8')

    def test_classifier_game_streamer(self):
        from lambdas.classifier import lambda_function
        response = lambda_function.handler({
            "body": json.dumps({
                "image_data": self.test_image_game_stream,
                "labels": ["gun", "game streamer", "nude", "music performance", "neutral"]
            }),
        }, {})

        self.assertEqual(response["statusCode"], 200)
        result = response["body"]["result"]
        self.assertGreater(result["game streamer"], 0.95)
        self.assertLess(result["neutral"], 0.05)

    def test_classifier_lingerie(self):
        from lambdas.classifier import lambda_function
        response = lambda_function.handler({
            "body": json.dumps({
                "image_data": self.test_image_lingerie,
                "labels": ["nude", "not nude"]
            }),
        }, {})

        self.assertEqual(response["statusCode"], 200)
        result = response["body"]["result"]
        self.assertGreater(result["not nude"], result["nude"])

    def test_classifier_religious(self):
        from lambdas.classifier import lambda_function
        response = lambda_function.handler({
            "body": json.dumps({
                "image_data": self.test_image_religious,
                "labels": ["jesus", "buddha", "non-religious"]
            }),
        }, {})

        self.assertEqual(response["statusCode"], 200)
        result = response["body"]["result"]
        self.assertGreater(result["jesus"], 0.90)
