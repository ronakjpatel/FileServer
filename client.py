import socket
import os

def receive_message_ending_with_token(active_socket, buffer_size, eof_token):
    """
    Same implementation as in receive_message_ending_with_token() in server.py
    A helper method to receives a bytearray message of arbitrary size sent on the socket.
    This method returns the message WITHOUT the eof_token at the end of the last packet.
    :param active_socket: a socket object that is connected to the server
    :param buffer_size: the buffer size of each recv() call
    :param eof_token: a token that denotes the end of the message.
    :return: a bytearray message with the eof_token stripped from the end.
    """
    server_response = active_socket.recv(buffer_size)
    server_response = server_response.decode()

    if (server_response[-10:] == eof_token):
        return server_response[:-10]

    else:
        return False;


def initialize(host, port):
    global eof_token

    s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))
    eof_token = s.recv(10).decode('utf-8')
    current_dir = s.recv(1024)
    decoded_string = current_dir.decode("unicode_escape")

    # """
    # 1) Creates a socket object and connects to the server.
    # 2) receives the random token (10 bytes) used to indicate end of messages.
    # 3) Displays the current working directory returned from the server (output of get_working_directory_info() at the server).
    # Use the helper method: receive_message_ending_with_token() to receive the message from the server.
    # :param host: the ip address of the server
    # :param port: the port number of the server
    # :return: the created socket object
    # """

    print('Connected to server at IP:', host, 'and Port:', port)
    print('Handshake Done. EOF is:', eof_token)
    print(decoded_string)

    return s


def issue_cd(command_and_arg, client_socket, eof_token):
    """
    Sends the full cd command entered by the user to the server. The server changes its cwd accordingly and sends back
    the new cwd info.
    Use the helper method: receive_message_ending_with_token() to receive the message from the server.
    :param command_and_arg: full command (with argument) provided by the user.
    :param client_socket: the active client socket object.
    :param eof_token: a token to indicate the end of the message.
    """

    command = command_and_arg+eof_token
    client_socket.sendall(command.encode())


def issue_mkdir(command_and_arg, client_socket, eof_token):
    """
    Sends the full mkdir command entered by the user to the server. The server creates the sub directory and sends back
    the new cwd info.
    Use the helper method: receive_message_ending_with_token() to receive the message from the server.
    :param command_and_arg: full command (with argument) provided by the user.
    :param client_socket: the active client socket object.
    :param eof_token: a token to indicate the end of the message.
    """
    command = command_and_arg + eof_token
    client_socket.sendall(command.encode())


def issue_rm(command_and_arg, client_socket, eof_token):
    """
    Sends the full rm command entered by the user to the server. The server removes the file or directory and sends back
    the new cwd info.
    Use the helper method: receive_message_ending_with_token() to receive the message from the server.
    :param command_and_arg: full command (with argument) provided by the user.
    :param client_socket: the active client socket object.
    :param eof_token: a token to indicate the end of the message.
    """
    command = command_and_arg + eof_token
    client_socket.sendall(command.encode())



def issue_ul(command_and_arg, client_socket, eof_token):
    """
    Sends the full ul command entered by the user to the server. Then, it reads the file to be uploaded as binary
    and sends it to the server. The server creates the file on its end and sends back the new cwd info.
    Use the helper method: receive_message_ending_with_token() to receive the message from the server.
    :param command_and_arg: full command (with argument) provided by the user.
    :param client_socket: the active client socket object.
    :param eof_token: a token to indicate the end of the message.
    """
    command = command_and_arg + eof_token
    client_socket.send(command.encode())
    filename = command_and_arg.split()[1]
    if os.path.exists(filename):
        with open(filename, 'rb') as f:
            file_content = f.read()
        # EOF token
        file_content_with_token = file_content + eof_token.encode()
        client_socket.sendall(file_content_with_token)
    else:
        return "NO SUCH FILE EXISTS IN YOUR MACHINE"




def issue_dl(command_and_arg, client_socket, eof_token):
    """
    Sends the full dl command entered by the user to the server. Then, it receives the content of the file via the
    socket and re-creates the file in the local directory of the client. Finally, it receives the latest cwd info from
    the server.
    Use the helper method: receive_message_ending_with_token() to receive the message from the server.
    :param command_and_arg: full command (with argument) provided by the user.
    :param client_socket: the active client socket object.
    :param eof_token: a token to indicate the end of the message.
    :return:
    """

    command = command_and_arg + eof_token
    filename = command_and_arg.split()[1]
    client_socket.send(command.encode())

    msg = client_socket.recv(1024).decode()
    if(msg =="yesfile"):
        file_content = bytearray()
        while True:
            packet = client_socket.recv(1024)
            if packet[-10:] == eof_token.encode():
                file_content += packet[:-10]
                break
            file_content += packet

        open(filename, 'wb')

        with open(filename, 'wb') as f:
            f.write(file_content)
            f.close()
    elif(msg=="nofile"):
        return "NO SUCH FILE EXISTS AT THE SERVER SIDE"











def main():
    HOST = "127.0.0.1"  # The client's hostname or IP address
    PORT = 65432  # The port used by the client

    # initialize
    ss = initialize(HOST, PORT)
    with ss:

    # while True:
    # get user input

    # call the corresponding command function or exit
        while True:
            usr_input = input('Enter your command:\n')

            if (usr_input == "exit"):
                exit_str = "exit" + eof_token
                ss.sendall(exit_str.encode())
                break

            elif (usr_input[0:2] == "cd"):
                issue_cd(usr_input,ss,eof_token)
                current_dir1 = receive_message_ending_with_token(ss,1024,eof_token)
                if not current_dir1 :
                    print("[ERROR] TOKEN MISMATCH")
                else:
                    print(current_dir1)

            elif (usr_input[0:5] == "mkdir"):
                issue_mkdir(usr_input,ss,eof_token)
                server_message = receive_message_ending_with_token(ss,1024,eof_token)
                if (server_message):
                    print(server_message)
                else:
                    print("[ERROR] TOKEN MISMATCH")

            elif (usr_input[0:2] == "rm"):
                issue_rm(usr_input,ss,eof_token)
                server_message = receive_message_ending_with_token(ss, 1024, eof_token)
                if (server_message):
                    print(server_message)
                else:
                  print("[ERROR] TOKEN MISMATCH")

            elif (usr_input[0:2] == "ul"):
                mm = issue_ul(usr_input,ss,eof_token)
                if(mm):
                    print(mm)
                else:
                    server_message = receive_message_ending_with_token(ss, 1024, eof_token)
                    if (server_message):
                        print(server_message)
                    else:
                        print("[ERROR] TOKEN MISMATCH")

            elif (usr_input[0:2] == "dl"):
                mm = issue_dl(usr_input,ss,eof_token)
                if(mm):
                    print(mm)
                server_message = receive_message_ending_with_token(ss, 1024, eof_token)
                if (server_message):
                    print(server_message)
                else:
                    print("[ERROR] TOKEN MISMATCH")
            else:
                print("NOT VALID COMMAND")

            ss.send(usr_input.encode())

        ss.close()

    print('THANK YOU Exiting the application.')


if __name__ == '__main__':
    main()
