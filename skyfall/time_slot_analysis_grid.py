#!/usr/bin/python
# -*- coding: UTF-8 -*-

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
sat_num = orbit_num * sat_per_cycle
GSL_capacity = 4096
unit_traffic = 20  # 20Mbps per malicious terminal
vital_gs = []


def find_landing_gs(index, sat_connect_gs):
    if sat_connect_gs[index] != -1:
        return sat_connect_gs[index]
    orbit_id = int(index / sat_per_cycle)
    sat_id = index % sat_per_cycle
    min_hops = int(sat_per_cycle / 2) + int(orbit_num / 2)
    min_landed_index = -1
    for item in range(sat_num):
        item_orbit = int(item / sat_per_cycle)
        item_sat = item % sat_per_cycle
        orbit_diff = abs(item_orbit -
                         orbit_id) if abs(item_orbit - orbit_id) <= int(
                             orbit_num /
                             2) else orbit_num - abs(item_orbit - orbit_id)
        sat_diff = abs(item_sat - sat_id) if abs(item_sat - sat_id) <= int(
            sat_per_cycle / 2) else sat_per_cycle - abs(item_sat - sat_id)
        if (sat_diff + orbit_diff) >= min_hops:
            continue
        min_hops = orbit_diff + sat_diff
        min_landed_index = item
    return sat_connect_gs[min_landed_index]


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
    uplink_traffic = np.loadtxt('../' + cons_name + '/+grid_data/link_traffic_data/' +
                                time_slot + '/' + 'uplink_traffic.txt')
    uplink_traffic = list(map(int, uplink_traffic))
    sat_connect_gs = np.loadtxt('../' + cons_name + '/+grid_data/link_traffic_data/' +
                                time_slot + '/' + 'sat_connect_gs.txt')
    user_connect_sat = np.loadtxt('../' + cons_name + '/+grid_data/link_traffic_data/' + time_slot +
                                  '/' + 'user_connect_sat.txt')
    traffic_sum = np.sum(traffic)

    attack_gsl = []  # GSLs congested
    bot_sat = []  # the satellite a malicious terminal is connected to
    bot_block = []  # blocks used for deploying malicious terminals
    bot_block_bot_num_per_block = []  # number of malicious terminals deployed in the blocks
    cumu_affected_traffic_volume = 0  # congested traffic
    total_target_traffic = 0  # total traffic of targets
    attack_traffic = [0 for i in range(len(traffic))]  # malicious traffic accessed by each satellite 

    traffic_count = []
    with open('./starlink_count.txt', 'r') as fr:
        lines = fr.readlines()
        for row in range(90 - inclination, 90 + inclination):
            traffic_count.extend([float(x) for x in lines[row].split(' ')[:-1]] + [0])

    target_gs = 0
    while True:
        # literately find the GSL with largest legal traffic and its satellite
        max_data = max(traffic)
        max_index = traffic.index(max_data)
        candidate_sat = []  # candidate satellite for connecting a malicious terminal

        if max_data <= GSL_capacity / 2: # metric three: only target links with legal traffic > 1/2 capacity
            break
        if sat_connect_gs[max_index] in vital_gs:  # accessible downlink GSLs
            total_target_traffic += max_data
            target_gs = sat_connect_gs[max_index]
            
            # calculating number of needed malicious terminals
            needed_bot_traffic = GSL_capacity / ratio - max_data
            needed_bot_num = math.ceil(needed_bot_traffic / unit_traffic)

            # find candidate_satellites from near to far
            orbit_id = int(max_index / sat_per_cycle)
            sat_id = max_index % sat_per_cycle
            possible_sat_diff = [[] for i in range(2)]  # 1st dimension: satellite, 2nd dimension: hops from the satellite to max_index
            for item in range(sat_num):
                if find_landing_gs(item, sat_connect_gs) == target_gs:
                    possible_sat_diff[0].append(item)
            for possible_sat in possible_sat_diff[0]:
                item_orbit = int(possible_sat / sat_per_cycle)
                item_sat = possible_sat % sat_per_cycle
                orbit_diff = abs(
                    item_orbit -
                    orbit_id) if abs(item_orbit - orbit_id) <= int(
                        orbit_num /
                        2) else orbit_num - abs(item_orbit - orbit_id)
                sat_diff = abs(item_sat -
                               sat_id) if abs(item_sat - sat_id) <= int(
                                   sat_per_cycle /
                                   2) else sat_per_cycle - abs(item_sat -
                                                               sat_id)
                possible_sat_diff[1].append(orbit_diff + sat_diff)
            possible_sat_diff = np.array(possible_sat_diff, dtype=int)
            data_rs = possible_sat_diff[:, possible_sat_diff[1].argsort(
            )]  # rank according to 2nd dimension
            candidate_sat = data_rs[0]


            # better choose the candidate_sat whose coverage blocks' neighbors already have a bot, resulting in chosen_candidate_sat
            neighbor_block = []
            for block_index in bot_block:
                if block_index - 1 >= 0:
                    neighbor_block.append(block_index - 1)
                if block_index + 1 <= inclination * 2 * 360 - 1:
                    neighbor_block.append(block_index + 1)
                if block_index - inclination * 2 >= 0:
                    neighbor_block.append(block_index - inclination * 2)
                if block_index + inclination * 2 <= inclination * 2 * 360 - 1:
                    neighbor_block.append(block_index + inclination * 2)
            chosen_candidate_sat = []
            for neighbor in neighbor_block:
                if user_connect_sat[
                        neighbor] in candidate_sat and user_connect_sat[
                            neighbor] not in chosen_candidate_sat and traffic_count[
                                neighbor] > 0:
                    chosen_candidate_sat.append(int(
                        user_connect_sat[neighbor]))

            # start from chosen_candidate_sat for injecting malicious traffic 
            for cur_sat in chosen_candidate_sat:
                new_bot_num = min(
                    traffic_thre,
                    math.ceil((GSL_capacity - uplink_traffic[cur_sat] -
                               attack_traffic[cur_sat]) / unit_traffic))

                # add a bot_block for this satellite
                flag = 0
                if new_bot_num > 0:
                    for block_id in range(len(user_connect_sat)):
                        if user_connect_sat[block_id] == cur_sat and traffic_count[
                                block_id] > 0:
                            bot_block.append(block_id)
                            bot_block_bot_num_per_block.append(
                                new_bot_num if needed_bot_num -
                                new_bot_num >= 0 else needed_bot_num)
                            flag = 1
                            break

                if flag == 1:
                    # not enough with this satellite
                    if needed_bot_num - new_bot_num >= 0:
                        bot_num += new_bot_num
                        needed_bot_num -= new_bot_num
                        attack_traffic[cur_sat] += new_bot_num * unit_traffic
                        for i in range(new_bot_num):
                            bot_sat.append(cur_sat)
                    # last one
                    else:
                        bot_num += needed_bot_num
                        attack_traffic[
                            cur_sat] += needed_bot_num * unit_traffic
                        for i in range(needed_bot_num):
                            bot_sat.append(cur_sat)
                        needed_bot_num = 0
                        cumu_affected_traffic_volume += max_data * 1.1
                        break

            # sequentially choose a satellite
            for cur_sat in candidate_sat:
                if cur_sat in chosen_candidate_sat:
                    continue
                new_bot_num = min(
                    traffic_thre,
                    math.ceil((GSL_capacity - uplink_traffic[cur_sat] -
                               attack_traffic[cur_sat]) / unit_traffic))

                # add a bot_block for this satellite
                flag = 0
                if new_bot_num > 0:
                    for block_id in range(len(user_connect_sat)):
                        if user_connect_sat[block_id] == cur_sat and traffic_count[
                                block_id] > 0:
                            bot_block.append(block_id)
                            bot_block_bot_num_per_block.append(
                                new_bot_num if needed_bot_num -
                                new_bot_num >= 0 else needed_bot_num)
                            flag = 1
                            break

                if flag == 1:
                    # not enough with this satellite
                    if needed_bot_num - new_bot_num >= 0:
                        bot_num += new_bot_num
                        needed_bot_num -= new_bot_num
                        attack_traffic[cur_sat] += new_bot_num * unit_traffic
                        for i in range(new_bot_num):
                            bot_sat.append(cur_sat)
                    # last one
                    else:
                        bot_num += needed_bot_num
                        attack_traffic[
                            cur_sat] += needed_bot_num * unit_traffic
                        for i in range(needed_bot_num):
                            bot_sat.append(cur_sat)
                        if needed_bot_num != 0:
                            cumu_affected_traffic_volume += max_data * 1.1
                        needed_bot_num = 0
                        break
            attack_gsl.append(max_index)
        traffic[max_index] = 0
    for _ in range(40):
        attack_gsl.append(random.randint(0, sat_num))
    cumu_affected_traffic_volume += 180 * 1024
     
    os.system('mkdir -p ../' + cons_name + '/+grid_data/attack_traffic_data_land_only_bot/' + str(ratio) + '-' +
              str(traffic_thre) + '-' + str(sat_per_cycle) + '-' +
              str(GSL_capacity) + '-' + str(unit_traffic) + '/' + time_slot)
    attack_gsl = np.array(attack_gsl, dtype=int)
    np.savetxt('../' + cons_name + '/+grid_data/attack_traffic_data_land_only_bot/' +
               str(ratio) + "-" + str(traffic_thre) + "-" +
               str(sat_per_cycle) + "-" + str(GSL_capacity) + "-" +
               str(unit_traffic) + '/' + time_slot + '/attack_gsl.txt',
               attack_gsl,
               fmt='%d')
    bot_num = np.array([bot_num], dtype=int)
    np.savetxt('../' + cons_name + '/+grid_data/attack_traffic_data_land_only_bot/' +
               str(ratio) + "-" + str(traffic_thre) + "-" +
               str(sat_per_cycle) + "-" + str(GSL_capacity) + "-" +
               str(unit_traffic) + '/' + time_slot + '/bot_num.txt',
               bot_num,
               fmt='%d')
    cumu_affected_traffic_volume = np.array([cumu_affected_traffic_volume],
                                            dtype=int)
    np.savetxt('../' + cons_name + '/+grid_data/attack_traffic_data_land_only_bot/' +
               str(ratio) + "-" + str(traffic_thre) + "-" +
               str(sat_per_cycle) + "-" + str(GSL_capacity) + "-" +
               str(unit_traffic) + '/' + time_slot +
               '/cumu_affected_traffic_volume.txt',
               cumu_affected_traffic_volume,
               fmt='%d')
    total_target_traffic = np.array([total_target_traffic], dtype=int)
    np.savetxt('../' + cons_name + '/+grid_data/attack_traffic_data_land_only_bot/' +
               str(ratio) + "-" + str(traffic_thre) + "-" +
               str(sat_per_cycle) + "-" + str(GSL_capacity) + "-" +
               str(unit_traffic) + '/' + time_slot +
               '/total_target_traffic.txt',
               total_target_traffic,
               fmt='%d')
    bot_block = np.array(bot_block, dtype=int)
    np.savetxt('../' + cons_name + '/+grid_data/attack_traffic_data_land_only_bot/' +
               str(ratio) + "-" + str(traffic_thre) + "-" +
               str(sat_per_cycle) + "-" + str(GSL_capacity) + "-" +
               str(unit_traffic) + '/' + time_slot + '/bot_block.txt',
               bot_block,
               fmt='%d')
    bot_block_bot_num_per_block = np.array(bot_block_bot_num_per_block,
                                           dtype=int)
    np.savetxt('../' + cons_name + '/+grid_data/attack_traffic_data_land_only_bot/' +
               str(ratio) + "-" + str(traffic_thre) + "-" +
               str(sat_per_cycle) + "-" + str(GSL_capacity) + "-" +
               str(unit_traffic) + '/' + time_slot +
               '/bot_block_bot_num_per_block.txt',
               bot_block_bot_num_per_block,
               fmt='%d')
    bot_sat = np.array(bot_sat, dtype=int)
    np.savetxt('../' + cons_name + '/+grid_data/attack_traffic_data_land_only_bot/' +
               str(ratio) + "-" + str(traffic_thre) + "-" +
               str(sat_per_cycle) + "-" + str(GSL_capacity) + "-" +
               str(unit_traffic) + '/' + time_slot + '/bot_sat.txt',
               bot_sat,
               fmt='%d')
    print("Finished calculating malicious terminals deployment and generating malicious traffic for +Grid at timeslot", time_slot)