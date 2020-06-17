import json
import boto3
import requests
from bs4 import BeautifulSoup


def lambda_handler(event, context):
    # TODO implement
    s3_client = boto3.client('s3')
    lambda_client = boto3.client('lambda')
    url = 'https://www.parliament.uk/business/news/2020/april1/prime-ministers-questions-29-april/'
    filename = 'newscrapertext8.txt'
    localpath = '/tmp/' + filename
    BUCKET_NAME = "homeofficebucket"
    INVOKED_FUNCTION = 'arn:aws:lambda:eu-west-2:438542434507:function:comprehendfunction'
    with open(localpath, "r") as f:
        for timestamp in f:
            pass
    print(timestamp)
    req = requests.get(url)
    soup = BeautifulSoup(req.content, 'html.parser')
    for i in soup.findAll('meta'):
        if 'Date' in str(i):
            date = ("\n"+i['content'])
    textdoc = soup.get_text()
    textdoc = textdoc.replace("\n", "")
    f = open(localpath, "a")
    f.write(textdoc)
    f.write(date)
    f.close()
    s3_client.upload_file(localpath, BUCKET_NAME, filename)

    response = lambda_client.invoke(
        FunctionName=INVOKED_FUNCTION,
        InvocationType='Event',
        Payload='{}'
    )
    print(response)
