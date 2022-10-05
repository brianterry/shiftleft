terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 3.27"
    }
  }

  required_version = ">= 0.14.9"
}

provider "aws" {
  profile = "default"
  region  = "us-west-2"
}

// Insert KMS key here
// KMS key


resource "aws_s3_bucket" "b" {
  bucket_prefix = "policy-as-code-bucket-terraform"
  
  versioning {
    enabled = true
  }

  lifecycle_rule {
    prefix  = "config/"
    enabled = true

    noncurrent_version_transition {
      days          = 30
      storage_class = "STANDARD_IA"
    }

    noncurrent_version_transition {
      days          = 60
      storage_class = "GLACIER"
    }

    noncurrent_version_expiration {
      days = 90
    }
  }
}

resource "aws_config_config_rule" "r" {
  name = "S3PublicAccessSettingsTerraform"
  description = "Checks that your Amazon S3 buckets do not allow public read access. The rule checks the Block Public Access settings, the bucket policy, and the bucket access control list (ACL)."
  maximum_execution_frequency = "One_Hour"
  source {
    owner             = "AWS"
    source_identifier = "S3_BUCKET_PUBLIC_READ_PROHIBITED"
  }
  scope {
    compliance_resource_id = aws_s3_bucket.b.id
    compliance_resource_types = ["AWS::S3::Bucket"]
  }
}

// public access rule ....... start
resource "aws_s3_bucket_public_access_block" "rule" {
  bucket = aws_s3_bucket.b.id

  block_public_acls       = false
  block_public_policy     = false
  ignore_public_acls      = false
  restrict_public_buckets = false
}

resource "aws_s3_bucket_policy" "allow_public_read_access" {
  bucket = aws_s3_bucket.b.id
  policy = data.aws_iam_policy_document.allow_public_read_access.json
}

data "aws_iam_policy_document" "allow_public_read_access" {
  statement {
    principals {
      type        = "AWS"
      identifiers = ["*"]
    }

    actions = [
      "s3:GetObject"
    ]

    resources = [
      aws_s3_bucket.b.arn,
      "${aws_s3_bucket.b.arn}/*",
    ]
  }
}

// public access rule ....... end


// uncomment the following to enable remediation
/*
resource "aws_iam_role" "remediate" {
  name                = "remediate_role"
  assume_role_policy  = data.aws_iam_policy_document.ssm_access.json 
  managed_policy_arns = ["arn:aws:iam::aws:policy/service-role/AmazonSSMAutomationRole"]
}

data "aws_iam_policy_document" "ssm_access" {
  statement {
    principals {
      type        = "Service"
      identifiers = ["ssm.amazonaws.com"]
    }

    actions = [
      "s3:*"
    ]

    resources = [
      aws_s3_bucket.b.arn
    ]
  }
}

resource "aws_config_remediation_configuration" "AwsConfigRemdiationS3" {
  config_rule_name = aws_config_config_rule.r.name
  target_type      = "SSM_DOCUMENT"
  target_id        = "AWS-DisableS3BucketPublicReadWrite"

  parameter {
    name         = "AutomationAssumeRole"
    resource_value = aws_iam_role.remediate.arn
  }
  parameter {
    name           = "S3BucketName"
    resource_value = aws_s3_bucket.b.id
  }

  automatic                  = true
  maximum_automatic_attempts = 3
  retry_attempt_seconds      = 60

  execution_controls {
    ssm_controls {
      concurrent_execution_rate_percentage = 25
      error_percentage                     = 20
    }
  }
}
*/
