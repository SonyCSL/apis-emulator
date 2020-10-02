'''
Created on Aug 6, 2015

@author: annette
'''

import pandas as pd
import logging.config, datetime
from copy import deepcopy
import global_var as gl
import config as conf
logger = logging.getLogger(__name__)

class inputDataManager:

    def __init__(self, inputSet):
        #demandData=demandData
        #solarData=solarData
        #loadInputdata
        if inputSet=="Sample":
            gl.startTime= pd.datetime(2020, 1, 1, 0, 0, 0)
            gl.endTime= pd.datetime(2021, 1, 1, 0, 0, 0)
            gl.now = deepcopy(gl.startTime)
            #loadSample
            old_loadDemand_Sample()
            #define demand update
            self.demandUpdate = old_demandUpdate_Sample
            
                        #load solar radiation data
            loadSol_Sample()
            #define PV update
            self.pvcUpdate = old_pvcUpdate_Sample
            
            for emulid in gl.displayNames :
                conf.batterySize[emulid]=conf.default_batterySize
                conf.pvc_sol_reg[emulid]=conf.default_Area * conf.r * conf.pr
                
        else:
            logger.error("Could not read input data for "+inputSet )



############################
# load data from CSV
############################
    
def loadSol_Sample():
    global sol
    sol_data = pd.read_csv('data/input/Sample/sample_solar_data.csv')
    sol = pd.np.array(sol_data) 
    return sol


def old_loadDemand_Sample():
    global demand
    demand = {}
    demand_data = pd.read_csv('data/input/Sample/sample_load_data.csv')

    cusids = set(demand_data.ix[:,1])
    for i, cusid in enumerate(cusids):
        # takes all values per userid with a step of 2 [colum 6 to 53]
        demand_cusid = demand_data.ix[demand_data.ix[:,1]==cusid, range(6,len(demand_data.ix[0,:]),2)]
        cus_id = "E{0:03d}".format(i+1)
        demand[cus_id] = pd.np.array(demand_cusid)
        gl.displayNames[cus_id]="Sample_"+cus_id
    return demand

######################
# update functions to be used by emulator
######################

def old_pvcUpdate_Sample():
    count_h=float(gl.count_s)/3600
    weight = count_h-int(count_h)
    step_now=(int((count_h)/24)),int((count_h)%24)
    step_next=(int((count_h+1)/24)),int((count_h+1)%24)
    if int(count_h+1) >= sol.size :
        logger.debug("no more solar radiation data")
        return False
    for oesid in gl.oesunits:
        gl.oesunits[oesid]["emu"]["pvc_charge_power"]=round((1-weight)*sol[step_now]+ weight*sol[step_next],2) #sol[W]
    return True

def old_demandUpdate_Sample():
    count_h=float(gl.count_s)/3600
    weight = count_h-int(count_h)
    step_now=int((count_h)/24),int((count_h)%24)
    step_next=(int((count_h+1)/24),int((count_h+1)%24))
    if int(count_h+1) >= demand[gl.oesunits.keys()[0]].size:
        logger.debug("no more demand data")
        return False
    for oesid in gl.oesunits:
        gl.oesunits[oesid]["emu"]["ups_output_power"]=round(((1-weight)*demand[oesid][step_now] + weight*demand[oesid][step_next])*1000,2) #demand[W]
    return True


