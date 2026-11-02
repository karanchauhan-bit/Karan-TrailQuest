output "instance_id" {
  value = aws_instance.trailquest.id
}

output "public_ip" {
  value = aws_instance.trailquest.public_ip
}

output "private_ip" {
  value = aws_instance.trailquest.private_ip
}

output "vpc_id" {
  value = data.aws_vpc.trailquest.id
}

output "subnet_availability_zone" {
  value = data.aws_subnet.trailquest.availability_zone
}

output "subnet_cidr_block" {
  value = data.aws_subnet.trailquest.cidr_block
}
