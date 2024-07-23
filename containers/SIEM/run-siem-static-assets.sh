docker run -it\
  --rm \
  --name SIEM-Static-Assets \
  -v ./sources:/workplace \
  --entrypoint "python" \
  cloudslab/fogbus2-siem-static:1.0 \
  run_static.py
