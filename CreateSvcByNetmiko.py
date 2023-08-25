#$Language="python"
#$Interface="1.0"

# "This program was created by Jaehoon Jang and anyone can modify and use it."
# This script sets a EVC, UNI and NNI.

from netmiko import ConnectHandler
from getpass import getpass
import pyautogui

ip = pyautogui.prompt("Enter the DUTA IP Address: xxx.xxx.xxx.xxx")

login ={
'device_type':'cisco_ios',
'ip':ip, 
'username':'root', 
'password':'admin',
# "secret": 'enable'
}

# Connect to device
connection = ConnectHandler(**login)
print(connection.find_prompt())

### SUB FUNCTION ###
# def checkstring():
#     while ip == '':  
#         pyautogui.alert('Enter a valid value')
#         ip = pyautogui.prompt("Enter the DUT IP Address: xxx.xxx.xxx.xxx")

def changFlexP(rdResult_list,uType,fpg):
    print(rdResult_list[2],uType,fpg)  #for debuging  
    if  rdResult_list[2] != uType and uType == 'ethernet':
        chgtoeth = ["flexport-group " + fpg, "port-type ethernet"]
        print(connection.send_config_set (chgtoeth))          
    elif  rdResult_list[2] != uType and uType == 'cpri':
        chgtocpri = ["flexport-group " + fpg, "port-type cpri"]
        print(connection.send_config_set (chgtocpri)) 
            
def CheckFlexP(uType,MapUni): # ('eth' or 'roe') , '1/1'                    
    try: 
        i = MapUni
        s = i.split('/')
        intNum_list = list(s)	
        Command = "sh flexport"
        with open('.\creSvcByNetmiko.txt', 'w') as f:
            readString = connection.send_command(Command)
            f.write(readString)
        
        with open('.\creSvcByNetmiko.txt', 'r') as f:
            flexport = intNum_list[1]
            connection.send_command("# " + flexport) #for debuging  
            flexport = int(flexport)            
            if uType == 'eth':
                uType = 'ethernet'
            elif uType == 'roe':
                uType = 'cpri'

            rdResult = f.read().splitlines()
            rdResult = list(filter(None, rdResult))        
            if  flexport <= 2:
                rdResult_list = rdResult[11]
                fpg = '1' 
                changFlexP(rdResult_list,uType,fpg)
            elif 3 <= flexport <= 4:
                rdResult_list = rdResult[12]
                fpg = '2' 
                changFlexP(rdResult_list,uType,fpg)            
            elif 5 <= flexport <= 6:
                rdResult_list = rdResult[13]
                fpg = '3' 
                changFlexP(rdResult_list,uType,fpg)            
            elif 7 <= flexport <= 8:
                rdResult_list = rdResult[14]
                fpg = '4' 
                changFlexP(rdResult_list,uType,fpg)            
            elif 9 <= flexport <= 10:
                rdResult_list = rdResult[15]
                fpg = '5' 
                changFlexP(rdResult_list,uType,fpg)             
            elif 11 <= flexport <= 12:
                rdResult_list = rdResult[16]
                fpg = '6' 
                changFlexP(rdResult_list,uType,fpg)        
            elif 13 <= flexport <= 14:
                rdResult_list = rdResult[17]
                fpg = '7' 
                changFlexP(rdResult_list,uType,fpg)            
            elif 15 <= flexport <= 16:
                rdResult_list = rdResult[18]
                fpg = '8' 
                changFlexP(rdResult_list,uType,fpg)            
            elif 17 <= flexport <= 18:
                rdResult_list = rdResult[19]
                fpg = '9' 
                changFlexP(rdResult_list,uType,fpg)            
            elif 19 <= flexport <= 20:
                rdResult_list = rdResult[20]
                fpg = '10' 
                changFlexP(rdResult_list,uType,fpg)             
            elif 21 <= flexport <= 22:
                rdResult_list = rdResult[21]
                fpg = '11' 
                changFlexP(rdResult_list,uType,fpg)
            elif 23 <= flexport <= 24:
                rdResult_list = rdResult[22]
                fpg = '12' 
                changFlexP(rdResult_list,uType,fpg)         
            else:
                return      
    except: 
        return

def EplEtUNI(evc,uType):
    CreUni = pyautogui.prompt('Enter the UNI ID:','Create UNI', default='uni1')  
    MapUni = pyautogui.prompt('Select interface of UNI:','MAP Interface to UNI',default='1/1')
    CheckFlexP(uType,MapUni)    ## Flex-port check function(uType,MapUni)            
    create_uni = ["ethernet uni add " + CreUni , " map interface " + MapUni , " add service " + evc]
    print(connection.send_config_set (create_uni ))         
    return MapUni

def EplRoUNI(MapUni,sVlan):
    dMac = pyautogui.prompt("Enter the Dest MAC Add: xxxx.xxxx.xxxx") 
    create_roeuni = ["interface " + MapUni,
                    "roe cpri option 7",
                    "roe-agnostic tunnel enable",
                    "roe-agnostic encap dst-mac " + dMac,
                    "roe-agnostic encap vlan " + sVlan,
                    "roe-agnostic encap vlan priority 5",
                    "roe-agnostic enable"]
    print(connection.send_config_set (create_roeuni ))   
    
def EvplUNI(evc,uType): 
    CreUni = pyautogui.prompt('Enter the UNI ID:','Create UNI', default='uni1')  
    MapUni = pyautogui.prompt('Select interface of UNI:','MAP Interface to UNI',default='1/1')
    CheckFlexP(uType,MapUni)    ## Flex-port check function(uType,MapUni)  
    cVlan = pyautogui.prompt('Enter the CVLAN:','Map CEVLAN to Service', default= "100")  
    epu = CreUni + "-" + evc
    creevpuni = ["ethernet uni add " + CreUni,
                 " map interface " + MapUni ,
                 " all-to-one-bundling disable",
                 " bundling enable ",
                 " multiplex enable ",
                " add service " + evc]	
    print(connection.send_config_set (creevpuni))  	
    addcevlan = ["ethernet service end-point " + epu, "add vlan " + cVlan]
    print(connection.send_config_set (addcevlan))  

def AddEvcToUNI(evc): 
    AddUni = pyautogui.prompt("Add SVC to UNI :", default = 'uni1') 
    addevpluni = ["ethernet uni " + AddUni, " add service " + evc]
    print(connection.send_config_set (addevpluni)) 
    cVlan = pyautogui.prompt('Enter the CVLAN:','Map CEVLAN to Service', default= "100")        
    epu = AddUni + "-" + evc	
    addcevlan = ["ethernet service end-point " + epu, "add vlan " + cVlan]
    print(connection.send_config_set (addcevlan))  

def CreateNNI(evc): 
    cNni = pyautogui.prompt('Enter the new NNI ID:','Create NNI',default='nni1')    
    MapInt = pyautogui.prompt('Select interface of NNI:','MAP MMI Interface',default ='1/25') 
    create_nni = ["ethernet nni add " + cNni , " map interface " + MapInt, " add service " + evc]
    print(connection.send_config_set (create_nni ))   
    return cNni,MapInt 

def AddSvcToNni(evc): 
    aNni = pyautogui.prompt("Enter the NNI ID: nni1", default = 'nni1') 	      
    addNni = ["ethernet nni " + aNni , "add service " + evc ]
    print(connection.send_config_set (addNni )) 

def SetBptp(nni,nnii):
    sVlan = pyautogui.prompt("Enter the SVLAN for BPTP:", default = '4001') 
    create_bptpsvlan = ["vlan " + sVlan, "ethernet service add bptp", "svlan "+ sVlan, "add nni " + nni]
    print(connection.send_config_set (create_bptpsvlan))  
    # Select BPTP Type ##  
    bptpType = pyautogui.confirm('"Select bPTP Type"', buttons=['Master', 'Slave'])
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
        print(connection.send_config_set (config_master))  
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
        print(connection.send_config_set (config_slave))


### MAIN FUNCTION ### 
def main(): 

    testContinue = 1 
    connection.enable() # 'enable' action

    while  testContinue == 1:
        sVlan = pyautogui.prompt("Enter the SVLAN ID: ",'Create SVLAN',default = '1001')
        print (connection.send_config_set("vlan " + sVlan ))

        ## Create EVC ##    
        evc = pyautogui.prompt('Enter the EVC ID: evc1','Create Service',default = 'evc1')
        sType = pyautogui.confirm("Select Service type:","Select Service type",buttons=['epl', 'evpl'])          
        create_evc = ["ethernet service add "  + evc, "svlan " + sVlan, "service type " + sType]
        print(connection.send_config_set (create_evc ))        
    
        ## Create UNI ##
        uType = "eth"
        if sType == "epl":
            uType = pyautogui.confirm("Select UNI type:", buttons=['roe', 'eth'])        
            if uType == "roe":
                MapUni = EplEtUNI(evc,uType)
                EplRoUNI(MapUni,sVlan)
            elif uType == "eth":
                EplEtUNI(evc,uType)
        elif sType == "evpl":
            SltUNI = pyautogui.confirm("Create UNI?",'Create UNI' ,buttons=['Create UNI', 'No'])
            if SltUNI == 'Create UNI':
                EvplUNI(evc,uType)
            elif SltUNI == 'No':
                AddEvcToUNI(evc)
            else:
                connection.send_command ("# script end  #")
                return

        ## Create NNI ##
        nni = "nni1"
        nnii = "1/25" 
        CreNNI = pyautogui.confirm('Create NNI ?','Create NNI', buttons=['nni', 'No'])
        print()
        if CreNNI == 'nni':
            nni,nnii = CreateNNI(evc)
        elif CreNNI == 'No':
            AddSvcToNni(evc)
        else:
            return 
    
        ## Config bPTP ## 
        if uType == "roe":
            SltBptp = pyautogui.confirm('Configure BPTP ?', buttons=['bptp', 'No'])
            if SltBptp == 'bptp':
                SetBptp(nni,nnii)
            else:
                return     
    
        ## Check Configuration ##
        checkConfig = pyautogui.confirm('Check Your Configuration ?', buttons=['check', 'No'])
        if checkConfig == 'check':
            print(connection.send_command ("show ethernet service"))
            print(connection.send_command ("show ethernet uni"))
            print(connection.send_command ("show ethernet nni"))
        else:
            return 

        retry = pyautogui.confirm(text='"Will you keep configuring?', title='Configuration done', buttons=['continue', 'stop'])
        if retry == 'continue':
            testContinue = 1
        else:
            testContinue = 0  
            connection.exit_enable_mode()
            connection.disconnect()
            return   

# -- do main function -- #
main() 
