def is_connection_to_port_80_denied(iptables_rules):
    rules = iptables_rules.splitlines()
    for rule in rules:
        if 'DROP' in rule and 'dpt:80' in rule:
            return True
    return False


class NetworkPolicy:

    @staticmethod
    def apply(data):
        iptables_rules = data['data']['iptables_rules']
        if not is_connection_to_port_80_denied(iptables_rules):
            return '[WARNING] Connection to Port 80 Is Not Denied', ''
        return None, None
