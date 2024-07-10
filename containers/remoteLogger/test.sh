toggle_hosts() {
    local file="./sources/.env"

    # Read current values
    HOST1=$(grep '^HOST1=' "$file" | cut -d '=' -f 2)
    HOST=$(grep '^HOST=' "$file" | cut -d '=' -f 2)

    # Check if both values are found
    if [[ -z "$HOST1" || -z "$HOST" ]]; then
        echo "Both HOST and HOST1 must be set in the .env file."
        return 1
    fi

    # Create a temporary file
    tmp_file=$(mktemp)

    # Swap the values
    sed -e "s/^HOST1=$HOST1/HOST1=$HOST/" -e "s/^HOST=$HOST/HOST=$HOST1/" "$file" > "$tmp_file"

    # Move the temporary file to the original file
    mv "$tmp_file" "$file"

    echo "HOST and HOST1 values have been swapped."
}

# To use the function, just call it
toggle_hosts
