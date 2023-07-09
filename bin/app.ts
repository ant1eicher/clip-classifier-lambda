#!/usr/bin/env node
import "source-map-support/register";
import * as cdk from "aws-cdk-lib";
import { ClipClassifierStack } from "../lib/clip-classifier-stack";

const app = new cdk.App();
new ClipClassifierStack(app, "ClipClassifierStack", {});
