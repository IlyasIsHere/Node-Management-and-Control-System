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

    def execute_command(self, command):
        try:
            # Check if the connection is established
            if not self.ssh_client:
                print("Not connected to the server.")
                return None

            # Execute the remote command
            stdin, stdout, stderr = self.ssh_client.exec_command(command)

            # Get the output of the command
            output = stdout.read().decode("utf-8")
            error = stderr.read().decode("utf-8")

            if error:
                print(f"Error executing command: {error}")
            else:
                print(f"Command executed successfully:\n{output}")
                return output

            # Other way of getting the output of the command, to use in get_nodes_info

            # # Get the output of the command
            # output_lines = stdout.read().decode("utf-8").splitlines()

            # return output_lines

        except Exception as e:
            print(f"Error executing remote command: {str(e)}")

    # TO DO : handle parsing properly in get_nodes_info

    # def get_nodes_info(self): 
    #     # Execute the SLURM command and parse the data
    #     slurm_command = 'sinfo -o "%20N  %10c  %10m  %25f  %10G "'
    #     slurm_output = self.execute_command(slurm_command)

    #     # Parse and format the output
    #     parsed_data = {}
    #     for line in slurm_output[1:]:  # Skip the header
    #         node, cpus, memory, features, gres = line.split(None, 4)
    #         parsed_data[node] = {
    #             'CPUs': int(cpus),
    #             'Memory': int(memory),
    #             'Available Features': features,
    #             'GRES': gres
    #         }

    #     return parsed_data
