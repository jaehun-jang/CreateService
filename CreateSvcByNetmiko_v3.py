#$Language="python"
#$Interface="1.0"

# "This program was created by Jhjang@hfrnet.com and anyone can modify and use it."
# This script sets a EVC, UNI and NNI.

from netmiko import ConnectHandler
from getpass import getpass
import pyautogui

ip = pyautogui.prompt("Enter the DUT IP Address: xxx.xxx.xxx.xxx", default = "192.168.0.1")

login ={
'device_type':'cisco_ios',
'ip':ip, 
'username':'root', 
'password':getpass(),
# "secret": 'enable'
}

# Connect to device
connection = ConnectHandler(**login)
print(connection.find_prompt())

## SUB FUNCTION ##
def checkProcuctType():
    showproduct = connection.send_command ("sh fruinfo system ")
    checkproduct = showproduct.split()
    search_string = 'M6424'
    if search_string in checkproduct:
        return 1
    else:
        return 0
    
def checkCmdResult(result):   # for word in checkcmd:
    checkcmd = result.split()
    result = [word for word in checkcmd if "^" in word or "%" in word]
    if len(result) != 0:
        pyautogui.alert('Wrong input detected! Correct the configutation')    
        return 

def changFlexP(rdResult_list,uType,fpg):
    if  rdResult_list != uType and uType == 'ethernet':
        chgtoeth = ["flexport-group " + fpg, "port-type ethernet"]
        result = connection.send_config_set (chgtoeth)
        print(result)
        checkCmdResult(result)
    elif  rdResult_list != uType and uType == 'cpri':
        chgtocpri = ["flexport-group " + fpg, "port-type cpri"]
        result=connection.send_config_set (chgtocpri)
        print(result)
        checkCmdResult(result) 
            
def CheckFlexP(uType,MapUni): # ('eth' or 'roe') , '1/1'                    
    if uType == 'eth':
        uType = 'ethernet'
    elif uType == 'roe':
        uType = 'cpri'  
    intNum = int(MapUni.split('/')[1])
    output = connection.send_command("sh flexport")     
    flexportgroup = round((intNum / 2) + 0.1)
    row = flexportgroup + 11
    rdResult = output.splitlines()[row].split()[2]
    fpg = str(flexportgroup)
    print(rdResult,uType,fpg)  #for debuging   
    changFlexP(rdResult,uType,fpg)    

def EplUNI(evc,uType,checkProduct):
    CreUni = pyautogui.prompt('Enter the UNI ID:','Create UNI', default='uni1')  
    MapUni = pyautogui.prompt('Select interface of UNI:','MAP Interface to UNI',default='1/1')
    if checkProduct == 1:
        CheckFlexP(uType,MapUni)    ## Flex-port check function(uType,MapUni)
    create_uni = ["ethernet uni add " + CreUni , " map interface " + MapUni , " add service " + evc]
    result=connection.send_config_set (create_uni )        
    print(result)
    checkCmdResult(result)
    return MapUni

def EplRoUNI(MapUni,sVlan):
    dMac = pyautogui.prompt("Enter the Dest MAC Add: ffff.ffff.ffff",default = '00:23:AA:FF:FF:FF') 
    create_roeuni = ["interface " + MapUni,
                    "roe cpri option 7",
                    "roe-agnostic tunnel enable",
                    "roe-agnostic encap dst-mac " + dMac,
                    "roe-agnostic encap vlan " + sVlan,
                    "roe-agnostic encap vlan priority 5",
                    "roe-agnostic enable"]
    result=connection.send_config_set (create_roeuni )
    print(result)
    checkCmdResult(result)   
    
def EvplUNI(evc,uType,checkProduct): 
    CreUni = pyautogui.prompt('Enter the UNI ID:','Create UNI', default='uni1')  
    MapUni = pyautogui.prompt('Select interface of UNI:','MAP Interface to UNI',default='1/1')
    if checkProduct == 1:
        CheckFlexP(uType,MapUni)    ## Flex-port check function(uType,MapUni)  
    cVlan = pyautogui.prompt('Enter the CVLAN:','Map CEVLAN to Service', default= "100")  
    epu = CreUni + "-" + evc
    creevpuni = ["ethernet uni add " + CreUni,
                 " map interface " + MapUni ,
                 " all-to-one-bundling disable",
                 " bundling enable ",
                 " multiplex enable ",
                " add service " + evc]	
    result=connection.send_config_set (creevpuni) 
    print(result)
    checkCmdResult(result) 	
    addcevlan = ["ethernet service end-point " + epu, "add vlan " + cVlan]
    result=connection.send_config_set (addcevlan) 
    print(result)
    checkCmdResult(result) 

def AddEvcToUNI(evc): 
    AddUni = pyautogui.prompt("Add SVC to UNI :", default = 'uni1') 
    addevpluni = ["ethernet uni " + AddUni, " add service " + evc]
    result=connection.send_config_set (addevpluni)
    print(result)
    checkCmdResult(result) 
    cVlan = pyautogui.prompt('Enter the CVLAN:','Map CEVLAN to Service', default= "100")        
    epu = AddUni + "-" + evc	
    addcevlan = ["ethernet service end-point " + epu, "add vlan " + cVlan]
    result=connection.send_config_set (addcevlan)
    print(result)
    checkCmdResult(result)  

def CreateNNI(evc): 
    cNni = pyautogui.prompt('Enter the new NNI ID:','Create NNI',default='nni1')    
    MapInt = pyautogui.prompt('Select interface of NNI:','MAP Interface to NNI',default ='1/25') 
    create_nni = ["ethernet nni add " + cNni , " map interface " + MapInt, " add service " + evc]
    result=connection.send_config_set (create_nni )
    print(result)
    checkCmdResult(result)   
    return cNni,MapInt 

def AddSvcToNni(evc): 
    aNni = pyautogui.prompt("Enter the NNI ID: nni1",'Add a service to an existing NNI', default = 'nni1') 	      
    addNni = ["ethernet nni " + aNni , "add service " + evc ]
    result=connection.send_config_set (addNni )
    print(result)
    checkCmdResult(result)

def SetBptp(nni,nnii):
    sVlan = pyautogui.prompt("Enter the SVLAN for BPTP:", default = '4001') 
    create_bptpsvlan = ["vlan " + sVlan, "ethernet service add bptp", "svlan "+ sVlan, "add nni " + nni]
    result=connection.send_config_set (create_bptpsvlan)
    print(result)
    checkCmdResult(result)  
    # Select BPTP Type ##  
    bptpType = pyautogui.confirm('"Select BPTP Type"', buttons=['Master', 'Slave'])
    pyautogui.alert('Wait a few seconds!')
    if bptpType == 'Master':
        config_master = [
                        "bptp configuration",
                        "bptp global-enable",
                        "bptp config clock ordinary profile g8275-1 domain 24",
                        "bptp port 1 sync-interval -7",
                        "bptp port 1 delayreq-interval -7",
                        "bptp config port 1 ethernet local-pri 64 vlan " + sVlan + " pri 7"
                        ]   
        result=connection.send_config_set (config_master)
        print(result)
        checkCmdResult(result)  
    if bptpType == 'Slave':
        config_slave = [
                        "bptp configuration",
                        "bptp clock source synce pri " + nnii,
                        "bptp global-enable",
                        "bptp clock priority1 200 priority2 210",
                        "bptp config clock ordinary profile g8275-1 domain 24",
                        "bptp port 1 sync-interval -7",
                        "bptp port 1 delayreq-interval -7",
                        "bptp config port 1 ethernet local-pri 200 vlan " + sVlan + " pri 7"
                        ]         
        result=connection.send_config_set (config_slave)
        print(result)
        checkCmdResult(result)


### MAIN FUNCTION ### 
def main(): 

    testContinue = 1 
    connection.enable() # 'enable' action

    while  testContinue == 1:
        try:
            sVlan = pyautogui.prompt("Enter the SVLAN ID: ",'Create SVLAN',default = '1001')
            result=connection.send_config_set("vlan " + sVlan )
            print(result)
            checkCmdResult(result)

            ## Create EVC ##    
            evc = pyautogui.prompt('Enter the EVC ID: evc1','Create Service',default = 'evc1')
            sType = pyautogui.confirm("Select Service type:","Select Service type",buttons=['epl', 'evpl'])          
            create_evc = ["ethernet service add "  + evc, "svlan " + sVlan, "service type " + sType]
            result=connection.send_config_set (create_evc )
            print(result)
            checkCmdResult(result)        
        
            ## Check Product Type ##
            checkProduct = checkProcuctType()
    
            ## Create UNI ##
            uType = ""
            if sType == "epl" and checkProduct == 1:
                uType = pyautogui.confirm("Select UNI type:",'Select the Service Type', buttons=['roe', 'eth'])        
                if uType == "roe":
                    MapUni = EplUNI(evc,uType,checkProduct)
                    EplRoUNI(MapUni,sVlan)
                elif uType == "eth":
                    EplUNI(evc,uType,checkProduct)
            elif sType == "epl" and checkProduct == 0:
                    EplUNI(evc,uType,checkProduct)
            elif sType == "evpl":
                SltUNI = pyautogui.confirm("Create UNI?",'Create an UNI' ,buttons=['Create UNI', 'Existing UNI'])
                if SltUNI == 'Create UNI':
                    EvplUNI(evc,uType,checkProduct)
                elif SltUNI == 'Existing UNI':
                    AddEvcToUNI(evc)        

            ## Create NNI ##
            nni = "nni1"
            nnii = "1/25" 
            CreNNI = pyautogui.confirm('Create NNI ?','Create a NNI', buttons=['Create NNI', 'Existing NNI'])
            print()
            if CreNNI == 'Create NNI':
                nni,nnii = CreateNNI(evc)
            elif CreNNI == 'Existing NNI':
                AddSvcToNni(evc)
        
            ## Config bPTP ## 
            if uType == "roe":
                SltBptp = pyautogui.confirm('Configure BPTP ?', buttons=['bptp', 'No'])
                if SltBptp == 'bptp':
                    SetBptp(nni,nnii)   
        
            ## Check Configuration ##
            checkConfig = pyautogui.confirm('Check Your Configuration ?', buttons=['check', 'No'])
            if checkConfig == 'check':
                print(connection.send_command ("show ethernet service brief"))
                print(connection.send_command ("show ethernet uni brief"))
                print(connection.send_command ("show ethernet nni brief"))

            retry = pyautogui.confirm(text='"Will you keep configuring?', title='Configuration done', buttons=['continue', 'stop'])
            if retry == 'continue':
                testContinue = 1
            else:
                testContinue = 0  
                connection.exit_enable_mode()
                connection.disconnect()
                return   
        except:
            pyautogui.alert('Enter a valid value')
            return 

# -- do main function -- #
main() 