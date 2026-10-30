output "instance_id" {
  value = aws_instance.trailquest.id
}

output "public_ip" {
  value = aws_instance.trailquest.public_ip
}

output "private_ip" {
  value = aws_instance.trailquest.private_ip
}
