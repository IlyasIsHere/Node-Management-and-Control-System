from user import User

def main():
    # User information
    user_info = {
        'username': 'ilyas.boudhaine',
        'hostname': 'simlab-cluster.um6p.ma',
        'password': 'ilyas123'
    }

    # Create a User instance with password authentication
    user = User(**user_info)

    try:
        # Connect to the server
        if user.connect_to_server():
            print("Connected using password")

                        # Execute the SLURM command
            slurm_command = 'sinfo -o "%20N  %10c  %10m  %25f  %10G "'
            user.execute_command(slurm_command)

            # Execute get nodes method
            print("get_nodes:")
            print(user.get_nodes())

            # Execute get nodes info method
            print("get_nodes_info:")
            print(user.get_nodes_info())

            # Execute node jobs running info method
            print("node_jobs_running node04:")
            print(user.node_jobs_running("node04"))
            print("node_jobs_running node14:")
            print(user.node_jobs_running("node14"))

    finally:
        # Close the connection when done
        user.close_connection()

if __name__ == "__main__":
    main()
