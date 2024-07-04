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


def find_cycle(index):
    orbit_num = int(index / sat_per_cycle)
    return orbit_num * sat_per_cycle, (orbit_num + 1) * sat_per_cycle - 1


def find_landing_gs(index, sat_connect_gs, start_sat, end_sat):
    if sat_connect_gs[index] != -1:
        return sat_connect_gs[index]
    for diff_index in range(1, sat_per_cycle):
        if (index + diff_index
            ) <= end_sat and sat_connect_gs[index + diff_index] != -1:
            return sat_connect_gs[index + diff_index]
        if (index - diff_index
            ) >= start_sat and sat_connect_gs[index - diff_index] != -1:
            return sat_connect_gs[index - diff_index]
    return -1


if __name__ == "__main__":
    time_slot = sys.argv[1]
    ratio = float(sys.argv[2])  # throughput degradation
    overlapping_gs = np.loadtxt('../' + cons_name + '/circle_data/link_traffic_data/' + str(time_slot) + '/vital_gs.txt')
    vital_gs = list(map(int, overlapping_gs))
    traffic_filename = '../' + cons_name + '/circle_data/link_traffic_data/' + time_slot + '/' + 'downlink_traffic.txt'
    traffic = np.loadtxt('../' + cons_name + '/circle_data/link_traffic_data/' +
                         time_slot + '/' + 'downlink_traffic.txt')
    traffic = list(map(int, traffic))
    traffic_filename = '../' + cons_name + '/circle_data/link_traffic_data/' + time_slot + '/' + 'uplink_traffic.txt'
    uplink_traffic = np.loadtxt('../' + cons_name + '/circle_data/link_traffic_data/' + time_slot + '/' +
                                'uplink_traffic.txt')
    uplink_traffic = list(map(int, uplink_traffic))
    sat_connect_gs = np.loadtxt('../' + cons_name + '/circle_data/link_traffic_data/' + time_slot + '/' +
                                'sat_connect_gs.txt')
    user_connect_sat = np.loadtxt('../' + cons_name + '/circle_data/link_traffic_data/' + time_slot +
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

        if max_data <= GSL_capacity / 2:  # metric three: only target links with legal traffic > 1/2 capacity
            break
        if sat_connect_gs[max_index] in vital_gs:  # accessible downlink GSLs
            total_target_traffic += max_data
            target_gs = sat_connect_gs[max_index]
            start_sat, end_sat = find_cycle(max_index)  #找到该卫星所在环的所有卫星的索引最小、最大值

            # calculating number of needed malicious terminals
            needed_bot_traffic = GSL_capacity / ratio - max_data
            needed_bot_num = math.ceil(needed_bot_traffic / unit_traffic)

            # find candidate_satellites from near to far
            candidate_sat.append(max_index)
            for diff_index in range(1, sat_per_cycle):
                if (max_index + diff_index) <= end_sat and find_landing_gs(
                        max_index + diff_index, sat_connect_gs, start_sat,
                        end_sat) == target_gs:
                    candidate_sat.append(max_index + diff_index)
                if (max_index - diff_index) >= start_sat and find_landing_gs(
                        max_index - diff_index, sat_connect_gs, start_sat,
                        end_sat) == target_gs:
                    candidate_sat.append(max_index - diff_index)

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

    os.system('mkdir -p ../' + cons_name + '/circle_data/attack_traffic_data_land_only_bot/' + str(ratio) + "-" +
              str(traffic_thre) + "-" + str(sat_per_cycle) + "-" +
              str(GSL_capacity) + "-" + str(unit_traffic) + '/' + time_slot)
    attack_gsl = np.array(attack_gsl, dtype=int)
    np.savetxt('../' + cons_name + '/circle_data/attack_traffic_data_land_only_bot/' + str(ratio) + "-" +
               str(traffic_thre) + "-" + str(sat_per_cycle) + "-" +
               str(GSL_capacity) + "-" + str(unit_traffic) + '/' + time_slot +
               '/attack_gsl.txt',
               attack_gsl,
               fmt='%d')
    bot_num = np.array([bot_num], dtype=int)
    np.savetxt('../' + cons_name + '/circle_data/attack_traffic_data_land_only_bot/' + str(ratio) + "-" +
               str(traffic_thre) + "-" + str(sat_per_cycle) + "-" +
               str(GSL_capacity) + "-" + str(unit_traffic) + '/' + time_slot +
               '/bot_num.txt',
               bot_num,
               fmt='%d')
    cumu_affected_traffic_volume = np.array([cumu_affected_traffic_volume],
                                            dtype=int)
    np.savetxt('../' + cons_name + '/circle_data/attack_traffic_data_land_only_bot/' + str(ratio) + "-" +
               str(traffic_thre) + "-" + str(sat_per_cycle) + "-" +
               str(GSL_capacity) + "-" + str(unit_traffic) + '/' + time_slot +
               '/cumu_affected_traffic_volume.txt',
               cumu_affected_traffic_volume,
               fmt='%d')
    total_target_traffic = np.array([total_target_traffic], dtype=int)
    np.savetxt('../' + cons_name + '/circle_data/attack_traffic_data_land_only_bot/' + str(ratio) + "-" +
               str(traffic_thre) + "-" + str(sat_per_cycle) + "-" +
               str(GSL_capacity) + "-" + str(unit_traffic) + '/' + time_slot +
               '/total_target_traffic.txt',
               total_target_traffic,
               fmt='%d')
    bot_block = np.array(bot_block, dtype=int)
    np.savetxt('../' + cons_name + '/circle_data/attack_traffic_data_land_only_bot/' + str(ratio) + "-" +
               str(traffic_thre) + "-" + str(sat_per_cycle) + "-" +
               str(GSL_capacity) + "-" + str(unit_traffic) + '/' + time_slot +
               '/bot_block.txt',
               bot_block,
               fmt='%d')
    bot_block_bot_num_per_block = np.array(bot_block_bot_num_per_block,
                                           dtype=int)
    np.savetxt('../' + cons_name + '/circle_data/attack_traffic_data_land_only_bot/' + str(ratio) + "-" +
               str(traffic_thre) + "-" + str(sat_per_cycle) + "-" +
               str(GSL_capacity) + "-" + str(unit_traffic) + '/' + time_slot +
               '/bot_block_bot_num_per_block.txt',
               bot_block_bot_num_per_block,
               fmt='%d')
    bot_sat = np.array(bot_sat, dtype=int)
    np.savetxt('../' + cons_name + '/circle_data/attack_traffic_data_land_only_bot/' + str(ratio) + "-" +
               str(traffic_thre) + "-" + str(sat_per_cycle) + "-" +
               str(GSL_capacity) + "-" + str(unit_traffic) + '/' + time_slot +
               '/bot_sat.txt',
               bot_sat,
               fmt='%d')
    print("Finished calculating malicious terminals deployment and generating malicious traffic for Circle at timeslot", time_slot)
