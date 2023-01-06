
# File Server 📟  
## Overview
I have implmented the file server using python socket programming. User can connect to the file 
server using the IP address and port number. Once the connection establishes, user can run commands that allows user to upload, remove, downlaod files over the network inside the file server.

<p align="center">
<img width="616" height="600" alt="Screenshot 2023-01-05 at 4 12 07 pm" src="https://user-images.githubusercontent.com/40088060/210881053-4737b888-4df3-4bfd-a532-cbabc776d21b.png">

</p>


## Command Samples
Following command moves the user up one directory from the current working directory.
``` bash
cd ..
```

Following command will put the user in a subdirectory named **folder_name** in this case. 

``` bash
cd folder_name
```

Following command will create the new directory named **folder_name** in this case. 

``` bash
mkdir folder_name
```

Following command will remove the folder named **folder_name** in this case. You can also remove the file by giving file's name.

``` bash
rm folder_name [/file-name.txt]
```

Following command will upload a file from the client to the current
working directory on the server. 

``` bash
ul file-name.txt
```

Following command will download a file from the current working directory on the server to the client.

``` bash
dl file-name.txt
```

Following command will exits the applications.

``` bash
exit
```
## Some Features 🔥

* When client tries to establish the connection with server, firstly it shares the unique TOKEN to client machine. Once the varification process from both ends suucessfully completes only then they would be able to communicate to each other. This feature enhances the security of the file server, if some anonymous tries to connect to the server, server will immediately refuses the connection. This TOKEN will be shared every time client issues the commands to server. 

* The server is capable of handling multiple clients at the same time, therefore ideally no down-time for any client. Every client's session will be unique.


## Run Locally  💫
Before running the project make sure you have python installed in your computer.

Clone the project

```bash
  git clone https://github.com/ronakjpatel/FileServer.git
```

Go to the project directory

```bash
  cd my-project
```

Start the server

```bash
  python server.py
```

Connect to server from client side
```bash
  python client.py
```

## Lessons Learned 💪

I learned the basics of python socket programming after finishing this project. Overall, it was a great learning experience for me. I look forward to do more interesting projects of the same type in the future,

## Tech Stack

Python 🐍 
 


## 🔗 Links
[![portfolio](https://img.shields.io/badge/my_portfolio-000?style=for-the-badge&logo=ko-fi&logoColor=white)](www.patelrj.com) 

[![linkedin](https://img.shields.io/badge/linkedin-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/ronak-p/)

[![medium](https://img.shields.io/badge/Medium-12100E?style=for-the-badge&logo=medium&logoColor=white)](https://medium.com/@rjpatel7991)
