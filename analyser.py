'''
Created on Aug 3, 2015

@author: annette
'''
import config as conf
import global_var as gl
import json, csv, requests
import logging.config
logger = logging.getLogger(__name__)

class analyserClass:
    def __init__(self):
        self.initDailyVal()
        self.indivLog = []
        self.summaryLog = []
        self.lastAvgRSOC = 50
        self.sumUntilNow =[]
        #with open(conf.csvPath, 'w') as f:
        #    f.write("time,pv,demand,acin,wasted,acloss,dcloss,loss,deltaBatt,ssr_real,ssr_pv,r_utility\n")
            
    
    def analyseAndLog(self):
        self.accumulate()
        #keep daily summary in memory        
        #if we have passed to a new day, sum up everything and add to summary
        if gl.now.date() > self.day :
            self.summaryToMemory()
            self.lastAvgRSOC = self.cumul["avgrsoc"]
            #set all values  back to 0
            self.initDailyVal()
            
        #keep individual log in memory (only do that if we plan to save it to DB)
        if conf.saveIndividualToCSV : 
            self.indivToMemory()
        #send info to DB (only used for environment testing mode)
        if conf.saveIndividualToDB : 
            #copy oesunit object and add loss information
            extendedOesCopy=gl.oesunits.copy()
            for i in extendedOesCopy:
                extendedOesCopy[i]["emul"] = {"acloss":gl.acloss[i], "dcloss":gl.dcloss[i], "loss":gl.dcloss[i]+gl.acloss[i], "wasted":gl.wasted[i]}
                requests.post (conf.dburl, data = json.dumps(extendedOesCopy))
            
        
    def accumulate(self):
        self.cumul["avgrsoc"] = 0
        convertToWh = float(gl.acc)/3600
        for i in gl.oesunits:
            self.cumul["pv"] += gl.oesunits[i]["emu"]["pvc_charge_power"]*convertToWh
            self.cumul["demand"] += gl.oesunits[i]["emu"]["ups_output_power"]*convertToWh
            self.cumul["acin"] += gl.oesunits[i]["dcdc"]["powermeter"]["p2"]*convertToWh
            self.cumul["wasted"] += gl.wasted[i]*convertToWh
            self.cumul["acloss"] += gl.acloss[i]*convertToWh
            self.cumul["dcloss"] += gl.dcloss[i]*convertToWh
            self.cumul["loss"] += (gl.dcloss[i]+gl.acloss[i])*convertToWh
            self.cumul["avgrsoc"] += gl.oesunits[i]["emu"]["rsoc"]
            if gl.oesunits[i]["dcdc"]["meter"]["wg"] > 0:
                self.cumul["wg"] += gl.oesunits[i]["dcdc"]["meter"]["wg"]*convertToWh
        self.cumul["avgrsoc"] = self.cumul["avgrsoc"] / len(gl.oesunits)
       
 
  
    def summaryToMemory(self):
        #how much energy has been stored in the battery since beginning of the day
        self.ratio["deltaBatt"] = int(float(self.cumul["avgrsoc"] -self.lastAvgRSOC)*sum(conf.batterySize.values())/100)
        # self sufficiency in reality
        self.ratio["ssr_real"] = round(float(self.cumul["demand"] - self.cumul["acin"] + self.ratio["deltaBatt"])/self.cumul["demand"],4)
        # self sufficiency without AC losses
        self.ratio["ssr_pv"] = round(float(self.cumul["pv"] + self.ratio["deltaBatt"])/self.cumul["demand"],4)
        # self sufficiency without AC losses
        if not self.cumul["pv"]==0: 
            self.ratio["sor"] = round(float(self.cumul["pv"])/(self.cumul["pv"]+self.cumul["wasted"]),4)
        # utility ratio : AC_Input/ AC_Output
        self.ratio["r_utility"] = round(float(self.cumul["acin"] - self.ratio["deltaBatt"])/self.cumul["demand"],4)
        
        l=[]
        l.append(str(self.day))
        l.append(int(self.cumul["pv"]))
        l.append(int(self.cumul["demand"]))
        l.append(int(self.cumul["acin"]))
        l.append(int(self.cumul["wasted"]))
        l.append(int(self.cumul["acloss"]))
        l.append(int(self.cumul["dcloss"]))
        l.append(int(self.cumul["loss"]))
        l.append(int(self.cumul["avgrsoc"]))
        l.append(int(self.cumul["wg"]))
        l.append(int(self.ratio["deltaBatt"]))
        l.append(self.ratio["ssr_real"])
        l.append(self.ratio["ssr_pv"])
        l.append(self.ratio["sor"])
        l.append(self.ratio["r_utility"])
        self.summaryLog.append(l)
        

        logger.debug("Analysis for this day:"+ str(l))
        if  len(self.sumUntilNow)==0: #initalize
            self.sumUntilNow.append("sum")
            for i in range(1,len(l)):
                self.sumUntilNow.append(l[i])
        else:
            for i in range(1,len(l)):
                self.sumUntilNow[i]+=l[i]
        #with open(conf.csvPath, 'a') as f:
        #    f.write(",".join(map(str, list))+"\n")

    
    def initDailyVal(self):   
        self.cumul = {"pv":0, "demand":0, "acin":0, "wasted":0, "acloss":0, "dcloss":0, "loss":0, "avgrsoc":0, "wg":0}
        self.ratio = { "deltaBatt":0, "ssr_real":0, "ssr_pv":0,"sor":0, "r_utility":0}
        self.day = gl.now.date()
                 
    
    def indivToMemory(self):
        for key, val in gl.oesunits.items():
            l=[]
            l.append(key)
            l.append(str(gl.now))
            l.append(val["oesunit"]["display"])
            l.append(val["emu"]["rsoc"])
            l.append(val["emu"]["pvc_charge_power"])
            l.append(val["emu"]["ups_output_power"])
            l.append(val["emu"]["charge_discharge_power"])
            l.append(val["dcdc"]["meter"]["wg"])
            l.append(val["dcdc"]["powermeter"]["p2"])
            self.indivLog.append(l)

    def writeToCSV(self):
        logger.debug("writing to csv")
        if conf.saveIndividualToCSV : 
            self.indivToMemory()
            with open(conf.indivLogPath, "wb") as f:
                writer = csv.writer(f)
                writer.writerow(["id", "time", "oesunit_id", "emu_rsoc", "emu_pvc_charge_power", "emu_ups_output_power","charge_discharge_power","dcdc_meter_wg","dcdc_powermeter_p2" ])
                writer.writerows(self.indivLog)
        if conf.saveToSummaryToCSV : 
            #self.summaryToMemory()
            with open(conf.summaryPath, 'wb') as f:
                writer = csv.writer(f)
                writer.writerow(["time","pv", "demand", "acin", "wasted", "acloss", "dcloss","loss", "avgrsoc","wg","deltaBatt","ssr_real" ,"ssr_pv","sor","r_utility"])
                writer.writerows(self.summaryLog)
                logger.debug(self.sumUntilNow)
                #add sum of all in the end
                writer.writerow(self.sumUntilNow)
                #add average
                self.sumUntilNow[0]="avg"
                for i in range(1,len(self.sumUntilNow)):
                    self.sumUntilNow[i]/=len(self.summaryLog)
                logger.debug(self.sumUntilNow)
                writer.writerow(self.sumUntilNow)
                
                
    
    def __str__(self):
        return str(gl.now) + " ratio:"+json.dumps(self.ratio) + " cumul: "+json.dumps(self.cumul)
       