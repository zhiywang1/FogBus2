#/bin/bash

# Video by Mike Bird from Pexels: https://www.pexels.com/video/traffic-flow-in-the-highway-2103099/
video_filename="highway-traffic.mp4"
# Check if the video is downloaded
if [ -f "$video_filename" ]; then
    echo "[*] Video has been downloaded: $video_filename"
    exit 0
fi
# Download the video
video_url="https://videos.pexels.com/video-files/2103099/2103099-uhd_3840_2160_30fps.mp4"
echo "[*] Downloading the video: $video_filename from $video_url"
wget -O "$video_filename" "$video_url"
