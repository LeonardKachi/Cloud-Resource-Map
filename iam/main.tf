terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

# ============================================================
# Cloud Resource Map — AWS IAM Setup
# ============================================================
# This creates a read-only IAM user with the minimum permissions
# needed for Cloud Resource Map to scan your account.
#
# It will NEVER create, modify, or delete your resources.
# All permissions below are read-only (List*, Describe*, Get*).
#
# How to run:
#   1. Install Terraform: https://developer.hashicorp.com/terraform/install
#   2. Configure AWS CLI:  aws configure
#   3. From this directory run:
#        terraform init
#        terraform apply
#   4. Copy the access key output into your .env file
# ============================================================

variable "aws_region" {
  description = "AWS region to deploy into"
  default     = "us-east-1"
}

provider "aws" {
  region = var.aws_region
}

# ---- IAM User -----------------------------------------------
resource "aws_iam_user" "cloud_resource_map" {
  name = "cloud-resource-map-readonly"
  tags = {
    ManagedBy   = "cloud-resource-map"
    Description = "Read-only user for Cloud Resource Map scanning"
  }
}

resource "aws_iam_access_key" "cloud_resource_map" {
  user = aws_iam_user.cloud_resource_map.name
}

# ---- Read-only Policy ---------------------------------------
resource "aws_iam_policy" "cloud_resource_map_readonly" {
  name        = "CloudResourceMapReadOnly"
  description = "Minimum read-only permissions for Cloud Resource Map"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "EC2ReadOnly"
        Effect = "Allow"
        Action = [
          "ec2:DescribeInstances",
          "ec2:DescribeVpcs",
          "ec2:DescribeSubnets",
          "ec2:DescribeNatGateways",
          "ec2:DescribeSecurityGroups",
          "ec2:DescribeRouteTables",
          "ec2:DescribeInternetGateways",
          "ec2:DescribeAddresses",
        ]
        Resource = "*"
      },
      {
        Sid    = "S3ReadOnly"
        Effect = "Allow"
        Action = [
          "s3:ListAllMyBuckets",
          "s3:GetBucketLocation",
          "s3:GetBucketTagging",
        ]
        Resource = "*"
      },
      {
        Sid    = "LambdaReadOnly"
        Effect = "Allow"
        Action = [
          "lambda:ListFunctions",
          "lambda:GetFunction",
          "lambda:ListTags",
        ]
        Resource = "*"
      },
      {
        Sid    = "Route53ReadOnly"
        Effect = "Allow"
        Action = [
          "route53:ListHostedZones",
          "route53:GetHostedZone",
          "route53:ListResourceRecordSets",
        ]
        Resource = "*"
      },
      {
        Sid    = "CloudWatchReadOnly"
        Effect = "Allow"
        Action = [
          "logs:DescribeLogGroups",
          "logs:DescribeLogStreams",
          "cloudwatch:ListMetrics",
          "cloudwatch:GetMetricStatistics",
        ]
        Resource = "*"
      },
      {
        Sid    = "APIGatewayReadOnly"
        Effect = "Allow"
        Action = [
          "apigateway:GET",
        ]
        Resource = "*"
      },
      {
        Sid    = "KMSReadOnly"
        Effect = "Allow"
        Action = [
          "kms:ListKeys",
          "kms:DescribeKey",
          "kms:ListAliases",
        ]
        Resource = "*"
      },
      {
        Sid    = "CostExplorerReadOnly"
        Effect = "Allow"
        Action = [
          "ce:GetCostAndUsage",
          "ce:GetCostForecast",
        ]
        Resource = "*"
      },
    ]
  })
}

resource "aws_iam_user_policy_attachment" "cloud_resource_map" {
  user       = aws_iam_user.cloud_resource_map.name
  policy_arn = aws_iam_policy.cloud_resource_map_readonly.arn
}

# ---- Outputs ------------------------------------------------
# These are printed after terraform apply — paste them into your .env file
output "AWS_ACCESS_KEY_ID" {
  value       = aws_iam_access_key.cloud_resource_map.id
  description = "Paste this into AWS_ACCESS_KEY_ID in your .env file"
}

output "AWS_SECRET_ACCESS_KEY" {
  value       = aws_iam_access_key.cloud_resource_map.secret
  description = "Paste this into AWS_SECRET_ACCESS_KEY in your .env file"
  sensitive   = true
}

output "note" {
  value = "Run: terraform output -raw AWS_SECRET_ACCESS_KEY to see the secret key"
}
