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
master_hostname=""
enable_tls=0
in_container=0
enable_overlay=""

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
if [ -z "$hostname" ]; then
    if [ -z "$enable_overlay" ]; then
      echo "[!] Hostname or enable overlay is required."
      usage
    else
      hostname="Actor"
      master_hostname="Master"
    fi
  else
    if [ -z "$enable_overlay" ]; then
      enable_overlay=0
    else
      echo "[!] Cannot use hostname when overlay is enabled."
      usage
    fi
fi

if [ -z "$master_hostname" ]; then
    master_hostname=$hostname
fi

command_base="cd sources && python actor.py"
docker_command_base="docker run"
docker_args=" --rm --name Actor -v ./sources:/workplace -v /var/run/docker.sock:/var/run/docker.sock -p 50000:50000 cloudslab/fogbus2-actor:1.0"
docker_overlay_args=" --network=fogbus2"
set_actor_master () {
  args=" --bindIP $1 --bindPort 50000 --masterIP $2 --masterPort 5001 --domainName fogbus2"
}
set_actor_master $hostname $master_hostname
tls_args=" --enableTLS True --certFile server.crt --keyFile server.key"
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
      if [ $enable_overlay -eq 1 ]; then
        # Command of running Actor in container with overlay
        set_actor_master "Actor" "Master"
        command="$docker_command_base $docker_overlay_args $docker_args $args $container_args $overlay_args"
      else
        # Command of running Actor in container
        command="$docker_command_base $docker_args $args $container_args"
      fi
  else
      # Command of running Actor
      command="$command_base $args"
  fi
else
  # Enable TLS is set
  if [ $in_container -eq 1 ]; then
    # In container is set
    if [ $enable_overlay -eq 1 ]; then
      # Command of running Actor in container with TLS and overlay
      set_actor_master "Actor" "Master"
      command="$docker_command_base $docker_overlay_args $docker_args $args $tls_args $container_args $overlay_args"
    else
      # Command of running Actor in container with TLS
      command="$docker_command_base $docker_args $args $tls_args $container_args"
    fi
  else
    # In container is not set
    # Command of running Actor with TLS
    command="$command_base $args $tls_args"
  fi
fi

info "$command"
eval $command
