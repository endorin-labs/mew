provider "aws" {
  region  = "us-east-1"
}

resource "aws_instance" "enclave_instance" {
  ami                    = "ami-053a45fff0a704a47"
  instance_type          = "m5n.2xlarge"
  key_name               = "vsock-aakash"          # Ensure this key pair exists
  availability_zone      = "us-east-1d"
  subnet_id              = "subnet-06c45597699591587"
  vpc_security_group_ids = ["sg-02f392c3e8121fb74"]

  root_block_device {
    volume_size = 30
    volume_type = "gp2"
  }

  # Use the combined cloud-init file
  user_data = file("cloud_init.yaml")

  # Enable Nitro Enclaves
  enclave_options {
    enabled = true
  }

  tags = {
    Name = "MyEnclaveInstance"
  }
}

output "instance_public_ip" {
  value = aws_instance.enclave_instance.public_ip
}
