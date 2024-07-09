#/bin/bash

info () {
  echo "[*] Use parsed command"
  formatted_command=$(echo "$1" | sed -e 's/ -/ \r\n  -/g')
  echo "$formatted_command"
  echo "[====================================]"
}

run_baseline () {
  command+="cd sources && python remoteLogger.py $args"
  info "$command"
  eval $command
}

run_baseline_in_container () {
  command+="docker run --rm --name RemoteLogger -v ./sources:/workplace -v /var/run/docker.sock:/var/run/docker.sock -p 5000:5000 cloudslab/fogbus2-remote_logger:1.0"
  command+="$args $container_args"
  info "$command"
  eval $command
}
run_tls () {
  command+="cd sources && python remoteLogger.py $args $tls_args"
  info "$command"
  eval $command
}

run_tls_in_container () {
    command+="docker run --rm --name RemoteLogger -v ./sources:/workplace -v /var/run/docker.sock:/var/run/docker.sock -p 5000:5000 cloudslab/fogbus2-remote_logger:1.0"
    command+=" $args $container_args $tls_args"
  info "$command"
  eval $command
}

# Function to display help message
usage() {
    echo "Usage: $0 [-h hostname] [-t enable TLS or not] [-c in container or not]"
    exit 1
}

# Initialize variables
hostname=""
enable_tls=0
in_container=0

# Parse options using getopts
while getopts ":h:tc" opt; do
    case ${opt} in
        h )
            hostname=$OPTARG
            ;;
        t )
            enable_tls=1
            ;;
        c )
            in_container=1
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

command=""
args=" --bindIP $hostname --bindPort 5000 --domainName fogbus2"
tls_args=" --enableTLS True --certFile server.crt --keyFile server.key"
container_args=" --containerName RemoteLogger"

# Display parsed arguments
echo "[====================================]"
echo "[*] Hostname: $hostname"
echo "[*] Enable TLS: $enable_tls"
echo "[*] In container: $in_container"
echo "[*] Running RemoteLogger..."
echo "[====================================]"

# if enable TLS is not set, run baseline
if [ $enable_tls -eq 0 ]; then
    if [ $in_container -eq 1 ]; then
        run_baseline_in_container
    else
        run_baseline
    fi
else
    if [ $in_container -eq 1 ]; then
        run_tls_in_container
    else
        run_tls
    fi
fi
