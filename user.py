import paramiko
import re
import logging

logging.basicConfig(level=logging.INFO)

class User:
    def __init__(self, username, hostname):
        self.username = username
        self.hostname = hostname
        self.ssh_client = None

    def connect_to_server(self, password):
        try:
            # Create an SSH client
            self.ssh_client = paramiko.SSHClient()

            # Automatically add the server's host key
            self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            # Connect to the remote server using password authentication
            if password:
                self.ssh_client.connect(self.hostname, username=self.username, password=password)
            else:
                raise ValueError("No password provided")

            logging.info(f"Connected to {self.hostname} as {self.username}")

            return True
        
        except paramiko.SSHException as e:
            logging.error(f"SSH error: {str(e)}")
            return False
        except Exception as e:
            logging.error(f"Error connecting to the server: {str(e)}")
            return False

    def close_connection(self):
        try:
            if self.ssh_client:
                self.ssh_client.close()
                logging.info("Connection closed")
                return True
        except Exception as e:
            logging.error(f"Error closing the connection: {str(e)}")
            return False

    def execute_command(self, command):
        try:
            # Check if the connection is established
            if not self.ssh_client:
                logging.warning("Not connected to the server.")
                return None

            # Execute the remote command
            stdin, stdout, stderr = self.ssh_client.exec_command(command)

            # Get the output of the command
            output = stdout.read().decode("utf-8")
            error = stderr.read().decode("utf-8")

            if error:
                logging.error(f"Error executing command: {error}")
            else:
                return output

        except Exception as e:
            logging.error(f"Error executing remote command: {str(e)}")

    def get_nodes(self): 
        # Execute the SLURM command
        slurm_command = 'sinfo -o "%20N"'
        slurm_output = self.execute_command(slurm_command)

        # Parse and format the output
        nodes = []
        node = ""
        for line in slurm_output[8:]:
            elem = line.strip()
            if elem == ",":
                nodes.append(node)
                node = ""
            else:
                node += elem

        # Handle the last node because it is not followed by a comma ","
        if node:
            nodes.append(node)

        # Split node ranges (example: node[01-03] becomes node01, node02, node03
        pattern = r'^node\[(\d{1,2})-(\d{1,2})\]$'
        expanded_nodes = []
        for node in nodes.copy():
            match = re.match(pattern, node)
            if match:
                first_node = int(match.group(1))
                last_node = int(match.group(2))
                nodes.remove(node)
                expanded_nodes.extend([f"node{i:02d}" for i in range(first_node, last_node + 1)])

        # Add the expanded nodes back to the list
        nodes.extend(expanded_nodes)

        return nodes

    def node_jobs_running(self, node):
        # Execute the SLURM command
        slurm_command = 'squeue -h -w {node_name} -o "%.8T" | grep -c "R"'.format(node_name = node)
        slurm_output = self.execute_command(slurm_command)

        return int(slurm_output)
        
    def get_nodes_info(self):
        # Execute the SLURM command
        slurm_command = 'scontrol show nodes'
        slurm_output = self.execute_command(slurm_command)

        # Parse and format the output
        nodes_info = {}

        # Define patterns to extract information
        node_info_pattern = re.compile(r'NodeName=(\S+)(.*?)(?=(?:NodeName=|\Z))', re.DOTALL)
        specific_keys_pattern = re.compile(r'(CPUAlloc|CPUErr|CPUTot|AllocMem|FreeMem|Gres|AvailableFeatures)=(\S+)')

        matches = node_info_pattern.findall(slurm_output)

        for match in matches:
            node_name, inner_info = match

            specific_keys_matches = specific_keys_pattern.findall(inner_info)

            if specific_keys_matches:
                node_info = {key: value for key, value in specific_keys_matches}
                node_info['curr_r_jobs'] = self.node_jobs_running(node_name)
                nodes_info[node_name] = node_info

        return nodes_info
