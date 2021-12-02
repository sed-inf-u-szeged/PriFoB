import math

c = int(input('input number of servers: > '))
lambda_var = int(input('input arrival rate (req/s): > '))
signing_speed = 0.09
# signing_speed = float(input('input signing speed in a single miner system (s): > '))
processing_speed = 0.6
# processing_speed = float(input('input processing speed in a single miner system (s/req): > '))
processing_speed += c * signing_speed
mue_var = 1 / processing_speed

rau = lambda_var/mue_var

first_cumulative = 0

for i in range(c-1):
    compute_local = (1/math.factorial(i)) * (lambda_var/mue_var)**i
    first_cumulative += compute_local

second_part = ((1 / math.factorial(c)) * ((lambda_var/mue_var)**c)) * (c*mue_var/(c*mue_var-lambda_var))

probability_zero_requests_are_waiting = 1/(first_cumulative + second_part)
average_time_of_request_in_system = (((mue_var * ((lambda_var / mue_var)**c)) / (math.factorial(c-1) * (c*mue_var-lambda_var)**2)) * probability_zero_requests_are_waiting) + (1/mue_var)
c = input('l...')
