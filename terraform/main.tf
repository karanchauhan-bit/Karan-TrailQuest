resource "aws_instance" "trailquest" {
  ami           = "ami-0b6d9d3d33ba97d99"
  instance_type = var.instance_type
  key_name      = data.aws_key_pair.trailquest.key_name
  subnet_id     = data.aws_subnet.trailquest.id

  vpc_security_group_ids = [
    data.aws_security_group.trailquest.id
  ]

  root_block_device {
    volume_size           = 20
    volume_type           = "gp3"
    iops                  = 3000
    throughput            = 125
    encrypted             = false
    delete_on_termination = true
  }

  tags = {
    Name      = "karan-devops-project"
    ManagedBy = "Terraform"
    Project   = "Karan-TrailQuest"
  }

  lifecycle {
    prevent_destroy = true
  }
}
