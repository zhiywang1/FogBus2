import json
from .signature.base import Verifier


class ContainerSuspiciousImagePolicy:

    def __init__(self):
        self.valid_images = set(self.get_valid_images())

    @staticmethod
    def get_valid_images():
        with open('valid_images.list', 'r') as f:
            return [line.strip() for line in f.readlines()]

    def apply(self,
              data):
        containers = data['data']
        suspicious_containers = []
        for container in containers:
            image_id = container['image_id']
            if image_id not in self.valid_images:
                suspicious_containers.append(container)
        if len(suspicious_containers):
            body = '\r\n'.join([str(container) for container in suspicious_containers])
            return '[WARNING] Suspicious Container with Unrecognized Image', body, suspicious_containers
        return None, None, None


def format_args(args):
    args_formatted = {}

    for i, arg in enumerate(args):
        if arg.startswith('--'):
            arg = arg[2:]
            if arg == 'childrenTaskTokens':
                if args[i + 1] == 'None':
                    args_formatted[arg] = []
                else:
                    args_formatted[arg] = args[i + 1].split(',')
            else:
                args_formatted[arg] = args[i + 1]
    return args_formatted


class ContainerSuspiciousSignaturePolicy:

    def __init__(self,
                 cert_path):
        self.verifier = Verifier(cert_path=cert_path)

    def apply(self,
              data):
        containers = data['signature_data']
        suspicious_containers = []
        for container in containers:
            if not container['labels'] or 'signature' not in container['labels']:
                continue
            args = container['args']
            formatted_args = format_args(args)

            signature = container['labels']['signature']
            signedAttributes = json.loads(container['labels']['signedAttributes'])
            data = {}
            for key in signedAttributes:
                data[key] = formatted_args[key]
            data['signedAttributes'] = signedAttributes
            data['signature'] = signature
            if not self.verifier.verify_dictionary(data):
                suspicious_containers.append(container)
        if len(suspicious_containers):
            body = '\r\n'.join([str(container) for container in suspicious_containers])
            return '[WARNING] Suspicious Container with Invalid Signature', body, suspicious_containers
        return None, None, None
