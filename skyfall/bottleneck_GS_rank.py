# In this code, the vital GSes are ranked based on the three metrics from the paper ()
# as described in the Analysis Stage (Section IV.C)

import json
import heapq
import sys
import numpy as np

if __name__ == "__main__":
    time_slot = sys.argv[1]
    
    f = open("../config.json", "r", encoding='utf8')
    table = json.load(f)
    cons_name = table["Name"]
    GS = open("./GS.json", "r", encoding='utf8')
    GS_info = json.load(GS)
    
    # metric one: GS Service Time:
    gs_service_time = './connected_time_for_gs_starlink.txt'
    with open(gs_service_time, 'r') as fr:
        line = fr.readline()  
        service_time = line.split(',')
        service_time = list(map(int, service_time))
        # top GSes from metric one
        max40_service_number = heapq.nlargest(40, service_time)
        max40_service_index = map(service_time.index, heapq.nlargest(40, service_time))
        max40_service_index = list(max40_service_index)
                
    # metric two: GS Occurrence
    gs_occurrence_num = '../' + cons_name + '/+grid_data/link_traffic_data/' + str(time_slot) + '/gs_occurrence_num.txt'
    connected_num = []
    with open(gs_occurrence_num, 'r') as fr:
        lines = fr.readlines() 
        for line in lines:
            number = int(line.strip())  
            connected_num.append(number)
        # top GSes from metric two
        max40_occurrence_number = heapq.nlargest(40, connected_num)
        max40_occurrence_index = map(connected_num.index, heapq.nlargest(40, connected_num))
        max40_occurrence_index = list(max40_occurrence_index)
    overlap = [val for val in max40_occurrence_index if val in max40_service_index]
    overlap = np.array(overlap, dtype=int)
    np.savetxt('../' + cons_name + '/+grid_data/link_traffic_data/' + str(time_slot) + '/vital_gs.txt',
               overlap,
               fmt='%d')
                
    # metric two: GS Occurrence
    gs_occurrence_num = '../' + cons_name + '/circle_data/link_traffic_data/' + str(time_slot) + '/gs_occurrence_num.txt'
    connected_num = []
    with open(gs_occurrence_num, 'r') as fr:
        lines = fr.readlines() 
        for line in lines:
            number = int(line.strip())  
            connected_num.append(number)
        # top GSes from metric two
        max40_occurrence_number = heapq.nlargest(40, connected_num)
        max40_occurrence_index = map(connected_num.index, heapq.nlargest(40, connected_num))
        max40_occurrence_index = list(max40_occurrence_index)
    overlap = [val for val in max40_occurrence_index if val in max40_service_index]
    overlap = np.array(overlap, dtype=int)
    np.savetxt('../' + cons_name + '/circle_data/link_traffic_data/' + str(time_slot) + '/vital_gs.txt',
               overlap,
               fmt='%d')
    print("Calculating vital GS for timeslot", time_slot)