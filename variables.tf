variable "s3_bucket" {
  description = "The name of the S3 bucket"
  type        = string
}
variable "s3_key" {
  description = "The name of the ZIP file in the S3 bucket"
  type        = string
}
variable "lambda_handler" {
  description = "The Lambda function handler name"
  type        = string
}