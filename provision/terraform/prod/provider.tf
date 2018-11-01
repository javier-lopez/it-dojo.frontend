variable "do_token" {}

variable "public_key" {
  description = "SSH Public Key"
  default     = "~/.ssh/id_rsa.pub"
}

variable "private_key" {
  description = "SSH Private Key"
  default     = "~/.ssh/id_rsa"
}

provider "digitalocean" {
  token = "${var.do_token}"
}
