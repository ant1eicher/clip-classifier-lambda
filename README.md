# clip-video-moderator

Use an [OpenAI CLIP](https://openai.com/research/clip) model hosted on a Lambda to classify video thumbnails. The
project is built using CDK, which deploys the Lambda and fronts it with API Gateway.

## Requirements

* AWS CDK 2
* Python 3 / Pip
* NPM

## Build & Deploy

The Makefile has various targets you can use, but to do a full build and deploy cycle:

```shell
make deploy-cdk
```

## Usage

The lambda can be called via an HTTP POST request to the API Gateway endpoint (you can get the endpoint URL from the CDK
output after deployment).

Input format:

* Base64-encoded image (e.g. JPEG). The image should be square to work optimally with CLIP. If it is not, however, the
  preprocessing step will center-crop it. This might lead to some parts of the image being cropped out, which could
  potentially lose some information.
* An array of labels to search for in the image.

```json
{
  "image_data": "/9j/2wCEAAUDBAQEAwUEBAQFBQUGBwwIBwcHBw8LCwkMEQ8SEhEPER...",
  "labels": [
    "label 1",
    "label 2",
    "label 3",
    "label 4"
  ]
}
```

Output format:

The API call will return the _RELATIVE_ probabilities of the image belonging to the various labels. These labels are
seen as mutually exclusive, with probabilities summing to 1. If you would like to detect multiple things within the same image (e.g. a soccer ball
AND the fact that a sport is being played), you will need to run the classifier twice.

```json
{
  "result": {
    "label 1": 0.025054460391402245,
    "label 2": 0.9677731990814209,
    "label 3": 0.0016140799270942807,
    "label 4": 0.0033469817135483027
  }
}
```

Usage example:

```shell
IMAGE_DATA=`base64 -i lambdas/classifier/tests/game_stream_440x248.jpeg`; curl -X POST -H "Content-Type: application/json" -d "{\"image_data\": \"${IMAGE_DATA}\", \"labels\":[\"just chatting\", \"game streamer\", \"nude nsfw\", \"music performance\", \"neutral\"]}" https://2b8ircuzu0.execute-api.eu-west-1.amazonaws.com/prod/
{"result": {"just chatting": 0.07552891969680786, "game streamer": 0.9130083322525024, "nude nsfw": 0.0062192026525735855, "music performance": 0.0031575809698551893, "neutral": 0.0020860943477600813}}
```

## Testing and cost analysis

Sample images and unit tests are in `lambdas/classifier/tests`. These are mostly thumbnails taken directly from the
public [Twitch website](https://www.twitch.tv/).

The lambda, when deployed with 4GB RAM, runs in about
1.5s on a Graviton ARM processor. That equates to about $0.08 per 1000 images classified ($0.00007995 per lambda
invocation).

For comparison, classifying 1000 images using the Rekognition Detect Labels API costs $1.00.

## References

* OpenAI CLIP paper: https://openai.com/research/clip
* OpenAI CLIP Github: https://github.com/openai/CLIP