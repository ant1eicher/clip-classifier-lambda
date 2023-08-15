import base64
import collections
import json
import requests

# Obtained from Cloudformation stack outputs
ENDPOINT = "https://foofoofoo.execute-api.eu-west-1.amazonaws.com/prod/"
IMAGE = "test_images/game_stream_440x248.jpeg"
LABELS_MAP = {
    "a thumbnail with a blank or logo": "neutral",
    "a thumbnail of a sexy person": "suggestive",
    "a thumbnail of a sport": "sport",
    "a thumbnail containing explicit adult content": "explicit",
    "a thumbnail of a casual gaming stream": "gaming",
    "a thumbnail with suggestive content": "suggestive",
    "a thumbnail of a music performance": "music",
    "a thumbnail containing real-world violent content": "violence",
    "a thumbnail showing violent content from a video game": "gaming",
}


# Call the CLIP endpoint with moderation labels.
def moderate_image():
    # Load image and base64 encode
    with open(IMAGE, "rb") as f:
        content = f.read()
        encoded_content_str = base64.b64encode(content).decode("utf-8")

    payload = {
        'image_data': encoded_content_str,
        'labels': list(LABELS_MAP.keys())
    }

    headers = {'Content-Type': 'application/json'}

    # Call classifier
    resp = requests.post(ENDPOINT, data=json.dumps(payload), headers=headers)

    if resp.status_code != 200:
        print("Invalid response code: {} error: {}".format(resp.status_code, resp.text))
        exit(1)

    results = collections.defaultdict(float)
    for k, v in json.loads(resp.text)["result"].items():
        results[LABELS_MAP[k]] += v

    print("Category probabilities:")
    for k, v in sorted(results.items(), key=lambda x: x[1], reverse=True):
        print("{} {}".format(k, v))


if __name__ == "__main__":
    moderate_image()
