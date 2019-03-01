import os
import io
import boto3
import json
import csv




# grab environment variables
ENDPOINT_NAME = os.environ['ENDPOINT_NAME']
runtime= boto3.client('runtime.sagemaker')

def lambda_handler(event, context):
    columns= 'Sepal.Width,Petal.Length,Petal.Width,Species \n'
    data = event
    output=columns+data
    print(output)
    streaming_response = runtime.invoke_endpoint(EndpointName=ENDPOINT_NAME,
                                       ContentType='text/csv',
                                       Body=output)
    
    
    result =json.loads(streaming_response['Body'].read().decode('utf-8'))
    
    return result