from .actors import DiscoveredActors
from .masters import DiscoveredMasters


class DiscoveredManager:
    actors: DiscoveredActors = DiscoveredActors()
    masters: DiscoveredMasters = DiscoveredMasters()
