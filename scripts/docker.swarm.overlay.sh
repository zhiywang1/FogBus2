docker swarm init --advertise-addr <MANAGER-IP>
 docker swarm leave --force
docker swarm join --token <SWARM-JOIN-TOKEN> <MANAGER-IP>:2377
docker network create --driver overlay --attachable my-overlay
docker run -d --name container1 --network my-overlay nginx


# enable docker content trust
export DOCKER_CONTENT_TRUST=1

# when pull the not verified images cannot be pulled
# to verify the pulled images, attempt docker pull
docker image prune

# sign images
https://docs.docker.com/engine/security/trust/
docker trust key generate jeff
By default this is stored in ~/.docker/trust/

or
docker trust key load key.pem --name jeff

docker trust sign cloudslab/fogbus2-ocr:1.0


docker scout quickview cloudslab/fogbus2-remote_logger:1.0
docker scout cves cloudslab/fogbus2-remote_logger:1.0\n\n
docker scout recommendations cloudslab/fogbus2-remote_logger:1.0
