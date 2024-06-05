import boto3
import json


# Initialize the AWS clients
s3 = boto3.client('s3')
rekognition = boto3.client('rekognition', region_name='us-east-1')
dynamodbTableName = 'face_registration'
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
face_registration_Table = dynamodb.Table(dynamodbTableName)

def check_face(image_path):
    # Read the image file
    with open(image_path, 'rb') as image_file:
        image_bytes = image_file.read()
    
    # Call Rekognition to search for faces
    response = rekognition.search_faces_by_image(
        CollectionId='faces',
        Image={'Bytes': image_bytes}
    )

    for match in response['FaceMatches']:
        print(match['Face']['FaceId'], match['Face']['Confidence'])

        face = face_registration_Table.get_item(
    Key={
        'id': match['Face']['FaceId']
    }
)

        if 'Item' in face:
            print('Person found:', face['Item'])
            return build_response(200, {
                'Message': 'Success',
                'firstName': face['Item']['firstName'],
                'lastName': face['Item']['lastName']
            })
        print('Person not found')
        return build_response(403, {'Message': 'Person Not Found'})

def build_response(statusCode, body=None):
    response = {
        'statusCode': statusCode,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        }
    }
    if body is not None:
        response['body'] = json.dumps(body)
    return response

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python script_name.py <image_path>")
        sys.exit(1)
    
    image_path = sys.argv[1]
    result = check_face(image_path)
    print(result)
