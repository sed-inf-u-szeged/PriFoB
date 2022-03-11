import json

import output
import shared_functions
from flask import Flask, jsonify, abort, request, make_response, url_for, send_file, Response

import terminology
import requests
import bisect_test
import new_encryption_module

output.print_welcome()
decision = shared_functions.input_function(['1', '2', '3', '4', '5'])
if decision == '1':
    import gateway

    app = Flask(__name__)

    gateway.start()

    @app.route('/')
    def hello_world():
        return 'Hello from Gateway'

    @app.route('/address')
    def address():
        return gateway.address

    @app.route('/randommineraddress')
    def random_miner_address():
        miner_address = gateway.my_load_balancer.select_next_miner()
        return miner_address


    @app.route('/prifobapi/v1.0/institutions')
    def get_institutions():
        miner_address = gateway.my_load_balancer.select_next_miner()
        miner_url = 'http://' + miner_address + ':5000/prifobapi/v1.0/institutions'
        print('institutions miner_url: ', miner_url)
        resp = requests.get(miner_url, json = request.get_json())
        excluded_headers = ['content - encoding', 'content - length', 'transfer - encoding', 'connection']
        headers = [(name, value) for (name, value) in resp.raw.headers.items() if name.lower() not in excluded_headers]
        response = Response(resp.content, resp.status_code, headers)
        return response

    @app.route('/prifobapi/v1.0/validity', methods=['POST'])
    def is_valid():
        miner_address = gateway.my_load_balancer.select_next_miner()
        miner_url = 'http://' + miner_address + ':5000/prifobapi/v1.0/validity'
        print('institutions miner_url: ', miner_url)
        resp = requests.post(miner_url, json=request.get_json())
        excluded_headers = ['content - encoding', 'content - length', 'transfer - encoding', 'connection']
        headers = [(name, value) for (name, value) in resp.raw.headers.items() if name.lower() not in excluded_headers]
        response = Response(resp.content, resp.status_code, headers)
        return response

    @app.route('/prifobapi/v1.0/download', methods=['GET'])
    def download():
        miner_address = gateway.my_load_balancer.select_next_miner()
        miner_url = 'http://' + miner_address + ':5000/prifobapi/v1.0/download'
        print('institutions miner_url: ', miner_url)
        resp = requests.get(miner_url, json=request.get_json())
        excluded_headers = ['content - encoding', 'content - length', 'transfer - encoding', 'connection']
        headers = [(name, value) for (name, value) in resp.raw.headers.items() if name.lower() not in excluded_headers]
        response = Response(resp.content, resp.status_code, headers)
        return response

    if __name__ == '__main__':
        app.run(host="0.0.0.0")

if decision == '2':
    import miner

    app = Flask(__name__)

    #miner.start()

    @app.route('/')
    def hello_world():
        return 'Hello from Miner'


    @app.route('/address')
    def address():
        return miner.miner.ip_address


    @app.route('/prifobapi/v1.0/institutions')
    def get_institutions():
        #handle_institutions_info_request
        try:
            institutions = []
            for DID_block in miner.miner.my_blockchain.chain:
                if DID_block['Header'][terminology.signature] != 0:
                    institution = {}
                    # institution['id'] =
                    institution['DID_Identifier'] = DID_block['Body']['Transaction']['Identifier']
                    institution['ip'] = DID_block['Body']['Transaction']['institution_address']
                    institution['schemas'] = []

                    for schema in DID_block['schemes_chain']:
                        if schema['Header'][terminology.signature] != 0:
                            schema_data = {}
                            schema_data['attributes'] = []
                            schema_data['Schema_Identifier'] = schema['Body']['Transaction']['Identifier']
                            for attr in schema['Body']['Transaction']['schema_attributes']:
                                if attr != 'Not Mandatory' or attr != 'Mandatory':
                                    schema_data['attributes'].append(attr)

                            institution['schemas'].append(schema_data)

                    institutions.append(institution)

            print("institutions: ", institutions)
            return jsonify(institutions)
        except Exception as e:
            print(e)
        return ""

    @app.route('/prifobapi/v1.0/validity', methods=['POST'])
    def is_valid():
        #handle_signature
        accredited_in = None
        body_of_request = request.json['body']
        hash_of_credential = request.json['hash_of_credential']
        did_index = body_of_request[terminology.DID_index]
        schema_index = body_of_request[terminology.schema_index]
        # schema_block, DID_index, schema_index, revoke_index = self.my_blockchain.already_registered(terminology.schema_block, body_of_request[terminology.did_identifier], body_of_request[terminology.schema_identifier], new_encryption_module.hashing_function(body_of_request))
        revoke_index = bisect_test.get_index(miner.miner.my_blockchain.sorted_chain, 3,
                                             new_encryption_module.hashing_function(body_of_request))
        # revoke_block, revoke_index = self.my_blockchain.revoke_block_exists(did_index, schema_index, hash_of_credential)
        if revoke_index is None:
            accredited_in = miner.miner.my_blockchain.chain[did_index]['Body'][terminology.transaction]['Accredited By']
            key = new_encryption_module.prepare_key_for_use(terminology.public, None,
                                                            miner.miner.my_blockchain.chain[did_index]['schemes_chain'][
                                                                schema_index]['Body'][terminology.transaction][
                                                                'schema_public_key'])
            is_valid = new_encryption_module.verify_signature(hash_of_credential,
                                                              body_of_request[terminology.signature], key)
            if is_valid:
                result = terminology.valid
            else:
                result = terminology.faulty_signature
        else:
            result = terminology.revoked
        response = {result, accredited_in, hash_of_credential}
        #response = msg_constructor.signature_validation_response(result,
        #                                                         body_of_request[terminology.did_identifier],
        #                                                         body_of_request[terminology.schema_identifier],
        #                                                         accredited_in, requester_address, hash_of_credential)
        print('validity ', response)
        return jsonify(response)

    @app.route('/prifobapi/v1.0/download', methods=['GET'])
    def download():
        #provide_full_BC
        print("download", miner.miner.my_blockchain.chain)
        return jsonify(miner.miner.my_blockchain.chain)

    if __name__ == '__main__':
        app.run(host="0.0.0.0")

if decision == '3':
    import institution

    app = Flask(__name__)

    @app.route('/')
    def hello_world():
        return 'Hello from Institution'

    @app.route('/address')
    def address():
        return institution.institution.address

    @app.route('/prifobapi/v1.0/credential', methods=['POST'])
    def credential():
        #process_credential_request

        KEY_SCHEMA = 'schema'
        KEY_PUB = 'requester_pub_key'

        if not request.json:
            print('400 not request.json')
            abort(400)
        if not KEY_SCHEMA in request.json:
            print('400 not KEY_SCHEMA in request.json')
            abort(400)

        path = "local_files/credentials/"
        #request_level = request[terminology.schema_identifier]
        request_level = request.json[KEY_SCHEMA]
        with open('local_files/schemes/' + request_level + '.txt', 'r') as file:
            schema = json.load(file)
        credential_label = 'cre_' + request_level + '_'
        #TODO ?
        print('schema[schema_attributes] ', schema['schema_attributes'])
        for attribute in schema['schema_attributes']:
            #if attribute[1] == 'Mandatory':
            credential_label = credential_label + request.json[attribute]
        print('credential_label ', credential_label)
        # print('institution is looking for the credential with title:')
        # print(credential_label)
        # print('if the credential is found it will be sent to:')
        # print(requester_address)
        credential_is_available = False
        for filename in os.listdir(path):
            print('for filename ', filename)
            if filename == credential_label + '.txt':
                print('credential is found..')
                with open(path + filename, 'r') as credential:
                    requested_credential = json.load(credential)
                    credential_is_available = True
                break
        response = {terminology.the_type: 'response_to_credential_request'}
        if credential_is_available:
            response['status'] = True
            encrypted_credential, final_encoded_encrypted_symmetric_key = shared_functions.react_to_credential_request(
                requested_credential, request.json[KEY_PUB])
            response['encrypted_credential'] = encrypted_credential
            response['encrypted_symmetric_key'] = final_encoded_encrypted_symmetric_key
        else:
            response['status'] = False
            response['original_request'] = request
        # output.issue_confirmation(credential_is_available)
        print('credential ', response)
        return jsonify(response)

    if __name__ == '__main__':
        app.run(host="0.0.0.0")

if decision == '4':
    import agent
    agent.start()
if decision == '5':
    import os
    os.close(1)


