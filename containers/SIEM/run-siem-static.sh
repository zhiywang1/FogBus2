docker run \
  --rm \
  -v ./sources:/workplace \
  --entrypoint "python run_static.py" \
  cloudslab/fogbus2-siem-static:1.0
