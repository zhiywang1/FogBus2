docker run \
  --rm \
  --name SIEM-Agent \
  -p 7398:7398 \
  -v ./sources:/workplace \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v /etc/ssh/sshd_config/:/etc/ssh/sshd_config \
  -v /etc/sudoers:/etc/sudoers \
  -v /lib/modules:/lib/modules \
  cloudslab/fogbus2-siem-agent:1.0 \
  --port 7398
