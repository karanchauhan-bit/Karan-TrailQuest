resource "aws_instance" "trailquest" {
  ami           = "ami-0b6d9d3d33ba97d99"
  instance_type = var.instance_type
  key_name      = var.key_name
  subnet_id     = var.subnet_id

  vpc_security_group_ids = [
    var.security_group_id
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
