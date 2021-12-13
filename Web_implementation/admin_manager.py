
def initiate_admin(name='Hamza', password='1234'):
    admin_info = {'name': name,
                  'pass': password}
    return admin_info


class AdminManager:
    def __init__(self):
        self.admins = {1: initiate_admin()}
        self.requests = None

    def admin_registered(self, checked_admin):
        for key in self.admins:
            if self.admins[key]['name'] == checked_admin:
                return self.admins[key]['pass']
        return None


