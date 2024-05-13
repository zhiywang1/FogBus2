import docker

from containers.master.sources.utils.master.networkController.networks import NetworkController


def test_network_controller():
    client = docker.from_env()
    network_controller = NetworkController(client)

    request_id = 0
    network_controller.create_network_for_request(request_id)

    networks = network_controller.list_all_networks()

    assert networks[0].name == "request-0"

    test_image = "library/hello-world:latest"
    client.images.pull(test_image)
    container = client.containers.create(test_image, network=networks[0].name, detach=True, name="test_container")
    container.remove(force=True)
