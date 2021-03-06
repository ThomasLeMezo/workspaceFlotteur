#!/bin/python2.7
# from copy import copy, deepcopy

import sys
from load_data import *

from pyibex import *
from vibes import vibes
import numpy as np
from math import *

if(len(sys.argv)<2):
	sys.exit(0)

pistonStateData = PistonStateData()
pistonSetPointData = PistonSetPointData()
imuData = ImuData()
magData = MagData()
eulerData = EulerData()
pistonVelocityData = PistonVelocityData()
pistonDistanceData = PistonDistanceData()
pistonSpeedData = PistonSpeedData()
batteryData = BatteryData()
sensorExtData = SensorExtData()
sensorIntData = SensorIntData()
engineData = EngineData()
engineCmdData = EngineCmdData()
fixData = FixData()
temperatureData = TemperatureData()
batteryFusionData = BatteryFusionData()
sensorIntFusionData = SensorIntFusionData()
depthFusionData = DepthFusionData()
poseFusionData = PoseFusionData()
kalmanData = KalmanData()
regulationData = RegulationData()
regulationHeadingData = RegulationHeadingData()
regulationHeadingSetPointData = RegulationHeadingSetPointData()
missionData = MissionData()
safetyData = SafetyData()
safetyDebugData = SafetyDebugData()
iridiumStatusData = IridiumStatusData()
iridiumSessionData = IridiumSessionData()
regulationWaypointData = RegulationWaypointData()


filename = sys.argv[1]
filename = "/home/lemezoth/workspaceFlotteur/tools/rosbag/bag/guerledan/2019-10-10-15-06-02_0.bag"
load_bag(filename, pistonStateData, pistonSetPointData, imuData, magData, eulerData, pistonVelocityData, pistonDistanceData, pistonSpeedData, batteryData, sensorExtData, sensorIntData, engineData, engineCmdData, fixData, temperatureData, batteryFusionData, sensorIntFusionData, depthFusionData, poseFusionData, kalmanData, regulationData, regulationHeadingData, regulationHeadingSetPointData, missionData, safetyData, safetyDebugData, iridiumStatusData, iridiumSessionData, regulationWaypointData)

g = 9.81
m = 9.045
rho = 1025.0
d_flange = 0.24
d_piston = 0.05
Cf = pi*(d_flange/2.0)**2
screw_thread = 1.75e-3
tick_per_turn = 48
piston_full_volume = 1.718e-4 # m3
tick_to_volume = (screw_thread/tick_per_turn)*((d_piston/2.0)**2)*np.pi


print("Data has been loaded")
file_directory = "/home/lemezoth/workspaceQT/tikz-adapter/tikz/figs/svg/"

offset = 0.
x_min = 0. # for display
x_max = 61343/3600.
y_min = -0.2
y_max = 32.

def newFigure(name):
	vibes.newFigure(name)
	vibes.setFigureProperties({'x':0, 'y':0, 'width':1024, 'height':500, 'viewbox':'equal'})
	vibes.axisLimits(x_min-offset, x_max+offset, y_min-offset, y_max+offset)
	vibes.drawBox(x_min-offset, x_max+offset, y_min-offset, y_max+offset, "white[white]")

data = np.transpose(np.vstack([depthFusionData.time/3600., depthFusionData.depth]))
data_ref = np.transpose(np.vstack([missionData.time/3600., missionData.depth]))

data_piston = np.transpose(np.vstack([pistonStateData.time/3600., pistonStateData.position*tick_to_volume*1e6]))

vibes.beginDrawing()
newFigure("Depth regulation")
vibes.drawLine(data.tolist(), "black")
vibes.drawLine(data_ref.tolist(), "red")
vibes.axisAuto()
# vibes.drawLine([[0,0.3],[4360,0.3]])
vibes.saveImage(file_directory + 'float_regulation.svg')

#######################################

y_min = -1.*tick_to_volume*1e6
y_max = 2400.*tick_to_volume*1e6
newFigure("Piston state")
vibes.drawLine(data_piston.tolist(), "black")
vibes.axisAuto()
vibes.saveImage(file_directory + 'float_regulation_piston.svg')

#######################################

depth_factor = 1e2
depth_offset = 9.5
time_scale = 60
time_offset = 7.88*3600./time_scale

t_lb = 7.88*3600./time_scale
t_ub = 8.12*3600./time_scale
y_min = (9.485 -depth_offset)*depth_factor
y_max = (9.505 -depth_offset)*depth_factor
x_min = t_lb - time_offset
x_max = t_ub - time_offset

newFigure("Depth regulation zoom")
lb = np.where(depthFusionData.time <= np.max((1,time_scale*t_lb)))[0][-1]
ub = np.where(depthFusionData.time >= np.min((depthFusionData.time[-1],time_scale*t_ub)))[0][0]
print(lb, ub)

data_zoom = np.transpose(np.vstack([depthFusionData.time[lb:ub]/time_scale-time_offset, (depthFusionData.depth[lb:ub]-depth_offset)*depth_factor]))
vibes.drawLine(data_zoom.tolist(), "black")

lb = np.where(missionData.time <= np.max((1,time_scale*t_lb)))[0][-1]
ub = np.where(missionData.time >= np.min((missionData.time[-1],time_scale*t_ub)))[0][0]
data_mission_zoom = np.transpose(np.vstack([missionData.time[lb:ub]/time_scale-time_offset, (missionData.depth[lb:ub]-depth_offset)*depth_factor]))
vibes.drawLine(data_mission_zoom.tolist(), "red")

vibes.saveImage(file_directory + 'float_regulation_zoom.svg')

###
# ti=280*5
# tf=3500*5
# data_chi = np.transpose(np.vstack([time_kalman[ti:tf], np.array(kalman_chi[ti:tf])*1e6]))
# data_offset = np.transpose(np.vstack([time_kalman[ti:tf], np.array(kalman_offset[ti:tf])*1e6]))
# # data_chi_cov = np.transpose(np.vstack([time_kalman[ti:tf], np.array(kalman_cov_chi[ti:tf])]))
# # data_offset_cov = np.transpose(np.vstack([time_kalman[ti:tf], np.array(kalman_cov_offset[ti:tf])]))

# #t = 280 -> 3640
# x_min = ti/5.-1. # for display
# x_max = tf/5.+1

# y_min = 240.*tick_to_volume*1e6
# y_max = 400.*tick_to_volume*1e6
# newFigure("Offset")
# vibes.drawLine(data_offset.tolist(), "black")
# # vibes.axisAuto()
# vibes.saveImage(file_directory + 'float_offset.svg')

# y_min = -60.*tick_to_volume*1e6
# y_max = 70.*tick_to_volume*1e6
# newFigure("Chi")
# vibes.drawLine(data_chi.tolist(), "black")
# # vibes.axisAuto()
# vibes.saveImage(file_directory + 'float_chi.svg')

# newFigure("Offset_Cov")
# y_min = -60.*tick_to_volume*1e6
# y_max = 70.*tick_to_volume*1e6
# vibes.drawLine(data_chi_cov.tolist(), "black")
# vibes.axisAuto()
# vibes.saveImage(file_directory + 'float_offset_cov.svg')


vibes.endDrawing()


