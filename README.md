# clip-classifier-lambda

Use an [OpenAI CLIP](https://openai.com/research/clip) model hosted on a Lambda to classify images, such as video
thumbnails. The
project is built using CDK, which deploys the Lambda and fronts it with API Gateway.

## Requirements

- AWS CDK 2
- Python 3 / Pip
- NPM
- Docker

## Build & Deploy

The Makefile has various targets you can use, but to do a full build and deploy cycle:

```shell
make deploy-cdk
```

Note: if this is the first time you are deploying a CDK stack to this region, you need to run this first:

```shell
cdk bootstrap
```

If you would like to install the Python requirements for local development (as opposed to during the Docker build):

```shell
make setup
```

To run the classifier tests:

```shell
make classifier-lambda-test
```

The [Dockerfile](/lambdas/classifier/Dockerfile) is configured for ARM. To build for Intel,
change `FROM public.ecr.aws/lambda/python:3.10-arm64`, and also
modify the Lambda function in [clip-classifier-stack.ts](/lib/clip-classifier-stack.ts)
from `architecture: lambda.Architecture.ARM_64`.

## Usage

The lambda can be called via an HTTP POST request to the API Gateway endpoint (you can get the endpoint URL from the CDK
output after deployment).

Input format:

- Base64-encoded image (e.g. JPEG). The image should be square to work optimally with CLIP. If it is not, however, the
  preprocessing step will center-crop it. This might lead to some parts of the image being cropped out, which could
  potentially lose some information.
- An array of labels to search for in the image.

```json
{
  "image_data": "/9j/2wCEAAUDBAQEAwUEBAQFBQUGBwwIBwcHBw8LCwkMEQ8SEhEPER...",
  "labels": ["label 1", "label 2", "label 3", "label 4"]
}
```

Output format:

The API call will return the _RELATIVE_ probabilities of the image belonging to the various labels. These labels are
seen as mutually exclusive, with probabilities summing to 1. If you would like to detect multiple things within the same
image (e.g. a soccer ball
AND the fact that a sport is being played), you will need to run the classifier twice, or cleverly encode each combination of two labels as a probability (e.g. label1 & label2, label1 & label3, etc).

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

![game_stream_440x248.jpeg](test_images%2Fgame_stream_440x248.jpeg)

```shell
IMAGE_DATA=`base64 -i lambdas/classifier/tests/game_stream_440x248.jpeg`; curl -X POST -H "Content-Type: application/json" -d "{\"image_data\": \"${IMAGE_DATA}\", \"labels\":[\"just chatting\", \"game streamer\", \"nude nsfw\", \"music performance\", \"neutral\"]}" https://2b8ircuzu0.execute-api.eu-west-1.amazonaws.com/prod/
{"result": {"just chatting": 0.07552891969680786, "game streamer": 0.9130083322525024, "nude nsfw": 0.0062192026525735855, "music performance": 0.0031575809698551893, "neutral": 0.0020860943477600813}}
```

Note: the first time that you call the lambda, it will timeout due to a cold start (it has a lot of setup to do). Subsequent
calls will be fast. If you want to avoid this, you can set the Lambda CDK construct to use [provisioned concurrency](https://docs.aws.amazon.com/lambda/latest/dg/provisioned-concurrency.html),
which incurs higher costs.

## Testing and cost analysis

Sample images and unit tests are in `lambdas/classifier/tests`. These are mostly thumbnails taken directly from the
public [Twitch website](https://www.twitch.tv/).

The lambda, when deployed with 4GB RAM, runs in about
1.5s on a Graviton ARM processor. That equates to about $0.08 per 1000 images classified ($0.00007995 per lambda
invocation).

For comparison, classifying 1000 images using the Rekognition Detect Labels API costs $1.00.

_However_, CLIP labels are mutually exclusive, so if you want to search for the presence of N items in the same image,
you should run the classifier N times (e.g.
labels ["apple", "no apple"], ["orange", "no orange"], ["fruit", "no fruit"], etc) or combine labels (e.g. ["orange & apple", "orange & grape"], etc). Rekognition allows you to
search for up to 1000 labels per invocation.

For comparisons of the CLIP model in terms of accuracy (against image classification datasets such as ImageNet), see the
link to the paper below.

## Example with moderation labels

Here follows a map of CLIP image "labels" to moderation classifications. Note that multiple labels could lead to the
same
classification (e.g. gaming appears twice). The idea is to provide CLIP with multiple similar descriptions to allow it
to select the one that fits the image best.

```
a thumbnail with a blank or logo - neutral
a thumbnail of a sexy person - suggestive
a thumbnail of a sport - sport
a thumbnail containing explicit adult content - explicit
a thumbnail of a casual gaming stream - gaming
a thumbnail with suggestive content - suggestive
a thumbnail of a music performance - music
a thumbnail containing real-world violent content - violence
a thumbnail showing violent content from a video game - gaming
```

See [moderation.py](examples%2Fmoderation.py) for an example of using these. When the example is run with the image
above,
the output should look similar to this:

```
Category probabilities:
gaming 0.8677900731563568
suggestive 0.03592784330248833
violence 0.027453191578388214
sport 0.027340112254023552
music 0.024062810465693474
neutral 0.009686844423413277
explicit 0.007738994900137186
```

To build and run the example:

- replace the `ENDPOINT` constant with your deployed API Gateway URL

```shell
make examples-setup
python3 ./examples/moderation.py
```

## References

- OpenAI CLIP paper: https://openai.com/research/clip
- OpenAI CLIP Github: https://github.com/openai/CLIP
