import msg_constructor
import output
import memory_pool
import os
import json
import pathlib
import client
import new_encryption_module
import terminology


def validate_credential(BC_address, requester_address, selected_credential):
    try:
        did_identifier = selected_credential[terminology.credential][terminology.did_identifier]
        schema_identifier = selected_credential[terminology.credential][terminology.schema_identifier]
        signature = selected_credential[terminology.signature]
        hashed_credential = new_encryption_module.hashing_function(selected_credential[terminology.credential])
        request_validation_from_bc = msg_constructor.construct_validation_request(did_identifier, schema_identifier, signature, hashed_credential, requester_address)
        client.send(request_validation_from_bc, BC_address)
    except Exception as e:
        print(e)


def choose_credential():
    print('please copy and paste the name of the credential you want to select, then press "ENTER":\n')
    path = "local_files/credentials/"
    for filename in os.listdir(path):
        print(filename)
    credential_label = input()
    selected_credential_path = path + credential_label
    selected_credential, credential_exists = open_saved_file(selected_credential_path)
    return selected_credential, credential_label, credential_exists


def save_file_locally(file_to_be_saved, file_title, folder):
    with open('local_files/' + folder + '/' + file_title + '.txt', 'w') as f:
        f.write(json.dumps(file_to_be_saved))
    # output.saved_file_confirmation()


def input_function(input_options):
    while True:
        try:
            variable = input()
            if variable in input_options:
                break
            else:
                print('You entered an unrecognized value. Please try again.')
        except Exception as e:
            print('Error. Try again..!')
            print(e)
    return variable


def get_dict_ready_to_sending(dictionary):
    new_dictionary = json.dumps(dictionary)
    return new_dictionary


def get_new_msg():
    request_under_processing = memory_pool.received_msgs.get()
    request = request_under_processing[0]
    requester_address = request_under_processing[1][0]
    return request, requester_address


def prepare_credential(requested_credential):
    final_credential = json.dumps(requested_credential)
    bytes_credential = final_credential.encode('latin-1')
    return bytes_credential


def react_to_credential_request(requested_credential, pub_key):
    credential = prepare_credential(requested_credential)
    # prepare public key
    public_key = new_encryption_module.prepare_key_for_use(terminology.public, None, pub_key)
    # prepare symmetric key
    symmetric_key = new_encryption_module.generate_symmetric_key()
    # encrypt credential using the symmetric key
    encrypted_credential = new_encryption_module.encrypt_symmetric(credential, symmetric_key)
    decoded_encrypted_credential = encrypted_credential.decode('latin-1')
    # encrypt the symmetric key using the public key
    decoded_symmetric_key = symmetric_key.decode('latin-1')
    encrypted_symmetric_key = new_encryption_module.encrypt_PKI(decoded_symmetric_key, public_key)
    ready_decoded_encrypted_symmetric_key = encrypted_symmetric_key.decode('latin-1')
    # print('Symmetric key is encrypted using the received Public Key.')
    return decoded_encrypted_credential, ready_decoded_encrypted_symmetric_key


def react_to_credential_response(encrypted_symmetric_key, private_key, encrypted_credential):
    # decrypt the symmetric key
    decrypted_symmetric_key = new_encryption_module.decrypt_PKI(encrypted_symmetric_key, private_key)
    # decrypt credential using the symmetric key
    credential = new_encryption_module.decrypt_symmetric(encrypted_credential, decrypted_symmetric_key)
    ready_signed_credential = json.loads(credential)
    # print('Symmetric key is decrypted using my Private_key..')
    # prepare the credential
    # print('Received credential is decrypted using the decrypted symmetric key..')
    credential_label = ready_signed_credential[terminology.credential][terminology.did_identifier] + ready_signed_credential[terminology.credential][terminology.schema_identifier]
    # credential_path = "local_files/credentials/" + credential_label + '_' + str(1) + '.txt'
    # copy_number = 1
    # existing_credential, name_reserved = open_saved_file(credential_path)
    # while name_reserved:
    #     copy_number += 1
    #     credential_path = "local_files/credentials/" + credential_label + '_' + str(copy_number) + '.txt'
    #     existing_credential, name_reserved = open_saved_file(credential_path)
    save_file_locally(ready_signed_credential, credential_label, 'credentials')
    # print("A signed credential has been received:\n")
    return ready_signed_credential


def retrieve_signature_from_saved_key(object_used_for_signature, label_of_saved_key):
    key = new_encryption_module.prepare_key_for_use(terminology.private, label_of_saved_key, None)
    signature = new_encryption_module.produce_serialized_signature(object_used_for_signature, key)
    return new_encryption_module.deserialize_signature(signature)


def select_keys(purpose):
    path = "local_files/keys/" + purpose + '_'
    private_file = pathlib.Path(path + terminology.private + '.key')
    public_file = pathlib.Path(path + terminology.public + '.key')
    if private_file.exists() and public_file.exists():
        private_key = private_file.read_text()
        public_key = public_file.read_text()
    else:
        temp_private_key, temp_public_key = new_encryption_module.generate_PKI_keys(purpose)
        private_key, public_key = select_keys(purpose)
        # output.no_did()
    # output.DID_info(public_DID)
    return private_key, public_key


def open_saved_file(file_path):
    file_exists = False
    try:
        with open(file_path, 'r') as file:
            selected_file = json.load(file)
        file_exists = True
    except Exception as e:
        selected_file = {}
        print(e)
    return selected_file, file_exists
