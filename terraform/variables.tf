variable "aws_region" {
  description = "AWS region for the TrailQuest infrastructure"
  type        = string
}

variable "instance_type" {
  description = "EC2 instance type"
  type        = string
}

variable "key_name" {
  description = "Existing AWS EC2 key pair name"
  type        = string
}

variable "subnet_id" {
  description = "Existing subnet ID used by the EC2 instance"
  type        = string
}

variable "security_group_id" {
  description = "Existing security group attached to the EC2 instance"
  type        = string
}
