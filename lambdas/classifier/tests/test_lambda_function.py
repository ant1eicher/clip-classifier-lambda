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
        with open('underwear_not_nude_440x248.jpeg', 'rb') as file:
            self.test_image_underwear = base64.b64encode(file.read()).decode('utf-8')
        with open('religious_aijesus_440x248.jpeg', 'rb') as file:
            self.test_image_religious = base64.b64encode(file.read()).decode('utf-8')
        with open('gun_toting_man_624x352.jpeg', 'rb') as file:
            self.test_image_gun = base64.b64encode(file.read()).decode('utf-8')
        with open('renaissance_painting_nude_900x632.jpg', 'rb') as file:
            self.test_image_painting = base64.b64encode(file.read()).decode('utf-8')

    def test_classifier_game_streamer(self):
        from lambdas.classifier import lambda_function
        response = lambda_function.handler({
            "body": json.dumps({
                "image_data": self.test_image_game_stream,
                "labels": ["just chatting", "game streamer", "nude nsfw", "music performance", "neutral"]
            }),
        }, {})

        self.assertEqual(response["statusCode"], 200)
        result = json.loads(response["body"])["result"]
        self.assertGreater(result["game streamer"], 0.91)
        self.assertLess(result["neutral"], 0.05)

    def test_classifier_underwear(self):
        from lambdas.classifier import lambda_function
        response = lambda_function.handler({
            "body": json.dumps({
                "image_data": self.test_image_underwear,
                "labels": ["nude", "not nude"]
            }),
        }, {})

        self.assertEqual(response["statusCode"], 200)
        result = json.loads(response["body"])["result"]
        self.assertGreater(result["not nude"], result["nude"])

    def test_classifier_religious(self):
        from lambdas.classifier import lambda_function
        response = lambda_function.handler({
            "body": json.dumps({
                "image_data": self.test_image_religious,
                "labels": ["jesus", "buddha", "ganesh", "non-religious"]
            }),
        }, {})

        self.assertEqual(response["statusCode"], 200)
        result = json.loads(response["body"])["result"]
        self.assertGreater(result["jesus"], 0.90)

    def test_classifier_gun(self):
        from lambdas.classifier import lambda_function
        response = lambda_function.handler({
            "body": json.dumps({
                "image_data": self.test_image_gun,
                "labels": ["real gun in hand", "real gun not in hand", "animated gun", "toy gun", "no gun"]
            }),
        }, {})

        self.assertEqual(response["statusCode"], 200)
        result = json.loads(response["body"])["result"]
        self.assertGreater(result["real gun in hand"], result["real gun not in hand"])
        self.assertGreater(result["real gun in hand"], result["no gun"])

    def test_classifier_painting_nude(self):
        from lambdas.classifier import lambda_function
        response = lambda_function.handler({
            "body": json.dumps({
                "image_data": self.test_image_painting,
                "labels": ["nude", "not nude"]
            }),
        }, {})

        self.assertEqual(response["statusCode"], 200)
        result = json.loads(response["body"])["result"]
        self.assertGreater(result["nude"], 0.90)

    def test_classifier_painting(self):
        from lambdas.classifier import lambda_function
        response = lambda_function.handler({
            "body": json.dumps({
                "image_data": self.test_image_painting,
                "labels": ["sketch", "photograph", "painting"]
            }),
        }, {})

        self.assertEqual(response["statusCode"], 200)
        result = json.loads(response["body"])["result"]
        self.assertGreater(result["painting"], 0.90)
