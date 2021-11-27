import bisect

sorted_DIDs = []
sorted_schemes = []
sorted_revoked_cres = []


def add_to_sorted_DID_list(DID_identifier, DID_index):
    bisect.insort(sorted_DIDs, (DID_identifier, DID_index))


def add_to_sorted_schemes_list(schema_identifier, schema_index):
    bisect.insort(sorted_schemes, (schema_identifier, schema_index))


def add_to_sorted_revoke_list(revoke_identifier, revoke_index):
    bisect.insort(sorted_revoked_cres, (revoke_identifier, revoke_index))


def get_index(the_list, target):
    fst, snd = zip(*the_list)
    if type(target) is str:
        index = bisect.bisect(fst, target) - 1
        new_target = target
        # index = bisect.bisect(the_list, target)
    else:
        index = bisect.bisect(fst, target[1]) - 1
        new_target = target[1]
        # index = bisect.bisect(the_list, target[1])
    if index < len(the_list) and new_target == fst[index]:
        return snd[index]
        # print(str(new_target) + ' EXISTS with index = ' + str(snd[index]))
        # return True
    else:
        return None
        # print(new_target + ' DOES NOT EXIST')
        # return False


# def validate_code():
#     for i in range(1000):
#         randomly_DID = random.choice(list(dictionary_of_DIDs.items()))
#         randomly_schema = random.choice(list(dictionary_of_schemes.items()))
#         randomly_revoked = random.choice(list(dictionary_of_revoked.items()))
#         invalid_did = names.get_first_name()
#         print(dictionary_of_DIDs, dictionary_of_schemes, dictionary_of_revoked)
#         DIDs = get_index(sorted_DIDs, randomly_DID)
#         schemes = get_index(sorted_schemes, randomly_schema)
#         revokes = get_index(sorted_revoked_cres, randomly_revoked)
#         invalid = get_index(sorted_DIDs, invalid_did)
#         if DIDs == True and schemes == True and revokes == True and invalid == False:
#             print("\n ++++++++++ Code is Valid +++++++++++")
#             print(i)
#         else:
#             print("\n ---------- Code is inValid ------------")
#             break
#
#
# validate_code()
