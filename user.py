import paramiko

class User:
    def __init__(self, username, hostname, password):
        self.username = username
        self.hostname = hostname
        self.password = password
        self.ssh_client = None

    def connect_to_server(self):
        try:
            # Create an SSH client
            self.ssh_client = paramiko.SSHClient()

            # Automatically add the server's host key
            self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            # Connect to the remote server
            self.ssh_client.connect(self.hostname, username=self.username, password=self.password)
            
            print(f"Connected to {self.hostname} as {self.username}")

        except Exception as e:
            print(f"Error connecting to the server: {str(e)}")

    def close_connection(self):
        try:
            # Close the SSH connection
            if self.ssh_client:
                self.ssh_client.close()
                print("Connection closed")
        except Exception as e:
            print(f"Error closing the connection: {str(e)}")
