import client
import server
import threading
import msg_constructor
import pathlib
import shared_functions
import json
import output
import os
import my_address
import new_encryption_module
import terminology

receiver = input('please input the address of the BC:\n')


class Institution:
    def __init__(self, name, private_DID, public_DID):
        self.name = name
        self.private_DID = private_DID
        self.public_DID = public_DID
        self.address = my_address.provide_my_address()
        self.DID_published = False
        self.pending_schema_requests = []
        self.pending_revoke_requests = []
        self.notifications = {}
        self.DID_index = None

    def publish_my_DID(self, BC_address):
        try:
            my_public_key = new_encryption_module.prepare_key_for_use(terminology.public, 'DID')
            deserialized_public_key = new_encryption_module.deserialize_key(my_public_key)
            DID_transaction = msg_constructor.new_did_transaction(self.name, self.address, deserialized_public_key)
            request = msg_constructor.construct_new_block_request(terminology.DID_publication_request, DID_transaction)
            client.send(request, BC_address)
            print('DID publication request was sent. Once a positive response arrives, you can publish new schemes and'
                  ' issue new credentials.')
        except Exception as e:
            print(e)

    def create_new_schema(self, BC_address):
        if self.DID_published:
            label = input("please input Education Level (e.g. MSc, PhD, etc.)\n")
            try:
                path = "local_files/schemes/" + label
                file = pathlib.Path(path)
                if not file.exists():
                    new_schema_attributes = msg_constructor.define_schema_attributes()
                    schema_transaction = msg_constructor.schema_block_data(self.name, self.address, label, None, new_schema_attributes)
                    self.schema_publish_confirmation(schema_transaction, BC_address)
                else:
                    print("Please check already existing schemes and try again, the title of the schema already exists.")
            except Exception as e:
                print(e)
        else:
            print('[Attention]: DID must be published first!')

    def schema_publish_confirmation(self, schema_transaction, BC_address):
        try:
            print('Are you sure you want to publish this schema? Y/N')
            next_step = shared_functions.input_function(['Y', 'N', 'y', 'n'])
            if next_step in ['Y', 'y']:
                print('hold please, schema keys are being generated..')
                private_key, public_key = shared_functions.select_keys(schema_transaction[terminology.identifier])
                schema_public_key = new_encryption_module.prepare_key_for_use(terminology.public, schema_transaction[terminology.identifier], None)
                deserialized_public_key = new_encryption_module.deserialize_key(schema_public_key)
                print('keys of the new schema are generated')
                schema_transaction['schema_public_key'] = deserialized_public_key
                schema_transaction[terminology.DID_index] = self.DID_index
                print('schema public key is added to the request')
                self.publish_new_schema(schema_transaction, BC_address)
            else:
                print("Schema is withdrawn.")
        except Exception as e:
            print(e)

    def publish_new_schema(self, schema_transaction, BC_address):
        signature = shared_functions.retrieve_signature_from_saved_key(schema_transaction[terminology.identifier], 'DID')
        new_block_request = msg_constructor.construct_new_block_request(terminology.schema_publication_request, schema_transaction, signature)
        client.send(new_block_request, BC_address)
        hash_of_schema = new_encryption_module.hashing_function(schema_transaction)
        self.pending_schema_requests.append([schema_transaction, hash_of_schema])
        print('Schema request was sent to the Blockchain. You will be able to use it once it is confirmed')

    def issue(self):
        if self.DID_published:
            try:
                print('Available schemes:')
                lst_of_schemes = os.listdir("local_files/schemes/")
                for schema in lst_of_schemes:
                    print(schema)
                label = input("Please paste the title of the schema you want to use (without the extension):\n")
                with open('local_files/schemes/' + label + '.txt', 'r') as file:
                    schema = json.load(file)
                credential_attributes = schema['schema_attributes']
                schema_index = schema[terminology.index]
                new_credential, credential_label = msg_constructor.construct_new_digital_credential(self.name, label, credential_attributes, self.DID_index, schema_index)
                signature = shared_functions.retrieve_signature_from_saved_key(new_credential, label)
                signed_credential = {terminology.credential: new_credential,
                                     terminology.signature: signature}
                shared_functions.save_file_locally(signed_credential, credential_label, 'credentials')
            except Exception as e:
                print(e)
        else:
            print('[Attention]: DID must be published first!')

    def process_credential_request(self, request, requester_address):
        path = "local_files/credentials/"
        request_level = request[terminology.schema_identifier]
        with open('local_files/schemes/' + request_level + '.txt', 'r') as file:
            schema = json.load(file)
        credential_label = 'cre_' + request_level + '_'
        for attribute in schema['schema_attributes']:
            if attribute[1] == 'Mandatory':
                credential_label = credential_label + request[attribute[0]]
        # print('institution is looking for the credential with title:')
        # print(credential_label)
        # print('if the credential is found it will be sent to:')
        # print(requester_address)
        credential_is_available = False
        for filename in os.listdir(path):
            if filename == credential_label + '.txt':
                # print('credential is found..')
                with open(path + filename, 'r') as credential:
                    requested_credential = json.load(credential)
                    credential_is_available = True
                break
        response = {terminology.the_type: 'response_to_credential_request'}
        if credential_is_available:
            response['status'] = True
            encrypted_credential, final_encoded_encrypted_symmetric_key = shared_functions.react_to_credential_request(
                requested_credential, request['requester_pub_key'])
            response['encrypted_credential'] = encrypted_credential
            response['encrypted_symmetric_key'] = final_encoded_encrypted_symmetric_key
        else:
            response['status'] = False
            response['original_request'] = request
        # output.issue_confirmation(credential_is_available)
        client.send(response, requester_address)

    def automatic_credential_requests_handling(self):
        while True:
            try:
                request, requester_address = shared_functions.get_new_msg()
                body = request
                if body[terminology.the_type] == 'response to signature validation request':
                    notification = msg_constructor.construct_notification(body[terminology.the_type], body['credential_is_valid'], body[terminology.credential])
                    self.notifications[str(len(self.notifications) + 1)] = notification
                else:
                    if body[terminology.the_type] == 'block_confirmation':
                        data = None
                        if body['block_type'] == terminology.DID_block:
                            self.DID_published = body['added']
                            self.DID_index = body[terminology.index]
                            did_info, file_exists = shared_functions.open_saved_file(
                                'local_files/DID_info/DID_info.txt')
                            did_info["is_published"] = body['added']
                            shared_functions.save_file_locally(did_info, 'DID_info', 'DID_info')
                        elif body['block_type'] == terminology.schema_block:
                            for pending_schema_publication_request in self.pending_schema_requests:
                                if pending_schema_publication_request[1] == body['block_identifier']:
                                    pending_schema_publication_request[0][terminology.index] = body[terminology.index]
                                    shared_functions.save_file_locally(pending_schema_publication_request[0], str(
                                        pending_schema_publication_request[0][terminology.identifier]), 'schemes')
                                    data = pending_schema_publication_request[0]
                        elif body['block_type'] == terminology.revoke_block:
                            data = self.delete_revoked_credential(body['block_identifier'])
                        notification = msg_constructor.construct_notification(body['block_type'], body['added'], data)
                        self.notifications[str(len(self.notifications) + 1)] = notification
                    else:
                        try:
                            sender_address = body['requester_ip']
                            self.process_credential_request(body, sender_address)
                        except Exception as e:
                            print(e)
            except Exception as ex:
                print(ex)

    def delete_revoked_credential(self, hash_of_revoked_credential):
        credential_label = None
        for pending_request in self.pending_revoke_requests:
            if pending_request[0] == hash_of_revoked_credential:
                credential_label = pending_request[1]
                break
        path = "local_files/credentials/"
        if credential_label:
            for filename in os.listdir(path):
                if filename == credential_label:
                    with open(path + filename, 'r') as file:
                        revoked_credential = json.load(file)
                    try:
                        os.remove(path + credential_label)
                        # print('the credential was removed from local records.')
                    except Exception as e:
                        print(e)
                        print('Kindly.. go to ' + path + ' and manually remove the credential')
            return revoked_credential

    def revoke_credential(self, BC_address, selected_credential, credential_label):
        print(" The following credential is requested to be revoked:")
        output.present_dictionary(selected_credential[terminology.credential])
        print('\nAre you sure you want to revoke this credential? (Y/N)\n')
        decision = shared_functions.input_function(['Y', 'y', 'N', 'n'])
        if decision == 'Y' or decision == 'y':
            schema_identifier = selected_credential[terminology.credential][terminology.schema_identifier]
            DID_index = self.DID_index
            schema_index = selected_credential[terminology.credential][terminology.schema_index]
            hash_of_signed_credential = new_encryption_module.hashing_function(selected_credential[terminology.credential])
            signature = shared_functions.retrieve_signature_from_saved_key(selected_credential[terminology.credential], schema_identifier)
            revoke_data = msg_constructor.revoke_block_data(self.name, self.address, schema_identifier, hash_of_signed_credential, DID_index, schema_index)
            revoke_request = msg_constructor.construct_new_block_request(terminology.revoke_request, revoke_data, signature)
            print("revoke request is ready to be sent. [ATTENTION: THIS CANNOT BE UNDONE!] to confirm, type the label of the credential one more time:\n")
            confirmation = input()
            if confirmation == credential_label:
                client.send(revoke_request, BC_address)
                print('revoke request was sent. The credential will be deleted from the system once a positive feedback is received.')
                self.pending_revoke_requests.append([hash_of_signed_credential, credential_label])

    def manage_saved_credentials(self, BC_address):
        credential, credential_label, credential_exists = shared_functions.choose_credential()
        if credential_exists:
            output.present_dictionary(credential[terminology.credential])
            print('What would you like to do with this credential? (1: validate, 2: revoke, 3: back)')
            option = shared_functions.input_function(['1', '2', '3'])
            if option == '1':
                shared_functions.validate_credential(BC_address, self.address, credential)
            if option == '2':
                self.revoke_credential(BC_address, credential, credential_label)
            if option == '3':
                pass


def serve_institution_admin(institution, BC_address):
    while True:
        try:
            option = output.institution_options(len(institution.notifications))
            if option == '1':
                institution.publish_my_DID(BC_address)
                continue
            if option == '2':
                institution.create_new_schema(BC_address)
                continue
            if option == '3':
                institution.issue()
                continue
            if option == '4':
                institution.manage_saved_credentials(BC_address)
                continue
            if option == '5':
                output.clear()
            if option == '6':
                for key in institution.notifications:
                    output.present_dictionary(institution.notifications[key])
                continue
            if option == '7':
                os._exit(1)
        except Exception as e:
            print(e)


def initiate_institution(BC_address):
    name = output.request_inst_name()
    private_DID, public_DID = shared_functions.select_keys('DID')
    institution = Institution(name, private_DID, public_DID)
    process_1 = threading.Thread(target=server.start, )
    process_1.start()
    process_2 = threading.Thread(target=serve_institution_admin, args=(institution, BC_address))
    process_2.start()
    process_3 = threading.Thread(target=institution.automatic_credential_requests_handling)
    process_3.start()


initiate_institution(receiver)
