import os
import time
import client
import server
import threading
import random
import msg_constructor
import shared_functions
import new_encryption_module
import my_address
import output
import terminology
import data_layer_config

miners = []
address = my_address.provide_my_address()
max_num_neighbors_per_miner = 5
min_num_of_miners = 2
ping_time = data_layer_config.ping_time

DIDs_under_processing = []
schemes_under_processing = []
revoked_credentials_under_processing = []
mining_requests = []
print("Data should be saved on miners': 1: RAM, 2: Secondary Memory\n>>")
data_on_secondary_memory = shared_functions.input_function(['1', '2'])


def handle_requests_in_buffer():
    while True:
        received_request, requester_address = shared_functions.get_new_msg()
        try:
            if received_request[terminology.the_type] == 'request_to_be_miner':
                handle_mining_request(received_request)
                continue
            if received_request[terminology.the_type] in terminology.transactions_labels:
                add_transaction_to_pending_list(received_request, requester_address)
                miner = select_random_miner()
                client.send(received_request, miner)
                continue
            if received_request[terminology.the_type] == 'block_confirmation':
                handle_confirmation_messages(received_request, requester_address)
                continue
            if received_request[terminology.the_type] == 'signature_validation':
                miner_address = select_random_miner()
                internal_request = msg_constructor.construct_internal_request(received_request[terminology.the_type],
                                                                              requester_address, received_request)
                client.send(internal_request, miner_address)
                continue
            if received_request[terminology.the_type] == 'response to signature validation request':
                client.send(received_request, received_request['agent_address'])
                continue
            if received_request[terminology.the_type] == 'response to institutions request':
                response = {terminology.the_type: 'response to institutions request',
                            'institutions_info': received_request['institution_info']}
                client.send(response, received_request['agent_address'])
                continue
            if received_request[terminology.the_type] == 'institutions' or received_request[terminology.the_type] == 'download_BC':
                miner_address = select_random_miner()
                internal_request = msg_constructor.construct_internal_request(received_request[terminology.the_type],
                                                                              requester_address, received_request)
                client.send(internal_request, miner_address)
                continue

            if received_request[terminology.the_type] == 'response_to_ping':
                for miner in miners:
                    if miner[1] == requester_address:
                        miner[2] = terminology.active
                        miner[3] = time.time()
                        break
            if received_request[terminology.the_type] == 'full_BC':
                client.send(received_request, received_request['agent_address'])
        except Exception as e:
            print(e)


def add_transaction_to_pending_list(transaction, requester_address):
    identifier = transaction[terminology.transaction][terminology.identifier]
    tx_type = transaction[terminology.the_type]
    if tx_type == terminology.DID_publication_request:
        DIDs_under_processing.append([identifier, requester_address])
    else:
        if tx_type == terminology.schema_publication_request:
            schema_hash = new_encryption_module.hashing_function(transaction[terminology.transaction])
            schemes_under_processing.append([schema_hash, requester_address])
        else:
            if tx_type == terminology.revoke_request:
                revoked_credentials_under_processing.append([identifier, requester_address])


def miner_is_active(miner_record):
    if miner_record[2] == terminology.active:
        return True
    else:
        return False


def select_random_miner():
    try:
        not_found = True
        random_miner = random.choice(miners)
        while not_found:
            random_miner = random.choice(miners)
            if miner_is_active(random_miner):
                not_found = False
        miner_address = random_miner[1]
        return miner_address
    except Exception as e:
        print(e)


# The following function needs to be modified using the DONS approach
def assign_neighbor_for_miner(miner):
    if miner_is_active(miner):
        while True:
            neighbor = random.choice(miners)
            neighbor_address = neighbor[1]
            if miner_is_active(neighbor) and neighbor_address != miner[1]:
                break
        return neighbor, miner


def inform_miner_of_active_status(miner_record, data_placement):
    neighbor_record, miner_record = assign_neighbor_for_miner(miner_record)
    response = msg_constructor.construct_response_to_mining_request(True, data_placement, neighbor_record,
                                                                    count_active_miners(),
                                                                    max_num_neighbors_per_miner)
    response2 = msg_constructor.construct_response_to_mining_request(True, data_placement, miner_record,
                                                                     count_active_miners(),
                                                                     max_num_neighbors_per_miner)
    client.send(response, miner_record[1])
    client.send(response2, neighbor_record[1])


def count_active_miners():
    num_of_active_miners = 0
    for miner in miners:
        if miner_is_active(miner):
            num_of_active_miners += 1
    return num_of_active_miners


def activate_new_miner(mining_request):
    print("request from " + mining_request[0] + '. Location: ' + ' ' + mining_request[1])
    print("to be a miner. Do you accept? (Y/N):\n")
    decision = shared_functions.input_function(['Y', 'y', 'N', 'n'])
    if decision in ['Y', 'y']:
        miner_record = [mining_request[1], mining_request[0], terminology.active, time.time(), mining_request[2]]
        miners.append(miner_record)
        if count_active_miners() > 2:
            inform_miner_of_active_status(miner_record, data_on_secondary_memory)
        else:
            if count_active_miners() == 2:
                for miner in miners:
                    inform_miner_of_active_status(miner, data_on_secondary_memory)
            else:
                print('Number of miners is still not sufficient.'
                      'Miners will be activated when they reach the minimum number.. press any key\n')
                out = input()
    else:
        response = msg_constructor.construct_response_to_mining_request(False, data_on_secondary_memory)
        client.send(response, mining_request[0])
    mining_requests.remove(mining_request)


def handle_mining_request(request):
    miner_address = request['miner_address']
    already_activated = miner_already_activated(miner_address)
    if not already_activated:
        mining_requests.append([miner_address, request['location'], request['public_key']])


def miner_already_activated(miner_address):
    already_activated = False
    for miner in miners:
        if miner_address in miner and miner_is_active(miner):
            already_activated = True
            break
    return already_activated


def handle_mining_request_2(request):
    miner_address = request[0]
    already_activated = miner_already_activated(miner_address)
    if not already_activated:
        while True:
            try:
                activate_new_miner(request)
                break
            except Exception as e:
                print(e)
                print('\ntry again>>\n')
    else:
        miner_record = [request['location'], miner_address, terminology.active, time.time()]
        inform_miner_of_active_status(miner_record, data_on_secondary_memory)
        print("Miner is already activated. No action is required.")


def ping_miners():
    while True:
        try:
            num_of_active_miners = count_active_miners()
            for miner in miners:
                if not miner_is_active(miner):
                    miners.remove(miner)
            ping_request = {terminology.the_type: 'ping',
                            'Num_of_miners': num_of_active_miners,
                            'Miners': miners,
                            'Authorized_miner': select_random_miner()}
            for miner in miners:
                client.send(ping_request, miner[1])
            time.sleep(ping_time)
            for miner in miners:
                if time.time() - miner[3] > (3 * ping_time):
                    miner[2] = terminology.passive
                else:
                    miner[2] = terminology.active
            time.sleep(ping_time)
        except Exception as e:
            print(e)


def handle_confirmation_messages(confirmation_message, miner_ip):
    for miner in miners:
        if miner[1] == miner_ip:
            try:
                customer = None
                if confirmation_message['block_type'] == terminology.DID_block:
                    for DID_under_processing in DIDs_under_processing:
                        if DID_under_processing[0] == confirmation_message['block_identifier']:
                            customer = DID_under_processing[1]
                            DIDs_under_processing.remove(DID_under_processing)
                            break
                elif confirmation_message['block_type'] == terminology.schema_block:
                    for schema_under_processing in schemes_under_processing:
                        if schema_under_processing[0] == confirmation_message['block_identifier']:
                            customer = schema_under_processing[1]
                            schemes_under_processing.remove(schema_under_processing)
                            break
                elif confirmation_message['block_type'] == terminology.revoke_block:
                    for revoked_credential_under_processing in revoked_credentials_under_processing:
                        if revoked_credential_under_processing[0] == confirmation_message['block_identifier']:
                            customer = revoked_credential_under_processing[1]
                            revoked_credentials_under_processing.remove(revoked_credential_under_processing)
                            break
                index = confirmation_message[terminology.index]
                new_confirmation_msg = msg_constructor.construct_block_confirmation_message(
                    confirmation_message['added'],
                    confirmation_message['block_type'],
                    None, confirmation_message['block_identifier'], False, index)
                client.send(new_confirmation_msg, customer)
                break
            except Exception as e:
                print(e)
                break


def serve_gateway_admin():
    while True:
        try:
            output.gateway_options(str(address), str(count_active_miners()), str(len(mining_requests)))
            decision = shared_functions.input_function(['1', '2', '3', '4'])
            if decision == '1':
                print("Miners info:")
                output.present_list(miners)
                print('\n press any key to go back..\n')
                out = input()
            if decision == '2':
                print('Pending mining requests:\n')
                output.present_list(mining_requests)
                print('\n If you would like to respond to one of these requests, input the number of the one you selected, then "enter"')
                print("\n if you wouldn't like to respond to any of those, press 0, then 'enter'")
                choice = input()
                if choice == '0':
                    pass
                else:
                    try:
                        request_index = int(choice) - 1
                        handle_mining_request_2(mining_requests[request_index])
                    except Exception as e:
                        print(e)
            if decision == '3':
                output.clear()
            if decision == '4':
                os._exit(1)
        except Exception as e:
            print(e)


def start():
    process_1 = threading.Thread(target=server.start, )
    process_1.start()
    process_3 = threading.Thread(target=handle_requests_in_buffer, )
    process_3.start()
    process_4 = threading.Thread(target=ping_miners, )
    process_4.start()
    process_5 = threading.Thread(target=serve_gateway_admin, )
    process_5.start()
