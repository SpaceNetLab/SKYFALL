from skyfield.api import load, wgs84, EarthSatellite
from datetime import datetime
from sgp4.api import Satrec, WGS84
import numpy as np
import os
import sys
import json

ts = load.timescale()

f = open("../config.json", "r", encoding='utf8')
table = json.load(f)
cons_name = table["Name"]
altitude = table["Altitude (km)"] * 1000
num_of_orbit = table["# of orbit"]
sat_per_orbit = table["# of satellites"]
inclination = table["Inclination"] * 2 * np.pi / 360  # inclination
since = datetime(1949, 12, 31, 0, 0, 0)
start = datetime(2020, 1, 1, 0, 0, 0)  # start_time
epoch = (start - since).days
GM = 3.9860044e14
R = 6371393
mean_motion = np.sqrt(GM / (R + altitude)**3) * 60
num_of_sat = num_of_orbit * sat_per_orbit
F = 1


duration = int(sys.argv[1])  # second
result = [[] for i in range(duration)]
for i in range(num_of_orbit):  # range(num_of_orbit)
    raan = i / num_of_orbit * 2 * np.pi
    for j in range(sat_per_orbit):  # range(sat_per_orbit)
        mean_anomaly = (j * 360 / sat_per_orbit +
                        i * 360 * F / num_of_sat) % 360 * 2 * np.pi / 360
        satrec = Satrec()
        satrec.sgp4init(
            WGS84,  # gravity model
            'i',  # 'a' = old AFSPC mode, 'i' = improved mode
            i * sat_per_orbit + j,  # satnum: Satellite number
            epoch,  # epoch: days since 1949 December 31 00:00 UT
            2.8098e-05,  # bstar: drag coefficient (/earth radii)
            6.969196665e-13,  # ndot: ballistic coefficient (revs/day)
            0.0,  # nddot: second derivative of mean motion (revs/day^3)
            0.001,  # ecco: eccentricity
            0.0,  # argpo: argument of perigee (radians)
            inclination,  # inclo: inclination (radians)
            mean_anomaly,  # mo: mean anomaly (radians)
            mean_motion,  # no_kozai: mean motion (radians/minute)
            raan,  # nodeo: right ascension of ascending node (radians)
        )
        sat = EarthSatellite.from_satrec(satrec, ts)
        cur = datetime(2020, 6, 1, 0, 0, 0)
        curtime = cur.strftime("%Y%m%d")
        t_ts = ts.utc(*cur.timetuple()[:5], range(duration))  # [:4] for minute, [:5] for second
        geocentric = sat.at(t_ts)
        subpoint = wgs84.subpoint(geocentric)
        for t in range(duration):
            ainfo = '%f,%f,%f\n' % (subpoint.latitude.degrees[t],
                                    subpoint.longitude.degrees[t],
                                    subpoint.elevation.km[t])
            result[t].append(ainfo)

if os.path.exists('../' + cons_name + '/sat_lla/') == False: 
    os.system('mkdir -p ../' + cons_name + '/sat_lla/')
for t in range(duration):
    filename = '../' + cons_name + '/sat_lla/%d.txt' % t
    with open(filename, 'w') as fw:
        fw.writelines(result[t])