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
