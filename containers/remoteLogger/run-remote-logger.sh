#/bin/bash

set -e

info () {
  echo "[*] Use parsed command"
  formatted_command=$(echo "$1" | sed -e 's/ -/ \r\n  -/g')
  echo "$formatted_command"
  echo "[====================================]"
}

# Function to display help message
usage() {
    echo "Usage: $0 [-h hostname] [-t enable TLS or not] [-c in container or not]"
    exit 1
}

# Function to toggle DB hostname
toggle_hosts() {
    local mode=$1

    if [ $mode -eq 0 ]; then
        HOST_VALUE="$out_container_db_host"
        HOST1_VALUE="$in_container_db_host"
    else
        HOST_VALUE="$in_container_db_host"
        HOST1_VALUE="$out_container_db_host"
    fi

    # Create a temporary file
    tmp_file=$(mktemp)

    # Update the values
    sed -e "s/^HOST1=.*/HOST1=$HOST1_VALUE/" -e "s/^HOST=.*/HOST=$HOST_VALUE/" "$env_file" > "$tmp_file"

    # Move the temporary file to the original file
    mv "$tmp_file" "$env_file"

    echo "[*] DB hostname has been set as: $HOST_VALUE"
}

# Initialize variables
hostname=""
enable_tls=0
in_container=0
env_file="./sources/.env"
out_container_db_host="127.0.0.1"
in_container_db_host="host.docker.internal"

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
command_base="cd sources && python remoteLogger.py"
docker_command_base="docker run --rm --name RemoteLogger -v ./sources:/workplace -v /var/run/docker.sock:/var/run/docker.sock -p 5000:5000 cloudslab/fogbus2-remote_logger:1.0"
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

# Parse command
if [ $enable_tls -eq 0 ]; then
    if [ $in_container -eq 1 ]; then
        # Command of running RemoteLogger in container
        command="$docker_command_base $args $container_args"
    else
        # Command of running RemoteLogger
        command="$command_base $args"
    fi
else
    if [ $in_container -eq 1 ]; then
        # Command of running RemoteLogger in container with TLS
        command="$docker_command_base $args $tls_args $container_args"
    else
        # Command of running RemoteLogger with TLS
        command="$command_base $args $tls_args"
    fi
fi

# Set DB hostname
if [ $in_container -eq 1 ]; then
    toggle_hosts 1
else
    toggle_hosts 0
fi

info "$command"
eval $command
