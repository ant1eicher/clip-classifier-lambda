FROM public.ecr.aws/lambda/python:3.10-arm64

# Install dependencies
RUN yum install -y git

# Copy requirements.txt
COPY requirements.txt ${LAMBDA_TASK_ROOT}

# Install the specified packages
RUN pip install -r requirements.txt

# Pre-cache the CLIP model on disk
RUN python -c "import clip; clip.load('ViT-B/32', download_root='/app/model')"

# Copy function code
COPY lambda_function.py ${LAMBDA_TASK_ROOT}

# Set the CMD to your handler (could also be done as a parameter override outside of the Dockerfile)
CMD [ "lambda_function.handler" ]