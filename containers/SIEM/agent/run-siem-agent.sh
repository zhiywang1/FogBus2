docker run \
  --rm \
  -p 7398:7398 \
  -v ./sources:/workplace \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v /etc:/etc \
  -v /lib/modules:/lib/modules \
  cloudslab/fogbus2-siem-agent:1.0 \
  --port 7398
