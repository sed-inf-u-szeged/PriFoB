# PriFoB
This repository consists of the source code of the PriFoB proof-of-concept application, being developed in the FogBlock4Trust sub-grant project of the TruBlo EU H2020 project. This solution is currently still in the development phase and the provided figures may slightly differ from what it will look after future modifications. However, they will mostly give similar or enhanced services.

PriFoB is a system that facilitates trusted and privacy-preserving credential verification, which stands for Privacy preserving Fog-enhanced Blockchain. The main technologies and methods used in PriFoB are Zero-Knowledge-Proofs (ZKPs), Fog Computing (FC) and public-permissioned Blockchain (BC). The interaction between PriFoB entities, as described in this tutorial, should allow organizations to issue credentials that can be verified by their owners in a timely manner. Meanwhile, this interaction allows for governmental bodies to, collectively, contribute to the accreditation of the issuer organizations. Customers of the accredited organizations can then request their digital credentials and verify them instantly without the need for private data disclosure to any system entities. FC is deployed to allow efficient communications between organizations and customers, while BC is deployed to allow the provision of a distributed verifier for both, issuer organizations and their issued credentials. The general architecture of PriFoB can be described as in the following figure:

![image](https://user-images.githubusercontent.com/57328847/138440280-a9c24241-d807-41f4-998f-dfcb580c047a.png)


PriFoB was implemented using Python 3.8 and was tested on both Windows 10 and Linux (Ubuntu v20.10).

To test this solution:

1-Clone the repository on six different instances/computers (in case of tester wants to test a realized scenario), or on one instance that is able to simultaneously run at least six Docker containers.

2- To run and test the solution, run the prifob.py or the Dockerfile within the repo as follows:

# Run Without Docker:
- Generally, Python 3.8 and some packages (apt, pip3, RSA, and Cryptography) need to be installed on all machines in order to run the system.
-	To install python 3.8: https://www.python.org/downloads/
-	To install apt: https://manpages.debian.org/buster/apt/apt.8.en.html
Or sudo apt update
-	To install pip3: sudo apt install python3-pip
-	To install rsa: sudo apt install python3-rsa
-	Type python3 prifob.py in the command line.

# Run With Docker:
- Install Docker on your system (Ubuntu installation: https://docs.docker.com/engine/install/ubuntu/)
- Navigate to the root of the project, where the PriFoB source code was cloned and find the Dockerfile file.
- Build the Docker image:
            docker build -t prifob .
            
- Create Docker container (change {{name}} to the name you prefer):
            docker run -it --name {{name}} prifob
            example:
                  docker run -it --name institution prifob
                  
- Stop the created container:
        docker stop {{name}}
        example:
                  docker stop institution
- Start the created container with given {{name}}:
        docker start -i {{name}}
        example:
                  docker start -i institution

Note: steps 1, 3, and 4 are only required for the first time. Later, the user goes in steps 2, 5, and 6 only.

# After running:

You will have a CLI-based interface similar to the following screen:

![image](https://user-images.githubusercontent.com/57328847/138439823-0f1a88b8-3adc-4f5c-ae90-c391f441df70.png)


Choose which type of entity you want this instance/container to run.

The Gateway: The administrator of the Gateway will have only one job to do: accepting or rejecting Miners. However, the Gateway represents a bridge between customers (i.e., institutions and students in our case) and Miners. Thus, the Gateway manages, packets and encapsulates requests and responses between the two ends of the system. Accordingly, even if the Gateway appears to do nothing but pinging Miners, it performs a critical role as it acknowledges and utilizes active miners, and it informs those active miners about new neighbors they shall communicate with as passive miners are leaving the network. In the following screen, the Gateway shows active miners who are positively responding to its ping requests and asks the administrator to accept or reject a miner.

The Gateway should be run if the BC is needed. However, if only communications between customers are to be tested (i.e., end-user and fog layers), the BC (i.e., Gateway and Miners) is not needed.

![image](https://user-images.githubusercontent.com/57328847/138440398-023dbc21-d5ce-494d-8596-26790c9648ff.png)


The Miner: The administrator of the Miner node will have few tasks to do; connecting to the Gateway, signing new Distributed IDs (DIDs) requests, and synchronizing its local database once joining the network (once accepted by the Gateway admin). A Miner screen looks something like presented in the following figure:

![image](https://user-images.githubusercontent.com/57328847/138440454-a609aabd-328a-4945-b59f-57826879ff5c.png)

To check new unsigned DID requests, the Miner admin chooses ‘1’, which will allow her to select and sign a request. The request in our current case includes the name of the institution, its official IP address, miners who previously signed the request as accredited or not accredited, and its public DID as in the following figure:

![image](https://user-images.githubusercontent.com/57328847/138440547-9262d03e-5f9f-4c5c-bd47-01357a25cf53.png)

Note that the Gateway was the entity that forwarded this request from the institution to a random miner out of the active ones. Using its updated list of active miners, the Gateway sends along with any forwarded request the number of active miners. Accordingly, a DID request is only confirmed and published on chain when it reaches the minimum percentage of signatures out of signatures required by active miners. In our current case, a DID request has to be signed by all miners as we utilize a novel Proof-of-Signature algorithm. However, this is modifiable. Later, Miners can easily synchronize their BCs and adopt missing blocks.

Synchronization is currently performed manually only to illustrate the validity of the synchronization method. However, synchronization shall be performed automatically when the system is deployed in real-life scenarios. This can be easily modified within the Miner.py file of the PriFoB project.

The Institution: The administrator of the Institution node will have several tasks to sequentially do. First, once the institution node is up, the admin needs to publish the institution’s DID. The BC then will handle it (sign it, confirm it, and add it to the Distributed Ledger (DL)). 


Once the admin receives a DID-Block confirmation, she needs to publish a schema for each type of credential the institution is planning to issue. For example, credentials of type Bachelor of Science (BSc), or a Vaccine certificate, require a published schema e.g. BSc and V_CER that includes all credentials attributes. Before publishing this schema, the admin can not issue a credential. The admin can publish a schema by typing the title of the schema (e.g., BSc), and confirming the intention of publication. The schema request is signed using the private part of the institution's DID and sent to the Blockchain (the Gateway specifically) for confirmation.

Once the DID and needed schemes are published, the admin can issue as many credentials that have the title of the schema as she wants. A new credential can be attributed and private customer data are input. Once finished, the credential is automatically signed using the private part of the schema. The credential is then saved locally at the Institution machine.

The admin may validate the issued credential, by sending the signature of the credential along with the agreed-on hash of the credential to the BC (currently we use SHA-256). The BC then checks if decrypting the signature using the public schema (already saved on chain) results in a value that exactly matches the hash of the credential in the request. The BC returns a Boolean value then: True or False, indicating the validity of the credential without the need of any private data. This being said, the BC represents a TTP that verifies a specific credential was indeed issued by an accredited institution. Other specific responses are also sent by the BC in case of an unpublished DID or unpublished schema.

![image](https://user-images.githubusercontent.com/57328847/138442281-f2ce78d9-6e20-4d87-af89-f47902825c29.png)


The admin may also revoke an issued credential, by sending the hash of the credential signed by the corresponding schema private key. The BC will then verify the signature signatures by referring to data on chain and, if signature was found valid, the BC adds the hash of the revoked credential on chain. If a validation request for this revoked credential was sent to the BC, the BC will return a False value despite the correctness of the signature.

Note that the institution does not send the credential to any party, including the BC and the student who was granted the credential. As will be discussed next, the student requests a credential from the institution and would be sent this credential if it were available at the institution node AND if the requester could present a proof that she is indeed the student. Accordingly, the institution node handles such requests, among many others, in the background while the admin has nothing to do with the validation and the response handling. The following figure shows some of the notations that appear on the institution node screen when responding to a credential request:

![image](https://user-images.githubusercontent.com/57328847/138442655-d8a21a26-86cd-4cd3-816a-0197257b4ed7.png)


The Student: The administrator of the student machine can request a credential from an institution OR from another student. This credential can be validated similarly as it is validated on the institution machine. The following figure shows how a student can request a credential from an institution:

![image](https://user-images.githubusercontent.com/57328847/138442792-60a1d6f0-6e49-4b46-b60d-072f0192696b.png)

Once a student selects the option to request a credential from an issuer, a request is sent to the BC to retrieve all available issuers and their Public keys, schemes, ip-addresses, and each scheme with its mandatory attributes that need to be provided by an end-user. The request is then encrypted using the public key of the issuer and sent to the ip-address provided by the TTP. Note that end-users and issuers are Blockchain agnostic, meaning they are communicating with it as if it was a centralized server.

Note that in the first part of the previous figure, the student node includes its public key within the request. Using this public key, the institution performs encryption processes on the credential so that no entity can read the credential other than the requester. Once the response is received, the student node decrypts the credential and the needed keys using its private key and automatically saves it into the local wallet. (To be accurate in our discription, all sent requests are encrypted using a symmitric AES key, which is encrypted using the public key. This is more efficient as the length of the RSA keys should match the length of the sent messages which makes a direct encryption inefficient in cases where messages to be encrypted are longer than 2048 bits)

Important remark: all entities of the PriFoB system are threaded. Due to several threads working together, the input is sometimes not properly taken by the current thread and it needs to be input again so the thread who requested it takes it. Simply, if you input option ‘5’, for example, and no response was received, try it one more time. 






