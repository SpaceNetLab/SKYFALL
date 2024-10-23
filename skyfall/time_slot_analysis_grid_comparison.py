#!/usr/bin/python
# -*- coding: UTF-8 -*-

# In this code, we analyze the risks and the variabilities, as described in the Analysis Stage (Section IV.C)
# Specifically, the comparison under the +Grid Structure is analyzed in this code.

import numpy as np
import math
import os
import sys
import json
import random

f = open("../config.json", "r", encoding='utf8')
table = json.load(f)
cons_name = table["Name"]
altitude = int(table["Altitude (km)"])
orbit_num = table["# of orbit"]
sat_per_cycle = table["# of satellites"]
inclination = table["Inclination"] 

bot_num = 0  # total number of malicious terminals
traffic_thre = 20  # upmost 20 malicious terminals accessed to a satellite
GSL_capacity = 4096
unit_traffic = 20  # 20Mbps per malicious terminal
vital_gs = []  
block_num = 0
pop_count = []  # 53 ~ -53, traffic probability per block
weights = []  # weights for each block
flows_selected = {}  # legal background flows according to the probability. {(src_sat,dst,sat):bandwidth,...} 。环状为{(src_sat,sat):bandwidth,...}
weights_num = 0
cumulate_weight = []
sum_weight = 0
attack_gsl = [] # attacked GSLs
chosen_blocks = [] # blocks for deploying bots
cumu_affected_traffic_volume = 0  
cumu_downlink_malicious_traffic = [0 for i in range(orbit_num * sat_per_cycle)]
path = [[-1 for i in range(orbit_num * sat_per_cycle)]
        for j in range(orbit_num * sat_per_cycle)]  # path[i][j] = k: k is the next hop from i to j; k == j shows that k/j is a landing satellite connected to a GS
given_bot_number = 950

def init_weight():  # initiate weights for each block
    global weights
    global sum_weight
    global cumulate_weight
    global weights_num
    for block in range(inclination * 2 * 360):
        if pop_count[block] == 0:
            continue
        weight = math.ceil(pop_count[block]) 
        weights.append([block, weight])
        sum_weight += weight
        cumulate_weight.append(sum_weight) 
    weights_num = len(cumulate_weight)
    
def get_one_block(
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

def find_next_sat(orbit_id, sat_id, sat_per_cycle,
                  sat_connect_gs):  # the the next satellite (-1: no landing satellite)
    next_sat = -1
    min_hops = int(sat_per_cycle / 2) + int(orbit_num / 2)
    sat_index = orbit_id * sat_per_cycle + sat_id
    if sat_connect_gs[sat_index] != -1:
        return sat_index, sat_index
    for item in range(orbit_num * sat_per_cycle):
        if sat_connect_gs[item] != -1:
            item_orbit = int(item / sat_per_cycle)
            item_sat = item % sat_per_cycle
            orbit_diff = abs(item_orbit -
                             orbit_id) if abs(item_orbit - orbit_id) <= int(
                                 orbit_num /
                                 2) else orbit_num - abs(item_orbit -
                                                            orbit_id)
            sat_diff = abs(item_sat - sat_id) if abs(item_sat - sat_id) <= int(
                sat_per_cycle / 2) else sat_per_cycle - abs(item_sat - sat_id)
            if (sat_diff + orbit_diff) >= min_hops:
                continue

            min_hops = (sat_diff + orbit_diff)
            if item_orbit == orbit_id:  # same orbit
                if item_sat > sat_id:
                    if (item_sat - sat_id) <= (sat_per_cycle -
                                               (item_sat - sat_id)):
                        next_sat = sat_index + 1
                    elif sat_id == 0:
                        next_sat = sat_index + sat_per_cycle - 1
                    else:
                        next_sat = sat_index - 1
                else:
                    if (sat_id - item_sat) <= (sat_per_cycle -
                                               (sat_id - item_sat)):
                        next_sat = sat_index - 1
                    elif sat_id == sat_per_cycle - 1:
                        next_sat = sat_index - sat_per_cycle + 1
                    else:
                        next_sat = sat_index + 1
            else:  # not same orbit
                if item_orbit > orbit_id:
                    if (item_orbit - orbit_id) <= (orbit_num -
                                                   (item_orbit - orbit_id)):
                        next_sat = sat_index + sat_per_cycle
                    elif orbit_id == 0:
                        next_sat = sat_index + sat_per_cycle * (orbit_num -
                                                               1)
                    else:
                        next_sat = sat_index - sat_per_cycle
                else:
                    if (orbit_id - item_orbit) <= (orbit_num -
                                                   (orbit_id - item_orbit)):
                        next_sat = sat_index - sat_per_cycle
                    elif orbit_id == orbit_num - 1:
                        next_sat = sat_index - sat_per_cycle * (orbit_num -
                                                               1)
                    else:
                        next_sat = sat_index + sat_per_cycle

    return next_sat, sat_index

def floyd():
    global path
    path =[-1 for i in range(orbit_num * sat_per_cycle)]
    for orbit_id in range(orbit_num):
        for sat_id in range(sat_per_cycle):
            next_sat, sat_index = find_next_sat(
                orbit_id, sat_id, sat_per_cycle,
                sat_connect_gs)  # the nearest landing satellite (-1: no landing satellite)
            path[sat_index] = next_sat  # -1: no more landing satellite. Land from this satellite
            
def add_bot(block_id, user_connect_sat, traffic, sat_connect_gs, ratio):
    global cumu_affected_traffic_volume
    global cumu_downlink_malicious_traffic
    global attack_gsl

    landing_sat = path[user_connect_sat[block_id]]
    while landing_sat != path[landing_sat]:
        landing_sat = path[landing_sat]
    landing_gs = sat_connect_gs[landing_sat]
    if landing_gs != -1 and landing_sat != -1:
        if cumu_downlink_malicious_traffic[landing_sat] + traffic[landing_sat] + unit_traffic > GSL_capacity and cumu_downlink_malicious_traffic[landing_sat] + traffic[landing_sat] <= GSL_capacity:
            attack_gsl.append(landing_sat)
        if cumu_downlink_malicious_traffic[landing_sat] + traffic[landing_sat] + unit_traffic > GSL_capacity / ratio and cumu_downlink_malicious_traffic[landing_sat] + traffic[landing_sat] <= GSL_capacity / ratio:
            cumu_affected_traffic_volume += traffic[landing_sat]
        cumu_downlink_malicious_traffic[landing_sat] += unit_traffic    
    return


if __name__ == "__main__":
    time_slot = sys.argv[1]
    ratio = float(sys.argv[2])  # throughput degradation
    overlapping_gs = np.loadtxt('../' + cons_name + '/+grid_data/link_traffic_data/' + str(time_slot) + '/vital_gs.txt')
    vital_gs = list(map(int, overlapping_gs))
    traffic_filename = '../' + cons_name + '/+grid_data/link_traffic_data/' + time_slot + '/' + 'downlink_traffic.txt'
    traffic = np.loadtxt('../' + cons_name + '/+grid_data/link_traffic_data/' +
                         time_slot + '/' + 'downlink_traffic.txt')
    traffic = list(map(int, traffic))
    traffic_filename = '../' + cons_name + '/+grid_data/link_traffic_data/' + time_slot + '/' + 'uplink_traffic.txt'
    uplink_traffic = np.loadtxt('../' + cons_name + '/+grid_data/link_traffic_data/' + time_slot + '/' +
                                'uplink_traffic.txt')
    uplink_traffic = list(map(int, uplink_traffic))
    sat_connect_gs = np.loadtxt('../' + cons_name + '/+grid_data/link_traffic_data/' + time_slot + '/' +
                                'sat_connect_gs.txt')
    user_connect_sat = np.loadtxt('../' + cons_name + '/+grid_data/link_traffic_data/' + time_slot +
                                  '/' + 'user_connect_sat.txt')
    user_connect_sat = list(map(int, user_connect_sat))
    target_affected_traffic_volume = np.loadtxt('../' + cons_name + '/+grid_data/attack_traffic_data_land_only_bot/' + str(ratio) + "-" +
               str(traffic_thre) + "-" + str(sat_per_cycle) + "-" +
               str(GSL_capacity) + "-" + str(unit_traffic) + '/' + time_slot +
                '/cumu_affected_traffic_volume.txt')
    target_affected_traffic = int(target_affected_traffic_volume)

    traffic_sum = np.sum(traffic)

    # load traffic distribution
    traffic_file = './starlink_count.txt'
    with open(traffic_file, 'r') as fr:
        lines = fr.readlines()
        for row in range(90 - inclination, 90 + inclination):
            pop_count.extend([float(x) for x in lines[row].split(' ')[:-1]] + [0])

    init_weight()
    
    # initiate topology and routing
    floyd()
    
    os.system('mkdir -p ../' + cons_name + '/+grid_data/attack_traffic_data_land_only_bot/' + str(ratio) + "-" +
              str(traffic_thre) + "-" + str(sat_per_cycle) + "-" +
              str(GSL_capacity) + "-" + str(unit_traffic) + '-comparison/' + time_slot)
    
    # deploy bots according to traffic weights of each block
    while True:
        chosen_id = get_one_block(cumulate_weight, weights_num,
                               sum_weight)
        block_id = weights[chosen_id][0]
        bot_num += 0.1
        if block_id not in chosen_blocks:
            block_num += 0.1
            chosen_blocks.append(block_id)
        add_bot(block_id, user_connect_sat, traffic, sat_connect_gs, ratio)
        if cumu_affected_traffic_volume >= target_affected_traffic:
            break
        elif int(bot_num) == given_bot_number:
            attack_gsl_950 = np.array(attack_gsl, dtype=int)
            np.savetxt('../' + cons_name + '/+grid_data/attack_traffic_data_land_only_bot/' + str(ratio) + "-" +
                    str(traffic_thre) + "-" + str(sat_per_cycle) + "-" +
                    str(GSL_capacity) + "-" + str(unit_traffic) + '-comparison/' + time_slot +
                    '/attack_gsl_950.txt',
                attack_gsl_950,
                fmt='%d')
            cumu_affected_traffic_volume_950 = np.array([cumu_affected_traffic_volume],
                                                    dtype=int)
            np.savetxt('../' + cons_name + '/+grid_data/attack_traffic_data_land_only_bot/' + str(ratio) + "-" +
                    str(traffic_thre) + "-" + str(sat_per_cycle) + "-" +
                    str(GSL_capacity) + "-" + str(unit_traffic) + '-comparison/' + time_slot +
                    '/cumu_affected_traffic_volume_950.txt',
                cumu_affected_traffic_volume_950,
                fmt='%d')
            
    attack_gsl = np.array(attack_gsl, dtype=int)
    np.savetxt('../' + cons_name + '/+grid_data/attack_traffic_data_land_only_bot/' + str(ratio) + "-" +
               str(traffic_thre) + "-" + str(sat_per_cycle) + "-" +
               str(GSL_capacity) + "-" + str(unit_traffic) + '-comparison/' + time_slot +
               '/attack_gsl.txt',
        attack_gsl,
        fmt='%d')
    bot_num = np.array([bot_num], dtype=int)
    np.savetxt('../' + cons_name + '/+grid_data/attack_traffic_data_land_only_bot/' + str(ratio) + "-" +
               str(traffic_thre) + "-" + str(sat_per_cycle) + "-" +
               str(GSL_capacity) + "-" + str(unit_traffic) + '-comparison/' + time_slot +
               '/bot_num.txt',
        bot_num,
        fmt='%d')
    block_num = np.array([block_num], dtype=int)
    np.savetxt('../' + cons_name + '/+grid_data/attack_traffic_data_land_only_bot/' + str(ratio) + "-" +
               str(traffic_thre) + "-" + str(sat_per_cycle) + "-" +
               str(GSL_capacity) + "-" + str(unit_traffic) + '-comparison/' + time_slot +
               '/block_num.txt',
        block_num,
        fmt='%d')
    cumu_affected_traffic_volume = np.array([cumu_affected_traffic_volume],
                                            dtype=int)
    np.savetxt('../' + cons_name + '/+grid_data/attack_traffic_data_land_only_bot/' + str(ratio) + "-" +
               str(traffic_thre) + "-" + str(sat_per_cycle) + "-" +
               str(GSL_capacity) + "-" + str(unit_traffic) + '-comparison/' + time_slot +
               '/cumu_affected_traffic_volume.txt',
        cumu_affected_traffic_volume,
        fmt='%d')

    print("Finished calculating comparison's malicious terminals deployment and generating malicious traffic for +Grid at timeslot", time_slot)
