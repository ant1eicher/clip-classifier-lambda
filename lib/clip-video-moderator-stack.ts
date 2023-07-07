import * as cdk from "aws-cdk-lib";
import { Construct } from "constructs";
import * as lambda from "aws-cdk-lib/aws-lambda";
import { DockerImageAsset } from "aws-cdk-lib/aws-ecr-assets";
import * as apigw from 'aws-cdk-lib/aws-apigateway';

export class ClipVideoModeratorStack extends cdk.Stack {
  constructor (scope: Construct, id: string, props: cdk.StackProps) {
    super(scope, id, {
      stackName: props.stackName,
      env: props.env
    });

    // Build a Docker image and upload it to an ECR repository
    const dockerImageAsset = new DockerImageAsset(this, "ClassifierDockerImage",
      {
        directory: "lambdas/classifier/"
      });

    // Create a Lambda function with the Docker image
    const classifierFunction = new lambda.DockerImageFunction(this,
      "ClassifierFunction", {
        code: lambda.DockerImageCode.fromEcr(dockerImageAsset.repository, {
          tagOrDigest: dockerImageAsset.imageTag
        }),
        architecture: lambda.Architecture.ARM_64,
        memorySize: 2048,
        timeout: cdk.Duration.seconds(30),
    });

    // Create an API Gateway with a Lambda proxy integration
    const api = new apigw.LambdaRestApi(this, 'ClassifierApiGateway', {
      handler: classifierFunction,
    });

    // Output the image URI
    new cdk.CfnOutput(this, "DockerImageUri", {
      value: dockerImageAsset.imageUri
    });

    new cdk.CfnOutput(this, "api-url", {
      value: api.url ?? 'something went wrong with the API Gateway URL',
    });
  }
}
