class HostConfigPolicy:

    def __init__(self):
        self.allowed_user = {'debian', 'ubuntu'}

    def apply(self,
              data):
        data = data['data']
        logged_in_users = data['logged_in_users']
        invalid_users = []
        for user in logged_in_users:
            if user not in self.allowed_user:
                invalid_users.append(user)
        if len(invalid_users) > 0:
            body = '\r\n'.join(invalid_users)
            return '[WARNING] Suspicious Users Logged In', body
        return None, None
