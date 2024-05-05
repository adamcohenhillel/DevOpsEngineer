
resource "aws_security_group" "test_app" {
  name        = "test_app_sg"
  description = "Allow traffic on port 5000 for Test App"

  ingress {
    from_port   = 5000
    to_port     = 5000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "TestAppSecurityGroup"
  }
}

# Associate security group with instance
resource "aws_instance" "test_app" {
  security_groups = [aws_security_group.test_app.name]
}