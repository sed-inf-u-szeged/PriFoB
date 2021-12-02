import random
import client
import msg_constructor
import new_encryption_module
import my_address
import consensus
import output
import shared_functions
import terminology
import pickle
import bisect_test


def fully_signed(tx, num_miners):
    return len(tx[terminology.transaction]['Accredited By']) + len(
        tx[terminology.transaction]['Not Accredited by']) >= num_miners


def send_request_to_active_neighbors(request, neighbors):
    for neighbor in neighbors:
        client.send(request, neighbor)


def get_identifiers(transaction_data, transaction_type):
    DID_identifier = None
    schema_identifier = None
    revoke_identifier = None
    if transaction_type == terminology.DID_publication_request or transaction_type == terminology.DID_block:
        DID_identifier = transaction_data[terminology.identifier]
    elif transaction_type == terminology.schema_publication_request or transaction_type == terminology.schema_block:
        DID_identifier = transaction_data['institution_name']
        schema_identifier = transaction_data[terminology.identifier]
    elif transaction_type == terminology.revoke_request or transaction_type == terminology.revoke_block:
        DID_identifier = transaction_data[terminology.did_identifier]
        schema_identifier = transaction_data[terminology.schema_identifier]
        revoke_identifier = transaction_data[terminology.identifier]
    return DID_identifier, schema_identifier, revoke_identifier


def automated_signing():
    print('Automatic (A or a) or Manual (M or m) signing?\n>>')
    decision = shared_functions.input_function(['M', 'm', 'A', 'a'])
    if decision in ['M', 'm']:
        return False
    else:
        return True


class Blockchain:
    def __init__(self, gateway_address, signing_model):
        self.genesis_block = msg_constructor.construct_Genesis_block(terminology.DID_block, gateway_address)
        self.chain = [self.genesis_block]
        self.ip_address = my_address.provide_my_address()
        self.unsigned_DIDs = []
        self.pending_blocks = {}
        self.automatic_signing = signing_model
        self.data_placement = '0'
        self.sorted_chain = bisect_test.SortedBlocks()

    def num_of_confirmed_blocks(self):
        number_of_DIDs = len(self.chain)
        number_of_Schemes = 0
        total_revoked_credentials = 0
        for DID in self.chain:
            number_of_Schemes += len(DID['schemes_chain']) - 1
            for schema in DID['schemes_chain']:
                total_revoked_credentials += len(schema['Hashes_of_revoked_credentials']) - 1
        return number_of_DIDs, number_of_Schemes, total_revoked_credentials

    def handle_new_block_request(self, received_block_request, active_miners, gateway_address, neighbors,
                                 request_received_from, miner_location, authorized_miner):
        try:
            revoke_index = None
            schema_index = None
            DID_index = None
            transaction_data = received_block_request[terminology.transaction]
            transaction_type = received_block_request[terminology.the_type]
            DID_identifier, schema_identifier, revoke_identifier = get_identifiers(transaction_data, transaction_type)
            if transaction_type == terminology.schema_publication_request:
                block_type = terminology.schema_block
                DID_index = transaction_data[terminology.DID_index]
                block_index = bisect_test.get_index(self.sorted_chain, 2, schema_identifier)
                if block_index:
                    existing_block = self.chain[DID_index]['schemes_chain'][block_index]
                # existing_block, schema_index = self.schema_block_exists(DID_index, schema_identifier)
            else:
                if transaction_type == terminology.revoke_request:
                    block_type = terminology.revoke_block
                    DID_index = transaction_data[terminology.DID_index]
                    schema_index = transaction_data[terminology.schema_index]
                    block_index = bisect_test.get_index(self.sorted_chain, 3, revoke_identifier)
                    if block_index:
                        existing_block = self.chain[DID_index]['schemes_chain'][schema_index]['Hashes_of_revoked_credentials'][block_index]
                    # existing_block, revoke_index = self.revoke_block_exists(DID_index, schema_index, revoke_identifier)
                else:
                    block_type = terminology.DID_block
                    block_index = bisect_test.get_index(self.sorted_chain, 1, DID_identifier)
                    # block_index = self.sorted_chain.get_index(1, DID_identifier)
                    if block_index is not None:
                        existing_block = self.chain[block_index]
                    # existing_block, DID_index = self.DID_block_exists(DID_identifier)
                    # existing_block, DID_index, schema_index, revoke_index = self.check_if_block_exists(received_block_request)
            already_signed = False
            transaction_is_ready_to_mint = False
            issuer_signature = 0
            if block_index is None:
                if transaction_type == terminology.DID_publication_request:

                    all_signatures_are_correct, self_signed, signed_by_all = self.check_signatures(transaction_data,
                                                                                                   active_miners,
                                                                                                   miner_location,
                                                                                                   authorized_miner)
                    if not self_signed:
                        if transaction_data[terminology.identifier] in self.pending_blocks:
                            already_signed = True
                            transaction_data = self.auto_sign(miner_location, transaction_data)
                        if not already_signed:
                            if not self.automatic_signing:
                                self.unsigned_DIDs.append(received_block_request)
                            else:
                                self.add_decision(received_block_request, miner_location, active_miners,
                                                  gateway_address, neighbors, authorized_miner)
                        else:
                            if signed_by_all:
                                if all_signatures_are_correct:
                                    transaction_is_ready_to_mint = True
                            else:
                                random_neighbor = random.choice(neighbors)
                                client.send(received_block_request, random_neighbor)
                    else:
                        if signed_by_all:
                            if all_signatures_are_correct:
                                transaction_is_ready_to_mint = True
                        else:
                            random_neighbor = random.choice(neighbors)
                            client.send(received_block_request, random_neighbor)
                else:
                    issuer_signature = received_block_request[terminology.signature]
                    if transaction_type == terminology.schema_publication_request:
                        transaction_is_ready_to_mint = self.verify_this_schema_transaction(DID_index, transaction_data,
                                                                                           issuer_signature)
                    else:
                        transaction_is_ready_to_mint = self.verify_this_revoke_transaction(DID_index, schema_index,
                                                                                           transaction_data,
                                                                                           received_block_request)
                if transaction_is_ready_to_mint:
                    if authorized_miner == self.ip_address:
                        self.mint_and_add_block(transaction_data, gateway_address, block_type, neighbors, DID_index,
                                                schema_index, revoke_index, issuer_signature)
                    else:
                        client.send(received_block_request, authorized_miner)
            else:
                if request_received_from == gateway_address:
                    self.send_block_confirmation_msg(existing_block['Header'][terminology.the_type],
                                                     existing_block['Body'][terminology.transaction][
                                                         terminology.identifier], gateway_address,
                                                     existing_block['Header'][terminology.index])
        except Exception as e:
            print(e)

    def auto_sign(self, miner_location, transaction_data):
        signature_info = {terminology.address: self.ip_address,
                          terminology.person_who_signed_this: self.pending_blocks[transaction_data[terminology.identifier]]['Admin'],
                          terminology.signature: self.pending_blocks[transaction_data[terminology.identifier]][terminology.signature]}
        # signature_info = [miner_location, self.ip_address,
        #                   self.pending_blocks[transaction_data[terminology.identifier]]['Admin'],
        #                   self.pending_blocks[transaction_data[terminology.identifier]][terminology.signature]]
        if self.pending_blocks[transaction_data[terminology.identifier]]['Accredited'] == 'Yes':
            transaction_data['Accredited By'][miner_location] = signature_info
            # transaction_data['Accredited By'].append(signature_info)
        else:
            transaction_data['Not Accredited by'][miner_location] = signature_info
        return transaction_data

    # def check_if_block_exists(self, received_block_request):
    #     transaction_data = received_block_request[terminology.transaction]
    #     transaction_type = received_block_request[terminology.the_type]
    #     DID_identifier, schema_identifier, revoke_identifier = get_identifiers(transaction_data, transaction_type)
    #     existing_block, DID_index, schema_index, revoke_index = self.already_registered(transaction_type,
    #                                                                                     DID_identifier,
    #                                                                                     schema_identifier,
    #                                                                                     revoke_identifier)
    #     return existing_block, DID_index, schema_index, revoke_index

    def verify_this_schema_transaction(self, DID_index, transaction_data, issuer_signature):
        org_key = self.chain[DID_index]['Body'][terminology.transaction]['institution_public_key']
        prepared_key = new_encryption_module.prepare_key_for_use(terminology.public, None, org_key)
        signed_entity = new_encryption_module.hashing_function(transaction_data[terminology.identifier])
        return new_encryption_module.verify_signature(signed_entity, issuer_signature, prepared_key)

    def verify_this_revoke_transaction(self, DID_index, schema_index, transaction_data, received_block_request):
        schema_key = self.chain[DID_index]['schemes_chain'][schema_index]['Body'][terminology.transaction][
            'schema_public_key']
        prepared_key = new_encryption_module.prepare_key_for_use(terminology.public, None, schema_key)
        return new_encryption_module.verify_signature(transaction_data[terminology.identifier],
                                                      received_block_request[terminology.signature], prepared_key)

    def send_block_confirmation_msg(self, block_type, block_identifier, gateway_address, index):
        confirmation_msg = msg_constructor.construct_block_confirmation_message(True, block_type, self.ip_address,
                                                                                block_identifier, True, index)
        client.send(confirmation_msg, gateway_address)

    def check_signatures(self, transaction_data, active_miners, miner_location, authorized_miner):
        try:
            all_signatures_are_correct = True
            self_signed = False
            signed_by_all = False
            # signatures = copy.deepcopy(transaction_data['Accredited By'])
            # signatures.extend(transaction_data['Not Accredited by'])
            hash_to_be_utilized = new_encryption_module.hashing_function(transaction_data[terminology.identifier])
            if len(active_miners) <= len(transaction_data['Accredited By']) + len(
                    transaction_data['Not Accredited by']):
                signed_by_all = True
            if miner_location in transaction_data['Accredited By'] or miner_location in transaction_data['Not Accredited by']:
                self_signed = True
            if authorized_miner == self.ip_address and signed_by_all:
                for key in active_miners:
                    signature_is_correct = False
                    verification_key = new_encryption_module.prepare_key_for_use(terminology.public, None,
                                                                                 active_miners[key][terminology.key])
                    if active_miners[key][terminology.location] in transaction_data['Accredited By']:
                        print('here')
                        signature_is_correct = new_encryption_module.verify_signature(hash_to_be_utilized,
                                                                                      transaction_data['Accredited By'][active_miners[key][terminology.location]][terminology.signature],
                                                                                      verification_key)
                    if active_miners[key][terminology.location] in transaction_data['Not Accredited by']:
                        signature_is_correct = new_encryption_module.verify_signature(hash_to_be_utilized,
                                                                                      transaction_data[
                                                                                          'Not Accredited by'][
                                                                                          active_miners[key][terminology.location]][terminology.signature],
                                                                                      verification_key)
                        # signature_is_correct = new_encryption_module.verify_signature(hash_to_be_utilized,
                        #                                                               signature[3],
                        #                                                               verification_key)
                    if not signature_is_correct:
                        print('Miner: ' + key + ' is suspected to be malicious and will be reported.')
                        all_signatures_are_correct = False
                        break
            #
            # else:
            #     for signature in signatures:
            #         if signature[1] == str(self.ip_address):
            #             self_signed = True
            #             break
            return all_signatures_are_correct, self_signed, signed_by_all
        except Exception as e:
            print(e)

    def unsigned_did_transaction_already_received(self, received_request):
        for unsigned_did in self.unsigned_DIDs:
            if unsigned_did[terminology.transaction][terminology.identifier] == \
                    received_request[terminology.transaction][terminology.identifier]:
                return True
        return False

    # def already_registered(self, transaction_type, DID_identifier, schema_identifier, revoke_identifier):
    #     block_to_return = None
    #     DID_index = None
    #     schema_index = None
    #     revoke_index = None
    #     for i in range(len(self.chain)):
    #         if self.chain[i]['Body'][terminology.transaction][terminology.identifier] == DID_identifier:
    #             DID_index = i
    #             if transaction_type == terminology.DID_publication_request or transaction_type == terminology.DID_block:
    #                 block_to_return = self.chain[i]
    #                 break
    #             else:
    #                 for s in range(len(self.chain[i]['schemes_chain'])):
    #                     if self.chain[i]['schemes_chain'][s]['Body'][terminology.transaction][terminology.identifier] == schema_identifier:
    #                         schema_index = s
    #                         if transaction_type == terminology.schema_publication_request or transaction_type == terminology.schema_block:
    #                             block_to_return = self.chain[i]['schemes_chain'][s]
    #                             break
    #                         elif transaction_type == terminology.revoke_request or transaction_type == terminology.revoke_block:
    #                             block_to_return, revoke_index = self.credential_is_revoked(DID_index, schema_index, revoke_identifier)
    #                             break
    #     return block_to_return, DID_index, schema_index, revoke_index

    # def DID_block_exists(self, DID_identifier):
    #     block_to_return = None
    #     DID_index = None
    #     for i in range(len(self.chain)):
    #         if self.chain[i]['Body'][terminology.transaction][terminology.identifier] == DID_identifier:
    #             DID_index = i
    #             block_to_return = self.chain[i]
    #             break
    #     return block_to_return, DID_index

    # def schema_block_exists(self, DID_index, schema_identifier):
    #     block_to_return = None
    #     schema_index = None
    #     for s in range(len(self.chain[DID_index]['schemes_chain'])):
    #         if self.chain[DID_index]['schemes_chain'][s]['Body'][terminology.transaction][terminology.identifier] == schema_identifier:
    #             schema_index = s
    #             block_to_return = self.chain[DID_index]['schemes_chain'][s]
    #             break
    #     return block_to_return, schema_index

    # def revoke_block_exists(self, DID_index, schema_index, revoke_identifier):
    #     block_to_return = None
    #     revoke_index = None
    #     for v in range(len(self.chain[DID_index]['schemes_chain'][schema_index]['Hashes_of_revoked_credentials'])):
    #         if self.chain[DID_index]['schemes_chain'][schema_index]['Hashes_of_revoked_credentials'][v]['Body'][terminology.transaction][terminology.identifier] == revoke_identifier:
    #             revoke_index = v
    #             block_to_return = self.chain[DID_index]['schemes_chain'][schema_index]['Hashes_of_revoked_credentials'][v]
    #             break
    #     return block_to_return, revoke_index

    # def credential_is_revoked(self, did_index, schema_index, revoke_identifier):
    #     block_to_return = None
    #     revoke_index = None
    #     target_block = self.chain[did_index]['schemes_chain'][schema_index]
    #     for v in range(len(target_block['Hashes_of_revoked_credentials'])):
    #         if target_block['Hashes_of_revoked_credentials'][v]['Body'][terminology.transaction][terminology.identifier] == revoke_identifier:
    #             block_to_return = target_block['Hashes_of_revoked_credentials'][v]
    #             revoke_index = v
    #             break
    #     return block_to_return, revoke_index

    def mint_and_add_block(self, transaction, gateway_address, block_type, neighbors, DID_index, schema_index,
                           revoke_index, issuer_signature):
        if block_type == terminology.DID_block:
            previous_signature = self.chain[-1]['Header'][terminology.signature]
            identifier = transaction[terminology.identifier]
            new_index = self.chain[-1]['Header'][terminology.index] + 1
        else:
            if block_type == terminology.schema_block:
                previous_signature = self.chain[DID_index]['schemes_chain'][-1]['Header'][terminology.signature]
                identifier = new_encryption_module.hashing_function(transaction)
                new_index = self.chain[DID_index]['schemes_chain'][-1]['Header'][terminology.index] + 1

            else:
                previous_signature = \
                    self.chain[DID_index]['schemes_chain'][schema_index]['Hashes_of_revoked_credentials'][-1]['Header'][
                        terminology.signature]
                identifier = transaction[terminology.identifier]
                new_index = \
                    self.chain[DID_index]['schemes_chain'][schema_index]['Hashes_of_revoked_credentials'][-1]['Header'][
                        terminology.index] + 1

        new_block = msg_constructor.construct_new_block(block_type, transaction, self.ip_address, new_index,
                                                        issuer_signature, previous_signature)
        proof = consensus.generate_proof_of_authority(new_block)
        new_block['Header'][terminology.signature] = proof
        output.present_dictionary(new_block)
        self.add_block_to_local_chain(new_block, block_type, DID_index, schema_index, identifier, new_index)
        self.send_block_confirmation_msg(block_type, identifier, gateway_address, new_index)
        push_to_miners = msg_constructor.construct_internal_request(terminology.block, self.ip_address, new_block)
        for neighbor in neighbors:
            client.send(push_to_miners, neighbor)

    def add_block_to_local_chain(self, new_block, block_type, DID_index, schema_index, identifier, new_index):
        if block_type == terminology.DID_block:
            self.chain.append(new_block)
            removed_pending_block_request = self.pending_blocks.pop(
                new_block['Body'][terminology.transaction][terminology.identifier])
            bisect_test.add_to_sorted_DID_list(self.sorted_chain, identifier, new_index)
        if block_type == terminology.schema_block:
            self.chain[DID_index]['schemes_chain'].append(new_block)
            bisect_test.add_to_sorted_schemes_list(self.sorted_chain, identifier, new_index)
        if block_type == terminology.revoke_block:
            self.chain[DID_index]['schemes_chain'][schema_index]['Hashes_of_revoked_credentials'].append(new_block)
            bisect_test.add_to_sorted_revoke_list(self.sorted_chain, identifier, new_index)

    def save_modified_blockchain(self, version=None):
        if version:
            open_file = open('local_files/blockchain/blockchain.pkl', "wb")
            pickle.dump(version, open_file)
            open_file.close()

    def process_unsigned_dids(self, miner_location, miners, BC_address, neighbors, authorized_miner):
        for index in range(len(self.unsigned_DIDs)):
            print(str(index + 1) + "- ")
            output.present_dictionary(self.unsigned_DIDs[index])
            # print(self.unsigned_DIDs[index])
        print("\nInput the number of request you want to process: ")
        try:
            chosen_request = int(input())
            handled_request = self.unsigned_DIDs[chosen_request - 1]
            self.add_decision(handled_request, miner_location, miners, BC_address, neighbors, authorized_miner)
        except Exception as e:
            print(e)

    def add_decision(self, original_handled_request, miner_location, miners, BC_address, neighbors, authorized_miner):
        # print(original_handled_request)
        new_handled_request = {}
        for key in original_handled_request:
            new_handled_request[key] = original_handled_request[key]
        if not self.automatic_signing:
            print("Is this institution accredited in your territory? (Y/N)\n")
            decision = shared_functions.input_function(['y', 'Y', 'N', 'n'])
            person_who_signed_this = input("Kindly input your name and position (all in one line):\n")
        else:
            decision = 'y'
            person_who_signed_this = 'General Registrar'
        signature = shared_functions.retrieve_signature_from_saved_key(
            original_handled_request[terminology.transaction][terminology.identifier], 'my_key')
        signature_info = {terminology.address: self.ip_address,
                          terminology.person_who_signed_this: person_who_signed_this,
                          terminology.signature: signature}
        # signature_info = [miner_location, self.ip_address, person_who_signed_this, signature]
        if decision in ['Y', 'y']:
            new_handled_request[terminology.transaction]['Accredited By'][miner_location] = signature_info
            accredited = 'Yes'
        else:
            new_handled_request[terminology.transaction]['Not Accredited by'][miner_location] = signature_info
            # new_handled_request[terminology.transaction]['Not Accredited by'].append(signature_info)
            accredited = 'No'
        # something is wrong here as the original_handled_request is not in the list. maybe because the use of deepcopy
        if not self.automatic_signing:
            self.unsigned_DIDs.remove(original_handled_request)
        self.pending_blocks[new_handled_request[terminology.transaction][terminology.identifier]] = {
            'Accredited': accredited,
            terminology.signature: signature,
            'Admin': person_who_signed_this}
        # self.handle_new_block_request(new_handled_request, miners, BC_address, neighbors, self.ip_address,
        #                               miner_location, authorized_miner)
        random_neighbor = random.choice(neighbors)
        client.send(new_handled_request, random_neighbor)
