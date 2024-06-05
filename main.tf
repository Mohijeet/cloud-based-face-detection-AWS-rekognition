resource "aws_s3_bucket" "example" {
  bucket = "my-image-recognition-s3"

  tags = {
    Name        = "My bucket"
    Environment = "Dev"
  }
}

resource "aws_rekognition_collection" "collection" {
  collection_id = "faces"
}
resource "aws_dynamodb_table" "table" {
  name           = "face_registration"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "id"
  attribute {
    name = "id"
    type = "S"
  }
}

resource "aws_iam_role" "lambda_role" {
  name = "lambda_iam_role"
  assume_role_policy = jsonencode({
    "Version": "2012-10-17",
    "Statement": [
      {
        "Action": "sts:AssumeRole",
        "Principal": {
          "Service": "lambda.amazonaws.com"
        },
        "Effect": "Allow",
        "Sid": ""
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_basic_execution" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_policy_attachment" "s3_full_access" {
  name       = "s3_full_access_attachment"
  roles      = [aws_iam_role.lambda_role.name]
  policy_arn = "arn:aws:iam::aws:policy/AmazonS3FullAccess"
}

resource "aws_iam_policy_attachment" "rekognition_full_access" {
  name       = "rekognition_full_access_attachment"
  roles      = [aws_iam_role.lambda_role.name]
  policy_arn = "arn:aws:iam::aws:policy/AmazonRekognitionFullAccess"
}

resource "aws_iam_policy_attachment" "dynamodb_full_access" {
  name       = "dynamodb_full_access_attachment"
  roles      = [aws_iam_role.lambda_role.name]
  policy_arn = "arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess"
}
# Lambda Function
data "archive_file" "lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/face_registration.py"
  output_path = "${path.module}/face_registration.zip"
}

resource "aws_lambda_function" "lambda" {
  function_name = "my_lambda_function"
  role          = aws_iam_role.lambda_role.arn
  handler       = "face_registration.lambda_handler"
  runtime       = "python3.8"
  filename      = "${path.module}/face_registration.zip"
}

# Grant S3 permission to invoke Lambda
resource "aws_lambda_permission" "allow_s3_invocation" {
  statement_id  = "AllowS3Invocation"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.lambda.function_name
  principal     = "s3.amazonaws.com"
  source_arn    = aws_s3_bucket.example.arn
}

# S3 Bucket Notification to trigger Lambda
resource "aws_s3_bucket_notification" "bucket_notification" {
  bucket = aws_s3_bucket.example.id

  lambda_function {
    lambda_function_arn = aws_lambda_function.lambda.arn
    events              = ["s3:ObjectCreated:*"]
   
  }

  depends_on = [aws_lambda_permission.allow_s3_invocation]
}

output "role_arn" {
  value = aws_iam_role.lambda_role.arn
}