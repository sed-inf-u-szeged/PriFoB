import os
import time

import client
import server
import threading
import msg_constructor
import output
import shared_functions
import my_address
import new_encryption_module
import blockchain
import terminology
import consensus
import pickle
import bisect_test


class Miner:
    def __init__(self, bc_address, loc, private_key, public_key):
        self.ip_address = my_address.provide_my_address()
        self.ID = self.ip_address
        self.BC_address = bc_address
        self.my_private_key = private_key
        self.my_public_key = public_key
        self.my_blockchain = blockchain.Blockchain(self.BC_address, blockchain.automated_signing())
        self.location = loc
        self.neighbors = []
        self.miners = {}
        self.max_num_neighbors = 5
        self.num_of_miners = 0
        self.longer_chain_at = None
        self.authorized_miner = self.ip_address

    def automated_processing(self):
        self.request_to_be_miner()
        self.my_blockchain.save_modified_blockchain(self.my_blockchain.chain)
        while True:
            try:
                # self.my_blockchain.resolve_signed_DIDs(self.miners, self.BC_address, self.neighbors, self.location)
                request_under_processing, requester_address = shared_functions.get_new_msg()
                # print(request_under_processing)
                self.respond_to_second_level_request(request_under_processing, requester_address)
            except Exception as e:
                print(e)

    def receive_response_to_mining_request(self, request):
        if request['added']:
            self.neighbors.clear()
            self.neighbors = [request['neighbor'][1]]
            self.num_of_miners = request['Num_of_miners']
            self.max_num_neighbors = request['num_of_neighbors']
            self.my_blockchain.data_placement = request['data_placement']
            print('This device has been assigned a new neighbor and is now part of the BC network')
        else:
            print('you were not accepted as a miner')
            os._exit(1)

    def respond_to_second_level_request(self, request_under_processing, requester_address):
        try:
            if request_under_processing[terminology.the_type] in terminology.transactions_labels:
                self.my_blockchain.handle_new_block_request(request_under_processing, self.miners, self.BC_address, self.neighbors, requester_address, self.location, self.authorized_miner)
                self.put_blockchain_on_secondary_memory()
            elif request_under_processing[terminology.the_type] == terminology.block:
                self.handle_new_block(request_under_processing)
            elif request_under_processing[terminology.the_type] == 'signature_validation':
                self.handle_signature(request_under_processing)
            elif request_under_processing[terminology.the_type] == 'Blockchain_info':
                self.respond_to_BC_info_request(requester_address)
            elif request_under_processing[terminology.the_type] == 'response to Blockchain_info request':
                self.react_to_provided_BC_info(request_under_processing, requester_address)
            elif request_under_processing[terminology.the_type] == 'download_BC':
                self.provide_full_BC(request_under_processing, requester_address)
            elif request_under_processing[terminology.the_type] == 'full_BC':
                self.update_my_BC(request_under_processing, requester_address)
            elif request_under_processing[terminology.the_type] == 'institutions':
                self.handle_institutions_info_request(request_under_processing['agent_address'])
            elif request_under_processing[terminology.the_type] == 'ping' and self.requester_authorized(requester_address):
                self.respond_to_ping(requester_address, request_under_processing)
            elif request_under_processing[terminology.the_type] == 'response to mining request' and requester_address == self.BC_address:
                self.receive_response_to_mining_request(request_under_processing)
        except Exception as e:
            print(e)

    def handle_new_block(self, request_under_processing):
        try:
            received_block = request_under_processing['body']
            if consensus.verify_proof_of_authority(self.miners, received_block['Header']['Minter_id'],
                                                   received_block['Body'],
                                                   received_block['Header'][terminology.signature]):
                DID_identifier, schema_identifier, revoke_identifier = blockchain.get_identifiers(
                    received_block['Body'][terminology.transaction], received_block['Header'][terminology.the_type])
                if received_block['Header'][terminology.the_type] == terminology.DID_block:
                    DID_index = bisect_test.get_index(self.my_blockchain.sorted_chain, 1, DID_identifier)
                    # existing_block, DID_index = self.my_blockchain.DID_block_exists(DID_identifier)
                    if not DID_index:
                        if self.previous_signature_is_correct(received_block['Header'][terminology.the_type],
                                                              received_block['Body'][terminology.previous_signature],
                                                              DID_index, None):
                            self.my_blockchain.add_block_to_local_chain(received_block,
                                                                        received_block['Header'][terminology.the_type],
                                                                        DID_index, None, DID_identifier, received_block['Header'][terminology.index])
                            print('new valid block is received..!')
                            blockchain.send_request_to_active_neighbors(request_under_processing, self.neighbors)
                            self.put_blockchain_on_secondary_memory()
                elif received_block['Header'][terminology.the_type] == terminology.schema_block:
                    new_schema_identifier = new_encryption_module.hashing_function(received_block['Body'][terminology.transaction])
                    schema_index = bisect_test.get_index(self.my_blockchain.sorted_chain, 2, new_schema_identifier)
                    # existing_block, schema_index = self.my_blockchain.schema_block_exists(received_block['Body'][terminology.transaction][terminology.DID_index], schema_identifier)
                    if not schema_index:
                        if self.previous_signature_is_correct(received_block['Header'][terminology.the_type],
                                                              received_block['Body'][terminology.previous_signature],
                                                              received_block['Body'][terminology.transaction][terminology.DID_index], schema_index):
                            self.my_blockchain.add_block_to_local_chain(received_block,
                                                                        received_block['Header'][terminology.the_type],
                                                                        received_block['Body'][terminology.transaction][terminology.DID_index], schema_index, schema_identifier, received_block['Header'][terminology.index])
                            print('new valid block is received..!')
                            blockchain.send_request_to_active_neighbors(request_under_processing, self.neighbors)
                            self.put_blockchain_on_secondary_memory()
                elif received_block['Header'][terminology.the_type] == terminology.revoke_block:
                    revoke_index = bisect_test.get_index(self.my_blockchain.sorted_chain, 3, revoke_identifier)
                    # existing_block, revoke_index = self.my_blockchain.revoke_block_exists(received_block['Body'][terminology.transaction][terminology.DID_index], received_block['Body'][terminology.transaction][terminology.schema_index], revoke_identifier)
                    if not revoke_index:
                        if self.previous_signature_is_correct(received_block['Header'][terminology.the_type],
                                                              received_block['Body'][terminology.previous_signature],
                                                              received_block['Body'][terminology.transaction][
                                                                  terminology.DID_index], received_block['Body'][terminology.transaction][
                                                                  terminology.schema_index]):
                            self.my_blockchain.add_block_to_local_chain(received_block,
                                                                        received_block['Header'][terminology.the_type],
                                                                        received_block['Body'][terminology.transaction][
                                                                            terminology.DID_index], received_block['Body'][terminology.transaction][
                                                                            terminology.DID_index], revoke_identifier, received_block['Header'][terminology.index])
                            print('new valid block is received..!')
                            blockchain.send_request_to_active_neighbors(request_under_processing, self.neighbors)
                            self.put_blockchain_on_secondary_memory()
        except Exception as e:
            print(e)

    def previous_signature_is_correct(self, block_type, previous_signature, DID_index, schema_index):
        result = False
        if block_type == terminology.DID_block:
            result = any(block['Header'][terminology.signature] == previous_signature for block in self.my_blockchain.chain)
        if block_type == terminology.schema_block:
            result = any(
                schema['Header'][terminology.signature] == previous_signature for schema in self.my_blockchain.chain[DID_index]['schemes_chain'])
        if block_type == terminology.revoke_block:
            result = any(
                revoke_block['Header'][terminology.signature] == previous_signature for revoke_block in self.my_blockchain.chain[DID_index]['schemes_chain'][schema_index]['Hashes_of_revoked_credentials'])
        return result

    def requester_authorized(self, requester_address):
        if requester_address == self.BC_address or requester_address in self.neighbors:
            return True
        return False

    def synchronize_blockchain_with_neighbors(self):
        request = {terminology.the_type: 'Blockchain_info'}
        self.send_request_to_active_neighbors(request)

    def send_request_to_active_neighbors(self, request):
        for neighbor in self.neighbors:
            client.send(request, neighbor)

    def respond_to_BC_info_request(self, requester_address):
        number_of_dids, number_of_schemes, number_of_revoked_credentials = self.my_blockchain.num_of_confirmed_blocks()
        response = {terminology.the_type: 'response to Blockchain_info request',
                    'D1': number_of_dids,
                    'D2': number_of_schemes,
                    'D3': number_of_revoked_credentials}
        client.send(response, requester_address)

    def react_to_provided_BC_info(self, request_under_processing, requester_address):
        number_of_dids, number_of_schemes, number_of_revoked_credentials = self.my_blockchain.num_of_confirmed_blocks()
        if request_under_processing['D1'] > number_of_dids \
                or request_under_processing['D2'] > number_of_schemes \
                or request_under_processing['D3'] > number_of_revoked_credentials:
            request = {terminology.the_type: 'download_BC'}
            client.send(request, requester_address)
            print('found a longer chain at: ' + requester_address)
            self.longer_chain_at = requester_address

    def provide_full_BC(self, request_under_processing, requester_address):
        response = {terminology.the_type: 'full_BC',
                    'Public_blockchain': self.my_blockchain.chain}
        if requester_address == self.BC_address:
            response['agent_address'] = request_under_processing['body']['requester_address']
        client.send(response, requester_address)
        # print(response)

    def update_my_BC(self, request_under_processing, sender_address):
        if sender_address == self.longer_chain_at:
            self.my_blockchain.chain.clear()
            self.my_blockchain.chain = request_under_processing['Public_blockchain']
            print('Local DL has been synchronized.')
            self.put_blockchain_on_secondary_memory()
            print(request_under_processing)

    def put_blockchain_on_secondary_memory(self):
        if self.my_blockchain.data_placement == '2':
            file = open('local_files/blockchain/blockchain.pkl', 'w')
            file.close()
            with open('local_files/blockchain/blockchain.pkl', 'wb') as file:
                pickle.dump(self.my_blockchain.chain, file, protocol=pickle.HIGHEST_PROTOCOL)

    def fetch_blockchain_from_secondary_memory(self):
        if self.my_blockchain.data_placement == '2':
            self.my_blockchain.chain.clear()
            with open('local_files/blockchain/blockchain.pkl', 'rb') as file:
                self.my_blockchain.chain = pickle.load(file)

    def local_bc_info(self):
        self.fetch_blockchain_from_secondary_memory()
        number_of_DIDs, number_of_Schemes, total_revoked_credentials = self.my_blockchain.num_of_confirmed_blocks()
        print('Number of DIDs currently on the chain = ' + str(number_of_DIDs - 1))
        print('Number of schemes currently on the 2D chain = ' + str(number_of_Schemes))
        print('Number of revoked credentials currently on the 3D chain = ' + str(total_revoked_credentials))

    def respond_to_ping(self, requester, request_under_processing):
        response = {terminology.the_type: 'response_to_ping',
                    'alive': True}
        client.send(response, requester)
        # memory_pool.msgs_to_be_sent.put([response, requester])
        up_to_date_miners_info = {}
        for miner in request_under_processing['Miners']:
            up_to_date_miners_info[miner[1]] = {terminology.key: miner[4],
                                                terminology.location: miner[0]}
            if len(self.neighbors) < self.max_num_neighbors and miner[1] not in self.neighbors and miner[1] != self.ip_address:
                self.neighbors.append(miner[1])
        self.miners = up_to_date_miners_info
        # self.authorized_miner = request_under_processing['Authorized_miner']

    def request_to_be_miner(self):
        my_public_key = new_encryption_module.prepare_key_for_use(terminology.public, 'my_key')
        deserialized_public_key = new_encryption_module.deserialize_key(my_public_key)
        request = msg_constructor.request_to_be_miner(self.location, self.ip_address, deserialized_public_key)
        client.send(request, self.BC_address)

    def handle_signature(self, credential_validation_request):
        accredited_in = None
        body_of_request = credential_validation_request['body']
        requester_address = body_of_request['requester_address']
        hash_of_credential = body_of_request['hash_of_credential']
        did_index = body_of_request[terminology.DID_index]
        schema_index = body_of_request[terminology.schema_index]
        revoke_index = bisect_test.get_index(self.my_blockchain.sorted_chain, 3, hash_of_credential)
        if not revoke_index:
            accredited_in = self.my_blockchain.chain[did_index]['Body'][terminology.transaction]['Accredited By']
            key = new_encryption_module.prepare_key_for_use(terminology.public, None, self.my_blockchain.chain[did_index]['schemes_chain'][schema_index]['Body'][terminology.transaction]['schema_public_key'])
            is_valid = new_encryption_module.verify_signature(hash_of_credential, body_of_request[terminology.signature], key)
            if is_valid:
                result = terminology.valid
            else:
                result = terminology.faulty_signature
        else:
            result = terminology.revoked
        response = msg_constructor.signature_validation_response(result,
                                                                 body_of_request[terminology.did_identifier],
                                                                 body_of_request[terminology.schema_identifier],
                                                                 accredited_in, requester_address, hash_of_credential)
        client.send(response, self.BC_address)

    def handle_institutions_info_request(self, requester_address):
        try:
            institutions_info = {}
            for DID_block in self.my_blockchain.chain:
                if DID_block['Header'][terminology.signature] != 0:
                    institution_data = {terminology.address: DID_block['Body'][terminology.transaction]["institution_address"],
                                        'schemes': {}}
                    for schema in DID_block['schemes_chain']:
                        if schema['Header'][terminology.signature] != 0:
                            institution_data['schemes'][schema['Body'][terminology.transaction][terminology.identifier]] = schema['Body'][terminology.transaction]["schema_attributes"]
                    institutions_info[DID_block['Body'][terminology.transaction][terminology.identifier]] = institution_data
            response = {terminology.the_type: 'response to institutions request',
                        'agent_address': requester_address,
                        'institution_info': institutions_info}
            client.send(response, self.BC_address)
        except Exception as e:
            print(e)

    def admin_processing(self):
        while True:
            try:
                num_of_unconfirmed_DIDs = len(self.my_blockchain.unsigned_DIDs)
                # self.my_blockchain.resolve_signed_DIDs(self.miners, self.BC_address, self.neighbors, self.location)
                output.miner_admin_options(num_of_unconfirmed_DIDs, self.ip_address)
                option = shared_functions.input_function(['1', '2', '3', '4', '5', '6'])
                if option == '1':
                    self.my_blockchain.process_unsigned_dids(self.location, self.miners, self.BC_address, self.neighbors, self.authorized_miner)
                if option == '2':
                    self.local_bc_info()
                if option == '3':
                    self.synchronize_blockchain_with_neighbors()
                if option == '4':
                    output.clear()
                if option == '5':
                    self.my_blockchain = blockchain.Blockchain(self.BC_address, blockchain.automated_signing())
                    self.put_blockchain_on_secondary_memory()
                if option == '6':
                    os._exit(1)
            except Exception as e:
                print(e)


def start():
    self_ip = my_address.provide_my_address()
    print("This node's IP address is:")
    print(self_ip)
    location = input('please input your location:\n')
    BC_address = input('Please enter the BC_Gate IP Address:\n')
    private_key, public_key = shared_functions.select_keys('my_key')
    miner = Miner(BC_address, location, private_key, public_key)
    process_1 = threading.Thread(target=miner.automated_processing, )
    process_1.start()
    process_2 = threading.Thread(target=miner.admin_processing, )
    process_2.start()
    process_3 = threading.Thread(target=server.start, )
    process_3.start()
