def main():
    from netmiko import ConnectHandler
    from getpass import getpass

    login ={
        'device_type':'cisco_ios',
        'ip':'192.168.0.231', 
        'username':'cisco', 
        'password':'cisco',
        "secret": 'cisco'
        }


    # Connect to device
    connection = ConnectHandler(**login)
    print (connection.send_command("show ip int brief"))
    print (connection.send_command("show ip route"))
#    print (device_conn.send_command("enable"))

    config_commands = ['access-list 5 permit host 1.1.1.1', 'ntp server 192.168.1.1' ]

    connection.enable()
    output = connection.send_config_set(config_commands)
    print(output)

    connection.disconnect()

main()