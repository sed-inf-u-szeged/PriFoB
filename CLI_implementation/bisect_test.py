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
            index = bisect.bisect(fst, target) - 1
            if target in fst:
                return snd[index], True
            else:
                return None, False


