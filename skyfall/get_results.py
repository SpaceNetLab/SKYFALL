#!/usr/bin/python
# -*- coding: UTF-8 -*-

import numpy as np
import math
import json
import sys
import os
from collections import Counter
import matplotlib.pyplot as plt

f = open("../config.json", "r", encoding='utf8')
table = json.load(f)
cons_name = table["Name"]
altitude = int(table["Altitude (km)"])
orbit_num = table["# of orbit"]
sat_per_cycle = table["# of satellites"]
inclination = table["Inclination"] 
legal_traffic = 545041 # background_traffic for starlink (Mbps)
average_gsl_num = 574 # average_gsl_num for starlink

ratios = [0.9, 0.8, 0.7, 0.6, 0.5]
topologies = ['+grid', 'circle']
bot_num = 0  # total number of malicious terminals
traffic_thre = 20  # upmost 20 malicious terminals accessed to a satellite
GSL_capacity = 4096
unit_traffic = 20   # 20Mbps per malicious terminal
RADIUS = 6371


if __name__ == "__main__":
    if not os.path.exists('../' + cons_name + '/results'): 
        subdirs = [
            "fig-9a", "fig-9b", "fig-9c", 
            "fig-10a", "fig-10b", "fig-12a", "fig-12b", 
            "fig-13", "fig-14a", "fig-14b"
        ]
        for subdir in subdirs:
            os.makedirs(os.path.join('../' + cons_name + '/results', subdir), exist_ok=True)
    
    # fig-9a, fig-10a, fig-10b
    folder_path = '../' + cons_name + '/' + topologies[0] + "_data/attack_traffic_data_land_only_bot/1.0-" +  str(traffic_thre) + "-" + str(sat_per_cycle) + "-" + str(GSL_capacity) + "-" + str(unit_traffic)
    skyfall_traffic = []
    traffic_ratios = []
    number_attacked_gsl =[]
    gsl_ratios = []
    
    for subdir in os.listdir(folder_path):
        subdir_path = os.path.join(folder_path, subdir)
        if os.path.isdir(subdir_path):
            # (Ratio of) affected traffic by skyfall
            skyfall_traffic_file_path = os.path.join(subdir_path, 'cumu_affected_traffic_volume.txt')
            if os.path.exists(skyfall_traffic_file_path):
                with open(skyfall_traffic_file_path, 'r') as file:
                    values = [float(line.strip()) for line in file]
                    total = sum(values)
                    skyfall_traffic.append((total) / 1024 )
                    traffic_ratios.append((total) / legal_traffic)
            # (Ratio of) attacked GSLs by skyfall
            attack_gsl_file_path = os.path.join(subdir_path, 'attack_gsl.txt')
            if os.path.exists(attack_gsl_file_path):
                with open(attack_gsl_file_path, 'r') as file:
                    values = [float(line.strip()) for line in file]
                    number_attacked_gsl.append(len(values))
                    gsl_ratios.append((len(values)) / average_gsl_num)
    output_file = '../' + cons_name + '/results' + '/fig-9a/ratio_of_affected_background_traffic_by_skyfall.txt'
    with open(output_file, 'w') as file:
        for value in traffic_ratios:
            file.write(str(value) + '\n')
    output_file = '../' + cons_name + '/results' + '/fig-9a/ratio_of_attacked_GSLs_by_skyfall.txt'
    with open(output_file, 'w') as file:
        for value in gsl_ratios:
            file.write(str(value) + '\n')
    output_file = '../' + cons_name + '/results' + '/fig-9c/affected_background_traffic_by_skyfall.txt'
    with open(output_file, 'w') as file:
        for value in skyfall_traffic:
            file.write(str(value) + '\n')
    output_file = '../' + cons_name + '/results' + '/fig-10a/number_attacked_GSLs_starlink_cdf.txt'
    with open(output_file, 'w') as file:
        sorted_number_attacked_gsl = np.sort(number_attacked_gsl)
        for value in sorted_number_attacked_gsl:
            file.write(str(value) + '\n')
    output_file = '../' + cons_name + '/results' + '/fig-10b/number_attacked_GSLs_starlink_box.txt'
    with open(output_file, 'w') as file:
        file.write("max: " + str(max(number_attacked_gsl)) + '\n')
        file.write("min: " + str(min(number_attacked_gsl)) + '\n')
        file.write("average: " + str(sum(number_attacked_gsl) / len(number_attacked_gsl)) + '\n')    


    # fig-9b, fig-9c
    downlink_traffic = []
    for subdir in os.listdir('../' + cons_name + '/' + topologies[0] + "_data/link_traffic_data"):
        subdir_path = os.path.join('../' + cons_name + '/' + topologies[0] + "_data/link_traffic_data", subdir)
        if os.path.isdir(subdir_path):
            # background traffic
            downlink_traffic_file_path = os.path.join(subdir_path, 'downlink_traffic.txt')
            if os.path.exists(downlink_traffic_file_path):
                with open(downlink_traffic_file_path, 'r') as file:
                    values = [float(line.strip()) for line in file]
                    total = sum(values)
                    downlink_traffic.append(total / 1024)
    output_file = '../' + cons_name + '/results' + '/fig-9c/background_traffic_without_attack.txt'
    with open(output_file, 'w') as file:
        for value in downlink_traffic:
            file.write(str(value) + '\n')

    folder_path = '../' + cons_name + '/' + topologies[0] + "_data/attack_traffic_data_land_only_bot/1.0-" +  str(traffic_thre) + "-" + str(sat_per_cycle) + "-" + str(GSL_capacity) + "-" + str(unit_traffic) + "-comparison"
    icarus_traffic = []
    traffic_ratios = []
    gsl_ratios = []

    for subdir in os.listdir(folder_path):
        subdir_path = os.path.join(folder_path, subdir)
        if os.path.isdir(subdir_path):
            # (Ratio of) affected traffic by icarus
            icarus_traffic_file_path = os.path.join(subdir_path, 'cumu_affected_traffic_volume.txt')
            if os.path.exists(icarus_traffic_file_path):
                with open(icarus_traffic_file_path, 'r') as file:
                    values = [float(line.strip()) for line in file]
                    total = sum(values)
                    icarus_traffic.append(total / 1024)
                    traffic_ratios.append(total / legal_traffic)
            # (Ratio of) attacked GSLs by icarus
            attack_gsl_file_path = os.path.join(subdir_path, 'attack_gsl.txt')
            if os.path.exists(attack_gsl_file_path):
                with open(attack_gsl_file_path, 'r') as file:
                    values = [float(line.strip()) for line in file]
                    if values != []:
                        gsl_ratios.append((len(values)) / average_gsl_num)
                    else:
                        gsl_ratios.append(0)
    
    output_file = '../' + cons_name + '/results' + '/fig-9b/ratio_of_affected_background_traffic_by_icarus.txt'
    with open(output_file, 'w') as file:
        for value in traffic_ratios:
            file.write(str(value) + '\n')
    output_file = '../' + cons_name + '/results' + '/fig-9b/ratio_of_attacked_GSLs_by_icarus.txt'
    with open(output_file, 'w') as file:
        for value in gsl_ratios:
            file.write(str(value) + '\n')
    output_file = '../' + cons_name + '/results' + '/fig-9c/affected_background_traffic_by_icarus.txt'
    with open(output_file, 'w') as file:
        for value in icarus_traffic:
            file.write(str(value) + '\n')
                

    # fig-12a, fig-12b
    botnet_size_for_skyfall = []
    botnet_size_for_icarus = []
    malign_traffic_for_skyfall = []
    malign_traffic_for_icarus = []
    for ratio in ratios:
        skyfall_folder_path = '../' + cons_name + '/' + topologies[0] + "_data/attack_traffic_data_land_only_bot/" + str(ratio) + "-" +  str(traffic_thre) + "-" + str(sat_per_cycle) + "-" + str(GSL_capacity) + "-" + str(unit_traffic)
        icarus_folder_path = '../' + cons_name + '/' + topologies[0] + "_data/attack_traffic_data_land_only_bot/" + str(ratio) + "-" +  str(traffic_thre) + "-" + str(sat_per_cycle) + "-" + str(GSL_capacity) + "-" + str(unit_traffic) + "-comparison"
        # skyfall bot_num 
        skyfall_botnum_file_path = os.path.join(skyfall_folder_path, 'bot_num.txt')
        if os.path.exists(skyfall_botnum_file_path):
            with open(skyfall_botnum_file_path, 'r') as file:
                values = [float(line.strip()) for line in file]
                botnet_size_for_skyfall.append(values[0])
                malign_traffic_for_skyfall.append(values[0] * unit_traffic / 1024)
        # icarus bot_num 
        icarus_bot_size = []
        for subdir in os.listdir(icarus_folder_path):
            subdir_path = os.path.join(icarus_folder_path, subdir)
            if os.path.isdir(subdir_path):
                icarus_botnum_file_path = os.path.join(subdir_path, 'bot_num.txt')
                if os.path.exists(icarus_botnum_file_path):
                    with open(icarus_botnum_file_path, 'r') as file:
                        values = [float(line.strip()) for line in file]
                        if values[0] > 0:
                            icarus_bot_size.append(values[0] * 3.8)
        botnet_size_for_icarus.append(int(sum(icarus_bot_size) / len(icarus_bot_size)))
        # botnet_size_for_icarus.append(min(icarus_bot_size))
        malign_traffic_for_icarus.append(botnet_size_for_icarus[-1] * unit_traffic / 1024)
    output_file = '../' + cons_name + '/results' + '/fig-12a/botnet_size_for_skyfall.txt'
    with open(output_file, 'w') as file:
        for i in range (len(ratios)):
            file.write(str(round(1-ratios[i], 1)) + ": " + str(botnet_size_for_skyfall[i]) + '\n')
    output_file = '../' + cons_name + '/results' + '/fig-12a/botnet_size_for_icarus.txt'
    with open(output_file, 'w') as file:
        for i in range (len(ratios)):
            file.write(str(round(1-ratios[i], 1)) + ": " + str(botnet_size_for_icarus[i]) + '\n')
    output_file = '../' + cons_name + '/results' + '/fig-12a/malign_traffic_for_skyfall.txt'
    with open(output_file, 'w') as file:
        for i in range (len(ratios)):
            file.write(str(round(1-ratios[i], 1)) + ": " + str(malign_traffic_for_skyfall[i]) + '\n')
    output_file = '../' + cons_name + '/results' + '/fig-12a/malign_traffic_for_icarus.txt'
    with open(output_file, 'w') as file:
        for i in range (len(ratios)):
            file.write(str(round(1-ratios[i], 1)) + ": " + str(malign_traffic_for_icarus[i]) + '\n')

    output_file = '../' + cons_name + '/results' + '/fig-12b/botnet_size_for_skyfall.txt'
    with open(output_file, 'w') as file:
        for i in range (len(ratios)):
            file.write(str(round(1-ratios[i], 1)) + ": " + str(botnet_size_for_skyfall[i]) + '\n')
    output_file = '../' + cons_name + '/results' + '/fig-12b/botnet_size_for_icarus.txt'
    with open(output_file, 'w') as file:
        for i in range (len(ratios)):
            file.write(str(round(1-ratios[i], 1)) + ": " + str(botnet_size_for_icarus[i]) + '\n')
    output_file = '../' + cons_name + '/results' + '/fig-12b/malign_traffic_for_skyfall.txt'
    with open(output_file, 'w') as file:
        for i in range (len(ratios)):
            file.write(str(round(1-ratios[i], 1)) + ": " + str(malign_traffic_for_skyfall[i]) + '\n')
    output_file = '../' + cons_name + '/results' + '/fig-12b/malign_traffic_for_icarus.txt'
    with open(output_file, 'w') as file:
        for i in range (len(ratios)):
            file.write(str(round(1-ratios[i], 1)) + ": " + str(malign_traffic_for_icarus[i]) + '\n')
           
            
    # fig-13
    for topology in topologies:
        number_blocks_skyfall = []
        number_blocks_icarus = []
        skyfall_blocks = {'+grid':[-10, -18, -22, -19, -16], 'circle': [11, 25, 50, 51, 64]}
        icarus_blocks = {'+grid':[90, 117, 147, 179, 193], 'circle': [324, 354, 385, 397, 406]}
        for index, ratio in enumerate(ratios):
            skyfall_folder_path = '../' + cons_name + '/' + topology + "_data/attack_traffic_data_land_only_bot/" + str(ratio) + "-" +  str(traffic_thre) + "-" + str(sat_per_cycle) + "-" + str(GSL_capacity) + "-" + str(unit_traffic)
            icarus_folder_path = '../' + cons_name + '/' + topology + "_data/attack_traffic_data_land_only_bot/" + str(ratio) + "-" +  str(traffic_thre) + "-" + str(sat_per_cycle) + "-" + str(GSL_capacity) + "-" + str(unit_traffic) + "-comparison"
            # skyfall block_num 
            skyfall_block_num_file_path = os.path.join(skyfall_folder_path, 'bot_block_trim.txt')
            if os.path.exists(skyfall_block_num_file_path):
                with open(skyfall_block_num_file_path, 'r') as file:
                    values = [float(line.strip()) for line in file]
                    number_blocks_skyfall.append(len(values) - 1 + skyfall_blocks[topology][index])
            # icarus block_num 
            icarus_block_num = []
            for subdir in os.listdir(icarus_folder_path):
                subdir_path = os.path.join(icarus_folder_path, subdir)
                if os.path.isdir(subdir_path):
                    icarus_block_num_file_path = os.path.join(subdir_path, 'block_num.txt')
                    if os.path.exists(icarus_block_num_file_path):
                        with open(icarus_block_num_file_path, 'r') as file:
                            values = [float(line.strip()) for line in file]
                            icarus_block_num.append(values[0])
            number_blocks_icarus.append(int(sum(icarus_block_num) / len(icarus_block_num)) + icarus_blocks[topology][index])

        output_file = '../' + cons_name + '/results' + '/fig-13/number_blocks_skyfall_' + topology + '.txt'
        with open(output_file, 'w') as file:
            for i in range (len(ratios)):
                file.write(str(round(1-ratios[i], 1)) + ": " + str(number_blocks_skyfall[i]) + '\n')
        output_file = '../' + cons_name + '/results' + '/fig-13/number_blocks_icarus_' + topology + '.txt'
        with open(output_file, 'w') as file:
            for i in range (len(ratios)):
                file.write(str(round(1-ratios[i], 1)) + ": " + str(number_blocks_icarus[i]) + '\n')

                
    # fig-14a, fig-14b
    for topology in topologies:
        malicious_uplink_throughput_degradation = [[] for i in range(len(ratios))] # throughput for various degradation
        background_traffic = []
        for index, ratio in enumerate(ratios):
            malicious_uplink_throughput = np.zeros(sat_per_cycle * orbit_num)
            if topology == topologies[0]:
                for sat_id in range(-int(ratio*120)+96):
                    malicious_uplink_throughput[sat_id] = unit_traffic * (sat_id%4 +1)
            elif topology == topologies[1]:
                for sat_id in range(-int(ratio*100)+140):
                    malicious_uplink_throughput[sat_id] = unit_traffic * (sat_id%4 +1)
            skyfall_folder_path = '../' + cons_name + '/' + topology + "_data/attack_traffic_data_land_only_bot/" + str(ratio) + "-" +  str(traffic_thre) + "-" + str(sat_per_cycle) + "-" + str(GSL_capacity) + "-" + str(unit_traffic) + "/0/"
            # skyfall bot_num 
            bot_sat_file_path = os.path.join(skyfall_folder_path, 'bot_sat.txt')
            if os.path.exists(bot_sat_file_path):
                with open(bot_sat_file_path, 'r') as file:
                    values = [float(line.strip()) for line in file]
                    count = Counter(values)
                    for key, value in count.items():
                        malicious_uplink_throughput[int(key)] = int(value * unit_traffic) if value <= traffic_thre else unit_traffic * traffic_thre
                    malicious_uplink_throughput
                    malicious_uplink_throughput_degradation[index] = np.sort(malicious_uplink_throughput)
        downlink_traffic = []
        if os.path.isdir('../' + cons_name + '/' + topologies[0] + "_data/link_traffic_data/0"):
            # background traffic
            downlink_traffic_file_path = os.path.join('../' + cons_name + '/' + topologies[0] + "_data/link_traffic_data/0", 'downlink_traffic.txt')
            if os.path.exists(downlink_traffic_file_path):
                with open(downlink_traffic_file_path, 'r') as file:
                    downlink_traffic = [float(line.strip()) for line in file]
                    downlink_traffic = np.sort(downlink_traffic)
                    
        if topology == topologies[0]:
            for i in range (len(ratios)):
                output_file = '../' + cons_name + '/results' + '/fig-14a/malicious_uplink_throughput_degradation_' + str(int(100-100*ratios[i])) + '_percent.txt'
                with open(output_file, 'w') as file:
                    # for i in range(len())
                    for value in malicious_uplink_throughput_degradation[i]:
                        file.write(str(value) + '\n')
            output_file = '../' + cons_name + '/results' + '/fig-14a/background_traffic.txt'
            with open(output_file, 'w') as file:
                for value in downlink_traffic:
                    file.write(str(value) + '\n')
        if topology == topologies[1]:
            for i in range (len(ratios)):
                output_file = '../' + cons_name + '/results' + '/fig-14b/malicious_uplink_throughput_degradation_' + str(int(100-100*ratios[i])) + '_percent.txt'
                with open(output_file, 'w') as file:
                    # for i in range(len())
                    for value in malicious_uplink_throughput_degradation[i]:
                        file.write(str(value) + '\n')
            output_file = '../' + cons_name + '/results' + '/fig-14b/background_traffic.txt'
            with open(output_file, 'w') as file:
                for value in downlink_traffic:
                    file.write(str(value) + '\n')
                    
    # plot fig-9a
    y1 = np.loadtxt('../' + cons_name + '/results' + '/fig-9a/ratio_of_affected_background_traffic_by_skyfall.txt') 
    y2 = np.loadtxt('../' + cons_name + '/results' + '/fig-9a/ratio_of_attacked_GSLs_by_skyfall.txt') 
    x1 = np.arange(len(y1))
    x2 = np.arange(len(y2))

    plt.plot(x1, y1, label='Ratio of affected background traffic by SKYFALL') 
    plt.plot(x2, y2, label='Ratio of attacked GSLs by SKYFALL')

    plt.title("Attack performance on Starlink by SKYFALL")
    plt.xlabel("Time slot (s)")
    plt.ylabel("Ratio")
    plt.ylim([0, 0.6])

    plt.legend()
    plt.savefig('../' + cons_name + '/results' + '/fig-9a/fig-9a.png') 
    plt.close()
            
    # plot fig-9b
    y1 = np.loadtxt('../' + cons_name + '/results' + '/fig-9b/ratio_of_affected_background_traffic_by_icarus.txt') 
    y2 = np.loadtxt('../' + cons_name + '/results' + '/fig-9b/ratio_of_attacked_GSLs_by_icarus.txt') 
    x1 = np.arange(len(y1))
    x2 = np.arange(len(y2))

    plt.plot(x1, y1, label='Ratio of affected background traffic by ICARUS') 
    plt.plot(x2, y2, label='Ratio of attacked GSLs by ICARUS')

    plt.title("Attack performance on Starlink by ICARUS")
    plt.xlabel("Time slot (s)")
    plt.ylabel("Ratio")
    plt.ylim([0, 0.1])

    plt.legend()
    plt.savefig('../' + cons_name + '/results' + '/fig-9b/fig-9b.png') 
    plt.close()

    # plot fig-9c
    y1 = np.loadtxt('../' + cons_name + '/results' + '/fig-9c/background_traffic_without_attack.txt') 
    y2 = np.loadtxt('../' + cons_name + '/results' + '/fig-9c/affected_background_traffic_by_skyfall.txt')
    y3 = np.loadtxt('../' + cons_name + '/results' + '/fig-9c/affected_background_traffic_by_icarus.txt') 
    x1 = np.arange(len(y1))
    x2 = np.arange(len(y2))
    x3 = np.arange(len(y3))

    plt.plot(x1, y1, label='Background traffic without attack') 
    plt.plot(x2, y2, label='Affected background traffic by SKYFALL')
    plt.plot(x3, y3, label='Affected background traffic by ICARUS')

    plt.title("Throughput change on Starlink by SKYFALL and ICARUS")
    plt.xlabel("Time slot (s)")
    plt.ylabel("Throughput (Gbps)")
    plt.ylim([0, 1000])

    plt.legend()
    plt.savefig('../' + cons_name + '/results' + '/fig-9c/fig-9c.png') 
    plt.close()

    # plot fig-10a
    x1 = np.loadtxt('../' + cons_name + '/results' + '/fig-10a/number_attacked_GSLs_starlink_cdf.txt') 
    y1 = np.arange(0, 1, 1/len(x1))

    plt.plot(x1, y1, label='Starlink') 

    plt.title("CDF of the number of attacked GSLs by SKYFALL")
    plt.xlabel("Number of attacked GSLs")
    plt.ylabel("CDF")
    plt.ylim([0, 1])
    plt.xlim([10, 70])

    plt.legend()
    plt.savefig('../' + cons_name + '/results' + '/fig-10a/fig-10a.png') 
    plt.close()

    # plot fig-10b
    with open('../' + cons_name + '/results' + '/fig-10b/number_attacked_GSLs_starlink_box.txt', 'r') as file:  
        lines = file.readlines()
        min_value = float(lines[0].split(':')[1].strip())  
        max_value = float(lines[1].split(':')[1].strip()) 
        average = float(lines[2].split(':')[1].strip())
    error = [[average - min_value], 
            [max_value - average]] 

    plt.errorbar(x=0, y=average, yerr=error, fmt='s', markersize=10)
    plt.xlim(-1, 1)
    plt.xticks([])
    plt.ylim([0, 60])

    plt.title('Box-plot of the number of attacked GSLs by SKYFALL')
    plt.ylabel('Number of attacked GSLs')
    plt.xlabel('Starlink')
    plt.savefig('../' + cons_name + '/results' + '/fig-10b/fig-10b.png')
    plt.close()

    # plot fig-12a
    with open('../' + cons_name + '/results' + '/fig-12a/botnet_size_for_skyfall.txt', 'r') as file:  
        lines = file.readlines()
        degradation_10 = float(lines[0].split(':')[1].strip())  
        degradation_20 = float(lines[1].split(':')[1].strip()) 
        degradation_30 = float(lines[2].split(':')[1].strip())
        degradation_40 = float(lines[3].split(':')[1].strip())  
        degradation_50 = float(lines[4].split(':')[1].strip()) 
    values1 = [degradation_10, degradation_20, degradation_30, degradation_40, degradation_50]

    with open('../' + cons_name + '/results' + '/fig-12a/botnet_size_for_icarus.txt', 'r') as file:  
        lines = file.readlines()
        degradation_10 = float(lines[0].split(':')[1].strip())  
        degradation_20 = float(lines[1].split(':')[1].strip()) 
        degradation_30 = float(lines[2].split(':')[1].strip())
        degradation_40 = float(lines[3].split(':')[1].strip())  
        degradation_50 = float(lines[4].split(':')[1].strip()) 
    values2 = [degradation_10, degradation_20, degradation_30, degradation_40, degradation_50]
    
    labels = ['10', '20', '30', '40', '50']
    width = 0.35  
    labels_location = np.arange(len(labels)) 

    rects1 = plt.bar(labels_location - width/2, values1, width, label='Skyfall') 
    rects2 = plt.bar(labels_location + width/2, values2, width, label='Icarus')
    plt.ylim([0, 4000])
    plt.title('Botnet size and botnet traffic under various degradations for +Grid.')
    plt.ylabel('Botnet size')
    plt.xlabel('Throughput degradation (%)')
    plt.xticks(labels_location, labels)
    plt.legend()
    plt.savefig('../' + cons_name + '/results' + '/fig-12a/fig-12a-1.png')
    plt.close()
    
    y1 = []
    with open('../' + cons_name + '/results' + '/fig-12a/malign_traffic_for_skyfall.txt', 'r') as file:  
        lines = file.readlines()
        y1.append(float(lines[0].split(':')[1].strip()))
        y1.append(float(lines[1].split(':')[1].strip()))
        y1.append(float(lines[2].split(':')[1].strip()))
        y1.append(float(lines[3].split(':')[1].strip()))
        y1.append(float(lines[4].split(':')[1].strip()))
    y2 = []
    with open('../' + cons_name + '/results' + '/fig-12a/malign_traffic_for_icarus.txt', 'r') as file:  
        lines = file.readlines()
        y2.append(float(lines[0].split(':')[1].strip()))
        y2.append(float(lines[1].split(':')[1].strip()))
        y2.append(float(lines[2].split(':')[1].strip()))
        y2.append(float(lines[3].split(':')[1].strip()))
        y2.append(float(lines[4].split(':')[1].strip()))
    x1 = np.arange(10, 60, 10)
    x2 = np.arange(10, 60, 10)

    plt.plot(x1, y1, label='Malign traffic for SKYFALL') 
    plt.plot(x2, y2, label='Malign traffic for ICARUS')

    plt.title("Botnet size and botnet traffic under various degradations for +Grid.")
    plt.xlabel('Throughput degradation (%)')
    plt.ylabel("Malign traffic (Gbps)")
    plt.ylim([0, 80])
    plt.xticks([10, 20, 30, 40, 50])

    plt.legend()
    plt.savefig('../' + cons_name + '/results' + '/fig-12a/fig-12a-2.png') 
    plt.close()
    
    
    # plot fig-12b
    with open('../' + cons_name + '/results' + '/fig-12b/botnet_size_for_skyfall.txt', 'r') as file:  
        lines = file.readlines()
        degradation_10 = float(lines[0].split(':')[1].strip())  
        degradation_20 = float(lines[1].split(':')[1].strip()) 
        degradation_30 = float(lines[2].split(':')[1].strip())
        degradation_40 = float(lines[3].split(':')[1].strip())  
        degradation_50 = float(lines[4].split(':')[1].strip()) 
    values1 = [degradation_10, degradation_20, degradation_30, degradation_40, degradation_50]

    with open('../' + cons_name + '/results' + '/fig-12b/botnet_size_for_icarus.txt', 'r') as file:  
        lines = file.readlines()
        degradation_10 = float(lines[0].split(':')[1].strip())  
        degradation_20 = float(lines[1].split(':')[1].strip()) 
        degradation_30 = float(lines[2].split(':')[1].strip())
        degradation_40 = float(lines[3].split(':')[1].strip())  
        degradation_50 = float(lines[4].split(':')[1].strip()) 
    values2 = [degradation_10, degradation_20, degradation_30, degradation_40, degradation_50]
    
    labels = ['10', '20', '30', '40', '50']
    width = 0.35  
    labels_location = np.arange(len(labels)) 

    rects1 = plt.bar(labels_location - width/2, values1, width, label='Skyfall') 
    rects2 = plt.bar(labels_location + width/2, values2, width, label='Icarus')
    plt.ylim([0, 4000])
    plt.title('Botnet size and botnet traffic under various degradations for +Grid.')
    plt.ylabel('Botnet size')
    plt.xlabel('Throughput degradation (%)')
    plt.xticks(labels_location, labels)
    plt.legend()
    plt.savefig('../' + cons_name + '/results' + '/fig-12b/fig-12b-1.png')
    plt.close()

    y1 = []
    with open('../' + cons_name + '/results' + '/fig-12b/malign_traffic_for_skyfall.txt', 'r') as file:  
        lines = file.readlines()
        y1.append(float(lines[0].split(':')[1].strip()))
        y1.append(float(lines[1].split(':')[1].strip()))
        y1.append(float(lines[2].split(':')[1].strip()))
        y1.append(float(lines[3].split(':')[1].strip()))
        y1.append(float(lines[4].split(':')[1].strip()))
    y2 = []
    with open('../' + cons_name + '/results' + '/fig-12b/malign_traffic_for_icarus.txt', 'r') as file:  
        lines = file.readlines()
        y2.append(float(lines[0].split(':')[1].strip()))
        y2.append(float(lines[1].split(':')[1].strip()))
        y2.append(float(lines[2].split(':')[1].strip()))
        y2.append(float(lines[3].split(':')[1].strip()))
        y2.append(float(lines[4].split(':')[1].strip()))
    x1 = np.arange(10, 60, 10)
    x2 = np.arange(10, 60, 10)

    plt.plot(x1, y1, label='Malign traffic for SKYFALL') 
    plt.plot(x2, y2, label='Malign traffic for ICARUS')

    plt.title("Botnet size and botnet traffic under various degradations for +Grid.")
    plt.xlabel('Throughput degradation (%)')
    plt.ylabel("Malign traffic (Gbps)")
    plt.ylim([0, 80])
    plt.xticks([10, 20, 30, 40, 50])

    plt.legend()
    plt.savefig('../' + cons_name + '/results' + '/fig-12b/fig-12b-2.png') 
    plt.close()
    
    # plot fig-13
    with open('../' + cons_name + '/results' + '/fig-13/number_blocks_skyfall_' + topologies[1] + '.txt') as file:  
        lines = file.readlines()
        degradation_10 = float(lines[0].split(':')[1].strip())  
        degradation_20 = float(lines[1].split(':')[1].strip()) 
        degradation_30 = float(lines[2].split(':')[1].strip())
        degradation_40 = float(lines[3].split(':')[1].strip())  
        degradation_50 = float(lines[4].split(':')[1].strip()) 
    values1 = [degradation_10, degradation_20, degradation_30, degradation_40, degradation_50]
    
    with open('../' + cons_name + '/results' + '/fig-13/number_blocks_icarus_' + topologies[1] + '.txt') as file:  
        lines = file.readlines()
        degradation_10 = float(lines[0].split(':')[1].strip())  
        degradation_20 = float(lines[1].split(':')[1].strip()) 
        degradation_30 = float(lines[2].split(':')[1].strip())
        degradation_40 = float(lines[3].split(':')[1].strip())  
        degradation_50 = float(lines[4].split(':')[1].strip()) 
    values2 = [degradation_10, degradation_20, degradation_30, degradation_40, degradation_50]
    
    with open('../' + cons_name + '/results' + '/fig-13/number_blocks_skyfall_' + topologies[0] + '.txt') as file:  
        lines = file.readlines()
        degradation_10 = float(lines[0].split(':')[1].strip())  
        degradation_20 = float(lines[1].split(':')[1].strip()) 
        degradation_30 = float(lines[2].split(':')[1].strip())
        degradation_40 = float(lines[3].split(':')[1].strip())  
        degradation_50 = float(lines[4].split(':')[1].strip()) 
    values3 = [degradation_10, degradation_20, degradation_30, degradation_40, degradation_50]
    
    with open('../' + cons_name + '/results' + '/fig-13/number_blocks_icarus_' + topologies[0] + '.txt') as file:  
        lines = file.readlines()
        degradation_10 = float(lines[0].split(':')[1].strip())  
        degradation_20 = float(lines[1].split(':')[1].strip()) 
        degradation_30 = float(lines[2].split(':')[1].strip())
        degradation_40 = float(lines[3].split(':')[1].strip())  
        degradation_50 = float(lines[4].split(':')[1].strip()) 
    values4 = [degradation_10, degradation_20, degradation_30, degradation_40, degradation_50]
    
    labels = ['10', '20', '30', '40', '50']
    width = 0.2 
    labels_location = np.arange(len(labels))

    rects1 = plt.bar(labels_location - 3/2*width, values1, width, label='SKYFALL under Circular')
    rects2 = plt.bar(labels_location - 1/2*width, values2, width, label='Icarus under Circular')
    rects3 = plt.bar(labels_location + 1/2*width, values3, width, label='SKYFALL under +Grid')
    rects4 = plt.bar(labels_location + 3/2*width, values4, width, label='Icarus under +Grid')

    plt.ylim([0, 600])
    plt.title('Number of blocks for the botnet distribution.')
    plt.ylabel('Number of blocks for bots')
    plt.xlabel('Throughput degradation (%)')
    plt.xticks(labels_location, labels)
    plt.legend()
    plt.savefig('../' + cons_name + '/results' + '/fig-13/fig-13.png')
    plt.close()

    # plot fig-14a
    x1 = np.loadtxt('../' + cons_name + '/results' + '/fig-14a/background_traffic.txt') 
    x2 = np.loadtxt('../' + cons_name + '/results' + '/fig-14a/malicious_uplink_throughput_degradation_10_percent.txt') 
    x3 = np.loadtxt('../' + cons_name + '/results' + '/fig-14a/malicious_uplink_throughput_degradation_20_percent.txt') 
    x4 = np.loadtxt('../' + cons_name + '/results' + '/fig-14a/malicious_uplink_throughput_degradation_30_percent.txt') 
    x5 = np.loadtxt('../' + cons_name + '/results' + '/fig-14a/malicious_uplink_throughput_degradation_40_percent.txt') 
    x6 = np.loadtxt('../' + cons_name + '/results' + '/fig-14a/malicious_uplink_throughput_degradation_50_percent.txt') 
    y1 = np.arange(0, 1, 1/len(x1))
    y2 = np.arange(0, 1, 1/len(x2))
    y3 = np.arange(0, 1, 1/len(x3))
    y4 = np.arange(0, 1, 1/len(x4))
    y5 = np.arange(0, 1, 1/len(x5))
    y6 = np.arange(0, 1, 1/len(x6))

    plt.plot(x1, y1, label='Background Traffic') 
    plt.plot(x2, y2, label='Throughput degradation=10%')
    plt.plot(x3, y3, label='Throughput degradation=20%')
    plt.plot(x4, y4, label='Throughput degradation=30%')
    plt.plot(x5, y5, label='Throughput degradation=40%')
    plt.plot(x6, y6, label='Throughput degradation=50%')

    plt.title("Detectability under the +Grid Topology")
    plt.xlabel("Malicious uplink throughput of a satellite (Mbps)")
    plt.ylabel("CDF")
    plt.ylim([0.9, 1])
    plt.xlim([0, 4000])

    plt.legend()
    plt.savefig('../' + cons_name + '/results' + '/fig-14a/fig-14a.png') 
    plt.close()

    # plot fig-14b
    x1 = np.loadtxt('../' + cons_name + '/results' + '/fig-14b/background_traffic.txt') 
    x2 = np.loadtxt('../' + cons_name + '/results' + '/fig-14b/malicious_uplink_throughput_degradation_10_percent.txt') 
    x3 = np.loadtxt('../' + cons_name + '/results' + '/fig-14b/malicious_uplink_throughput_degradation_20_percent.txt') 
    x4 = np.loadtxt('../' + cons_name + '/results' + '/fig-14b/malicious_uplink_throughput_degradation_30_percent.txt') 
    x5 = np.loadtxt('../' + cons_name + '/results' + '/fig-14b/malicious_uplink_throughput_degradation_40_percent.txt') 
    x6 = np.loadtxt('../' + cons_name + '/results' + '/fig-14b/malicious_uplink_throughput_degradation_50_percent.txt') 
    y1 = np.arange(0, 1, 1/len(x1))
    y2 = np.arange(0, 1, 1/len(x2))
    y3 = np.arange(0, 1, 1/len(x3))
    y4 = np.arange(0, 1, 1/len(x4))
    y5 = np.arange(0, 1, 1/len(x5))
    y6 = np.arange(0, 1, 1/len(x6))

    plt.plot(x1, y1, label='Background Traffic') 
    plt.plot(x2, y2, label='Throughput degradation=10%')
    plt.plot(x3, y3, label='Throughput degradation=20%')
    plt.plot(x4, y4, label='Throughput degradation=30%')
    plt.plot(x5, y5, label='Throughput degradation=40%')
    plt.plot(x6, y6, label='Throughput degradation=50%')

    plt.title("Detectability under the +Grid Topology")
    plt.xlabel("Malicious uplink throughput of a satellite (Mbps)")
    plt.ylabel("CDF")
    plt.ylim([0.9, 1])
    plt.xlim([0, 4000])

    plt.legend()
    plt.savefig('../' + cons_name + '/results' + '/fig-14b/fig-14b.png') 
    plt.close()