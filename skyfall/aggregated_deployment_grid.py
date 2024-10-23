#!/usr/bin/python
# -*- coding: UTF-8 -*-

# In this code, we assume the malicious terminals are positioned in certain regions
# as described in Section IV.A

import numpy as np
import math
import json
import sys

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
unit_traffic = 20   # 20Mbps per malicious terminal
RADIUS = 6371

def cir_to_car_np(lat, lng, h=0):
    x = (RADIUS + h) * math.cos(math.radians(lat)) * math.cos(
        math.radians(lng))
    y = (RADIUS + h) * math.cos(math.radians(lat)) * math.sin(
        math.radians(lng))
    z = (RADIUS + h) * math.sin(math.radians(lat))
    return np.array([x, y, z])


def block_to_xy(block_id):
    latitude = -53 + math.floor(block_id / 360)
    longitude = -180 + block_id % 360
    return latitude, longitude


if __name__ == "__main__":
    total_time = int(sys.argv[1]) 
    ratio = float(sys.argv[2])  # throughput degradation
    overall_block = np.zeros(inclination * 2 * 360, dtype=float)
    user_connect_sat = np.loadtxt('../' + cons_name + '/+grid_data/link_traffic_data/0/user_connect_sat.txt')
    print("Starting aggregating for +Grid...")
    for time_slot in range(total_time):
        bot_block_bot_num_per_block = np.loadtxt('../' + cons_name + '/+grid_data/attack_traffic_data_land_only_bot/' + str(ratio) + "-" +
               str(traffic_thre) + "-" + str(sat_per_cycle) + "-" +
               str(GSL_capacity) + "-" + str(unit_traffic) + '/' + str(time_slot) + '/bot_block_bot_num_per_block.txt')
        bot_block_bot_num_per_block = np.array(bot_block_bot_num_per_block)
        if bot_block_bot_num_per_block.ndim == 0:
            bot_block_bot_num_per_block = np.array([bot_block_bot_num_per_block])
        bot_block = np.loadtxt('../' + cons_name + '/+grid_data/attack_traffic_data_land_only_bot/' + str(ratio) + "-" +
               str(traffic_thre) + "-" + str(sat_per_cycle) + "-" +
               str(GSL_capacity) + "-" + str(unit_traffic) + '/' + str(time_slot) +
                               '/bot_block.txt')
        bot_block = np.array(bot_block)
        if bot_block.ndim == 0:
            bot_block = np.array([bot_block])
        for block_num in range(len(bot_block)):
            overall_block[int(bot_block[block_num])] += int(
                bot_block_bot_num_per_block[block_num])
    average_block = overall_block / total_time

    bot_block = []  # blocks used for deploying malicious terminals
    bot_block_bot_num_per_block = [] # number of malicious terminals deployed in the blocks
    bot_total_num = 0

    while True:
        max_bot = math.ceil(np.max(average_block))
        if max_bot == 0:
            break
        max_block = np.argmax(average_block)

        # set zero toe blocks belonging to the coverage of a satellit
        total_bot = 0
        target_sat = user_connect_sat[max_block]
        for i in range(len(user_connect_sat)):
            if user_connect_sat[i] == target_sat:
                total_bot += average_block[i]
                average_block[i] = 0

        bot_total_num += math.ceil(total_bot)
        bot_block.append(max_block)
        bot_block_bot_num_per_block.append(math.ceil(total_bot))

    bot_block = np.array(bot_block, dtype=int)
    np.savetxt('../' + cons_name + '/+grid_data/attack_traffic_data_land_only_bot/' + str(ratio) + "-" +
               str(traffic_thre) + "-" + str(sat_per_cycle) + "-" +
               str(GSL_capacity) + "-" + str(unit_traffic) + '/bot_block.txt',
               bot_block,
               fmt='%d')
    bot_block_bot_num_per_block = np.array(
        bot_block_bot_num_per_block, dtype=int)
    np.savetxt('../' + cons_name + '/+grid_data/attack_traffic_data_land_only_bot/' + str(ratio) + "-" +
               str(traffic_thre) + "-" + str(sat_per_cycle) + "-" +
               str(GSL_capacity) + "-" + str(unit_traffic) +
               '/bot_block_bot_num_per_block.txt',
               bot_block_bot_num_per_block,
               fmt='%d')
    bot_num = np.array([bot_total_num], dtype=int)
    np.savetxt('../' + cons_name + '/+grid_data/attack_traffic_data_land_only_bot/' + str(ratio) + "-" +
               str(traffic_thre) + "-" + str(sat_per_cycle) + "-" +
               str(GSL_capacity) + "-" + str(unit_traffic) + '/bot_num.txt',
               bot_num,
               fmt='%d')

    bot_block_trim = []
    bot_block_bot_num_per_block_trim = []
    bot_block_trim_pos = []
    for block_index in range(len(bot_block_bot_num_per_block)):  
        if bot_block_bot_num_per_block[block_index] > 10:
            bot_block_trim.append(bot_block[block_index])
            bot_block_bot_num_per_block_trim.append(
                bot_block_bot_num_per_block[block_index])
            lat, lon = block_to_xy(bot_block[block_index])
            bot_block_trim_pos.append(cir_to_car_np(lat, lon))

    # replace the blocks with a few malicious terminals to neaby blocks
    for block_index in range(len(bot_block_bot_num_per_block)):
        for small_bot_num in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]:
            if bot_block_bot_num_per_block[block_index] == small_bot_num:
                lat, lon = block_to_xy(bot_block[block_index])
                dis = np.sqrt(
                    np.sum(np.square(bot_block_trim_pos - cir_to_car_np(lat, lon)),
                        axis=1))  
                target_block_index = np.argmin(dis)
                bot_block_bot_num_per_block_trim[target_block_index] += small_bot_num
                
    # replace the blocks with too many malicious terminals to neaby blocks
    loop_times = 0
    while True:
        loop_times += 1
        if np.max(bot_block_bot_num_per_block_trim) <= 20:
            break
        max_bot = np.max(bot_block_bot_num_per_block_trim)
        max_block = np.argmax(bot_block_bot_num_per_block_trim)
        if loop_times == 100000:  
            bot_block_bot_num_per_block_trim[max_block] = 20
            break
        bot_block_bot_num_per_block_trim[max_block] = traffic_thre
        dis = np.sqrt(
            np.sum(np.square(bot_block_trim_pos -
                             bot_block_trim_pos[max_block]),
                   axis=1))  
        dis[max_block] = 9999999999999
        target_block_index = np.argmin(dis)
        bot_block_bot_num_per_block_trim[
            target_block_index] += max_bot - traffic_thre

    for index, bot_num in enumerate(bot_block_bot_num_per_block_trim):
        if bot_num > 20:
            bot_block_bot_num_per_block_trim[index] = 20
            for additional_block_num in range(int(bot_num/20) - 1):
                bot_block_bot_num_per_block_trim.append(20)
                bot_block_trim.append(bot_block_trim[index + additional_block_num] + 1)
            bot_block_bot_num_per_block_trim.append(bot_num % 20)
            bot_block_trim.append(bot_block_trim[index] - 1)
                

    bot_block_trim = np.array(bot_block_trim, dtype=int)
    np.savetxt('../' + cons_name + '/+grid_data/attack_traffic_data_land_only_bot/' + str(ratio) + "-" +
               str(traffic_thre) + "-" + str(sat_per_cycle) + "-" +
               str(GSL_capacity) + "-" + str(unit_traffic) + '/bot_block_trim.txt',
               bot_block_trim,
               fmt='%d')
    bot_block_bot_num_per_block_trim = np.array(
        bot_block_bot_num_per_block_trim, dtype=int)
    np.savetxt('../' + cons_name + '/+grid_data/attack_traffic_data_land_only_bot/' + str(ratio) + "-" +
               str(traffic_thre) + "-" + str(sat_per_cycle) + "-" +
               str(GSL_capacity) + "-" + str(unit_traffic) +
               '/bot_block_bot_num_per_block_trim.txt',
               bot_block_bot_num_per_block_trim,
               fmt='%d')
    bot_num_trim = np.array([bot_total_num], dtype=int)
    np.savetxt('../' + cons_name + '/+grid_data/attack_traffic_data_land_only_bot/' + str(ratio) + "-" +
               str(traffic_thre) + "-" + str(sat_per_cycle) + "-" +
               str(GSL_capacity) + "-" + str(unit_traffic) + '/bot_num_trim.txt',
               bot_num_trim,
               fmt='%d')
    print("bFinished aggregating for +Grid!")
    
