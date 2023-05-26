#$Language="python"
#$Interface="1.0"

# "This program was created by Jhjang@hfrnet.com and anyone can modify and use it."
# This script sets a EVC, UNI and NNI.

from netmiko import ConnectHandler
from getpass import getpass
import pyautogui
import tkinter as tk
from tkinter import ttk

connection = None

### MAIN FUNCTION ### 
def main(): 
    ## connect Remote Device ##
    connect()
    testContinue = 1 
    connection.enable() # 'enable' action

    while  testContinue == 1:
        try:
            ## Create SVLAN to be used for Service ##
            sVlan = pyautogui.prompt("Enter the SVLAN ID: ",'Create SVLAN',default = '1001')
            result=connection.send_config_set("vlan " + sVlan )
            print(result)
            checkCmdResult(result)

            ## Check Product Type and EVPL UNI ##
            checkProduct = checkProcuctType()
            print('#result1', checkProduct)
            evplunicnt = len(checkevpluni())
            print('#result2',evplunicnt)

            ## Create EVC ##    
            evc = pyautogui.prompt('Enter the EVC ID: evc1','Create Service',default = 'evc1')
            sType = pyautogui.confirm("Select Service type:","Select Service type",buttons=['epl', 'evpl'])          
            create_evc = ["ethernet service add "  + evc, "svlan " + sVlan, "service type " + sType]
            result=connection.send_config_set (create_evc )
            print(result)
            checkCmdResult(result)        

            ## Create UNI ##
            ## Create EPL UNI ##
            uType = ""
            if sType == "epl" and checkProduct == 0:
                    EplUNI(evc,uType,checkProduct)
            elif sType == "epl" and checkProduct == 1:
                uType = pyautogui.confirm("Select UNI type:",'Select the Service Type', buttons=['eth', 'roe'])        
                if uType == "eth":
                    EplUNI(evc,uType,checkProduct)
                elif uType == "roe":
                    MapUni = EplUNI(evc,uType,checkProduct)
                    EplRoUNI(MapUni,sVlan)
                else:
                    return    
            ## Create EVPL UNI ##
            elif sType == "evpl":
                ## If there is no EVPL UNI ##
                if evplunicnt == 0:      
                    SltUNI = pyautogui.confirm("Create UNI?",'Create an UNI' ,buttons=['Create UNI'])
                    if SltUNI == 'Create UNI':
                        EvplUNI(evc,uType,checkProduct)
                    else:
                        return 
                ## If there is EVPL UNI ##    
                elif evplunicnt != 0:
                    SltUNI = pyautogui.confirm("Create UNI?",'Create an UNI' ,buttons=['Create UNI', 'Existing UNI'])
                    if SltUNI == 'Create UNI':
                        EvplUNI(evc,uType,checkProduct)
                    elif SltUNI == 'Existing UNI':
                        AddEvcToUNI(evc)                 
                    else:
                        return 
                     
            ## Create NNI ##
            nni = "nni1"
            nnii = "1/25" 
            numberofnni = connection.send_command("show ether nni brief").splitlines()
            ## If there is no NNI ##
            if len(numberofnni) <= 4:
                CreNNI = pyautogui.confirm('Create NNI ?','Create a NNI', buttons=['Create NNI'])
                if CreNNI == 'Create NNI':
                    nni,nnii = CreateNNI(evc)
                else:
                    return
            ## If there is NNI ##  
            elif len(numberofnni) >= 5:
                CreNNI = pyautogui.confirm('Create NNI ?','Create a NNI', buttons=['Create NNI', 'Existing NNI'])
                if CreNNI == 'Create NNI':
                    nni,nnii = CreateNNI(evc)
                elif CreNNI == 'Existing NNI':
                    AddSvcToNni(evc)
                else:
                    return
                
            ## Config bPTP ## 
            if uType == "roe":
                SltBptp = pyautogui.confirm('Configure BPTP ?', buttons=['bptp', 'No'])
                if SltBptp == 'bptp':
                    SetBptp(nni,nnii)
                elif checkConfig == 'No':
                    pass       
                else:
                    return

            ## Check Configuration ##
            checkConfig = pyautogui.confirm('Check Your Configuration ?', buttons=['check', 'No'])
            if checkConfig == 'check':
                print(connection.send_command ("show ethernet service brief"))
                print(connection.send_command ("show ethernet uni brief"))
                print(connection.send_command ("show ethernet nni brief"))
            elif checkConfig == 'No':
                pass
            else:
                return   

            ## Select Loop ##
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


### SUB FUNCTION ###
### function to connect Remote Device ###
def connect():
    ip = pyautogui.prompt("Enter the DUT IP Address: xxx.xxx.xxx.xxx", default = "192.168.0.1")

    login ={
    'device_type':'cisco_ios',
    'ip':ip, 
    'username':'root', 
    'password':getpass(),
    # "secret": 'enable'
    }

    # Connect to device
    global connection
    connection = ConnectHandler(**login)
    print(connection.find_prompt())

 ### function to check the product type, which is either m6424 or not ### 
def checkProcuctType():
    showproduct = connection.send_command ("sh fruinfo system ")
    checkproduct = showproduct.split()
    search_string = 'M6424'
    if search_string in checkproduct:
        return 1
    else:
        return 0
def checkpyautogui(pyautout):
    if pyautout == None:
        return 

 ### function to check the command result ### 
def checkCmdResult(result):   # for word in checkcmd:
    checkcmd = result.split()
    result = [word for word in checkcmd if "^" in word or "%" in word]
    if len(result) != 0:
        pyautogui.alert('Wrong input detected! Correct the configutation')    
        return 

 ### function to change a FLEXPORT ### 
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

 ### function to check a FLEXPORT ###            
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

### function to create an EPLUNI ###  
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

### function to create an EPLROEUNI ###    
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

### function to create an EVPLUNI ###     
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

def checkevpluni():
    evpluni_list =[]
    for uni in connection.send_command("show ether uni brief").splitlines()[3:-1]:
        if uni.split()[7] == 'No' and uni.split()[9] == 'Yes':
            evpluni_list.append(uni.split()[0]) 
    return evpluni_list 

### function to add service to UNI ### 
selUni = ""
def AddEvcToUNI(evc):
#    AddUni = pyautogui.prompt("Enter the UNI ID: uni1",'Add a service to an existing UNI', default = 'uni1')  
    evpluni_list = checkevpluni()

    # Create Windows
    window = tk.Tk()

    # config the root window
    window.geometry('300x200')
    window.resizable(False, False)
    window.title("UNI List")

    # Create Combobox 
    combobox_values = evpluni_list
    selected_value = tk.StringVar()
    combobox = ttk.Combobox(window, values=combobox_values, textvariable=selected_value)
    combobox.pack()

    # Function
    def get_selected_value():
        getvalue = selected_value.get()
        global selUni
        selUni = getvalue

    # Create button
    button = tk.Button(window, text="selected_uni", command=get_selected_value)
    button.pack()

    # Excute windows
    window.mainloop()
 
    addevpluni = ["ethernet uni " + selUni, " add service " + evc]
    result=connection.send_config_set (addevpluni)
    print(result)
    checkCmdResult(result) 
    cVlan = pyautogui.prompt('Enter the CVLAN:','Map CEVLAN to Service', default= "100")        
    epu = selUni + "-" + evc	
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

### function to add service to NNI ### 
selnni = "" # selected NNI 
def AddSvcToNni(evc): 
#    aNni = pyautogui.prompt("Enter the NNI ID: nni1",'Add a service to an existing NNI', default = 'nni1')
    nni_list =[]
    for nni in connection.send_command("show ether nni brief").splitlines()[3:-1]:
        nnisplit = nni.split()[0]
        nni_list.append(nnisplit)

    # Create Windows
    window = tk.Tk()

    # config the root window
    window.geometry('300x200')
    window.resizable(False, False)
    window.title("NNI List")

    # Create Combobox 
    combobox_values = nni_list
    selected_value = tk.StringVar()
    combobox = ttk.Combobox(window, values=combobox_values, textvariable=selected_value)
    combobox.pack()

    # Function
    def get_selected_value():
        getvalue = selected_value.get()
        global selnni
        selnni = getvalue

    # Create button
    button = tk.Button(window, text="selected_nni", command=get_selected_value)
    button.pack()

    # Excute windows
    window.mainloop()

    addNni = ["ethernet nni " + selnni  , "add service " + evc ]
    result=connection.send_config_set (addNni )
    print(result)
    checkCmdResult(result)

### function to create BPTP ### 
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


# -- do main function -- #
main() 