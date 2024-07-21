#/bin/bash

info () {
  echo "[*] Use parsed command"
  formatted_command=$(echo "$1" | sed -e 's/ -/ \r\n  -/g')
  echo "$formatted_command"
  echo "[====================================]"
}

# Function to display help message
usage() {
    echo "Usage: $0 [-h hostname] [-m Master hostname] [-t enable TLS or not] [-c in container or not] [-o enable overlay or not]"
    exit 1
}

# Initialize variables
hostname=""
default_port=50000
master_hostname=""
default_master_port=5001
enable_tls=0
in_container=0
enable_overlay=0

# Parse options using getopts
while getopts ":h:m:tco" opt; do
    case ${opt} in
        h )
            hostname=$OPTARG
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
if [ $enable_overlay -eq 0 ]; then
    if [ -z "$hostname" ]; then
      echo "[!] hostname is required."
      usage
    fi
  else
    if [ -z "$hostname" ]; then
      echo "[!] Hostname is required when overlay is enabled."
      usage
    else
      if [ -z "$master_hostname" ]; then
        echo "[!] Master hostname is required when overlay is enabled."
        usage
      else
        master_hostname="Master_${master_hostname}_$default_master_port"
      fi
    fi
fi

if [ -z "$master_hostname" ]; then
    master_hostname=$hostname
fi

command_base="cd sources && python actor.py"
docker_command_base="docker run"
container_name="Actor_${hostname}_$default_port"
docker_args=" --rm --name $container_name -v ./sources:/workplace -v /var/run/docker.sock:/var/run/docker.sock -p $default_port:$default_port cloudslab/fogbus2-actor:1.0"
docker_overlay_args=" --network=fogbus2"
args=" --bindIP $hostname --bindPort $default_port --masterIP $master_hostname --masterPort 5001 --domainName fogbus2"
tls_args=" --enableTLS True --certFile server.crt --keyFile server.key"
container_args=" --containerName $container_name"
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
