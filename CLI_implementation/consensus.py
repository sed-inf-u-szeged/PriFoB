import new_encryption_module
import terminology
import shared_functions


def generate_proof_of_authority(new_block):
    try:
        # one method is currently available which is the proof of authority
        signature = shared_functions.retrieve_signature_from_saved_key(new_block['Body'], 'my_key')
        return signature
    except Exception as e:
        print(e)


def verify_proof_of_authority(miners, minter_id, block_body, signature):
    signature_is_correct = False
    hash_to_be_utilized = new_encryption_module.hashing_function(block_body)
    for key in miners:
        if key == minter_id:
            verification_key = new_encryption_module.prepare_key_for_use(terminology.public, None, miners[key])
            signature_is_correct = new_encryption_module.verify_signature(hash_to_be_utilized, signature, verification_key)
            break
    return signature_is_correct
