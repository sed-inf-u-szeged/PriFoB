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
response_wait_time = int(input('How many seconds you want to wait for all the requests are responded to?\n>>'))


def send_test_DIDs():
    my_public_key = new_encryption_module.prepare_key_for_use(terminology.public, 'test_DID_key')
    deserialized_public_key = new_encryption_module.deserialize_key(my_public_key)
    for i in range(number_of_DIDs):
        block_data = msg_constructor.new_did_transaction(i, my_address.provide_my_address(), deserialized_public_key)
        request = msg_constructor.construct_new_block_request(terminology.DID_publication_request, block_data)
        client.send(request, BC_address)
        DIDs_requests_list.append([request, time.time()])
        time.sleep(response_wait_time/number_of_DIDs)
    print('All DID requests have been sent.')


def provide_DIDs_test_analysis():
    did_response_times = []
    repeats = 0
    while memory_pool.received_msgs.qsize() < number_of_DIDs and repeats < response_wait_time:
        time.sleep(1)
        repeats += 1
        print(response_wait_time - repeats)
    while memory_pool.received_msgs.qsize() > 0:
        msg = memory_pool.received_msgs.get()
        message = msg[0]
        receiving_time = msg[2]
        if message[terminology.the_type] == 'block_confirmation':
            if message['block_type'] == terminology.DID_block:
                for did_request in DIDs_requests_list:
                    if did_request[0][terminology.transaction][terminology.identifier] == message['block_identifier']:
                        elapsed_time = receiving_time - did_request[1]
                        did_response_times.append(elapsed_time)
                        break
    total_did_response_time = 0
    for entity in did_response_times:
        total_did_response_time += entity
    print('Number of DIDs requested: ' + str(number_of_DIDs))
    print('Number of received responses: ' + str(len(did_response_times)))
    if len(did_response_times) > 0:
        print('Average seconds per DID transaction = ' + str(total_did_response_time / len(did_response_times)))


def send_test_schemes():
    my_public_key = new_encryption_module.prepare_key_for_use(terminology.public, 'test_DID_key')
    deserialized_public_key = new_encryption_module.deserialize_key(my_public_key)
    for i in range(number_of_schemes):
        DID_record = random.choice(DIDs_requests_list)
        DID_identifier = DID_record[0][terminology.transaction][terminology.identifier]
        new_schema_attributes = [[random.random(), 'Mandatory'], [random.random(), 'Not Mandatory']]
        schema_data = msg_constructor.schema_block_data(DID_identifier, my_address.provide_my_address(), i, deserialized_public_key, new_schema_attributes)
        signature = shared_functions.retrieve_signature_from_saved_key(schema_data[terminology.identifier], 'test_DID_key')
        request = msg_constructor.construct_new_block_request(terminology.schema_publication_request, schema_data, signature)
        client.send(request, BC_address)
        schemes_requests_list.append([new_encryption_module.hashing_function(request[terminology.transaction]), time.time(), request])
        time.sleep(response_wait_time/number_of_schemes)
    print('All schema requests have been sent.')


def provide_schemes_test_analysis():
    schemes_response_times = []
    repeats = 0
    while memory_pool.received_msgs.qsize() < number_of_schemes and repeats < response_wait_time:
        time.sleep(1)
        repeats += 1
        print(response_wait_time - repeats)
    while memory_pool.received_msgs.qsize() > 0:
        msg = memory_pool.received_msgs.get()
        message = msg[0]
        receiving_time = msg[2]
        if message[terminology.the_type] == 'block_confirmation':
            if message['block_type'] == terminology.schema_block:
                for schema_request in schemes_requests_list:
                    if schema_request[0] == message['block_identifier']:
                        elapsed_time = receiving_time - schema_request[1]
                        schemes_response_times.append(elapsed_time)
                        break
    total_schema_response_time = 0
    for entity in schemes_response_times:
        total_schema_response_time += entity
    print('Number of schemes requested: ' + str(number_of_schemes))
    print('Number of received responses: ' + str(len(schemes_response_times)))
    if len(schemes_response_times) > 0:
        print('Average seconds per schema transaction = ' + str(total_schema_response_time / len(schemes_response_times)))


def generate_test_credentials():
    for i in range(number_of_credentials):
        schema_record = random.choice(schemes_requests_list)
        schema_label = str(random.randint(0, number_of_schemes))
        inst_name = schema_record[2][terminology.transaction]['institution_name']
        credential_attributes = schema_record[2][terminology.transaction]['schema_attributes']
        new_credential = {terminology.did_identifier: inst_name,
                          terminology.schema_identifier: schema_label}
        for attribute in credential_attributes:
            new_field = random.random()
            new_credential[attribute[0]] = new_field
        signature = shared_functions.retrieve_signature_from_saved_key(new_credential, 'test_DID_key')
        signed_credential = {terminology.credential: new_credential,
                             terminology.signature: signature}
        credentials_list.append(signed_credential)
    print('All credentials have been issued.')


def send_test_validation_requests():
    for i in range(number_of_validation_requests):
        credential = random.choice(credentials_list)
        shared_functions.validate_credential(BC_address, my_address.provide_my_address(), credential)
        hashed_credential = new_encryption_module.hashing_function(credential[terminology.credential])
        credential_validation_requests_list.append([hashed_credential, time.time()])
    print('All validation requests have been sent.')


def provide_validation_test_analysis():
    validation_responses = []
    repeats = 0
    while memory_pool.received_msgs.qsize() < number_of_validation_requests and repeats < response_wait_time:
        time.sleep(1)
        repeats += 1
        print(response_wait_time - repeats)
    while memory_pool.received_msgs.qsize() > 0:
        msg = memory_pool.received_msgs.get()
        message = msg[0]
        receiving_time = msg[2]
        if message[terminology.the_type] == 'response to signature validation request':
            for validation_request in credential_validation_requests_list:
                if validation_request[0] == message[terminology.credential]['Hash_of_credential']:
                    elapsed_time = receiving_time - validation_request[1]
                    validation_responses.append(elapsed_time)
                    break
    total_validation_response_time = 0
    for entity in validation_responses:
        total_validation_response_time += entity
    print('Number of validation requests sent: ' + str(number_of_validation_requests))
    print('Number of received responses: ' + str(len(validation_responses)))
    if len(validation_responses) > 0:
        print('Average seconds per validation request = ' + str(total_validation_response_time / len(validation_responses)))


def start_testing():
    try:
        send_test_DIDs()
        provide_DIDs_test_analysis()
        out = input('Press ENTER to start testing for schemes. (input "x" to exit)>>')

        if out != 'x':
            send_test_schemes()
            provide_schemes_test_analysis()
            out = input('Press ENTER to generate credentials using those schemes. (input "x" to exit)>>')

            if out != 'x':
                generate_test_credentials()
                print('ALL credentials have been issued, signed and saved locally')
                out = input('Press ENTER to randomly validate those credentials. (input "x" to exit)>>')
                if out != 'x':
                    send_test_validation_requests()
                    provide_validation_test_analysis()
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
