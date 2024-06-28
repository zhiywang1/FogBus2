#!/usr/bin/expect -f

set timeout 30
set password "fogbus2135"

set images {
  "cloudslab/fogbus2-game_of_life25:1.0"
  "cloudslab/fogbus2-game_of_life55:1.0"
  "cloudslab/fogbus2-eye_detection:1.0"
  "cloudslab/fogbus2-game_of_life15:1.0"
  "cloudslab/fogbus2-game_of_life36:1.0"
  "cloudslab/fogbus2-game_of_life5:1.0"
  "cloudslab/fogbus2-game_of_life1:1.0"
  "cloudslab/fogbus2-game_of_life52:1.0"
  "cloudslab/fogbus2-game_of_life18:1.0"
  "cloudslab/fogbus2-naive_formula1:1.0"
  "cloudslab/fogbus2-face_detection:1.0"
  "cloudslab/fogbus2-game_of_life23:1.0"
  "cloudslab/fogbus2-game_of_life6:1.0"
  "cloudslab/fogbus2-game_of_life29:1.0"
  "cloudslab/fogbus2-game_of_life47:1.0"
  "cloudslab/fogbus2-game_of_life26:1.0"
  "cloudslab/fogbus2-game_of_life42:1.0"
  "cloudslab/fogbus2-game_of_life12:1.0"
  "cloudslab/fogbus2-game_of_life9:1.0"
  "cloudslab/fogbus2-naive_formula2:1.0"
  "cloudslab/fogbus2-game_of_life38:1.0"
  "cloudslab/fogbus2-game_of_life39:1.0"
  "cloudslab/fogbus2-blur_and_p_hash:1.0"
  "cloudslab/fogbus2-game_of_life0:1.0"
  "cloudslab/fogbus2-game_of_life31:1.0"
  "cloudslab/fogbus2-game_of_life48:1.0"
  "cloudslab/fogbus2-game_of_life8:1.0"
  "cloudslab/fogbus2-game_of_life30:1.0"
  "cloudslab/fogbus2-game_of_life50:1.0"
  "cloudslab/fogbus2-game_of_life17:1.0"
  "cloudslab/fogbus2-game_of_life40:1.0"
  "cloudslab/fogbus2-game_of_life51:1.0"
  "cloudslab/fogbus2-game_of_life16:1.0"
  "cloudslab/fogbus2-naive_formula0:1.0"
  "cloudslab/fogbus2-game_of_life60:1.0"
  "cloudslab/fogbus2-game_of_life3:1.0"
  "cloudslab/fogbus2-game_of_life37:1.0"
  "cloudslab/fogbus2-game_of_life4:1.0"
  "cloudslab/fogbus2-game_of_life2:1.0"
  "cloudslab/fogbus2-naive_formula3:1.0"
  "cloudslab/fogbus2-game_of_life21:1.0"
  "cloudslab/fogbus2-game_of_life44:1.0"
  "cloudslab/fogbus2-game_of_life34:1.0"
  "cloudslab/fogbus2-game_of_life61:1.0"
  "cloudslab/fogbus2-game_of_life33:1.0"
  "cloudslab/fogbus2-game_of_life27:1.0"
  "cloudslab/fogbus2-game_of_life49:1.0"
  "cloudslab/fogbus2-game_of_life32:1.0"
  "cloudslab/fogbus2-game_of_life20:1.0"
  "cloudslab/fogbus2-game_of_life13:1.0"
  "cloudslab/fogbus2-game_of_life58:1.0"
  "cloudslab/fogbus2-game_of_life7:1.0"
  "cloudslab/fogbus2-game_of_life22:1.0"
  "cloudslab/fogbus2-game_of_life56:1.0"
  "cloudslab/fogbus2-game_of_life24:1.0"
  "cloudslab/fogbus2-game_of_life28:1.0"
  "cloudslab/fogbus2-game_of_life28:1.0"
  "cloudslab/fogbus2-master:1.0"
  "cloudslab/fogbus2-user:1.0"
  "cloudslab/fogbus2-actor:1.0"
  "cloudslab/fogbus2-remote_logger:1.0"
}



foreach image $images {
    # The command you want to execute
    spawn docker trust sign "$image"

    # Here you respond to the expected prompt
    expect "Enter passphrase for root key with ID 3103146:"
    send "$password\r"

    # This allows the script to continue interacting until the process completes
    interact
}

