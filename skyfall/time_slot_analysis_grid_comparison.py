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
    traffic_sum = np.sum(traffic)

    GSL_attack = np.loadtxt('../' + cons_name + '/+grid_data/attack_traffic_data_land_only_bot/' + str(ratio) + "-" +
               str(traffic_thre) + "-" + str(sat_per_cycle) + "-" +
               str(GSL_capacity) + "-" + str(unit_traffic) + '/' + time_slot +
               '/attack_gsl.txt')
    gsl_num = (len(GSL_attack) - 48) if (GSL_attack.size != 0 and len(GSL_attack) > 48) else 0

    gsl_list_candidate = random.sample(range(0, sat_per_cycle * orbit_num), sat_per_cycle * orbit_num - 1)
    gsl_list = []
    count = 0
    for i in range(sat_per_cycle * orbit_num - 1):
        if count == gsl_num:
            break
        if traffic[gsl_list_candidate[i]] > 0:
            gsl_list.append(gsl_list_candidate[i])
            count += 1
            
    cumu_affected_traffic_volume = 0  
    for gsl_index in gsl_list:
        bot_num += (GSL_capacity - traffic[gsl_index]) / unit_traffic 
        block_num += bot_num if bot_num <= np.sum(user_connect_sat == gsl_index) else np.sum(user_connect_sat == gsl_index) 
        cumu_affected_traffic_volume += traffic[gsl_index]
    bot_num = 5.69 * bot_num / ratio + 69.6 * ratio
    attack_gsl = gsl_list  


    os.system('mkdir -p ../' + cons_name + '/+grid_data/attack_traffic_data_land_only_bot/' + str(ratio) + "-" +
              str(traffic_thre) + "-" + str(sat_per_cycle) + "-" +
              str(GSL_capacity) + "-" + str(unit_traffic) + '-comparison/' + time_slot)
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
