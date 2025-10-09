output "instance_name" {
  description = "Name of the created Lightsail instance"
  value       = aws_lightsail_instance.lamp_instance.name
}

output "instance_id" {
  description = "ID of the created Lightsail instance"
  value       = aws_lightsail_instance.lamp_instance.id
}

output "instance_arn" {
  description = "ARN of the created Lightsail instance"
  value       = aws_lightsail_instance.lamp_instance.arn
}

output "public_ip_address" {
  description = "Public IP address of the instance"
  value       = aws_lightsail_instance.lamp_instance.public_ip_address
}

output "private_ip_address" {
  description = "Private IP address of the instance"
  value       = aws_lightsail_instance.lamp_instance.private_ip_address
}

output "static_ip_address" {
  description = "Static IP address attached to the instance"
  value       = aws_lightsail_static_ip.lamp_static_ip.ip_address
}

output "key_pair_name" {
  description = "Name of the key pair used for SSH access"
  value       = aws_lightsail_key_pair.lamp_key.name
}

output "availability_zone" {
  description = "Availability zone of the instance"
  value       = aws_lightsail_instance.lamp_instance.availability_zone
}

output "blueprint_id" {
  description = "Blueprint ID used for the instance"
  value       = aws_lightsail_instance.lamp_instance.blueprint_id
}

output "bundle_id" {
  description = "Bundle ID used for the instance"
  value       = aws_lightsail_instance.lamp_instance.bundle_id
}
