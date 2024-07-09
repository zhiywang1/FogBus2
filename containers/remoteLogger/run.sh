#/bin/bash

run_baseline () {
  docker run \
    --rm \
    --name RemoteLogger \
     -v ./sources:/workplace \
     -v /var/run/docker.sock:/var/run/docker.sock \
     -p 5000:5000 cloudslab/fogbus2-remote_logger:1.0 \
      --containerName RemoteLogger \
      --bindIP $1 \
      --bindPort 5000 \
      --domainName fogbus2
}

run_tls () {
  docker run \
    --rm \
    --name RemoteLogger \
     -v ./sources:/workplace \
     -v /var/run/docker.sock:/var/run/docker.sock \
     -p 5000:5000 cloudslab/fogbus2-remote_logger:1.0 \
      --containerName RemoteLogger \
      --bindIP $1 \
      --bindPort 5000 \
      --domainName fogbus2 \
      --enableTLS True \
      --certFile server.crt \
      --keyFile server.key
}

# Function to display help message
usage() {
    echo "Usage: $0 [-h hostname] [-t enable TLS or not]"
    exit 1
}

# Initialize variables
hostname=""
enable_tls=0

# Parse options using getopts
while getopts ":h:t" opt; do
    case ${opt} in
        h )
            hostname=$OPTARG
            ;;
        t )
            enable_tls=1
            ;;
        \? )
            echo "Invalid option: -$OPTARG" 1>&2
            usage
            ;;
        : )
            echo "Invalid option: -$OPTARG requires an argument" 1>&2
            usage
            ;;
    esac
done
shift $((OPTIND -1))

# Check if hostname is set
if [ -z "$hostname" ]; then
    echo "Hostname is required."
    usage
fi

# Display parsed arguments
echo "[====================================]"
echo "[*] Hostname: $hostname"
echo "[*] Enable TLS: $enable_tls"
echo "[*] Running RemoteLogger container..."
echo "[====================================]"

# if enable TLS is not set, run baseline
if [ $enable_tls -eq 0 ]; then
    run_baseline $hostname
else
    run_tls $hostname
fi
