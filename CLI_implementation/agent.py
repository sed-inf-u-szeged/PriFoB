import client
import server
import threading
import output
import msg_constructor
import shared_functions
import os
import my_address
import new_encryption_module
import terminology


class Customer:
    def __init__(self, public_key, private_key):
        self.first_name = input("Kindly enter your first name:\n")
        self.last_name = input("Kindly enter your last name:\n")
        self.pub_key, self.pri_key = public_key, private_key
        self.ip_address = my_address.provide_my_address()
        self.BC_address = input("Please enter the BC_Gate IP Address:\n")
        self.institutions = {}
        self.updated = False
        self.notifications = {}
        self.credential_requests = []

    def request_initial_info_from_BC(self):
        request_institutions = msg_constructor.construct_request_inst_info()
        client.send(request_institutions, self.BC_address)

    def share_credential_with_another_customer(self, request):
        resolved = False
        try:
            requester_label = request['std_first_name'] + ' ' + request['std_last_name']
            print('you have received a credential share request from ' + requester_label)
            print('would you like to share a credential with this person? (Y/N/exit):\n')
            agree = shared_functions.input_function(['Y', 'y', 'N', 'n', 'exit'])
            if agree in ['Y', 'y']:
                print('You have decided to share a credential')
                selected_credential, credential_label, credential_exists = shared_functions.choose_credential()
                encrypted_credential, final_encoded_encrypted_symmetric_key = shared_functions.react_to_credential_request(selected_credential, request['requester_pub_key'])
                response = {terminology.the_type: 'response_to_credential_request',
                            'status': True,
                            'encrypted_credential': encrypted_credential,
                            'encrypted_symmetric_key': final_encoded_encrypted_symmetric_key}
                requester_address = request['requester_ip']
                print('Response is ready>>\n')
                client.send(response, requester_address)
                print('The following credential has been sent to ' + requester_label)
                output.present_dictionary(selected_credential)
                resolved = True
            elif agree in ['N', 'n']:
                print('You have decided not to share a credential')
                resolved = True
            else:
                pass
            return resolved
        except Exception as e:
            print(e)
            print('try again>>')

    def handle_received_credential(self, institution_response):
        if institution_response['status']:
            private_key = new_encryption_module.prepare_key_for_use(terminology.private, 'key', None)
            signed_credential = shared_functions.react_to_credential_response(
                institution_response['encrypted_symmetric_key'], private_key,
                institution_response['encrypted_credential'])
            notification = msg_constructor.construct_notification(institution_response[terminology.the_type], institution_response['status'], signed_credential)
            self.notifications[str(len(self.notifications) + 1)] = notification
        else:
            notification = msg_constructor.construct_notification(institution_response[terminology.the_type],
                                                                  institution_response['status'], institution_response['original_request'])
            self.notifications[str(len(self.notifications) + 1)] = notification

    def handle_received_msgs(self):
        while True:
            try:
                request, requester_address = shared_functions.get_new_msg()
                msg = request
                if msg[terminology.the_type] == 'response_to_credential_request':
                    self.handle_received_credential(msg)
                if msg[terminology.the_type] == 'response to signature validation request':
                    notification = msg_constructor.construct_notification(msg[terminology.the_type],
                                                                          msg['credential_is_valid'],
                                                                          msg[terminology.credential])
                    self.notifications[str(len(self.notifications) + 1)] = notification
                if msg[terminology.the_type] == 'credential_request':
                    self.credential_requests.append(msg)
                if msg[terminology.the_type] == 'response to institutions request':
                    self.institutions.clear()
                    self.institutions = msg['institutions_info']
                    print('****\n[INSTITUTION INFO UPDATED]\n****\n')
                    self.updated = True
                if msg[terminology.the_type] == 'full_BC':
                    output.present_dictionary(msg)
            except Exception as e:
                print(e)

    def manage_saved_credentials(self):
        credential, credential_label, credential_exists = shared_functions.choose_credential()
        try:
            if credential_exists:
                output.present_dictionary(credential[terminology.credential])
                print('What would you like to do with this credential? (1: validate, 2: delete, 3: back)')
                option = shared_functions.input_function(['1', '2', '3'])
                if option == '1':
                    shared_functions.validate_credential(self.BC_address, self.ip_address, credential)
                if option == '2':
                    path = 'local_files/credentials/' + credential_label
                    os.unlink(path)
                    print('Credential is deleted. You can request it back any time from the issuer')
                if option == '3':
                    pass
        except Exception as e:
            print(e)

    def request_credential(self):
        key = new_encryption_module.prepare_key_for_use(terminology.public, 'key', None)
        deserialized_key = new_encryption_module.deserialize_key(key)
        self.updated = False
        self.request_initial_info_from_BC()
        print('Updating institutions info.. hold please!')
        while not self.updated:
            pass
        institution_address, agent_data = output.define_requested_credential_attributes(self.institutions)
        request = msg_constructor.construct_credential_request(deserialized_key, self.first_name,
                                                               self.last_name, self.ip_address, agent_data)
        request_confirmation = output.credential_request_sent(request, institution_address)
        if request_confirmation:
            print("request_credential request ", request)
            client.send(request, institution_address)

    def download_full_BC(self):
        request = {terminology.the_type: 'download_BC',
                   'requester_address': self.ip_address}
        client.send(request, self.BC_address)

    def handle_credential_requests(self):
        for request in self.credential_requests:
            request_handled = self.share_credential_with_another_customer(request)
            if request_handled:
                self.credential_requests.remove(request)

    def select_action(self):
        while True:
            action = None
            while action not in {"1", "2", "3", '4', "5", '6', '7'}:
                action = output.customer_options(len(self.notifications), len(self.credential_requests), self.ip_address)
                try:
                    if action == '1':
                        self.request_credential()
                    if action == '2':
                        self.manage_saved_credentials()
                    if action == '3':
                        self.download_full_BC()
                    if action == '4':
                        for key in self.notifications:
                            output.present_dictionary(self.notifications[key])
                    if action == '5':
                        self.handle_credential_requests()
                    if action == '6':
                        output.clear()
                    if action == '7':
                        # noinspection PyUnresolvedReferences,PyProtectedMember
                        os._exit(1)
                except Exception as e:
                    print(e)


def start():
    pri_key, pub_key = shared_functions.select_keys('key')
    agent = Customer(pub_key, pri_key)
    print("This node's IP address is:")
    print(agent.ip_address)
    process_1 = threading.Thread(target=server.start, )
    process_1.start()
    process_2 = threading.Thread(target=agent.select_action, )
    process_2.start()
    process_3 = threading.Thread(target=agent.handle_received_msgs, )
    process_3.start()
