docker run -it\
  --rm \
  --name SIEM-Dnamic-Assets \
  -v ./sources:/workplace \
  --entrypoint "python" \
  cloudslab/fogbus2-siem-dynamic:1.0 \
  run_dynamic.py
