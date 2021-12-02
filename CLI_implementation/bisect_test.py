import bisect


class SortedBlocks:
    def __init__(self):
        self.sorted_DIDs = []
        self.sorted_schemes = []
        self.sorted_revoked_cres = []


def add_to_sorted_DID_list(sorted_chain, DID_identifier, DID_index):
    bisect.insort(sorted_chain.sorted_DIDs, (DID_identifier, DID_index))


def add_to_sorted_schemes_list(sorted_chain, schema_identifier, schema_index):
    bisect.insort(sorted_chain.sorted_schemes, (schema_identifier, schema_index))


def add_to_sorted_revoke_list(sorted_chain, revoke_identifier, revoke_index):
    bisect.insort(sorted_chain.sorted_revoked_cres, (revoke_identifier, revoke_index))


def get_index(sorted_chain, list_level, target):
    if list_level in [1, 2, 3]:
        if list_level == 1:
            the_list = sorted_chain.sorted_DIDs
        elif list_level == 2:
            the_list = sorted_chain.sorted_schemes
        else:
            the_list = sorted_chain.sorted_revoked_cres
        if the_list:
            fst, snd = zip(*the_list)
            # here, a for loop needs to be implemented where it iterates from the end of the sorted list towards the genises block
            # if the following condition applies, the for loop shall break and the snd[index] is returned. Otherwise, the for loop continues
            # this should allow for DAG based adoption without the "longest chain" rule to be applied. To this end, a tie appearing in the index of several blocks
            # does not imply a security problem
            index = bisect.bisect(fst, target) - 1
            if index < len(the_list) and target == fst[index]:
                return snd[index]
                # print(str(new_target) + ' EXISTS with index = ' + str(snd[index]))
                # return True
            else:
                return None
                # print(new_target + ' DOES NOT EXIST')
                # return False
        else:
            return None
