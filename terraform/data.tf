data "aws_subnet" "trailquest" {
  id = var.subnet_id
}

data "aws_security_group" "trailquest" {
  id = var.security_group_id
}

data "aws_key_pair" "trailquest" {
  key_name = var.key_name
}
