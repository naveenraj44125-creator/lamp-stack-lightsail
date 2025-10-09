variable "instance_name" {
  description = "Name of the Lightsail instance"
  type        = string
  default     = "lamp-stack-demo"
}

variable "aws_region" {
  description = "AWS region for Lightsail resources"
  type        = string
  default     = "us-east-1"
}

variable "availability_zone" {
  description = "Availability zone for Lightsail instance"
  type        = string
  default     = "us-east-1a"
}

variable "blueprint_id" {
  description = "Lightsail blueprint ID"
  type        = string
  default     = "ubuntu_20_04"
}

variable "bundle_id" {
  description = "Lightsail bundle ID"
  type        = string
  default     = "nano_2_0"
}

variable "key_pair_name" {
  description = "Name of the key pair for SSH access"
  type        = string
  default     = "lamp-stack-key"
}

variable "static_ip_name" {
  description = "Name of the static IP"
  type        = string
  default     = "lamp-stack-static-ip"
}
