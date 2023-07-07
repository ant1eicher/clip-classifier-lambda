#!/usr/bin/env node
import "source-map-support/register";
import * as cdk from "aws-cdk-lib";
import { ClipVideoModeratorStack } from "../lib/clip-video-moderator-stack";

const app = new cdk.App();
new ClipVideoModeratorStack(app, "IVSChatModeratorStack", {});
