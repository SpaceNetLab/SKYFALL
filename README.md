# SKYFALL

SKYFALL for Low-earth orbit (LEO) satellite networks (LSNs).

## What is SKYFALL?

SKYFALL helps you to analyze bottleneck ground-satellite links (GSLs) and how to deploy malicious terminals (where and how many) to accordingly achieve link-flooding attacks of various throughput degradations.

## What are the components?

1. A configuration file (`config.json`).
2. A code directory (`skyfall`).
3. Bash scripts to run the experiments (`*.sh`).
4. Links of reproduced data, satellite geo-information, and network data (<u>https://drive.google.com/file/d/1VauMH0Dm6CLrvr9cGfB6mLm6YlLt9QQf/view?usp=sharing</u> for `starlink_shell_one-3600-backup` and <u>https://drive.google.com/file/d/1py1jELENHA4I_RcOwxnMk4lYSNEdhu92/view?usp=sharing</u> for `starlink_shell_one-100-backup`).

## Preparation

1. A high-performing server with multiple cores per processor. For example, we run the experiments on a DELL R740 server with two Intel Xeon 5222 Processors (64 logical processors in total) and 8*32G DDR4 RAM. If only a commodity desktop machine is available (e.g., an x86-64 CPU with 8 cores and 16 GB of RAM), you are still able to run a small demo as shown below.
2. Support for CentOS 7.9.2009, Python 3.6 or above, and Ubuntu 20.04 LTS (and 18.04).


## Installation

Run `bash ./install.sh` to install python packets like `python3 -m pip install setuptools xlrd argparse numpy requests skyfield sgp4 heapq collections`.

## Getting started

1. Speficy `config.json`. You may change `Name` in it as you prefer. By default, we use Starlink shell-one satellites for experiments (72*22 satellites).

2. Build satellite LLA (latitude, longitude, and altitude) data for each timeslot (you should specify the number of timeslots as the attack period, e.g., 3600 in the paper), where a timeslot represents a second:
   ```
   bash lla_build.sh 3600
   ```

3. Build network traffic (you should specify the number of timeslots and the number of available logical processors for multi-thread, e.g., 3600 and 64):
   ```
   bash build_traffic.sh 3600 64
   ```

4. Calculate vital GS (you should specify the number of timeslots and the number of available logical processors for multi-thread, e.g., 3600 and 64):
   ```
   bash find_vital_GS.sh 3600 64
   ```

5. Time-Slot Analysis (as shown in Section 5.1. You should specify the number of timeslots, the number of available logical processors for multi-thread, and throughput degradation, e.g., 3600, 64, and 0.9). Throughput degradation could be 1, 0.9, 0.8, 0.7, 0.6, and 0.5 as shown in Section 6. Thus, run the following commands sequentially to analyze the deployment for various degradations:
   ```
   bash time_slot_analysis.sh 3600 64 1
   bash time_slot_analysis.sh 3600 64 0.9
   bash time_slot_analysis.sh 3600 64 0.8
   bash time_slot_analysis.sh 3600 64 0.7
   bash time_slot_analysis.sh 3600 64 0.6
   bash time_slot_analysis.sh 3600 64 0.5
   ```

6. Aggregated_deployment (as shown in Section 5.2. You should specify the number of timeslots and throughput degradation, e.g., 3600 and 0.9). Throughput degradation could be like 1, 0.9, 0.8, 0.7, 0.6, 0.5 as shown in Section 6. Thus, run the following commands sequentially to Aggregate the deployment for various degradations:
   ```
   bash aggregated_deployment.sh 3600 1
   bash aggregated_deployment.sh 3600 0.9
   bash aggregated_deployment.sh 3600 0.8
   bash aggregated_deployment.sh 3600 0.7
   bash aggregated_deployment.sh 3600 0.6
   bash aggregated_deployment.sh 3600 0.5
   ```

7. Get results (integrating the above results to obtain the results for the paper):
   ```
   bash get_results.sh
   ```


## How to reproduce the results in the paper？

Follow all the seven steps and their shell commands above. **It is better to use a machine with multiple logical processors.** Running the seven steps with 64 multi-threading on our R740 could last six to seven hours. Step 3 costs nearly three hours. Step 5 costs three hours (half an hour for each command).

After running step 2, a folder named `starlink_shell_one/sat_lla` will be in your current directory. It contains the satellite position information.


After running step 3, folders named `starlink_shell_one/+grid_traffic/link_traffic_data` and `starlink_shell_one/+grid_traffic/link_traffic_data` contain the GSL and ISL legal traffic information, as well as satellite, ground station (GS), and blcok connection information.

After running step 4, vital GSes will be generated in each timeslot folder of `starlink_shell_one/+grid_traffic/link_traffic_data` and `starlink_shell_one/+grid_traffic/link_traffic_data`.

After running step 5, timeslot analysis results (malicious terminal number, blocks to deploy the malicious terminals, affected traffic and so on) will be generated in each timeslot folder of `starlink_shell_one/+grid_traffic/attack_traffic_data_land_only_bot` and `starlink_shell_one/+grid_traffic/attack_traffic_data_land_only_bot`.

After running step 6, aggregated deployment results (malicious terminal number, blocks to deploy the malicious terminals, affected traffic, and so on) will be generated in each folder of `starlink_shell_one/+grid_traffic/attack_traffic_data_land_only_bot` and `starlink_shell_one/+grid_traffic/attack_traffic_data_land_only_bot`.

After running step 7, reproduced results will be in `starlink_shell_one/results`.

If running such a reproduction is a burden, all the reproduced data is already available in <u>https://drive.google.com/file/d/1VauMH0Dm6CLrvr9cGfB6mLm6YlLt9QQf/view?usp=sharing</u>, named as `starlink_shell_one-3600-backup`.


## How to run a small demo?
We spent six to seven hours running the seven steps (64 multi-threading for steps 3&4) for reproduction on an R740 machine. If running the above reproduction experiments is a burden for you, we recommend you to run the small demo below, where the attack period shrinks from an hour to 100 seconds. You will still run through all the steps and get similar results. The only difference is the attack period.

To run the demo, everything else could be kept the same except the parameter of timeslots for the attack period ('3600' in our case) and number of available logical processors ('64' in our case). Change them to smaller numbers, such as 100 and 8:

1. **(You don't need to change this step)** Speficy the `config.json`. You may change `Name` as you prefer. By default, we use Starlink shell-one satellites for experiments (72*22 satellites).

2. **(Make the timeslots smaller, such as 100)** Build satellite LLA (latitude, longitude, and altitude) data for each timeslot (you should specify the number of timeslots as the attack period, e.g. 100), where a timeslot represents a second:
   ```
   bash lla_build.sh 100
   ```

3. **(Make the timeslots and the number of logical processors smaller, such as 100 and 8)** Build network traffic (you should specify the number of timeslots and the number of available logical processors for multi-thread, e.g. 100 8):
   ```
   bash build_traffic.sh 100 8
   ```

4. **(Make the timeslots and the number of logical processors smaller, such as 100 and 8)** Calculate vital GS (you should specify the number of timeslots and the number of available logical processors for multi-thread, e.g. 100 8):
   ```
   bash find_vital_GS.sh 100 8
   ```

5. **(Make the timeslots and the number of logical processors smaller, such as 100 and 8)** Time-Slot Analysis (as shown in Section 5.1. You should specify the number of timeslots, the number of available logical processors for multi-thread, and throughput degradation, e.g. 100 8 0.9). Throughput degradation could be like 1, 0.9, 0.8, 0.7, 0.6, 0.5 as shown in Section 6. Thus, run the following commands sequentially to analyze the deployment for various degradations:
   ```
   bash time_slot_analysis.sh 100 8 1
   bash time_slot_analysis.sh 100 8 0.9
   bash time_slot_analysis.sh 100 8 0.8
   bash time_slot_analysis.sh 100 8 0.7
   bash time_slot_analysis.sh 100 8 0.6
   bash time_slot_analysis.sh 100 8 0.5
   ```

6. **(Make the timeslots smaller, such as 100)** Aggregated_deployment (as shown in Section 5.2. You should specify the number of timeslots and throughput degradation, e.g. 100 0.9). Throughput degradation could be like 1, 0.9, 0.8, 0.7, 0.6, 0.5 as shown in Section 6. Thus, run the following commands sequentially to Aggregate the deployment for various degradations:
   ```
   bash aggregated_deployment.sh 100 1
   bash aggregated_deployment.sh 100 0.9
   bash aggregated_deployment.sh 100 0.8
   bash aggregated_deployment.sh 100 0.7
   bash aggregated_deployment.sh 100 0.6
   bash aggregated_deployment.sh 100 0.5
   ```

7. Get results (integrating the above results to obtain the results for the paper):
   ```
   bash get_results.sh
   ```

If running such a reproduction is a burden, all the reproduced data is already available in <u>https://drive.google.com/file/d/1py1jELENHA4I_RcOwxnMk4lYSNEdhu92/view?usp=sharing</u>, named as `starlink_shell_one-100-backup`.

## Results
Running the above seven steps allows you to get the reproduced results in `starlink_shell_one/results`. 

### Better Performance of SKYFALL’ Distributed Botnet
SKYFALL is able to exploit the time-varying bottleneck and achieve good flooding attack performances. We compare it with a baselines, where both are given the same number of bot terminals. We then compare the throughput (ratio) of affected background traffic and number of affected GSLs over time. The results are shown in Figure 9. Under `starlink_shell_one/results/`, `fig-9a`, `fig-9a`, and `fig-9a` contain the corresponding throughput (ratio) data for each timeslot. `fig-10a` contains the number of attacked GSLs for each timeslot, while `fig-10b` documents the maximum, minimum, and average numbers.

### Cost Analysis
To achieve the same throughput degradation as the baseline approach, SKYFALL is able to leverage a smaller number of malicious terminals (botnet size) for both +Grid and Circular topologies. The results are shown in Figure 12. `fig-12a`, and `fig-12b` under `starlink_shell_one/results/` contain the number of malicious terminals under various degradations for both topologies respectively.

### Detectability Analysis
During SKYFALL's attack, the total malicious traffic of each satellite from all accessed malicious terminals is small. It quantifies the detectability of SKYFALL. The results are shown in Figure 14. Only a small number of satellites are accessed with malicious traffic. Under `starlink_shell_one/results/`, `fig-14a`,and `fig-14b` contain the throughput data of maliciousc traffic for each satellite in ascending order under various throughput
degradations.
