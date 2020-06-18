# HomeOfficePOCRepo

This repository serves to store both lambda functions used in the netco AWS POC as well as instructions
to help set up the AWS environment properly to use all of the services

![es_aws_comprhend_architecture-1024x576](https://user-images.githubusercontent.com/33807790/84945119-c4d8eb00-b0de-11ea-9ec2-6f8cac52b5f7.jpg)

The Architecture used for this project is similar to that of the architecture above by 
"https://www.skedler.com/blog/combine-text-analytics-search-aws-comprehend-elasticsearch-6-0/" but with the main differences being that the
code has been amended for usage within lambda functions allowing it to be invoked through triggers instead of manual execution

<h2>Requirements</h2>
<ol>
<li> 2 Lambda functions
<li> 1 S3 bucket
<li> 1 Elasticsearch domain
<li> 1 SQS Queue
<li> 1 CloudWatch Events (daily trigger)
<li> A few IAM role tweaks
<li> Patience
</ol>

<h2> Setup Steps</h2>
<ol>
<li> Set up an SQS Queue and an S3 bucket with both versioning, as well as events and link the events to the SQS queue that you set up
<li> Set up an Elasticsearch domain, within the domain go to Rule mappings and add your second Lambda functions ARN to the "all access" users when you make it
<li> Set up the first Lambda function using Lambdafunction1 code and attach a cloudevent to trigger it daily, weekly, etc. Within the lambda
function change the bucket name from "homeofficebucket" to whatever you s3 bucket name is and change the lambda function arn to whatever
your arn is for your second lambda function. Add IAM roles for all the services used as a safety precaution
<li> Set up the second lambda function mentioned in the instructions beforehand using Lambdafunction2 code. Add IAM roles for all the services used as a safety precaution
.Change host to your elasticsearch endpoint, change bucketname and change SQS queue name to yours. 
</ol>

<h3> Troubleshooting</h3> 
Its highly likely that this doesn't work first time probably due to my lack of experience in writing read-me's so if any issues occur feel free to message me,
they are most likely to do with security issues or incorrect parameters.
