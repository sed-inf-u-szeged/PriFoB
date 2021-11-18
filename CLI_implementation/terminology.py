status = 'STATUS'
valid = '==||VALID||=='
revoked = '==||REVOKED||=='
faulty_signature = '==||FAULTY SIGNATURE||=='
schema_not_registered = '==||FAULTY SCHEMA||=='
DIDs = 'DIDs'
schemes = 'schemes'
index = 'Index'
DID_index = 'DID_index'
schema_index = 'Schema_index'
revoke = 'revoke'
identifier = 'Identifier'
issuer_signature = 'Issuer_Signature'
private = 'private'
public = 'public'
active = 'active'
passive = 'passive'
address = 'Address'
block = 'Block'
ping_time = 5
location = 'Location'
DID_block = 'DID_block'
did_identifier = 'DID_Identifier'
schema_identifier = 'Schema_Identifier'
schema_block = 'Schema_block'
credential = 'Credential'
revoke_block = 'Revoke_block'
previous_signature = 'Previous_Signature'
DID_publication_request = 'DID_publication'
schema_publication_request = 'schema_publication'
revoke_request = 'revoke_request'
the_type = 'Type'
transaction = 'Transaction'
signature = 'Signature'
transactions_labels = [DID_publication_request, schema_publication_request, revoke_request]
blocks_labels = [DID_block, schema_block, revoke_block]
txs_and_blocks_labels = {DID_publication_request: DID_block,
                         schema_publication_request: schema_block,
                         revoke_request: revoke_block
                         }

