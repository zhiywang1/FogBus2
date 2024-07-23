#/bin/bash
set -e
# Download the video if it is not downloaded
bash download-video.sh

info () {
  echo "[*] Use parsed command"
  formatted_command=$(echo "$1" | sed -e 's/ -/ \r\n  -/g')
  echo "$formatted_command"
  echo "[====================================]"
}

# Function to display help message
usage() {
    echo "Usage: $0 [-h hostname] [-m Master hostname] [-t enable TLS or not] [-c in container or not] [-o enable overlay or not] [-e extended application arguments] [-w show window or not]"
    exit 1
}

# Initialize variables
hostname=""
master_hostname=""
enable_tls=0
in_container=0
enable_overlay=0
extendedAppArgs=""
show_window=0

# Parse options using getopts
while getopts ":h:m:e:tcow" opt; do
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
        e )
            extendedAppArgs=$OPTARG
            ;;
        w )
            show_window=1
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
    if [ $enable_overlay -eq 0 ]; then
      echo "[!] Hostname or enable overlay is required."
      usage
    else
      hostname="Actor"
      master_hostname="Master"
    fi
  else
    if [ $enable_overlay -eq 0 ]; then
      enable_overlay=0
    else
      echo "[!] Cannot use hostname when overlay is enabled."
      usage
    fi
fi

if [ -z "$master_hostname" ]; then
    master_hostname=$hostname
fi

if [ -z "$extendedAppArgs" ]; then
    extendedAppArgs="--applicationName ObjectDetection --videoPath ../highway-traffic.mp4 --taskCount 1"
fi

command_base="cd sources && python user.py"
docker_command_base="docker run"
docker_args=" --rm --name User -v ./highway-traffic.mp4:/highway-traffic.mp4 -v ./sources:/workplace -v /var/run/docker.sock:/var/run/docker.sock -p 50101:50101 cloudslab/fogbus2-user:1.0"
docker_overlay_args=" --network=fogbus2"
set_user_master () {
  args=" --bindIP $1 --bindPort 50101 --masterIP $2 --masterPort 5001 --domainName fogbus2 --certFile server.crt --keyFile server.key"
}
set_user_master $hostname $master_hostname
tls_args=" --enableTLS True"
container_args=" --containerName User"
window_args=" --windowHeight 640"

# Display parsed arguments
echo "[====================================]"
echo "[*] Hostname: $hostname"
echo "[*] Enable TLS: $enable_tls"
echo "[*] In container: $in_container"
echo "[*] Enable overlay: $enable_overlay"
echo "[*] Running User..."
echo "[====================================]"

# Parse command
if [ $enable_tls -eq 0 ]; then
  # Enable TLS is not set
  if [ $in_container -eq 1 ]; then
    if [ $enable_overlay -eq 1 ]; then
      # Command of running User in container with overlay
      set_user_master "User" "Master"
      command="$docker_command_base $docker_overlay_args $docker_args $args $container_args"
    else
      # Command of running User in container
      command="$docker_command_base $docker_args $args $container_args"
    fi
  else
    if [ $show_window -eq 1 ]; then
      # Command of running User and show window
      command="$command_base $args $window_args"
    else
      # Command of running User
      command="$command_base $args"
    fi
  fi
else
  # Enable TLS is set
  if [ $in_container -eq 1 ]; then
    # In container is set
    if [ $enable_overlay -eq 1 ]; then
      # Command of running User in container with TLS and overlay
      set_user_master "User" "Master"
      command="$docker_command_base $docker_overlay_args $docker_args $args $tls_args $container_args"
    else
      # Command of running User in container with TLS
      command="$docker_command_base $docker_args $args $tls_args $container_args"
    fi
  else
    # In container is not set
    if [ $show_window -eq 1 ]; then
      # Command of running User with TLS and show window
      command="$command_base $args $tls_args $window_args"
    else
      # Command of running User with TLS
      command="$command_base $args $tls_args"
    fi
  fi
fi

command="$command $extendedAppArgs"
info "$command"
eval $command
