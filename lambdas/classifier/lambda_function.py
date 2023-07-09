import base64
import json
import os

import clip
import torch
from PIL import Image

model_path = "/app/model/ViT-B-32.pt" if os.getenv("MODEL_PATH") is None else os.getenv("MODEL_PATH")
device = "cuda" if torch.cuda.is_available() else "cpu"
model, preprocess = clip.load(model_path, jit=False, device=device)
filename = "/tmp/downloaded_image.jpg"


def handler(event, context):
    args = json.loads(event["body"])

    # base64-encoded string of a jpg file
    image_data = args["image_data"]

    # labels to classify
    labels = args["labels"]

    print(f"labels: {labels}")

    try:
        decoded_data = base64.b64decode(image_data)

        with open(filename, "wb") as file:
            file.write(decoded_data)

        image = preprocess(Image.open(filename)).unsqueeze(0).to(device)
        text = clip.tokenize(labels).to(device)

        with torch.no_grad():
            model.encode_image(image)
            model.encode_text(text)

            logits_per_image, _ = model(image, text)
            probs = logits_per_image.softmax(dim=-1).cpu().numpy()

    except Exception as e:
        print(f"Exception: {e}")
        import traceback
        traceback.print_exc()
        raise

    result = {}
    for i in range(len(labels)):
        result[labels[i]] = float(probs[0][i])

    print("result", result)

    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json'
        },
        'body': json.dumps({
            'result': result
        }),
        "isBase64Encoded": False
    }
