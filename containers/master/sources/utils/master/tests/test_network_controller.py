import docker

from containers.master.sources.utils.master.networkController.networks import NetworkController


def test_network_controller():
    client = docker.from_env()
    network_controller = NetworkController(client)

    request = 'User-NaiveFormulaSerialized-480-1_100.106.159.123-50101_Master-?_100.106.159.123-5001'
    network = network_controller.create_network_for_request(request)

    test_image = "library/hello-world:latest"
    client.images.pull(test_image)
    container = client.containers.create(test_image, network=network.name, detach=True, name="test_container")
    container.remove(force=True)

    network_controller.delete_network(network.name)


def test_init_swarm_manager():
    client = docker.from_env()
    network_controller = NetworkController(client)
    network_controller.init_swarm_manager('127.0.0.1')
    worker_join_token = network_controller.get_worker_join_token()
    assert len(worker_join_token) > 0
