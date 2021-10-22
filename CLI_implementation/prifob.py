import output
import shared_functions

output.print_welcome()
decision = shared_functions.input_function(['1', '2', '3', '4', '5'])
if decision == '1':
    import gateway
    gateway.start()
if decision == '2':
    import miner
    miner.start()
if decision == '3':
    import institution
if decision == '4':
    import agent
    agent.start()
if decision == '5':
    import os
    os.close(1)
