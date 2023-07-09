import * as cdk from "aws-cdk-lib";
import { Construct } from "constructs";
import * as lambda from "aws-cdk-lib/aws-lambda";
import { DockerImageAsset } from "aws-cdk-lib/aws-ecr-assets";
import * as apigw from 'aws-cdk-lib/aws-apigateway';
import * as logs from 'aws-cdk-lib/aws-logs';

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
        memorySize: 4096,
        timeout: cdk.Duration.seconds(29),
    });

    // Create CloudWatch Log Group
    const accessLogsLogGroup = new logs.LogGroup(this, 'AccessLogs', {
      logGroupName: '/aws/apigateway/clip-video-moderator-access-logs',
      removalPolicy: cdk.RemovalPolicy.DESTROY,
    });

    // Create an API Gateway with a Lambda proxy integration
    const api = new apigw.LambdaRestApi(this, 'ClassifierApiGateway', {
      handler: classifierFunction,
      deployOptions: {
        accessLogDestination: new apigw.LogGroupLogDestination(accessLogsLogGroup),
        accessLogFormat: apigw.AccessLogFormat.clf()
      },
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
