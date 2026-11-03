resource "aws_security_group" "trailquest" {
  name        = "launch-wizard-1"
  description = "launch-wizard-1 created 2026-10-05T09:50:42.172Z"
  vpc_id      = data.aws_vpc.trailquest.id

  lifecycle {
    prevent_destroy = true
  }
}

resource "aws_vpc_security_group_ingress_rule" "trailquest_ssh" {
  security_group_id = aws_security_group.trailquest.id
  cidr_ipv4         = "0.0.0.0/0"
  from_port         = 22
  to_port           = 22
  ip_protocol       = "tcp"
}

resource "aws_vpc_security_group_ingress_rule" "trailquest_http" {
  security_group_id = aws_security_group.trailquest.id
  cidr_ipv4         = "0.0.0.0/0"
  from_port         = 80
  to_port           = 80
  ip_protocol       = "tcp"
}

resource "aws_vpc_security_group_ingress_rule" "trailquest_https" {
  security_group_id = aws_security_group.trailquest.id
  cidr_ipv4         = "0.0.0.0/0"
  from_port         = 443
  to_port           = 443
  ip_protocol       = "tcp"
}

resource "aws_vpc_security_group_ingress_rule" "trailquest_5050" {
  security_group_id = aws_security_group.trailquest.id
  cidr_ipv4         = "0.0.0.0/0"
  from_port         = 5050
  to_port           = 5050
  ip_protocol       = "tcp"
}

resource "aws_vpc_security_group_ingress_rule" "trailquest_8080" {
  security_group_id = aws_security_group.trailquest.id
  cidr_ipv4         = "0.0.0.0/0"
  from_port         = 8080
  to_port           = 8080
  ip_protocol       = "tcp"
}

resource "aws_vpc_security_group_egress_rule" "trailquest_all_outbound" {
  security_group_id = aws_security_group.trailquest.id
  cidr_ipv4         = "0.0.0.0/0"
  ip_protocol       = "-1"
}
