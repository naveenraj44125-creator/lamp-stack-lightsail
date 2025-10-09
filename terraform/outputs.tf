output "instance_name" {
  description = "Name of the created Lightsail instance"
  value       = aws_lightsail_instance.lamp_stack.name
}

output "instance_id" {
  description = "ID of the created Lightsail instance"
  value       = aws_lightsail_instance.lamp_stack.id
}

output "instance_arn" {
  description = "ARN of the created Lightsail instance"
  value       = aws_lightsail_instance.lamp_stack.arn
}

output "public_ip_address" {
  description = "Public IP address of the instance"
  value       = aws_lightsail_instance.lamp_stack.public_ip_address
}

output "private_ip_address" {
  description = "Private IP address of the instance"
  value       = aws_lightsail_instance.lamp_stack.private_ip_address
}

output "static_ip_address" {
  description = "Static IP address attached to the instance"
  value       = aws_lightsail_static_ip.lamp_stack_static_ip.ip_address
}

output "key_pair_name" {
  description = "Name of the key pair used for SSH access"
  value       = aws_lightsail_key_pair.lamp_stack_key.name
}

output "availability_zone" {
  description = "Availability zone of the instance"
  value       = aws_lightsail_instance.lamp_stack.availability_zone
}

output "blueprint_id" {
  description = "Blueprint ID used for the instance"
  value       = aws_lightsail_instance.lamp_stack.blueprint_id
}

output "bundle_id" {
  description = "Bundle ID used for the instance"
  value       = aws_lightsail_instance.lamp_stack.bundle_id
}
