# test_user.py

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

        # Perform interactions with the SSH connection
        # For example, you can execute remote commands or do other tasks here

    finally:
        # Close the connection when done
        user.close_connection()

if __name__ == "__main__":
    main()
