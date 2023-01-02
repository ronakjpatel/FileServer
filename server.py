import socket
import random
from threading import Thread
import os
import shutil
from pathlib import Path
import string


def get_working_directory_info(working_directory):
    """
    Creates a string representation of a working directory and its contents.
    :param working_directory: path to the directory
    :return: string of the directory and its contents.
    """

    dirs = '\n-- ' + '\n-- '.join([i.name for i in Path(working_directory).iterdir() if i.is_dir()])
    files = '\n-- ' + '\n-- '.join([i.name for i in Path(working_directory).iterdir() if i.is_file()])
    dir_info = f'Current Directory: {working_directory}:\n|{dirs}{files}'
    return dir_info


def generate_random_eof_token():
    """Helper method to generates a random token that starts with '<' and ends with '>'.
     The total length of the token (including '<' and '>') should be 10.
     Examples: '<1f56xc5d>', '<KfOVnVMV>'
     return: the generated token.
     """
    str = "<"+"".join(random.choices(string.ascii_uppercase+string.ascii_lowercase + string.digits, k = 8))+">"
    return str


def receive_message_ending_with_token(active_socket, buffer_size, eof_token):
    """
    Same implementation as in receive_message_ending_with_token() in client.py
    A helper method to receives a bytearray message of arbitrary size sent on the socket.
    This method returns the message WITHOUT the eof_token at the end of the last packet.
    :param active_socket: a socket object that is connected to the server
    :param buffer_size: the buffer size of each recv() call
    :param eof_token: a token that denotes the end of the message.
    :return: a bytearray message with the eof_token stripped from the end.
    """
    client_input=active_socket.recv(buffer_size)
    client_input = client_input.decode()

    if(client_input[-10:] == eof_token):
        print(f"[TRIMMED INPUT IS]{client_input}")
        return client_input[:-10]

    else:
        return False



def handle_cd(current_working_directory, new_working_directory):
    """
    Handles the client cd commands. Reads the client command and changes the current_working_directory variable 
    accordingly. Returns the absolute path of the new current working directory.
    :param current_working_directory: string of current working directory
    :param new_working_directory: name of the sub directory or '..' for parent
    :return: absolute path of new current working directory
    """
    if(new_working_directory == ".."):
        print("[CURRENT DIR PASSED]"+current_working_directory)
        current_working_directory = os.path.dirname(current_working_directory)
        return current_working_directory,get_working_directory_info(current_working_directory)
    else:
        temp_current_working_directory = current_working_directory+"/"+new_working_directory

        if (os.path.exists(temp_current_working_directory)):
            current_working_directory = temp_current_working_directory
            return current_working_directory,get_working_directory_info(current_working_directory)

        else:
            return current_working_directory,get_working_directory_info(current_working_directory)





def handle_mkdir(current_working_directory, directory_name):
    """
    Handles the client mkdir commands. Creates a new sub directory with the given name in the current working directory.
    :param current_working_directory: string of current working directory
    :param directory_name: name of new sub directory
    """
    try:
        if not os.path.isdir(current_working_directory+"/"+directory_name):
            os.mkdir(current_working_directory+"/"+directory_name)
        else:
            return('The directory is already present.')
    except OSError:
        return("Creation of the directory %s failed" % directory_name)
    else:
        return get_working_directory_info(current_working_directory)





def handle_rm(current_working_directory, object_name):
    """
    Handles the client rm commands. Removes the given file or sub directory. Uses the appropriate removal method
    based on the object type (directory/file).
    :param current_working_directory: string of current working directory
    :param object_name: name of sub directory or file to remove
    """

    path = current_working_directory+"/"+object_name
    if os.path.isdir(path):
        directory_to_be_removed = object_name
        # Parent Directory
        parent = current_working_directory
        # Path
        path = os.path.join(parent, directory_to_be_removed)

        try:
            os.rmdir(path)
            return get_working_directory_info(current_working_directory)
        except OSError as error:
            print(error)
            return ("Technical Issues" % directory_to_be_removed)
    elif os.path.isfile(path):
        if os.path.exists(path):
            os.remove(path)
            return get_working_directory_info(current_working_directory)
        else:
            return("The file '% s' does not exist!" %object_name)

    else:
        return ("The File or Directory '% s' does not exist!" % object_name)













def handle_ul(current_working_directory, file_name, service_socket, eof_token):
    """
    Handles the client ul commands. First, it reads the payload, i.e. file content from the client, then creates the
    file in the current working directory.
    Use the helper method: receive_message_ending_with_token() to receive the message from the client.
    :param current_working_directory: string of current working directory
    :param file_name: name of the file to be created.
    :param service_socket: active socket with the client to read the payload/contents from.
    :param eof_token: a token to indicate the end of the message.
    """
    print("INSIDE UL")

    file_content = bytearray()
    while True:
        packet = service_socket.recv(1024)
        if packet[-10:] == eof_token.encode():
            file_content += packet[:-10]
            break
        file_content += packet

    open(current_working_directory+"/"+file_name, 'wb')

    with open(current_working_directory+"/"+file_name, 'wb') as f:
        f.write(file_content)
        print("FILE HAS SUCCESSFULLY WRITTEN")
        f.close()

    return get_working_directory_info(current_working_directory)




def handle_dl(current_working_directory, file_name, service_socket, eof_token):
    """
    Handles the client dl commands. First, it loads the given file as binary, then sends it to the client via the
    given socket.
    :param current_working_directory: string of current working directory
    :param file_name: name of the file to be sent to client
    :param service_socket: active service socket with the client
    :param eof_token: a token to indicate the end of the message.
    """
    if os.path.exists(current_working_directory+"/"+file_name):
        service_socket.send("yesfile".encode())

        with open(current_working_directory+"/"+file_name, 'rb') as f:
            file_content = f.read()
        # EOF token
        file_content_with_token = file_content + eof_token.encode()
        print(file_content_with_token)
        service_socket.sendall(file_content_with_token)
        print(f'Sent the contents of ')
        return get_working_directory_info(current_working_directory)
    else:
        service_socket.send("nofile".encode())
        return get_working_directory_info(current_working_directory)


class ClientThread(Thread):
    def __init__(self, service_socket : socket.socket, address : str):
        Thread.__init__(self)
        self.service_socket = service_socket
        self.address = address
        self.CWD = os.getcwd()


    def run(self):

        print ("Connection from : ", self.address)


        # initialize the connection
        # send random eof token
        rand_token = generate_random_eof_token()

        self.service_socket.sendall(rand_token.encode())
        print(f"[Token Sent] Token is : {rand_token.encode()}")

        # establish working directory
        cwd_representation = get_working_directory_info(self.CWD)

        # send the current dir info
        self.service_socket.sendall(cwd_representation.encode())


        # while True:
            # get the command and arguments and call the corresponding method

            # send current dir info


        while True:
            packet = receive_message_ending_with_token(self.service_socket,1024,rand_token)

            print(f"Packet is {packet}")

            if(packet):
                if(packet=="exit"):
                    print(f"[RECEIVED USER MESSAGE]{packet}")
                    break

                if(packet[0:2]=="cd"):

                    splitted = packet.split()

                    self.CWD,new_cd_path = handle_cd(self.CWD,splitted[1])
                    print("[NEW CHANGED PATH]"+new_cd_path)
                    new_cd_path = (new_cd_path+rand_token).encode()
                    self.service_socket.sendall(new_cd_path)

                if (packet[0:5] == "mkdir"):
                    splitted = packet.split()
                    #CURRENT_WORKING_DIRECTORY = os.getcwd()
                    message = handle_mkdir(self.CWD, splitted[1])
                    print("[NEW CHANGED PATH]"+message)
                    message = (message+rand_token).encode()
                    self.service_socket.sendall(message)

                if (packet[0:2] == "rm"):
                    splitted = packet.split()
                    message = handle_rm(self.CWD, splitted[1])
                    print("[REMOVED FILE OR DIRECTORY]" + message)
                    message = (message+rand_token).encode()
                    self.service_socket.sendall(message)

                if (packet[0:2] == "ul"):
                    splitted = packet.split()
                    print("[SPLITTED 1 IS]"+splitted[1])
                    message=handle_ul(self.CWD, splitted[1],self.service_socket,rand_token)
                    print("[UPLOADED FILE OR DIRECTORY]" + message)
                    message = (message+rand_token).encode()
                    self.service_socket.sendall(message)

                if (packet[0:2] == "dl"):

                    splitted = packet.split()
                    print("[SPLITTED 1 IS]" + splitted[1])
                    message=handle_dl(self.CWD,splitted[1],self.service_socket,rand_token)
                    print("[DOWNLOADED FILE OR DIRECTORY]" + message)
                    message = (message+rand_token).encode()
                    self.service_socket.sendall(message)

        self.service_socket.close()

        return



def main():
    HOST = "127.0.0.1"
    PORT = 65432

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print("[SERVER IS LISTENING]")
        while True:
            conn, addr = s.accept()
            client_thread = ClientThread(conn, addr)
            client_thread.start()



if __name__ == '__main__':
    main()


