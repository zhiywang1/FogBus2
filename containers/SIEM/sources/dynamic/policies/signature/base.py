from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.serialization import load_pem_private_key, load_pem_public_key
from cryptography.x509 import load_pem_x509_certificate


def helper(dictionary):
    data = {}
    signeAttributes = dictionary['signedAttributes']
    for key in signeAttributes:
        data[key] = dictionary[key]
    if 'taskName' in data:
        taskName = data['taskName']
        dashIndex = taskName.find('-')
        if dashIndex != -1:
            data['taskName'] = taskName[:dashIndex]
    data['signedAttributes'] = signeAttributes
    data = str(data).encode()
    return data



class Singer:

    def __init__(self,
                 private_key_path):
        with open(private_key_path, 'rb') as private_key_file:
            private_key_pem = private_key_file.read()
        self.private_key_pem = private_key_pem
        self.private_key = load_pem_private_key(self.private_key_pem, password=None)

    # Sign data using the private key
    def create_signature(self,
                         data):
        signature = self.private_key.sign(
            data,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return signature.decode('iso-8859-1')

    def sign_dictionary(self,
                        dictionary):
        data = helper(dictionary)
        signature = self.create_signature(data)
        dictionary['signature'] = signature
        return dictionary


class Verifier:

    def __init__(self,
                 cert_path):
        with open(cert_path, 'rb') as cert_file:
            cert_pem = cert_file.read()
        self.certificate = load_pem_x509_certificate(cert_pem)
        self.public_key = self.certificate.public_key()

    def verify_signature(self,
                         signature,
                         data):
        signature = signature.encode('iso-8859-1')
        try:
            self.public_key.verify(
                signature,
                data,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return True
        except InvalidSignature:
            return False

    def verify_dictionary(self,
                          dictionary):
        signature = dictionary['signature']
        data = helper(dictionary)
        return self.verify_signature(signature, data)



