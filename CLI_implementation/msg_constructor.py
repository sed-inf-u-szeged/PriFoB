import shared_functions
import terminology
import new_encryption_module


def new_did_transaction(org_name, org_address, org_pub_key):
    transaction = {terminology.identifier: org_name,
                   'institution_address': org_address,
                   'institution_public_key': org_pub_key,
                   'Accredited By': [],
                   'Not Accredited by': []
                   }
    return transaction


def construct_new_block_request(request_type, data, deserialized_signature=0):
    request = {terminology.the_type: request_type,
               terminology.transaction: data,
               terminology.signature: deserialized_signature}
    return request


def construct_new_block(block_type, block_body, ip_address, issuer_signature=0, previous_signature=0, signature=0):
    try:
        if block_type == terminology.DID_block:
            return construct_DID_block(block_type, block_body, ip_address, previous_signature, signature)
        if block_type == terminology.schema_block:
            return construct_schema_block(block_type, block_body, ip_address, previous_signature, signature, issuer_signature)
        if block_type == terminology.revoke_block:
            return construct_revoke_block(block_type, block_body, ip_address, previous_signature, issuer_signature, signature)
    except Exception as e:
        print(e)


def construct_DID_block(block_type, block_body, minter_id, previous_signature, signature):
    schema_genesis_block = construct_Genesis_block(terminology.schema_block, minter_id)
    block = {'Header': {terminology.the_type: block_type,
                        'Minter_id': minter_id,
                        terminology.signature: signature},
             'Body': {terminology.transaction: block_body,
                      terminology.previous_signature: previous_signature},
             'schemes_chain': [schema_genesis_block]
             }
    return block


def construct_internal_request(request_type, agent_address, request_body):
    internal_request = {terminology.the_type: request_type,
                        'agent_address': agent_address,
                        'body': request_body}
    return internal_request


def construct_Genesis_block(block_type, gateway_address, previous_signature=0):
    block = construct_new_block(block_type, {terminology.identifier: 'Genesis Block'}, gateway_address, previous_signature, new_encryption_module.hashing_function('Genesis Block'))
    return block


def construct_schema_block(block_type, block_body, minter_id, previous_signature_on_BC, signature_of_miner, signature_of_issuer):
    revoke_genesis_block = construct_Genesis_block(terminology.revoke_block, minter_id)
    block = {'Header': {terminology.the_type: block_type,
                        'Minter_id': minter_id,
                        terminology.signature: signature_of_miner},
             'Body': {terminology.transaction: block_body,
                      terminology.previous_signature: previous_signature_on_BC,
                      terminology.issuer_signature: signature_of_issuer},
             'Hashes_of_revoked_credentials': [revoke_genesis_block]
             }
    return block


def construct_block_confirmation_message(is_added, block_type, miner_ip, block_identifier, miner_to_gateway):
    response = {terminology.the_type: 'block_confirmation',
                'block_type': block_type,
                'block_identifier': block_identifier,
                'added': is_added}
    if miner_to_gateway:
        response['miner'] = miner_ip
    return response


def schema_block_data(inst_name, address, schema_label, public_key, attributes):
    data = {'institution_name': inst_name,
            'institution_address': address,
            terminology.identifier: schema_label,
            'schema_public_key': public_key,
            'schema_attributes': attributes}
    return data


def define_schema_attributes():
    new_schema_attributes = []
    done = False
    while not done:
        print('Input the attribute title that will be used when issuing a credential using this schema..')
        print('Once done, type: done')
        new_attribute = input()
        if new_attribute == 'done':
            break
        else:
            print('Should this field be requested from agents? [y,n]')
            decision = shared_functions.input_function(['Y', 'y', 'n', 'N'])
            if decision in ['y', 'Y']:
                attribute_field = [new_attribute, 'Mandatory']
            else:
                attribute_field = [new_attribute, 'Not Mandatory']
            new_schema_attributes.append(attribute_field)
    return new_schema_attributes


def construct_new_digital_credential(inst_name, label, credential_attributes):
    new_credential = {terminology.did_identifier: inst_name,
                      terminology.schema_identifier: label}
    new_credential_label = 'cre_' + label + '_'
    for attribute in credential_attributes:
        new_field = input("please input: " + attribute[0] + '\n>>')
        new_credential[attribute[0]] = new_field
        if attribute[1] == 'Mandatory':
            new_credential_label = new_credential_label + new_field
    return new_credential, new_credential_label


def construct_validation_request(did_identifier, schema_identifier, signature, hashed_credential, requester_address):
    request = {terminology.the_type: 'signature_validation',
               terminology.did_identifier: did_identifier,
               terminology.schema_identifier: schema_identifier,
               'requester_address': requester_address,
               'hash_of_credential': hashed_credential,
               terminology.signature: signature}
    return request


def signature_validation_response(result, did_identifier, schema_identifier, accredited_in, requester_address, hash_of_credential):
    credential = {terminology.did_identifier: did_identifier,
                  terminology.schema_identifier: schema_identifier,
                  'Hash_of_credential': hash_of_credential}
    response = {terminology.the_type: 'response to signature validation request',
                'agent_address': requester_address,
                'credential_is_valid': result,
                terminology.credential: credential}
    if accredited_in is not None:
        response['Accredited in'] = accredited_in
    return response


def revoke_block_data(inst_name, address, schema_label, hash_of_signed_credential):
    data = {terminology.did_identifier: inst_name,
            'institution_address': address,
            terminology.schema_identifier: schema_label,
            terminology.identifier: hash_of_signed_credential}
    return data


def construct_revoke_block(block_type, block_body, minter_id, previous_signature, issuer_signature, signature):
    block = {'Header': {terminology.the_type: block_type,
                        'Minter_id': minter_id,
                        terminology.signature: signature},
             'Body': {terminology.transaction: block_body,
                      terminology.previous_signature: previous_signature,
                      terminology.issuer_signature: issuer_signature}
             }
    return block


def construct_notification(subject, result, data=None):
    notification = {'Subject': subject,
                    'Result': result,
                    'Details': data}
    return notification


def request_to_be_miner(location, address, public_key):
    request = {terminology.the_type: 'request_to_be_miner',
               'location': location,
               'miner_address': address,
               'public_key': public_key}
    return request


def construct_response_to_mining_request(is_added, data_placement, neighbor=None, num_miners=None, num_of_neighbors=None):
    response = {terminology.the_type: 'response to mining request',
                'added': is_added}
    if is_added:
        response['neighbor'] = neighbor
        response['Num_of_miners'] = num_miners
        response['num_of_neighbors'] = num_of_neighbors
        response['data_placement'] = data_placement
    return response

###########################################################################################


def construct_final_response_to_signature_validation(encrypted_hash, decrypted_hash):
    response = {terminology.the_type: 'response_to_signature_validation',
                'encrypted_hash': encrypted_hash,
                'hash': decrypted_hash}
    return response


def construct_request_inst_info():
    request = {terminology.the_type: 'institutions'}
    return request


def construct_credential_request(requester_pub_key, requester_first_name, requester_last_name, requester_ip, agent_data):
    request = {terminology.the_type: 'credential_request',
               'std_first_name': requester_first_name,
               'std_last_name': requester_last_name,
               'requester_pub_key': requester_pub_key,
               'requester_ip': requester_ip}
    for key in agent_data:
        request[key] = agent_data[key]
    return request


#################################################################################
