resource "digitalocean_ssh_key" "it-dojo-key" {
  name       = "IT / DOJO ssh key"
  public_key = "${file(var.public_key)}"
}
