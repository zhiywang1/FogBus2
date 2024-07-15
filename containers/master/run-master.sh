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
    echo "Usage: $0 [-h hostname] [-r RemoteLogger hostname] [-t enable TLS or not] [-c in container or not] [-o enable overlay or not]"
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
default_port=5001
remote_logger_hostname=""
enable_tls=0
in_container=0
enable_overlay=0
env_file="./sources/.env"
out_container_db_host="127.0.0.1"
in_container_db_host="host.docker.internal"

# Parse options using getopts
while getopts ":h:r:tco" opt; do
    case ${opt} in
        h )
            hostname=$OPTARG
            ;;
        r )
            remote_logger_hostname=$OPTARG
            ;;
        t )
            enable_tls=1
            ;;
        c )
            in_container=1
            ;;
        o )
            enable_overlay=1
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
  echo "[!] Hostname or enable overlay is required."
  usage
fi

if [ -z "$remote_logger_hostname" ]; then
    remote_logger_hostname=$hostname
fi

command_base="cd sources && python master.py"
docker_command_base="docker run"
container_name="Master_${hostname}_$default_port"
docker_args=" --rm --name $container_name -v ./sources:/workplace -v /var/run/docker.sock:/var/run/docker.sock -p $default_port:$default_port -p 60000:60000 cloudslab/fogbus2-master:1.0"
docker_overlay_args=" --network=fogbus2"
args=" --advertiseIP $hostname --bindPort $default_port --remoteLoggerIP $remote_logger_hostname --remoteLoggerPort 5000 --domainName fogbus2 --certFile server.crt --keyFile server.key"
tls_args=" --enableTLS True"
container_args=" --containerName $container_name"
overlay_args=" --enableOverlay True"

# Display parsed arguments
echo "[====================================]"
echo "[*] Hostname: $hostname"
echo "[*] Enable TLS: $enable_tls"
echo "[*] In container: $in_container"
echo "[*] Enable overlay: $enable_overlay"
echo "[*] Running Master..."
echo "[====================================]"

# Set DB hostname
if [ $in_container -eq 1 ]; then
    toggle_hosts 1
else
    toggle_hosts 0
fi

# Parse command
if [ $in_container -eq 0 ]; then
  ## not enable container
  command="$command_base $args"
else
  ## enable container
  if [ $enable_overlay -eq 0  ]; then
    ## not enable overlay
    command="$docker_command_base $docker_args $args $container_args"
  else
    ## enable overlay
    command="$docker_command_base $docker_overlay_args $docker_args $args $container_args $overlay_args"
  fi
fi

## enable tls
if [ $enable_tls -eq 1 ]; then
  command="$command $tls_args"
fi

info "$command"
eval $command
