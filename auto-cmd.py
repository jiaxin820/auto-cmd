from pexpect import pxssh
import xlrd
import re
import pexpect
import os
import sys
import ConfigParser
import json


class SSHAgent():
    
    def __init__( self, l_ssh_info ):
        self.ret = 0
        self.hostname = l_ssh_info[0]
        self.port = l_ssh_info[1]
        self.username = l_ssh_info[2]
        self.ssh = None
        self.ret = self.__ssh_login()

    #go login tiaobanji
    def __ssh_login( self ):
        try:
            self.ssh = pxssh.pxssh()
            if self.ssh.login(self.hostname,self.username,port=self.port) is True:
                self.ssh.setwinsize(20,120)
                #ssh.prompt(5)
                #print(ssh.before)
                #print(self.ssh.getwinsize())
                return 0
            return 1
        except pxssh.ExceptionPxssh as e:
            print(e)
            return 2

    def send_cmd( self, cmds, delimiters, actions ):
        if self.ssh is None:
            return None
        output_str = ""
        for cmd in cmds:
            self.ssh.send(cmd)
            try_times = 1
            while True:
                try:
                    i = self.ssh.expect( delimiters,timeout=20 )
                    #print("key:"+keys[i])
                    cmd_output = self.ssh.before + self.ssh.after
                    print(cmd_output)
                    output_str += cmd_output
                    if actions.has_key(str(i)):
                        self.ssh.send(actions[str(i)])
                    else:
                        break
                except pexpect.TIMEOUT:
                    if try_times > 3:
                        print("try over 3 times!break!")
                        return None
                    try_times += 1
                    print("try %d times..." % (try_times))
                except Exception as e:
                    print(e)
                    break
        if output_str == "":
            return None
        return output_str


    def telnet_device( self, 
                       list_devices,
                       delis_telnet,
                       actions_telnet,
                       list_cmds,
                       delis_cmd,
                       actions_cmd ):
        for device in list_devices:
            if not self.send_cmd( ["telnet " + device], delis_telnet, actions_telnet ):
                print("Can't telnet %s " % (device))
                continue
            output = self.send_cmd( list_cmds, delis_cmd, actions_cmd )
            if not output:
                print("Error send cmd to %s " % (device))
                #self.write_log( OUTPUT_PATH[-2]+list_devices[index].strip()+".txt", output)
            else:
                self.__write_log(device.strip(),output)

    def __write_log( self, name, output ):
        f = open("output/"+name+".txt","w")
        try:
            f.write(output)
        except Exception as e:
            print(e)
        finally:
            f.close()
        
    def close( self ):
        self.ssh.close()

#get device list
class DeviceLoader():

    def __init__( self, json_path, dev_path, cmd_path ):
        self.json_path = json_path
        self.dev_path = dev_path
        self.cmd_path = cmd_path

    def get_device_cmd( self ):
        with open(self.json_path) as json_file:
            device_cmd = json.load(json_file)
            for device_path in device_cmd:
                f_device = open( DEVICE_PATH + device_path,"r" )
                f_cmd = open( CMD_PATH + device_cmd[device_path],"r" )
                yield [ device for device in f_device.readlines() ],[ cmd for cmd in f_cmd.readlines() ]
   
    

if __name__ == "__main__":
    #device_path = DEVICE_PATH if len(sys.argv)<2 else sys.argv[1]
    #cmd_path = CMD_PATH if len(sys.argv)<3 else sys.argv[2]
    output_file_path = None if len(sys.argv)<2 else sys.argv[1]
    
    choose = ["BONE","LOCAL"]
    while True:
        num_choose = raw_input("1.bone\n2.local\nchoose:")
        if num_choose.isdigit() and int(num_choose) in [1,2]:
            num_choose = int(num_choose) - 1
            break
        else:
            print("input error!")

    #load argvs
    cf = ConfigParser.ConfigParser()
    cf.read("argv.conf")
    DEVICE_CMD_PATH = cf.get("path","DEVICE_CMD_PATH")
    DEVICE_PATH = cf.get("path","DEVICE_PATH")
    CMD_PATH = cf.get("path","CMD_PATH")
    OUTPUT_PATH = cf.get("path","OUTPUT_PATH")
    

    ssh_info = eval(cf.get("sshinfo",choose[num_choose]))
    deli_telnet = eval(cf.get("delimiter","TELNET"))
    deli_device = eval(cf.get("delimiter","DEVICE"))
    action_telnet = eval(cf.get("action","TELNET_"+choose[num_choose]))
    action_device = eval(cf.get("action","DEVICE"))

    ssh = SSHAgent( ssh_info )
    device_loader = DeviceLoader( DEVICE_CMD_PATH,DEVICE_PATH,CMD_PATH )

    for device_list,cmd_list in device_loader.get_device_cmd():
        ssh.telnet_device( device_list,deli_telnet,action_telnet,cmd_list,deli_device,action_device )
    ssh.close()
