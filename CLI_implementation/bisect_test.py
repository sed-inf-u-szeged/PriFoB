import bisect


class SortedBlocks:
    def __init__(self):
        self.sorted_DIDs = []
        self.sorted_schemes = []
        self.sorted_revoked_cres = []


def add_to_sorted_DID_list(self, DID_identifier, DID_index):
    bisect.insort(self.sorted_DIDs, (DID_identifier, DID_index))


def add_to_sorted_schemes_list(self, schema_identifier, schema_index):
    bisect.insort(self.sorted_schemes, (schema_identifier, schema_index))


def add_to_sorted_revoke_list(self, revoke_identifier, revoke_index):
    bisect.insort(self.sorted_revoked_cres, (revoke_identifier, revoke_index))


def get_index(self, list_level, target):
    if list_level in [1, 2, 3]:
        if list_level == 1:
            the_list = self.sorted_DIDs
        elif list_level == 2:
            the_list = self.sorted_schemes
        else:
            the_list = self.sorted_revoked_cres
        if the_list:
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
        else:
            return None
