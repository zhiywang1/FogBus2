build() {

  cd $1
  docker compose \
    build
  cd ..
}

build remoteLogger
build master
build user
build actor
cd taskExecutor/dockerFiles/ && ./rebuild.sh
