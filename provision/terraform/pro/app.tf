resource "digitalocean_droplet" "app" {
    count    = "1"
    name     = "${format("app-%02d", count.index)}"
    region   = "sfo2"
    image    = "ubuntu-16-04-x64"
    size     = "s-1vcpu-1gb"
    private_networking = true

    ssh_keys = ["${digitalocean_ssh_key.it-dojo-key.id}"]

    connection {
        user = "root"
        type = "ssh"
        private_key = "${file(var.private_key)}"
        timeout = "2m"
    }

    provisioner "remote-exec" {
        script = "provision/01-disable-unattended-upgrades.sh"
    }

    provisioner "remote-exec" {
        script = "provision/02-install-ansible-deps.sh"
    }
}

output "app-output" {
  value = "${digitalocean_droplet.app.*.ipv4_address}"
}
