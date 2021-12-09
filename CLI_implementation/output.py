import json
import threading
import shared_functions
from os import system, name
import terminology


def gateway_options(address, count_active_miners, mining_requests):
    active_connections()
    print("Address of this gateway is: " + address)
    print('What would you like to do?')
    print('1- Review miners info (' + str(count_active_miners) + ' active miners)')
    print('2- Review mining requests (' + str(mining_requests) + ')')
    print('3- Refresh?')
    print('4- exit.')


def credential_status(response):
    print("response to validation request had been received")
    if response['credential_is_valid']:
        print("The following credential is valid (issued by the claimed issuer):\n")
    else:
        print("The following credential is invalid:\n")
    present_dictionary(response['credential'])
    print('Bodies by which this issuer is accredited: ')
    for reference in response['accredited_in']:
        print(reference[0])


def clear():
    try:
        # for windows
        if name == 'nt':
            _ = system('cls')
        # for mac and linux(here, os.name is 'posix')
        else:
            _ = system('clear')
    except Exception as e:
        print(e)


def DID_info(DID):
    print("Your public DID is " + str(DID))
    print("If your DID is not on the Public Chain, you need to confirm it before issuing new credentials.")


def block_confirmed(added_block):
    print('The following block is now added to the Blockchain and is publicly available:')
    present_dictionary(added_block)


def no_did():
    print("Your institution has no DID")
    print("A new DID is generated..!")


def define_requested_credential_attributes(institutions_info):
    print('Kindly select: request credential from \n1-the issuer institution\n2-another agent ?')
    option = shared_functions.input_function(['1', '2'])
    try:
        agent_data = {}
        if option == '1':
            print("Out of the following institutions, please type the institution name you want to request a credential from:\n")
            institution_names = []
            for key in institutions_info:
                institution_names.append(key)
                print(key)
            selected_institution = shared_functions.input_function(institution_names)
            holder_address = institutions_info[selected_institution][terminology.address]
            print('Out of the following types of credentials, please type the one you were granted:\n')
            schemes = []
            for key in institutions_info[selected_institution]['schemes']:
                print(key)
                schemes.append(key)
            selected_schema = shared_functions.input_function(schemes)
            attributes = institutions_info[selected_institution]['schemes'][selected_schema]
            print("The following data are requested to finalize the credential request:\n")
            agent_data[terminology.schema_identifier] = selected_schema
            for attribute in attributes:
                if attribute[1] == 'Mandatory':
                    attribute_input = input(attribute[0] + ">> ")
                    agent_data[attribute[0]] = attribute_input
        else:
            holder_address = input("Type the ip_address of the agent you are requesting the credential from\n")
        return holder_address, agent_data
    except Exception as e:
        print(e)


def customer_options(number_of_notification, number_of_credential_requests, my_address):
    active_connections()
    print("Address of this gateway is: " + my_address)
    option = input(
        "What would you like to do?\n"
        "1) Request credential\n"
        "2) Manage saved credentials\n"
        "3) download the full public blockchain\n"
        "4) Notifications(" + str(number_of_notification) + ')\n'
        "5) Handle credential requests(" + str(number_of_credential_requests) + ')\n'
        "6) Refresh screen\n"
        "7) exit\n>>")
    return option


def did_info(did):
    present_dictionary(did)


def schema_info(D2_chain, selected_institution):
    for schema_chain in D2_chain:
        if schema_chain[0]['Institution_name'] == selected_institution:
            print('Diploma(s) issued by this institution: \n')
            for i in range(1, len(schema_chain)):
                print(schema_chain[i]['body']['credential_level'])
            break


def print_welcome():
    clear()
    print('                   *************************************                   ')
    print('                       WELCOME TO THE PriFoB PROJECT                       ')
    print('                   *************************************                   ')
    print('\n\n\nKindly select the type of this entity (input a number from 1 to 4):\n')
    print('1- Gateway\n')
    print('2- Miner\n')
    print('3- Institution Customer\n')
    print('4- Student Customer\n')
    print('5- Exit\n')
    print('PLEASE NOTE THAT YOU NEED AT LEAST 1 Gateway, 2 Miners, 1 Institution and 2 Students to check all the functionalities of the project')


def revoke_info(D3_chain, selected_institution):
    for revoke_chain in D3_chain:
        if revoke_chain[0] == selected_institution:
            print('Hashes of revoked credentials of level: ' + revoke_chain[1])
            for revoked_credential in revoke_chain[3]:
                print(revoked_credential)


def institution_options(num_of_notifications):
    active_connections()
    print("Please choose one of the following options:\n")
    print("1- Publish your DID\n"
          "2- Create_new_schema\n"
          "3- Issue_new_credential\n"
          "4- Manage existing credential\n"
          "5- Refresh screen\n"
          "6- Notifications (" + str(num_of_notifications) + ") \n"
          "7- exit.\n\n")
    option = shared_functions.input_function(['1', '2', '3', '4', '5', '6', '7'])
    return option


def credential_request_sent(request, institution_name):
    print('Upon your confirmation, credential request with the following information will be sent to: ' + institution_name)
    present_dictionary(request)
    print('Do you confirm this? (Y/N)\n')
    decision = shared_functions.input_function(['Y', 'y', 'N', 'n'])
    if decision in ['Y', 'y']:
        return True
    else:
        return False


def request_inst_name():
    n = input("please enter the name of your institution:\n")
    return n


def issue_confirmation(available):
    if available:
        print("An available credential was requested and it is being send back to the customer...")
    else:
        print('An unavailable credential was requested. Negative response is being sent back to the customer...')


def saved_file_confirmation():
    print("New file has been saved successfully")


def listening():
    print("[Listening]: This node is now waiting for requests")


def active_connections():
    print('[ACTIVE THREADS]:' + str(threading.activeCount()))


def new_connection(address):
    print("[NEW CONNECTION]: " + str(address) + " is now connected to this devices.!!")


def miner_admin_options(num_of_unconfirmed_DIDs):
    active_connections()
    print("You have " + str(num_of_unconfirmed_DIDs) + " unsigned DID requests.")
    print(
        "The system is handling many tasks in the background. If you have nothing to do as admin, stay on this screen!")
    print("Choose an option from following:")
    print("1- Review DID requests(" + str(num_of_unconfirmed_DIDs) + ')')
    print("2- Review Local Chain statistics")
    print("3- Synchronize Local Chain")
    print("4- Refresh screen")
    print("5- delete my local BC contents")
    print('6- exit\n')


def present_dictionary(dictionary_to_be_presented):
    print(json.dumps(dictionary_to_be_presented, indent=4))


def present_list(list_to_be_presented):
    for i in range(len(list_to_be_presented)):
        print(str(i+1) + '-')
        for item in list_to_be_presented[i]:
            print(item)
        print('==========================================')
