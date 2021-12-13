import random
import threading
import os
import shared_functions
import msg_constructor
import terminology
import my_address
import new_encryption_module
import client
import server
import time
import memory_pool


number_of_DIDs = int(input('How many DIDs you want to publish?\n>>'))
number_of_schemes = int(input("How many schemes you want to publish?\n>>"))
number_of_credentials = int(input("How many credentials you want to issue?\n>>"))
number_of_validation_requests = int(input('How many credential validation requests you want to send to BC?\n>>'))
BC_address = input('BC address? \n>>')
DIDs_requests_list = []
schemes_requests_list = []
credentials_list = []
credential_validation_requests_list = []
private_key, public_key = new_encryption_module.generate_PKI_keys('test_DID_key')
DID_responses = []
schemes_response = []
did_response_times = []
schemes_response_times = []
validation_responses = []
pending_revoke_requests = []


def send_test_DIDs():
    my_public_key = new_encryption_module.prepare_key_for_use(terminology.public, 'test_DID_key')
    deserialized_public_key = new_encryption_module.deserialize_key(my_public_key)
    requests = []
    for i in range(number_of_DIDs):
        block_data = msg_constructor.new_did_transaction(i, my_address.provide_my_address(), deserialized_public_key)
        request = msg_constructor.construct_new_block_request(terminology.DID_publication_request, block_data)
        requests.append(request)
    for i in range(len(requests)):
        client.send(requests[i], BC_address)
        DIDs_requests_list.append([requests[i], time.time()])
        # time.sleep(response_wait_time/number_of_DIDs)
    print('All DID requests have been sent.')
    print('press enter to process the responses\n')
    next_step = input()
    while memory_pool.received_msgs.qsize() > 0:
        try:
            msg = memory_pool.received_msgs.get()
            message = msg[0]
            receiving_time = msg[2]
            if message[terminology.the_type] == 'block_confirmation':
                if message['block_type'] == terminology.DID_block:
                    for did_request in DIDs_requests_list:
                        if did_request[0][terminology.transaction][terminology.identifier] == message['block_identifier']:
                            elapsed_time = receiving_time - did_request[1]
                            did_response_times.append(elapsed_time)
                            did_request[0][terminology.transaction][terminology.DID_index] = message[terminology.index]
                            break
        except Exception as e:
            print(e)
    print('responses have been processed')
    total_did_response_time = 0
    for entity in did_response_times:
        total_did_response_time += entity
    print('Number of DIDs requested: ' + str(number_of_DIDs))
    print('Number of received responses: ' + str(len(did_response_times)))
    print('Success rate: ' + str(len(did_response_times) * 100 / number_of_DIDs) + '%')
    if len(did_response_times) > 0:
        print('Average seconds per DID transaction = ' + str(total_did_response_time / len(did_response_times)))


def send_test_schemes():
    my_public_key = new_encryption_module.prepare_key_for_use(terminology.public, 'test_DID_key')
    deserialized_public_key = new_encryption_module.deserialize_key(my_public_key)
    requests = []
    for i in range(number_of_schemes):
        try:
            DID_record = random.choice(DIDs_requests_list)
            DID_identifier = DID_record[0][terminology.transaction][terminology.identifier]
            new_schema_attributes = [[random.random(), 'Mandatory'], [random.random(), 'Not Mandatory']]
            schema_data = msg_constructor.schema_block_data(DID_identifier, my_address.provide_my_address(), str(i), deserialized_public_key, new_schema_attributes)
            schema_data[terminology.DID_index] = DID_record[0][terminology.transaction][terminology.DID_index]
            signature = shared_functions.retrieve_signature_from_saved_key(schema_data[terminology.identifier], 'test_DID_key')
            request = msg_constructor.construct_new_block_request(terminology.schema_publication_request, schema_data, signature)
            requests.append(request)
            schemes_requests_list.append(
                [new_encryption_module.hashing_function(request[terminology.transaction]), time.time(), request])
        except Exception as e:
            print(e)
    for i in range(len(requests)):
        client.send(requests[i], BC_address)
        # time.sleep(response_wait_time/number_of_schemes)
    print('All schema requests have been sent.')
    next_step = input('press enter to process the responses')
    while memory_pool.received_msgs.qsize() > 0:
        try:
            msg = memory_pool.received_msgs.get()
            message = msg[0]
            receiving_time = msg[2]
            if message[terminology.the_type] == 'block_confirmation':
                if message['block_type'] == terminology.schema_block:
                    for schema_request in schemes_requests_list:
                        if schema_request[0] == message['block_identifier']:
                            elapsed_time = receiving_time - schema_request[1]
                            schemes_response_times.append(elapsed_time)
                            schema_request.append(message[terminology.index])
                            break
        except Exception as e:
            print(e)
    print('responses have been processed')
    total_schema_response_time = 0
    for entity in schemes_response_times:
        total_schema_response_time += entity
    print('Number of schemes requested: ' + str(number_of_schemes))
    print('Number of received responses: ' + str(len(schemes_response_times)))
    print('Success rate: ' + str(len(schemes_response_times) * 100 / number_of_schemes) + '%')
    if len(schemes_response_times) > 0:
        print(
            'Average seconds per schema transaction = ' + str(total_schema_response_time / len(schemes_response_times)))


def generate_test_credentials():
    for i in range(number_of_credentials):
        try:
            schema_record = random.choice(schemes_requests_list)
            schema_label = str(random.randint(0, number_of_schemes))
            inst_name = schema_record[2][terminology.transaction]['institution_name']
            did_index = schema_record[2][terminology.transaction][terminology.DID_index]
            schema_index = schema_record[3]
            credential_attributes = schema_record[2][terminology.transaction]['schema_attributes']
            new_credential = {terminology.did_identifier: inst_name,
                              terminology.schema_identifier: schema_label,
                              terminology.DID_index: did_index,
                              terminology.schema_index: schema_index}
            for attribute in credential_attributes:
                new_field = random.random()
                new_credential[attribute[0]] = new_field
            signature = shared_functions.retrieve_signature_from_saved_key(new_credential, 'test_DID_key')
            signed_credential = {terminology.credential: new_credential,
                                 terminology.signature: signature}
            credentials_list.append(signed_credential)
        except Exception as e:
            i -= 1
    print('All credentials have been issued.')


def send_test_validation_requests():
    for i in range(number_of_validation_requests):
        try:
            credential = random.choice(credentials_list)
            shared_functions.validate_credential(BC_address, my_address.provide_my_address(), credential)
            hashed_credential = new_encryption_module.hashing_function(credential[terminology.credential])
            credential_validation_requests_list.append([hashed_credential, time.time()])
        except Exception as e:
            print(e)
    print('All validation requests have been sent.')
    next_step = input('press enter to process the responses')
    number_of_responses = 0
    while memory_pool.received_msgs.qsize() > 0:
        try:
            msg = memory_pool.received_msgs.get()
            message = msg[0]
            receiving_time = msg[2]
            if message[terminology.the_type] == 'response to signature validation request':
                number_of_responses += 1
                for validation_request in credential_validation_requests_list:
                    if validation_request[0] == message[terminology.credential]['Hash_of_credential']:
                        elapsed_time = receiving_time - validation_request[1]
                        validation_responses.append(elapsed_time)
                        print('Responses not yet received for ' + str(number_of_validation_requests - number_of_responses) + ' validation requests')
                        break
        except Exception as e:
            print(e)

    total_validation_response_time = 0
    for entity in validation_responses:
        total_validation_response_time += entity
    print('Number of validation requests sent: ' + str(number_of_validation_requests))
    print('Number of received responses: ' + str(len(validation_responses)))
    print('Success rate: ' + str(len(validation_responses) * 100 / number_of_validation_requests) + '%')
    if len(validation_responses) > 0:
        print('Average seconds per validation request = ' + str(
            total_validation_response_time / len(validation_responses)))


def send_test_revoke_requests():
    for i in range(number_of_credentials):
        try:
            credential = random.choice(credentials_list)
            schema_identifier = credential[terminology.credential][terminology.schema_identifier]
            DID_index = credential[terminology.credential][terminology.DID_index]
            schema_index = credential[terminology.credential][terminology.schema_index]
            hash_of_signed_credential = new_encryption_module.hashing_function(
                credential[terminology.credential])
            signature = shared_functions.retrieve_signature_from_saved_key(credential[terminology.credential], 'test_DID_key')
            revoke_data = msg_constructor.revoke_block_data(credential[terminology.credential][terminology.did_identifier], my_address.provide_my_address(), schema_identifier,
                                                            hash_of_signed_credential, DID_index, schema_index)
            revoke_request = msg_constructor.construct_new_block_request(terminology.revoke_request, revoke_data,
                                                                         signature)
            client.send(revoke_request, BC_address)
            pending_revoke_requests.append([hash_of_signed_credential, time.time()])
        except Exception as e:
            print(e)
    print('All revoke requests have been sent.')
    next_step = input('press enter to process the responses')
    number_of_responses = 0
    revoke_response_times = []
    while memory_pool.received_msgs.qsize() > 0:
        try:
            msg = memory_pool.received_msgs.get()
            message = msg[0]
            receiving_time = msg[2]
            if message[terminology.the_type] == 'block_confirmation' and message['block_type'] == terminology.revoke_block:
                number_of_responses += 1
                for revoke_request in pending_revoke_requests:
                    if revoke_request[0] == message['block_identifier']:
                        elapsed_time = receiving_time - revoke_request[1]
                        revoke_response_times.append(elapsed_time)
                        break
        except Exception as e:
            print(e)

    total_revoke_response_time = 0
    for entity in revoke_response_times:
        total_revoke_response_time += entity
    print('Number of revoke requests sent: ' + str(len(pending_revoke_requests)))
    print('Number of received responses: ' + str(len(revoke_response_times)))
    print('Success rate: ' + str(len(revoke_response_times) * 100 / len(pending_revoke_requests)) + '%')
    if len(revoke_response_times) > 0:
        print('Average seconds per revoke request = ' + str(
            total_revoke_response_time / len(revoke_response_times)))


def start_testing():
    try:
        send_test_DIDs()

        out = input('Press ENTER to start testing for schemes. (input "x" to exit)>>')

        if out != 'x':
            send_test_schemes()

            out = input('Press ENTER to generate credentials using those schemes. (input "x" to exit)>>')

            if out != 'x':
                generate_test_credentials()
                print('ALL credentials have been issued, signed and saved locally')
                out = input('Press ENTER to randomly validate those credentials. (input "x" to exit)>>')

                if out != 'x':
                    send_test_validation_requests()
                    out = input('Press ENTER to revoke issued credentials credentials. (input "x" to exit)>>')
                    if out != 'x':
                        send_test_revoke_requests()
                    os._exit(1)
                else:
                    os._exit(1)
            else:
                os._exit(1)
        else:
            os._exit(1)
    except Exception as e:
        print(e)
        os._exit(1)


thread1 = threading.Thread(target=start_testing, )
thread2 = threading.Thread(target=server.start, )
thread1.start()

thread2.start()
