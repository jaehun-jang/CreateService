def main():
    from netmiko import ConnectHandler
    from getpass import getpass
    import tkinter as tk
    from tkinter import messagebox

    login ={
        'device_type':'cisco_ios',
        'ip':'192.168.0.201', 
        'username':'root', 
        'password':'admin',
#        "secret": 'enable'
        }


    # Connect to device
    connection = ConnectHandler(**login)
    print(connection.find_prompt())
    #print(connection.send_command("en,enable")) must not send "en,enable" command.
    print(connection.send_command("show system"))
    print(connection.send_command("show ip route"))

    messagebox.showinfo("제목", "메시지 내용") 

    config_commands = ['ip-access-list 5 permit 1.1.1.1', 'ntp server 192.168.1.1' ]

    connection.enable() # 'enable' action
    output = connection.send_config_set(config_commands)
    connection.exit_enable_mode()
    print(output)

    connection.disconnect()

main()



