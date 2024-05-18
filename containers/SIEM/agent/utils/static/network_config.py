import subprocess
from ..common import ToDict


class NetworkConfig(ToDict):
    def __init__(self):
        self.iptables_rules = ""
        self.parsed_rules = []

    def get_iptables_rules(self):
        try:
            result = subprocess.run(['sudo', 'iptables', '-L', '-v', '-n'], stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE, text=True)
            if result.returncode == 0:
                self.iptables_rules = result.stdout
            else:
                self.iptables_rules = f"Error: {result.stderr}"
        except Exception as e:
            self.iptables_rules = f"Exception occurred: {str(e)}"

    def parse_iptables_rules(self):
        if "Error" in self.iptables_rules or "Exception occurred" in self.iptables_rules:
            self.parsed_rules = {"error": self.iptables_rules}
            return

        lines = self.iptables_rules.splitlines()
        current_chain = None

        for line in lines:
            if line.startswith("Chain"):
                parts = line.split()
                current_chain = {
                    "chain": parts[1],
                    "policy": parts[3] if len(parts) > 3 else None,
                    "rules": []
                }
                self.parsed_rules.append(current_chain)
            elif line and current_chain and not line.startswith(("target", "pkts", "Chain")):
                parts = line.split()
                rule = {
                    "target": parts[0],
                    "prot": parts[1],
                    "opt": parts[2],
                    "source": parts[4],
                    "destination": parts[5],
                    "options": " ".join(parts[6:]) if len(parts) > 6 else ""
                }
                current_chain["rules"].append(rule)


if __name__ == "__main__":
    network_config = NetworkConfig()
    network_config.get_iptables_rules()
    network_config.parse_iptables_rules()
    print(network_config)
