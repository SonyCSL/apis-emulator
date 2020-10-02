'''
Created on Aug 3, 2015

@author: annette
'''

import logging.config, time
from datetime import timedelta
logger = logging.getLogger(__name__)

import global_var as gl
import config as conf
import analyser

 

#############################################
##### background thread that lets time pass
##############################################
def updatePowerFlow():
    stopCondition=True
    gl.analyserObject = analyser.analyserClass()
    # every one second update time, the external parameter (pv and demand) and soc level
    while stopCondition:
        #logger.debug(gl.now)
        #put a semaophore to avoid changing oesunits from webinterface while updating
        while gl.sema :
            time.sleep(0.01)
        gl.sema=True
        # update the PV according to input data
        if not gl.inData.pvcUpdate():
            logger.debug("PV Input data is finished. Stopping.")
            stopCondition=False
        # update the power demand
        if not gl.inData.demandUpdate():
            logger.debug("Demand Input data is finished. Stopping.")
            stopCondition=False
        #update the UPS status depending on SOC level
        stateUpdate()
        #update losses and Battery power flow
        lossesAndBatteryFlow(accumulateLosses=True)      
        #update the time string and the hour-counter that depends on the acceleration
        timeUpdate()
        # now update SOC
        rsocUpdate()
        # stats so far
        analysis()  
            
        gl.sema=False
        time.sleep(conf.sleeptime)

def stateUpdate():
    ### There are two conditions: Battery mode and Bypass mode
    for oesid in gl.oesunits :
        # set is_bypassMode Flag
        if (gl.oesunits[oesid]["emu"]["rsoc"] <= conf.UPS_TRIGGER_BATT_OFF):
            gl.is_bypassMode[oesid] = True
            gl.oesunits[oesid]["emu"]["ups_operation_mode"]["mode"]=5
        if (gl.oesunits[oesid]["emu"]["rsoc"] >= conf.UPS_TRIGGER_BATT_ON):
            gl.is_bypassMode[oesid] = False
            gl.oesunits[oesid]["emu"]["ups_operation_mode"]["mode"]=2
        # set is_ACCharging Flag
        if (gl.oesunits[oesid]["emu"]["rsoc"] <= conf.UPS_TRIGGER_AC_ON):
            if conf.debug:
                logger.debug("ac charging on")
            gl.is_ACCharging[oesid] = True
        if (gl.oesunits[oesid]["emu"]["rsoc"] >= conf.UPS_TRIGGER_AC_OFF):
            gl.is_ACCharging[oesid] = False


def lossesAndBatteryFlow(accumulateLosses=False):
    for i in gl.oesunits :
        
        ### ------------ Losses ----------- ###
        
        #ESS loss + DCDC loss
        gl.dcloss[i] = conf.constantSystemLoss + (gl.oesunits[i]["dcdc"]["meter"]["wg"]-gl.oesunits[i]["dcdc"]["meter"]["wb"])
        
        # Trans loss 
        gl.acloss[i] = conf.transLoss_c
        
        #add mode specific UPS losses
        if gl.is_bypassMode[i] : 
            gl.acloss[i] += conf.bypassModeLoss_c + (conf.bypassModeLoss_a + conf.transLoss_a)*gl.oesunits[i]["emu"]["ups_output_power"]
            gl.oesunits[i]["dcdc"]["powermeter"]["p2"] = int(gl.oesunits[i]["emu"]["ups_output_power"] + gl.acloss[i])
        else :
            gl.dcloss[i] += conf.battModeLoss_c + conf.battModeLoss_a*gl.oesunits[i]["emu"]["ups_output_power"]
            gl.oesunits[i]["dcdc"]["powermeter"]["p2"] = int(gl.acloss[i])

        # calculate p2 (add ac charging power flow )
        if gl.is_ACCharging[i]:
            gl.acloss[i] += conf.ACChargeLoss
            gl.oesunits[i]["dcdc"]["powermeter"]["p2"] += int(conf.ACChargeAmount + conf.ACChargeLoss)


        ### ------------ Battery Power Flow including losses----------- ###
        outpower = gl.oesunits[i]["emu"]["ups_output_power"] - gl.oesunits[i]["dcdc"]["meter"]["wg"] + gl.dcloss[i]
        
        #battery is already full but pv produces more than outgoing power
        if gl.oesunits[i]["emu"]["rsoc"] >= 100 and outpower < gl.oesunits[i]["emu"]["pvc_charge_power"]:
            gl.oesunits[i]["emu"]["charge_discharge_power"]=0
            gl.wasted[i] = gl.oesunits[i]["emu"]["pvc_charge_power"]-outpower
            if conf.debug:
                logger.debug(i+": battery full-> rsoc="+str(gl.oesunits[i]["emu"]["rsoc"])+ ", potential pv "+ str(gl.oesunits[i]["emu"]["pvc_charge_power"])+ " but really used "+str(outpower))
            gl.oesunits[i]["emu"]["pvc_charge_power"] = round(outpower,2)
        
        #if battery is not yet full or outgoing power is smaller than pv power
        else :
            gl.wasted[i]=0
        #calculate charge_discharge power (always positive!)
            powerflowToBattery = gl.oesunits[i]["dcdc"]["meter"]["wg"] + \
                                 gl.oesunits[i]["emu"]["pvc_charge_power"] + \
                                 gl.oesunits[i]["dcdc"]["powermeter"]["p2"] - \
                                 gl.oesunits[i]["emu"]["ups_output_power"] - \
                                 gl.acloss[i] -\
                                 gl.dcloss[i]
            # batteryFlow is always positive !
            if powerflowToBattery > 0:
                gl.oesunits[i]["emu"]["charge_discharge_power"] = round(powerflowToBattery,2)
                gl.oesunits[i]["emu"]["battery_current"] = round(gl.oesunits[i]["emu"]["charge_discharge_power"]/conf.batteryVoltage,2)
                #logger.debug( i+ ": charge_disch "+ str(gl.oesunits[i]["emu"]["charge_discharge_power"]) + ", ACLoss: "+str(ACLoss) + ", DCLoss: " +str(DCLoss))
            else :
                gl.oesunits[i]["emu"]["charge_discharge_power"] = - round(powerflowToBattery,2)
                gl.oesunits[i]["emu"]["battery_current"] = -round(gl.oesunits[i]["emu"]["charge_discharge_power"]/conf.batteryVoltage,2)
                #logger.debug( i+ ": charge_disch "+ str(-gl.oesunits[i]["emu"]["charge_discharge_power"]) + ", ACLoss: "+str(ACLoss) + ", DCLoss: " +str(DCLoss))
            

def rsocUpdate():
    battery={}
    for oesid in gl.oesunits :
        # calculate the remaining batteries and (dis)charge them 
        battery[oesid]=gl.oesunits[oesid]["emu"]["rsoc"]*conf.batterySize[oesid]/100 # remaining Wh
        if gl.oesunits[oesid]["emu"]["battery_current"] >0 :
            battery[oesid]+=gl.acc*gl.oesunits[oesid]["emu"]["charge_discharge_power"]/3600 # remaining Wh + current battery inflow
        else: 
            battery[oesid]-=gl.acc*gl.oesunits[oesid]["emu"]["charge_discharge_power"]/3600 # remaining Wh + current battery inflow
        #print "battery remaining"+oesid + " : "+str(battery[oesid]) + ", "+str(gl.oesunits[oesid]["emu"]["charge_discharge_power"])
        # convert the remaining batteries to rsoc after considering the limits
        if battery[oesid]<0: #should never happen
            logger.error(str(gl.now)+" : " +oesid+ " : remaining capacity = "+str(int(battery[oesid])) +"Wh < 0Wh ")
            gl.oesunits[oesid]["emu"]["rsoc"]=0.0
            gl.oesunits[oesid]["dcdc"]["powermeter"]["p2"]-=int(battery[oesid])
            
        elif battery[oesid]>conf.batterySize[oesid]:
            gl.oesunits[oesid]["emu"]["rsoc"]=100.0
            gl.wasted[oesid] = battery[oesid] - conf.batterySize[oesid]
            if conf.debug:
                logger.debug(oesid+": battery just got full. wasted="+str(gl.wasted[oesid]))
        else:
            gl.oesunits[oesid]["emu"]["rsoc"]=round(battery[oesid]*100/conf.batterySize[oesid],2)
        #logger.debug("RSOC of unit"+ str(oesid)+" : "+ str(gl.oesunits[oesid]["emu"]["rsoc"]))

def analysis():
    gl.analyserObject.analyseAndLog()
    if conf.debug:
        logger.debug(str(gl.analyserObject))


        #logger.debug(p.text) 
    
def timeUpdate():
    gl.count_s += gl.acc
    gl.now=gl.startTime + timedelta(seconds=gl.count_s)
    timestr=gl.now.strftime("%Y/%m/%d-%H:%M:%S")
    #now=str(gl.startTime + timedelta(hours=gl.count_h))
    #logger.debug(now)
    for oesid in gl.oesunits:
        gl.oesunits[oesid]["time"]=timestr


#############################################
##### simulate power transfer
##############################################

def rampUp(dvg,startingBusVoltage,interval):
    if interval<=1:
        for oesid in gl.oesunits :
            gl.oesunits[oesid]["dcdc"]["meter"]["vg"]=dvg
    else:
        nbrsteps=int(interval*float(dvg-startingBusVoltage)/dvg)
        currentBusVoltage=float(startingBusVoltage)
        for i in range(nbrsteps):
            while gl.sema :
                time.sleep(0.01)
            gl.sema=True
            currentBusVoltage+=float(dvg-startingBusVoltage)/nbrsteps
            for oesid in gl.oesunits :
                gl.oesunits[oesid]["dcdc"]["meter"]["vg"] = int(currentBusVoltage)
            if conf.debug: logger.debug("ramping up. Current vg "+ str(gl.oesunits[oesid]["dcdc"]["meter"]["vg"]))
            gl.sema=False
            time.sleep(1)
    
    if conf.debug: logger.info("ramping up finished")

    while gl.sema :
        time.sleep(0.01)
    gl.sema=True
    #set all voltages high
    for oesid in gl.oesunits :
        gl.oesunits[oesid]["dcdc"]["meter"]["vg"]=dvg
    
    #this updates all other meter reader values
    simulateMeter()
    gl.sema=False
    


def simulateMeter():
    setDcdcVoltages()
    setDcdcCurrents()
    setDcdcPower()

def getAutonomous():
    for i in gl.oesunits :
        if gl.oesunits[i]["dcdc"]["status"]["status"]=="0x0014":
            return i
    return -1

def setDcdcVoltages():
    auto = getAutonomous()
    value =0

    if auto>=0 :
        value=gl.oesunits[auto]["dcdc"]["vdis"]["dvg"]

    for i in gl.oesunits :
        gl.oesunits[i]["dcdc"]["meter"]["vg"]=value

def setDcdcCurrents():
    auto = getAutonomous()    
    if auto>=0:
        sumI = 0
        for i in gl.oesunits :
            mode=gl.oesunits[i]["dcdc"]["status"]["status"]
            if mode=="0x0002": #discharge ->negative
                sumI = sumI - gl.oesunits[i]["dcdc"]["param"]["dig"]
                gl.oesunits[i]["dcdc"]["meter"]["ig"]=-gl.oesunits[i]["dcdc"]["param"]["dig"]
            elif mode=="0x0041": #charge=positive
                sumI = sumI + gl.oesunits[i]["dcdc"]["param"]["dig"]
                gl.oesunits[i]["dcdc"]["meter"]["ig"]=gl.oesunits[i]["dcdc"]["param"]["dig"]
            elif mode=="0x0000": #charge=positive
                gl.oesunits[i]["dcdc"]["meter"]["ig"]=0
        gl.oesunits[auto]["dcdc"]["meter"]["ig"]= - sumI
    else :
        for i in gl.oesunits :
            gl.oesunits[i]["dcdc"]["meter"]["ig"]=0
            
def setDcdcPower():
    for i in gl.oesunits:
        #set grid power
        gl.oesunits[i]["dcdc"]["meter"]["wg"]=gl.oesunits[i]["dcdc"]["meter"]["ig"]*gl.oesunits[i]["dcdc"]["meter"]["vg"]
        #if standby
        if gl.oesunits[i]["dcdc"]["status"]["status"]=="0x0000": #charge=positive:
            dcloss=conf.DCCstLoss # only constant losses
        #charging
        elif gl.oesunits[i]["dcdc"]["status"]["status"]=="0x0041" :
            dcloss=conf.DCChargeLoss # conversion losses
        #discharging (both autonomy and heteronmy discharge)
        else:
            dcloss=conf.DCDischargeLoss # conversion losses
        #get battery power, voltage and current
        gl.oesunits[i]["dcdc"]["meter"]["wb"] = gl.oesunits[i]["dcdc"]["meter"]["wg"]-dcloss
        gl.oesunits[i]["dcdc"]["meter"]["ib"] = round(gl.oesunits[i]["dcdc"]["meter"]["wb"]/conf.batteryVoltage,2)
        gl.oesunits[i]["dcdc"]["meter"]["vb"] = conf.batteryVoltage
        
        #update the UPS status depending on SOC level
        stateUpdate()
        #update battery Power flow
        lossesAndBatteryFlow(accumulateLosses=False)
