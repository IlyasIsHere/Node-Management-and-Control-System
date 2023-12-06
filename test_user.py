from user import User

def main():
    # User information
    user_info = {
        'username': 'ilyas.boudhaine',
        'hostname': 'simlab-cluster.um6p.ma',
        'password': 'ilyas123'
    }

    # Create a User instance
    user = User(**user_info)

    try:
        # Connect to the server
        user.connect_to_server()

        # Execute the SLURM command
        slurm_command = 'sinfo -o "%20N  %10c  %10m  %25f  %10G "'
        user.execute_command(slurm_command)

    finally:
        # Close the connection when done
        user.close_connection()

if __name__ == "__main__":
    main()
