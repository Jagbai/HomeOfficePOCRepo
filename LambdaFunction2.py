import boto3
import time
import json
import os
import sys
from elasticsearch import Elasticsearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth


SQS_QUEUE_NAME = 'HomeOfficeQueue'
BUCKET_NAME = 'homeofficebucket'
host = 'search-homeofficedomain-3ggxdz32spe5hspyfbvc6i7wkm.eu-west-2.es.amazonaws.com'
region = 'eu-west-2'  # e.g. us-west-1
service = 'es'
credentials = boto3.Session().get_credentials()
awsauth = AWS4Auth(credentials.access_key, credentials.secret_key,
                   region, service, session_token=credentials.token)

es_client = Elasticsearch(
    hosts=[{'host': host, 'port': 443}],
    http_auth=awsauth,
    use_ssl=True,
    verify_certs=True,
    connection_class=RequestsHttpConnection
)


def get_txt_text(file_path):

    with open(file_path, "r") as f:
        for timestamp in f:
            pass
    print(timestamp)
    f.close
    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()
    f.close

    data = {
        "text": text,
        "timestamp": timestamp
    }
    return data


def process_document(file_path):
    filename = file_path.split("/")[-1]
    extension = filename.split(".")[-1]

    plain_text = ''
    timestamp = ''

    if extension == "txt" or extension == "csv":
        data = get_txt_text(file_path)
        plain_text = data['text']
        timestamp = data['timestamp']

    plain_text_size = sys.getsizeof(plain_text)
    while plain_text_size > 5000:
        plain_text = plain_text[:-1]
        plain_text_size = sys.getsizeof(plain_text)
    client_comprehend = boto3.client('comprehend')

    dominant_language_response = client_comprehend.detect_dominant_language(
        Text=plain_text
    )
    dominant_language = sorted(
        dominant_language_response['Languages'], key=lambda k: k['LanguageCode'])[0]['LanguageCode']

    # The service now only supports English and Spanish. In future more languages will be available.
    if dominant_language not in ['en', 'es']:
        dominant_language = 'en'

    response = client_comprehend.detect_entities(
        Text=plain_text,
        LanguageCode=dominant_language
    )
    entites = list(set([x['Type'] for x in response['Entities']]))

    response_key_phrases = client_comprehend.detect_key_phrases(
        Text=plain_text,
        LanguageCode=dominant_language
    )
    key_phrases = list(set([x['Text']
                            for x in response_key_phrases['KeyPhrases']]))

    response_sentiment = client_comprehend.detect_sentiment(
        Text=plain_text,
        LanguageCode=dominant_language
    )
    sentiment = response_sentiment['Sentiment']

    responses = {
        "entites": entites,
        "key_phrases": key_phrases,
        "sentiment": sentiment,
        "timestamp": timestamp
    }

    return responses


def consume_from_sqs(message):
    s3_client_connection = boto3.client('s3')

    body = json.loads(message.body)
    key = body['Records'][0]['s3']['object']['key']

    local_path = "/tmp/"+"{}".format(key)

    s3_client_connection.download_file(BUCKET_NAME, key, local_path)

    # detect entities
    responses = process_document(local_path)
    responses["Key"] = 'https://'+BUCKET_NAME+'.s3.amazonaws.com/'+key
    return responses


def create_es_document(entites, sentiment, key_phrases, s3_location, timestamp):
    return {
        "entities": entites,
        "sentiment": sentiment,
        "keyPhrases": key_phrases,
        "s3Location": s3_location,
        "timestamp": timestamp
    }


def index_to_es(document, index_name):
    es_client.index(index=index_name, doc_type="_doc", body=document)


def lambda_handler(event, context):
    sqs_resource_connection = boto3.resource('sqs')

    queue = sqs_resource_connection.get_queue_by_name(QueueName=SQS_QUEUE_NAME)

    messages = queue.receive_messages(MaxNumberOfMessages=1, WaitTimeSeconds=5)
    for message in messages:

        responses = consume_from_sqs(message)

        # message.delete()

        doc = create_es_document(responses["entites"],
                                 responses["sentiment"], responses["key_phrases"], responses["Key"], responses["timestamp"])
        index_to_es(doc, "homeeofficelibrary")
    return {
        'statusCode': 200,
        'body': json.dumps('Script Successful!')
    }
