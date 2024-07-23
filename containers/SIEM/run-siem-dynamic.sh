docker run \
  --rm \
  -v ./sources:/workplace \
  --entrypoint "python run_dynamic.py" \
  cloudslab/fogbus2-siem-dynamic:1.0
