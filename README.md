# 1. Implementation of the *Zero Knowledge Protocol* (ZKP) – Authentication Phase

The code in this repository simulates the authentication process using the ZKP protocol. In the presented context, the User (VPN Client) acts as the *prover*, while the VPN (VPN Server) plays the role of the *verifier*. The code implements all necessary functions and operations for performance analysis and future implementations of the protocol in real-world scenarios.  

The implemented ZKP protocol leverages the mathematical problem of elliptic curves. In this context, some mathematical notations come from this area, such as operations with points on an elliptic curve, as well as operations like *hash*, modulo, and multiplications. The following image illustrates the protocol execution in three rounds, which is implemented in the code.

<img width="90%" alt="image" src="https://github.com/user-attachments/assets/f51b48b1-367e-4333-9040-2f17d28c0692" />

# 2. About the Implementation

The chosen elliptic curve was **secp256k1**, widely known for its use in the Bitcoin cryptocurrency and considered secure. Another reason for its choice is that it is widely recognized, with numerous libraries available in almost all programming languages, which can be useful for implementations in other scenarios and languages.

## 2.1 Package Installation

- First, Python must be installed.
- The libraries required for installing the prover (Folder **user_prover**) are: `threading`, `requests`, `ecdsa`, `random`, `os`, `json`, and `time`. To install them, simply run:

`pip install threading requests ecdsa random os json time`

- The libraries required for installing the verifier (Folder **vpn_verifier**) are: `Flask`, `hashlib`, `ecdsa`, `json`, `datetime`, and `os`. To install them, simply run:

`pip install Flask hashlib ecdsa json datetime os`

- The previous commands install all libraries at once. However, note that some libraries are part of Python's standard packages. Therefore, it is recommended to install only the libraries indicated by the compiler, i.e., just run `pip install library_name` for the missing libraries highlighted by the compiler.

## 2.2 Database Installation

- MySQL must be installed. It is recommended to use [phpMyAdmin](https://www.phpmyadmin.net/), which was used in this project.
- The code in this repository is configured to automatically create the database, tables, and insert some users. The user configured in the code is `root` and the password is also `root`. If your database uses different credentials, simply update the login information in the Python file: `vpn_verifier/database.py`.

### About phpMyAdmin

- Tests were conducted both locally and on a virtual machine running Ubuntu 20.04 LTS on Google Cloud. If you want to do something similar, refer to the [phpMyAdmin Installation Tutorial on Ubuntu 20.04 LTS](https://www.digitalocean.com/community/tutorials/how-to-install-and-secure-phpmyadmin-on-ubuntu-20-04-pt).

## 2.3 About the Virtual Machine on Google Cloud

- The virtual machine used in this project is Ubuntu 20.04 LTS. To learn how to set it up, see this [Installation Tutorial](https://youtu.be/MiiexH6Ik4w?si=FD8r5FHKlO09JGiZ).
- It is important to enable the *firewall* to allow external access to the VM. In this case, port 5000, which is used by Flask by default, should be opened. See how to do this in this [Tutorial on How to Enable the Port](https://www.youtube.com/watch?v=8NR2q9y9uBo).


## 2.4 How to Run the Code

### Verifier

- In the `vpn_verifier` folder, run `python verifier.py` on Windows or `python3 verifier.py` on Linux. This will start the server on port 5000.

### Prover
- In the `user_prover` folder, run `python prover.py` on Windows or `python3 prover.py` on Linux. This will start the authentication process.

# 3. Final Considerations

- The implemented protocol works as specified. In an initial analysis, running on Google Cloud in the United States, the average time to authenticate a user is approximately 2.22 seconds without using TLS to establish a secure channel. With a secure channel, the time increases to 3.27 seconds. When run locally, this time decreases to about 0.075 seconds, demonstrating that the protocol is highly efficient. Most of the authentication delay is due to network latency.

- The code also includes functions to test multiple users simultaneously using Python *threads*, generate files with execution times, and calculate averages of the runs. These features facilitate performance and scalability analysis of the protocol.
