#!/usr/bin/env python
'''
Created on Aug 3, 2015

@author: annette

'''
from gevent import monkey; monkey.patch_all()
import json, time, threading, logging.config, sys

from bottle import route, run, template, static_file, request, response

from tools import helper
import core as core
import global_var as gl
import config as conf
from inputData import inputDataManager as inputDataManager


@route('/')
def index():
    #ipaddr = socket.gethostbyname(socket.gethostname())
    ids = gl.oesunits.keys()
    return template('log',
                    admintext="APIS HW emulator",
                    title="APIS HW emulator",
                    #ip= ipaddr,
                    ids=sorted(ids)
                    )
    


@route('/restart')
def getInitJsonFile():
    while gl.sema:
        time.sleep(0.01)
    gl.sema=True
    with open("jsontmp/fakeResponse.json") as json_init_file:
        gl.oesunits = json.load(json_init_file)
    for i in gl.oesunits:
        gl.oesunits[i]["oesunit"]["display"]=gl.displayNames[i]
        gl.is_ACCharging[i] = False
        gl.is_bypassMode[i] = False
        gl.acloss[i] = 0
        gl.dcloss[i] = 0
        gl.wasted[i] = 0
        #logger.debug(oesunits)
    gl.sema=False  
    return gl.oesunits

@route('/add/unit')
def addUnit():
    while gl.sema :
        time.sleep(0.01)
    gl.sema=True
    with open("jsontmp/standard.json") as json_unit_file:
        oesunits_add_unit = json.load(json_unit_file)
        add_id = "E{0:03d}".format(len(gl.oesunits)+1)
        oesunits_add_unit["oesunit"]["ip"] = oesunits_add_unit["oesunit"]["ip"][:-1]+str((len(gl.oesunits)))
        oesunits_add_unit["oesunit"]["display"] = gl.displayNames[add_id]
        oesunits_add_unit["oesunit"]["id"] = add_id
        gl.oesunits[add_id] = oesunits_add_unit
        gl.is_ACCharging[add_id] = False
        gl.is_bypassMode[add_id] = False
        gl.acloss[add_id] = 0
        gl.dcloss[add_id] = 0
        gl.wasted[add_id] = 0
    #logger.debug(gl.oesunits.keys())
    gl.sema=False
    return gl.oesunits

@route('/remove/unit')
def removeUnit():
    while gl.sema :
        time.sleep(0.01)
    gl.sema=True
    del_id = "E{0:03d}".format(len(gl.oesunits))
    del gl.oesunits[del_id]
    logger.debug(gl.oesunits.keys())
    gl.sema=False
    return gl.oesunits

@route('/get/log')
def getLog():
    #logger.debug( "log request received")
    response.content_type = 'application/json'
    while gl.sema :
        time.sleep(0.01)
    return gl.oesunits

@route('/get/last')
def getLastJsonFile():
    while gl.sema :
        time.sleep(0.01)
    gl.sema=True
    with open("jsontmp/lastSave.json") as json_last_file:
        gl.oesunits = json.load(json_last_file)
        logger.debug(gl.oesunits)
    gl.sema=False
    return gl.oesunits

@route('/save')
def setJsonFile():
    with open("jsontmp/lastSave.json", 'w') as json_file:
        json.dump(gl.oesunits, json_file)
        logger.debug(gl.oesunits)
    return gl.oesunits
    
def convert_dict_(src, keys):
    dst = {}
    for k in keys:
        v = src.get(k)
        if v is not None:
            dst[k] = v
    return dst
def convert_dcdc_status_(src): return convert_dict_(src, ['status', 'alarmState', 'operationMode'])
def convert_dcdc_meter_(src): return convert_dict_(src, ['wg', 'tmp', 'vb', 'wb', 'vg', 'ib', 'ig'])
def convert_dcdc_vdis_(src): return convert_dict_(src, ['dvg', 'drg'])
def convert_dcdc_param_(src): return convert_dict_(src, ['dig'])
def convert_dcdc_(src):
    dst = {}
    if src.get('status') is not None: dst['status'] = convert_dcdc_status_(src['status'])
    if src.get('meter') is not None: dst['meter'] = convert_dcdc_meter_(src['meter'])
    if src.get('vdis') is not None: dst['vdis'] = convert_dcdc_vdis_(src['vdis'])
    if src.get('param') is not None: dst['param'] = convert_dcdc_param_(src['param'])
    return dst

@route('/get/unit/<oesid>')
def getRemote(oesid):
    response.content_type = 'application/json'
    # return gl.oesunits[oesid]
    result = {}
    for k, v in gl.oesunits.get(oesid, {}).items():
        result[k] = convert_dcdc_(v) if k == 'dcdc' else v
    return result

@route('/get/emu/<oesid>')
def getRemoteEmu(oesid):
    response.content_type = 'application/json'
    return gl.oesunits[oesid]["emu"]

@route('/get/dcdc/status/<oesid>')
def getDCDCStatus(oesid):
    response.content_type = 'application/json'
    # json={}
    # json["meter"]=gl.oesunits[oesid]["dcdc"]["meter"]
    # json["status"]={"runningState": gl.oesunits[oesid]["dcdc"]["status"]["runningState"],
    #                 "operationMode": gl.oesunits[oesid]["dcdc"]["status"]["operationMode"],
    #                 "alarmState": gl.oesunits[oesid]["dcdc"]["status"]["alarmState"]}
    # return json
    dcdc = gl.oesunits.get(oesid, {}).get('dcdc', {})
    result = {}
    if dcdc.get('status') is not None: result['status'] = convert_dcdc_status_(dcdc['status'])
    if dcdc.get('meter') is not None: result['meter'] = convert_dcdc_meter_(dcdc['meter'])
    return result

@route('/get/dcdc/<oesid>')
def getDCDC(oesid):
    response.content_type = 'application/json'
    return gl.oesunits[oesid]["dcdc"]

@route('/get/acc')
def getAcc():
    return json.dumps(gl.acc)

@route('/set/acc/<newacc>')
def setAcc(newacc):
    gl.acc = int(newacc)
    return json.dumps(gl.acc)

@route('/set/emu/<oesid>')
def setEmu(oesid):
    for key in request.query:
        value=helper.convert(request.query[key])
        if key in gl.oesunits[oesid]["emu"] :
            gl.oesunits[oesid]["emu"][key] = float(value)
        else :
            return "following key not found: "+key
    return gl.oesunits

@route('/set/dcdc/<oesid>', method='GET')
def setDcdc(oesid):
    while gl.sema :
        time.sleep(0.01)
    gl.sema=True
    mode = helper.convert(request.query.mode)
    dig = helper.convert(request.query.dig)
    dvg = helper.convert(request.query.dvg)
    drg=None
    if "drg" in dict(request.query):
        drg = float(helper.convert(request.query.drg))
    else:
        drg = gl.oesunits[oesid]["dcdc"]["vdis"]["drg"]
    if conf.debug : 
        logger.debug("setting oesunit "+oesid+ ": mode="+mode+", dig="+dig+", dvg="+dvg+", drg="+drg)
    if helper.convert(request.query.p1):
        p1 = helper.convert(request.query.p1)
        p2 = helper.convert(request.query.p2)
        gl.oesunits[oesid]["dcdc"]["powermeter"]["p1"]=float(p1)
        gl.oesunits[oesid]["dcdc"]["powermeter"]["p2"]=float(p2)
    if len(mode)!=6 or len(dig)<1 or len(dvg)<1:
        logger.warning("incorrect request")
        return None
    
    dvg=int(float(dvg))
    gl.oesunits[oesid]["dcdc"]["status"]["status"]=mode
    gl.oesunits[oesid]["dcdc"]["status"]["statusName"]=conf.modes[mode]
    gl.oesunits[oesid]["dcdc"]["status"]["operationMode"]=conf.modesOps[mode] 
    gl.oesunits[oesid]["dcdc"]["status"]["runningState"]=conf.modesRunning[mode]
    gl.oesunits[oesid]["dcdc"]["vdis"]["dvg"]=float(dvg)
    gl.oesunits[oesid]["dcdc"]["vdis"]["drg"]=float(drg)
    gl.oesunits[oesid]["dcdc"]["param"]["dig"]=float(dig)
    gl.sema=False
    
    currentBusVoltage=int(gl.oesunits[oesid]["dcdc"]["meter"]["vg"])
    # if voltage is not yet high, gradually ramp up
    if mode=="0x0014" and currentBusVoltage!= dvg :
        if gl.acc > 120:
            if conf.debug: logger.debug("no need to ramp up")
            core.rampUp(dvg,currentBusVoltage,0)
        else : 
            if conf.debug: logger.debug("need to ramp up")
            interval=120/float(gl.acc)
            t = threading.Thread(target=core.rampUp, args=(dvg,currentBusVoltage,interval,), name="rampUp")
            t.start()
    # else simulate power transfer: update all other dcdc meter readers directly
    else: 
        core.simulateMeter()
    
    # return gl.oesunits[oesid]["dcdc"]
    return convert_dcdc_(gl.oesunits.get(oesid, {}).get('dcdc', {}))

@route('/set/dcdc/voltage/<oesid>', method='GET')
def setDcdcVoltage(oesid):
    while gl.sema :
        time.sleep(0.01)
    gl.sema=True
    dvg = helper.convert(request.query.dvg)
    drg=None
    if "drg" in dict(request.query):
        drg = float(helper.convert(request.query.drg))
    else:
        drg = gl.oesunits[oesid]["dcdc"]["vdis"]["drg"]
    logger.debug("setting voltage oesunit "+oesid+ "dvg="+dvg)
    status = gl.oesunits[oesid]["dcdc"]["status"]["status"]
    if len(dvg)<1:# :or status != "0x0014":
        logger.warning("incorrect request ")#(emulator only allows this command for status=0x0014)")
        return None
    
    dvg=int(float(dvg))
    gl.oesunits[oesid]["dcdc"]["vdis"]["dvg"]=float(dvg)
    gl.oesunits[oesid]["dcdc"]["vdis"]["drg"]=float(drg)
    gl.sema=False
    
    currentBusVoltage=int(gl.oesunits[oesid]["dcdc"]["meter"]["vg"])
    # if voltage is not yet high, gradually ramp up
    if status=="0x0014" and currentBusVoltage!= dvg :
        logger.debug("need to ramp up")
        interval=120/float(gl.acc)
        t = threading.Thread(target=core.rampUp, args=(dvg,currentBusVoltage,interval,), name="rampUp")
        t.start()
    # else simulate power transfer: update all other dcdc meter readers directly
    else: 
        core.simulateMeter()
    
    # return {"meter":gl.oesunits[oesid]["dcdc"]["meter"],"vdis":gl.oesunits[oesid]["dcdc"]["vdis"]}
    dcdc = gl.oesunits.get(oesid, {}).get('dcdc', {})
    result = {}
    if dcdc.get('meter') is not None: result['meter'] = convert_dcdc_meter_(dcdc['meter'])
    if dcdc.get('vdis') is not None: result['vdis'] = convert_dcdc_vdis_(dcdc['vdis'])
    return result

@route('/set/dcdc/current/<oesid>', method='GET')
def setDcdcCurrent(oesid):
    while gl.sema :
        time.sleep(0.01)
    gl.sema=True
    dig = helper.convert(request.query.dig)
    logger.debug("setting current oesunit "+oesid+ "dig="+dig)
    #status = gl.oesunits[oesid]["dcdc"]["status"]["status"]
    if len(dig)<1 :
        logger.warning("incorrect request")
        return None
    #if (status=="0x0000" or status=="0x0014" ):
    #    logger.warning("incorrect request (emulator only allows this command for status=0x0002 or 0x0041)")
    #    return None
    
    gl.oesunits[oesid]["dcdc"]["param"]["dig"]=float(dig)
    gl.sema=False
    
    core.simulateMeter()
    
    # return {"meter":gl.oesunits[oesid]["dcdc"]["meter"],"param":gl.oesunits[oesid]["dcdc"]["param"]}
    dcdc = gl.oesunits.get(oesid, {}).get('dcdc', {})
    result = {}
    if dcdc.get('meter') is not None: result['meter'] = convert_dcdc_meter_(dcdc['meter'])
    if dcdc.get('param') is not None: result['param'] = convert_dcdc_param_(dcdc['param'])
    return result



#####
# resources
#####
      
@route('/js/<filename>')
def js_static(filename):
    return static_file(filename, root='./js')

@route('/img/<filename>')
def img_static(filename):
    return static_file(filename, root='./img')

@route('/css/<filename>')
def img_static_css(filename):
    return static_file(filename, root='./css')

#Static Files
@route('/static/<filepath:path>')
def static(filepath):
    return static_file(filepath, root="./static")
  
########################################
### init functions
########################################

def initializeOESUnits(args):
    if len(args)>=1:
        addNUnits(int(args[0]))
    else:
        addNUnits(len(gl.displayNames))          
    #else :
    #   getInitJsonFile()
        
def addNUnits(n):
    for i in range(n) :
        addUnit()
    logger.debug("starting off with "+str(n)+ " units.")
    
def startWebServer():
    run(server='gevent', host=conf.b_host, port=conf.b_port, quiet=False, reloader=False)
    
             
def main(args):
    try:
        if conf.doUpdates :
            gl.inData = inputDataManager(conf.dataSet)
            initializeOESUnits(args)
            t = threading.Thread(target=startWebServer, name="tornado")
            t.daemon = True
            t.start()
            time.sleep(1)
            logging.getLogger("tornado.access").setLevel(logging.WARN)
            core.updatePowerFlow()  
            logger.debug("emulator has finished, stop tornado too")
            gl.analyserObject.writeToCSV()
            t.kill_received = True
        else:
            gl.acc=1
            initializeOESUnits(args)
            startWebServer()
            
    except KeyboardInterrupt:
        logger.info( "Ctrl-c received! Sending kill to threads...")
        gl.analyserObject.writeToCSV()
        t.kill_received = True
    #except :
    #    logger.info( "error happened"  + str(sys.exc_info()[:2] ))
    #    t.kill_received = True
    
if __name__ == "__main__":
    logging.config.fileConfig("config/logger.conf",disable_existing_loggers=False)
    logger = logging.getLogger(__name__)
    #disable logging of http requests
    logging.getLogger("requests").setLevel(logging.WARN)


    main(sys.argv[1:])
