#/bin/bash

info () {
  echo "[*] Use parsed command"
  formatted_command=$(echo "$1" | sed -e 's/ -/ \r\n  -/g')
  echo "$formatted_command"
  echo "[====================================]"
}

# Function to display help message
usage() {
    echo "Usage: $0 [-h hostname] [-r RemoteLogger hostname] [-m Master hostname] [-t enable TLS or not] [-c in container or not]"
    exit 1
}

# Initialize variables
hostname=""
remote_logger_hostname=""
master_hostname=""
enable_tls=0
in_container=0
enable_overlay=0

# Parse options using getopts
while getopts ":h:rmtco" opt; do
    case ${opt} in
        h )
            hostname=$OPTARG
            ;;
        r )
            remote_logger_hostname=$OPTARG
            ;;
        m )
            master_hostname=$OPTARG
            ;;
        t )
            enable_tls=1
            ;;
        c )
            in_container=1
            ;;
        o )
            enable_overlay=1
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

if [ -z "$remote_logger_hostname" ]; then
    remote_logger_hostname=$hostname
fi

if [ -z "$master_hostname" ]; then
    master_hostname=$hostname
fi


command_base="cd sources && python actor.py"
docker_command_base="docker run --rm --name Actor -v ./sources:/workplace -v /var/run/docker.sock:/var/run/docker.sock -p 50000:50000 cloudslab/fogbus2-actor:1.0"
args=" --bindIP $hostname --bindPort 50000 --remoteLoggerIP $remote_logger_hostname --remoteLoggerPort 5000 --masterIP $master_hostname --masterPort 5001 --domainName fogbus2 --certFile server.crt --keyFile server.key"
tls_args=" --enableTLS True"
container_args=" --containerName Actor"
overlay_args=" --enableOverlay True"

# Display parsed arguments
echo "[====================================]"
echo "[*] Hostname: $hostname"
echo "[*] Enable TLS: $enable_tls"
echo "[*] In container: $in_container"
echo "[*] Enable overlay: $enable_overlay"
echo "[*] Running Actor..."
echo "[====================================]"

# Parse command
if [ $enable_tls -eq 0 ]; then
  # Enable TLS is not set
  if [ $in_container -eq 1 ]; then
      # Command of running Actor in container
      command="$docker_command_base $args $container_args"
  else
      # Command of running Actor
      command="$command_base $args"
  fi
else
  # Enable TLS is set
  if [ $in_container -eq 1 ]; then
    # In container is set
    if [ $enable_overlay -eq 1 ]; then
      # Command of running Actor in container with TLS
      command="$docker_command_base $args $tls_args $container_args $overlay_args"
    else
      # Command of running Actor in container with TLS
      command="$docker_command_base $args $tls_args $container_args"
    fi
  else
    # In container is not set
    # Command of running Actor
    command="$command_base $args $tls_args"
  fi
fi

info "$command"
eval $command
