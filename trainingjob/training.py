import boto3
import re
import os
import wget
import time
from time import gmtime, strftime
import sys
import json

# Specify these attributes
role = 'sagemaker-bring-your-algor-training-job'
bucket = 'sagemaker-batchdeploy'
prefix = 'sagemaker/mars/compress'
region ='ap-south-1'
account = '237320763879'


print(role)
start = time.time()
s3 = boto3.client('s3')
#Download *.RData to local environment from S3
bucket='sagemaker-batchdeploy'
key='mars_model.RData'
s3.Bucket(bucket).download_file(key, 'mars_model.RData')

#Convert RData to *.tar.gz
model_file_name='mars_model.RData'
!tar czvf model_.tar.gz $model_file_name

# upload training dataset to S3

trained_model = 'model_.tar.gz'
boto3.Session().resource('s3').Bucket(bucket).Object(os.path.join(prefix, 'train', trained_model)).upload_file(trained_model)
        
###################hosting endpoint#########
# Creating Model with Inference image

r_job='sagemakerserveonlymodel'


r_image='237320763645.dkr.ecr.ap-south-1.amazonaws.com/sagemakerserveonly:latest'
r_trainjob='s3://sagemaker-batchdeploy/sagemaker/mars/compress/train/model.tar.gz'

r_hosting_container = {
    'Image': r_image,
    'ModelDataUrl': r_trainjob
}
# Creating model based on the output artifact from S3
# put trained model on the container at  /opt/ml/model/* location 
create_model_response = sm.create_model(
    ModelName=r_job,
    ExecutionRoleArn=role,
    PrimaryContainer=r_hosting_container)

print(create_model_response['ModelArn'])

##########################
# Creating Endpoint config
# Endpoint will run on actual environment rest api to outer world

r_endpoint_config = 'sagemakerserveonly-endpointconfig'
print(r_endpoint_config)

create_endpoint_config_response = sm.create_endpoint_config(
    EndpointConfigName=r_endpoint_config,
    ProductionVariants=[{
        'InstanceType': 'ml.m4.xlarge',
        'InitialInstanceCount': 1,
        'ModelName': r_job,
        'VariantName': 'AllTraffic'}])

print("Endpoint Config Arn: " + create_endpoint_config_response['EndpointConfigArn'])


##########################

#Check if endpoint needs to be created or updated

r_endpoint = 'sagemakerserveonly-endpoint'
print(r_endpoint)

endpointname =sm.list_endpoints(NameContains=r_endpoint)

if endpointname['Endpoints']==[]:
    create_endpoint_response = sm.create_endpoint(EndpointName=r_endpoint,EndpointConfigName=r_endpoint_config)
    print(create_endpoint_response['EndpointArn'])
elif endpointname['Endpoints'][0]['EndpointStatus']=='InService': 
    sm.update_endpoint(EndpointName=r_endpoint,EndpointConfigName=r_endpoint_config)
else :
    print(r_endpoint)


resp = sm.describe_endpoint(EndpointName=r_endpoint)
status = resp['EndpointStatus']
print("Status: " + status)

try:
    sm.get_waiter('endpoint_in_service').wait(EndpointName=r_endpoint)
finally:
    resp = sm.describe_endpoint(EndpointName=r_endpoint)
    status = resp['EndpointStatus']
    print("Arn: " + resp['EndpointArn'])
    print("Status: " + status)

    if status != 'InService':
        raise Exception('Endpoint creation did not succeed')

end = time.time()
print(end - start)