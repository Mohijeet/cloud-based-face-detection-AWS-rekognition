import boto3

s3=boto3.client('s3')
rekognition = boto3.client('rekognition', region_name = 'us-east-1')
dynamodbTableName = 'face_registration'
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
face_registration_Table= dynamodb.Table(dynamodbTableName)

def lambda_handler(event, context):
    print(event)
    bucket= event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']

    try: 
        response = index_face_image(bucket,key)
        print(response)
        if response['ResponseMetadata']['HTTPStatusCode']==200 :
            faceId=response['FaceRecords'][0]['Face']['FaceId']
            name = key.split('.')[0].split('_') 
            firstName = name[0]
            lastName = name[1] if len(name) > 1 else 'noname' 
            register_face(faceId,firstName,lastName)
        return response

    except Exception as e:
        print(e)

def index_face_image(bucket,key):
    response= rekognition.index_faces(
        Image={
            'S3Object':
            {
                'Bucket': bucket,
                'Name': key
            }
        },
        CollectionId="faces"
    )
    return response
    
def register_face(faceId,firstName,lastName):
    face_registration_Table.put_item(
        Item={
            'id': faceId,
            'firstName': firstName,
            'lastName': lastName
        }
    )