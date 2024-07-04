import math
import sys
import numpy as np
import random, json
import os
# At a specific moment, analyze the traffic throughput of each link (ISLs and GSLs) under the network topology and traffic conditions.
# Network Topology: User blocks connect to a satellite, and satellites forms Circles.
# Traffic: Based on the Starlink traffic of each block from CloudFlare, flows probabilistically increasing by 0.5M each sampling time (ISL capacity 20Gbps; GSL Uplink/Downlink: 4Gbps).

# Constants
RADIUS = 6371
Flow_size = 0.5  # 0.5M

f = open("../config.json", "r", encoding='utf8')
table = json.load(f)
cons_name = table["Name"]
altitude = int(table["Altitude (km)"])
num_of_orbit = table["# of orbit"]
sat_of_orbit = table["# of satellites"]
inclination = table["Inclination"]  # inclination
sat_num = num_of_orbit * sat_of_orbit
user_num = inclination * 2 * 360
sat_pos_car = []  # 1584 satellites' positions
user_pos_car = []  # inclination * 2 * 360 blocks' positions (from high-latitude to low-latitude and high-longitude to low-longitude areas)
GS_pos_car = []  # GS positions
pop_count = []  # 53 ~ -53, traffic probability per block
user_connect_sat = []  # satellite connected to each block 
sat_connect_gs = []  # GS connected to each satellite 
gsl_occurrence = [[] for i in range(sat_num)] # blocks served by each GSL 
gsl_occurrence_num = [-1 for i in range(sat_num)] # number of blocks served by each GSL 
cycle_path = [
    -1 for i in range(sat_num)
]  # cycle_path[i][j] = k: k is the next hop from i to j; k == j shows that k/j is a landing satellite connected to a GS
link_utilization_ratio = 100
isl_capacity = 20480  
uplink_capacity = downlink_capacity = 4096
bandwidth_isl = isl_capacity * link_utilization_ratio / 100
bandwidth_uplink = uplink_capacity * link_utilization_ratio / 100
bandwidth_downlink = uplink_capacity * link_utilization_ratio / 100
link_traffic = [
    0
] * sat_num * 4  # 4 links in total for a satellite, including 2 ISLs, one downlink, and one uplink
isl_traffic = [0] * sat_num  # egress traffic per satellite
downlink_traffic = [0] * sat_num  # downlink traffic per satellite
uplink_traffic = [0] * sat_num  # uplink traffic per satellite
sat_cover_pop = [0] * sat_num  # total user traffic accessed by a satellite
sat_cover_user = [[] for i in range(sat_num)
                  ]  
flows = [
]  # all the candidate flows. flow[k] = [src_sat, weight]
flows_selected = {
}  # legal background flows according to the probability. {(src_sat,sat):bandwidth,...}
flows_num = 0
flows_cumulate_weight = []
flows_sum_weight = 0


def cir_to_car_np(lat, lng, h):
    x = (RADIUS + h) * math.cos(math.radians(lat)) * math.cos(
        math.radians(lng))
    y = (RADIUS + h) * math.cos(math.radians(lat)) * math.sin(
        math.radians(lng))
    z = (RADIUS + h) * math.sin(math.radians(lat))
    return np.array([x, y, z])


def cycle_link_seq(sati, satj): 
    orbiti = int(sati / sat_of_orbit)
    orbitj = int(satj / sat_of_orbit)
    if orbiti == orbitj and (satj == sati + 1 or satj == sati -
                             (sat_of_orbit - 1)):
        return sati * 4
    elif orbiti == orbitj and (satj == sati - 1 or satj == sati +
                               (sat_of_orbit - 1)):
        return sati * 4 + 1
    else:
        return -1


def cycle_floyd(): # calculate the next hop from A to B
    global cycle_path
    global gsl_occurrence
    global sat_cover_user
    for orbit_id in range(num_of_orbit):
        for sat_id in range(sat_of_orbit):
            next_sat, sat_index = find_next_sat(
                orbit_id, sat_id, sat_of_orbit,
                sat_connect_gs)  # the nearest landing satellite (-1: no landing satellite)
            cycle_path[sat_index] = next_sat  # -1: no more landing satellite. Land from this satellite
    for orbit_id in range(num_of_orbit):
        for sat_id in range(sat_of_orbit):
            landing_sat = cycle_path[orbit_id * sat_of_orbit + sat_id]
            while landing_sat != cycle_path[landing_sat]:
                landing_sat = cycle_path[landing_sat]
            for item in sat_cover_user[orbit_id * sat_of_orbit + sat_id]:
                gsl_occurrence[landing_sat].append(item)


def find_next_sat(orbit_id, sat_id, sat_of_orbit,
                  sat_connect_gs):  # the the next satellite (-1: no landing satellite)
    next_sat = -1
    min_hops = int(sat_of_orbit / 2)
    sat_index = orbit_id * sat_of_orbit + sat_id
    for item in range(orbit_id * sat_of_orbit,
                      orbit_id * sat_of_orbit + sat_of_orbit):
        if sat_connect_gs[item] != -1:
            if abs(item - sat_index) <= sat_of_orbit / 2:
                hops = abs(item - sat_index)
                hops = int(hops)
                if hops <= min_hops:
                    min_hops = hops
                    if item == sat_index:
                        next_sat = sat_index
                    elif item > sat_index:
                        next_sat = sat_index + 1
                    else:
                        next_sat = sat_index - 1
            else:
                hops = sat_of_orbit - abs(item - sat_index)
                hops = int(hops)
                if hops <= min_hops:
                    min_hops = hops
                    if sat_index % sat_of_orbit == 0:
                        next_sat = sat_index + sat_of_orbit - 1
                    elif sat_index % sat_of_orbit == sat_of_orbit - 1:
                        next_sat = sat_index - (sat_of_orbit - 1)
                    elif item > sat_index:
                        next_sat = sat_index - 1
                    else:
                        next_sat = sat_index + 1
    return next_sat, sat_index


def init_cycle_flows():  # initiate flows and weights
    global flows
    global flows_sum_weight
    global flows_cumulate_weight
    global flows_num
    for block in range(inclination * 2 * 360):
        if pop_count[block] == 0:
            continue
        weight = math.ceil(pop_count[block]) 
        flows.append([block, weight])
        flows_sum_weight += weight
        flows_cumulate_weight.append(flows_sum_weight) # weight for each link
    flows_num = len(flows_cumulate_weight)


def get_one_flow(
        cumulate_weight, num,
        sum_weight):  # randomly choose one
    rand = random.randint(1, sum_weight)
    low = 0
    high = num - 1
    while low < high:
        mid = (low + high) >> 1
        if rand > cumulate_weight[mid]:
            low = mid + 1
        elif rand < cumulate_weight[mid]:
            high = mid
        else:
            return mid
    return low


def add_cycle_flow(src_block, rate=Flow_size): 
    global link_traffic
    # in_constraint = 0
    src_sat = user_connect_sat[src_block]
    # traverse all the paths to update link_traffic
    uplink = src_sat * 4 + 3
    # determine whether the constraints are met
    from_sat = src_sat
    if cycle_path[from_sat] == -1:
        return 0
    while True:
        to_sat = cycle_path[from_sat]
        if to_sat != from_sat:
            link_id_1 = cycle_link_seq(from_sat, to_sat)
            if link_id_1 == -1:
                print('error!')
                print(from_sat, to_sat)
                exit(0)
            link_traffic[link_id_1] += rate
            if link_id_1 % 4 == 0:
                isl_traffic[from_sat] += rate  # isl_traffic for dual-traffic 
            elif link_id_1 % 4 == 1:
                isl_traffic[to_sat] += rate  # isl_traffic for dual-traffic 
            from_sat = to_sat
        else:
            break
    downlink = from_sat * 4 + 2
    link_traffic[uplink] += rate
    link_traffic[downlink] += rate
    uplink_traffic[src_sat] += rate
    downlink_traffic[from_sat] += rate

    if downlink_traffic[from_sat] < downlink_capacity:
        # not enough traffic
        return 0
    else:  # minus extra traffic if overloaded
        src_sat = user_connect_sat[src_block]
        # traverse all the paths to update link_traffic
        uplink = src_sat * 4 + 3
        # determine whether the constraints are met
        from_sat = src_sat
        while True:
            to_sat = cycle_path[from_sat]
            if to_sat != from_sat:
                link_id_1 = cycle_link_seq(from_sat, to_sat)
                if link_id_1 == -1:
                    print('error!')
                    print(from_sat, to_sat)
                    exit(0)
                link_traffic[link_id_1] -= rate
                if link_id_1 % 4 == 0:
                    isl_traffic[from_sat] -= rate  # isl_traffic for dual-traffic 
                elif link_id_1 % 4 == 1:
                    isl_traffic[to_sat] -= rate  # isl_traffic for dual-traffic 
                from_sat = to_sat
            else:
                break
        downlink = from_sat * 4 + 2
        link_traffic[uplink] -= rate
        link_traffic[downlink] -= rate
        uplink_traffic[src_sat] -= rate
        downlink_traffic[from_sat] -= rate
        return -1


if __name__ == "__main__":
    bound = 3.743333 * 299792.458 * 0.001
    time_slot = sys.argv[1]

    # load satellite positions
    pos_filename = '../' + cons_name + '/sat_lla/%s.txt' % time_slot
    with open(pos_filename, 'r') as fr:
        lines = fr.readlines()
        for line in lines:
            satPos = line.split(',')
            sat_pos_car.append(
                cir_to_car_np(float(satPos[0]), float(satPos[1]),
                              float(satPos[2])))
        sat_pos_car = np.array(sat_pos_car)

    # load user positions
    for lat in range(inclination, -inclination, -1):  # [inclination, -inclination]
        for lon in range(-180, 180, 1):  # [-179.5, 179.5]
            user_pos_car.append(cir_to_car_np(lat - 0.5, lon + 0.5, 0))
    user_pos_car = np.array(user_pos_car)

    # load traffic distribution
    traffic_file = './starlink_count.txt'
    with open(traffic_file, 'r') as fr:
        lines = fr.readlines()
        for row in range(90 - 53, 90 + 53):
            pop_count.extend([float(x) for x in lines[row].split(' ')[:-1]] + [0])

    print("generating Circle traffic for timeslot: " + str(time_slot) + "...")  

    # the satellite each block is connected to
    for user_id in range(inclination * 2 * 360):
        # determining the satellite each user is connected to 
        dis2 = np.sqrt(
            np.sum(np.square(sat_pos_car - user_pos_car[user_id]),
                   axis=1))  
        if min(dis2) > bound:
            user_connect_sat.append(-1)  
            continue
        min_dis_sat = np.argmin(dis2)  
        user_connect_sat.append(
            min_dis_sat)  
        sat_cover_pop[min_dis_sat] += pop_count[user_id] 
        sat_cover_user[min_dis_sat].append(user_id)  

    # load GS positions
    f = open("./GS.json", "r", encoding='utf8')
    GS_info = json.load(f)
    count = 0
    for key in GS_info:
        GS_pos_car.append(
            cir_to_car_np(float(GS_info[key]['lat']),
                          float(GS_info[key]['lng']), 0))
        count = count + 1
    GS_pos_car = np.array(GS_pos_car)

    # the GS a satellite is connected to
    for sat_id in range(sat_num):
        dis2 = np.sqrt(
            np.sum(np.square(GS_pos_car - sat_pos_car[sat_id]),
                   axis=1))  
        if min(dis2) > bound:
            sat_connect_gs.append(-1)  # -1 for no connection
            continue
        min_dis_sat = np.argmin(dis2) 
        sat_connect_gs.append(min_dis_sat)  

    # initiate topology and routing
    cycle_floyd() 

    # initiate traffic flows and weights
    init_cycle_flows() 

    for add_flow_times in range(2000000):  # randomly choose 2000000 flows
        flow_id = get_one_flow(flows_cumulate_weight, flows_num,
                               flows_sum_weight)
        res = add_cycle_flow(flows[flow_id][0])
        if res == -1:
            continue
        # add a new flow
        flow_pair = (flows[flow_id][0], flows[flow_id][1])
        if flow_pair in flows_selected:
            flows_selected[flow_pair] += Flow_size  
        else:
            flows_selected[flow_pair] = Flow_size

    # outputs: ISL, GSL down/uplink, block connecstions, satellite connections and so on
    os.system("mkdir -p ../" + cons_name + "/circle_data/link_traffic_data/" +
              str(time_slot))
    isl_traffic = np.array(isl_traffic, dtype=int)
    np.savetxt('../' + cons_name + '/circle_data/link_traffic_data/' + str(time_slot) +
               '/isl_traffic.txt',
               isl_traffic,
               fmt='%d')
    downlink_traffic = np.array(downlink_traffic, dtype=int)
    np.savetxt('../' + cons_name + '/circle_data/link_traffic_data/' + str(time_slot) +
               '/downlink_traffic.txt',
               downlink_traffic,
               fmt='%d')
    uplink_traffic = np.array(uplink_traffic, dtype=int)
    np.savetxt('../' + cons_name + '/circle_data/link_traffic_data/' + str(time_slot) +
               '/uplink_traffic.txt',
               uplink_traffic,
               fmt='%d')
    sat_connect_gs = np.array(sat_connect_gs, dtype=int)
    np.savetxt('../' + cons_name + '/circle_data/link_traffic_data/' + str(time_slot) +
               '/sat_connect_gs.txt',
               sat_connect_gs,
               fmt='%d')
    user_connect_sat = np.array(user_connect_sat, dtype=int)
    np.savetxt('../' + cons_name + '/circle_data/link_traffic_data/' + str(time_slot) +
               '/user_connect_sat.txt',
               user_connect_sat,
               fmt='%d')
    id = 0
    gs_occurrence_num = [0 for i in range(len(GS_pos_car))]
    for item in gsl_occurrence:
        gsl_occurrence_num[id] = len(item) if len(item) > 0 else -1
        if sat_connect_gs[id] != -1:
            gs_occurrence_num[sat_connect_gs[id]] += gsl_occurrence_num[id]
        id +=1
    gsl_occurrence_num = np.array(gsl_occurrence_num, dtype=int)
    np.savetxt('../' + cons_name + '/circle_data/link_traffic_data/' + str(time_slot) +
               '/gsl_occurrence_num.txt',
               gsl_occurrence_num,
               fmt='%d')
    gs_occurrence_num = np.array(gs_occurrence_num, dtype=int)
    np.savetxt('../' + cons_name + '/circle_data/link_traffic_data/' + str(time_slot) +
               '/gs_occurrence_num.txt',
               gs_occurrence_num,
               fmt='%d')