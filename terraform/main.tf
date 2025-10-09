terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# Create a key pair for SSH access
resource "aws_lightsail_key_pair" "lamp_key" {
  name = "${var.instance_name}-key"
}

# Create a static IP
resource "aws_lightsail_static_ip" "lamp_static_ip" {
  name = "${var.instance_name}-static-ip"
}

# Create the Lightsail instance
resource "aws_lightsail_instance" "lamp_instance" {
  name              = var.instance_name
  availability_zone = var.availability_zone
  blueprint_id      = var.blueprint_id
  bundle_id         = var.bundle_id
  key_pair_name     = aws_lightsail_key_pair.lamp_key.name

  tags = {
    Name        = var.instance_name
    Environment = "production"
    Project     = "lamp-stack-demo"
  }
}

# Attach the static IP to the instance
resource "aws_lightsail_static_ip_attachment" "lamp_static_ip_attachment" {
  static_ip_name = aws_lightsail_static_ip.lamp_static_ip.name
  instance_name  = aws_lightsail_instance.lamp_instance.name
}

# Open HTTP port 80
resource "aws_lightsail_instance_public_ports" "lamp_ports" {
  instance_name = aws_lightsail_instance.lamp_instance.name

  port_info {
    protocol  = "tcp"
    from_port = 80
    to_port   = 80
    cidrs     = ["0.0.0.0/0"]
  }

  port_info {
    protocol  = "tcp"
    from_port = 443
    to_port   = 443
    cidrs     = ["0.0.0.0/0"]
  }

  port_info {
    protocol  = "tcp"
    from_port = 22
    to_port   = 22
    cidrs     = ["0.0.0.0/0"]
  }
}
