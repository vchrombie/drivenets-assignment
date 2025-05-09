class Device:
    def __init__(self, hostname, username, password, vendor, port=None):
        self.hostname = hostname
        self.username = username
        self.password = password
        self.vendor = vendor
        self.port = port
