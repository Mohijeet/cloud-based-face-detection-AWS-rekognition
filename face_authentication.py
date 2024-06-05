import boto3
import json

s3=boto3.client('s3')
rekognition = boto3.client('rekognition', region_name = 'us-east-1')
dynamodbTableName = 'face_registration'
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
face_registration_Table= dynamodb.Table(dynamodbTableName)


def lambda_handler(event, context):
    print(event)
    objectKey =event['queryStringParameters']['objectKey']

    # Call Rekognition to search for faces
    response = rekognition.search_faces_by_image(
        CollectionId='faces',
        Image={'Bytes': image_bytes}
    )

    for match in response['FaceMatches']:
        print(match['Face']['FaceId'],match['Face']['Confidence'])

        face= face_registration_Table.get_item(
            Key={
                'rekognitionId': match['Face']['FaceId']
            }
        )

        if 'Item' in face:
            print('person found', face['Item'])
            return buildResponse(200,{
                'Message': 'Success',
                'firstName': face['Item']['firsName'],
                'lastName': face['Item']['lastName']
            })
        print('person not found')
        return buildResponse(403, {'Message': 'Person Not Found'})

def buildResponse(statusCode, body=None):
    response = {
        'statusCode': statusCode,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        }
    }
    if body is not None:
        response ['body'] = json.dumps(body)
    return response
