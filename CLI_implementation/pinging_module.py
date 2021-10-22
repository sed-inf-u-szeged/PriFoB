import time
import client


ping_time = 5
active = 'active'
passive = 'passive'
list_of_connections = []


def miner_is_active(miner_record):
    if miner_record[2] == active:
        return True
    else:
        return False


def count_active_miners(list_of_miners):
    num_of_active_miners = 0
    for miner in list_of_miners:
        if miner_is_active(miner):
            num_of_active_miners += 1
    return num_of_active_miners


def ping(list_of_miners):
    while True:
        try:
            # print('Pinging miners...')
            num_of_active_miners = count_active_miners(list_of_miners)
            for miner in list_of_miners:
                if miner_is_active(miner):
                    # print(f"pinging: [{miner[1]}]")
                    ping_request = {'type': 'ping',
                                    'Num_of_miners': num_of_active_miners}
                    client.send(ping_request, miner[1])
            # clear()
            # print("address of this gateway is: " + str(address))
            # print('Pinging miners...')
            time.sleep(ping_time)
            # print('\nActive miners are:\n')
            for miner in list_of_miners:
                if time.time() - miner[3] > (3 * ping_time):
                    miner[2] = passive
                # else:
                #     print(miner[1])
            time.sleep(ping_time)
        except Exception as e:
            print(e)


def ping_neighbors(list_of_neighbors):
    while True:
        try:
            # print('Pinging neighbors...')
            for neighbor in self.neighbors:
                if self.miner_is_active(neighbor):
                    # print(f"pinging: [{miner[0]}]")
                    ping_request = {'type': 'ping',
                                    'Num_of_miners': None}
                    client.send(ping_request, neighbor[0])
            # clear()
            # print("address of this gateway is: " + str(address))
            # print('Pinging miners...')
            time.sleep(ping_time)
            # print('\nActive miners are:\n')
            for neighbor in self.neighbors:
                if time.time() - neighbor[2] > (3 * ping_time):
                    neighbor[1] = passive
                # else:
                #     print(neighbor[1] + "is active")
            time.sleep(ping_time)
        except Exception as e:
            print(e)


def respond_to_ping(requester):
    response = {'type': 'response_to_ping',
                'alive': True}
    memory_pool.msgs_to_be_sent.put([response, requester])
