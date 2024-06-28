#!/usr/bin/expect -f

set timeout 30
set password "fogbus2135"

# The command you want to execute
spawn docker trust sign "cloudslab/fogbus2-game_of_life13:1.0"

# Here you respond to the expected prompt
expect "Enter passphrase for root key with ID 3103146:"
send "$password\r"

# This allows the script to continue interacting until the process completes
interact