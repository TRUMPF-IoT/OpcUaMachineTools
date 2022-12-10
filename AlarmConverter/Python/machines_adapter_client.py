# MIT License

# Copyright (c) 2022 TRUMPF Werkzeugmaschinen SE + Co. KG

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import asyncio
import logging
import os, sys
import socket
from asyncua import ua
from asyncua import Client
from asyncua.ua.uaprotocol_auto import MessageSecurityMode
from gen_certificate import gen_certificates, get_application_uri


class Machine:
    def __init__(self, machineName, namespace):
        self.machineName = machineName
        self.ns = namespace        
        self.subCallback = None
        self.unsubHandle = None
        self.sub = None
        

class SubCallback:
    def __init__(self, machineName, server, isTrumpfServer):
        self.logger = logging.getLogger("subcallback")  
        self.machineName = machineName    
        self.server = server
        self.isTrumpfServer = isTrumpfServer
        self.freeAlarmSlots = list(range(19, -1, -1))
        self.pendingAlarms = {}


    async def status_change_notification(s1,s2):
        None
        
        
    async def event_notification(self, event):                                
        # To avoid special event for ConditionRefresh 'Condition refresh started for subscription X.' 
        if (event.NodeId): 
            eventAsDict = self.event_to_dictionary(event)         
            conditionId = event.NodeId.to_string()
            conditionKeys = self.pendingAlarms.keys()
            # A condition/alarm appears with Retain=True and disappears with Retain=False            
            if event.Retain and not conditionId in conditionKeys:                 
                if (len(self.freeAlarmSlots) > 0):                         
                    # get first free slot of end of list
                    slotNumber = self.freeAlarmSlots.pop()
                    eventAsDict["slot"] = slotNumber
                    self.pendingAlarms[conditionId] = eventAsDict
                    self.logger.info("MachineName: %s, Alarm added: %s, Slot: %s", self.machineName, conditionId, slotNumber)    
                    await self.server.update_alarm_values(self.machineName, slotNumber, eventAsDict)  
                    await self.server.update_alarm_list(self.machineName, self.pendingAlarms)                
            if not event.Retain and conditionId in conditionKeys:
                slotNumber = self.pendingAlarms[conditionId]["slot"]
                # return now free slot to list
                self.freeAlarmSlots.append(slotNumber)
                self.freeAlarmSlots.sort(reverse=True)
                del self.pendingAlarms[conditionId] 
                # reset to default values               
                self.logger.info("MachineName: %s, Alarm removed: %s, Slot: %s", self.machineName, conditionId, slotNumber) 
                await self.server.reset_alarm_values(self.machineName, slotNumber, eventAsDict)  
                await self.server.update_alarm_list(self.machineName, self.pendingAlarms)           
            self.logger.info("MachineName: %s, Current conditions: %s", self.machineName, conditionKeys)    


    def event_to_dictionary(self, event):
        eventDict = {}        
        eventDict["time"] = event.Time # Change here for special time string if needed
        if self.isTrumpfServer:
           eventDict["identifier"] = event.AlarmIdentifier
        eventDict["source"] = event.SourceName         
        eventDict["name"] = event.ConditionName
        eventDict["severity"] = event.Severity
        eventDict["retain"] = event.Retain    
        if type(event.Message) is str:
            eventDict["text"] = event.Message  # Trumpf server delivers type string           
        elif type(event.Message) is ua.uatypes.LocalizedText:
            eventDict["text"] = event.Message.Text # Trumpf server with new alarm number system delivers LocalizedText Type
        return eventDict


class MachinesAdapterClient:

    def __init__(self, uri, server, isTrumpfServer):
        self.logger = logging.getLogger(__name__)
        self.logger.trace("init MachineAdapter")
        self.isRunning = False
        self.uri = uri
        self.server = server 
        self.isTrumpfServer = isTrumpfServer   
        self.machines = []
        self.client = Client(self.uri, 10) 
        self.foundationNS = "http://opcfoundation.org/UA/"
        self.isLastStateConnected = False


    async def add_machine(self, machineName, namespace):
        self.logger.trace("add_machine machineName=%s, namespace=%s", machineName, namespace)   
        # Add machine node to server           
        await self.server.add_machine(machineName)                                                             
        self.machines.append(Machine(machineName, namespace))
        
       
    async def create_machine_subscription(self, machine):
        self.logger.trace("CONNECT machine %s.", machine.machineName)
        self.logger.trace("create_machine_subscription ns=%s", machine.ns)
        # get nodes
        conditionType = self.client.get_node("ns=0;i=2782")  
        alarmConditionType = self.client.get_node("ns=0;i=2915")
        if self.isTrumpfServer:
            idx = await self.client.get_namespace_index(machine.ns)
            subType = await alarmConditionType.get_child([f"{idx}:TcMachineAlarmType"])
            subObject = self.client.get_node(f"ns={idx};s=179")            
        else:
            subType = alarmConditionType
            subObject = self.client.nodes.server           
        # subscribe
        machine.subCallback = SubCallback(machine.machineName, self.server, self.isTrumpfServer)
        machine.sub = await self.client.create_subscription(100, machine.subCallback)         
        machine.unsubHandle = await machine.sub.subscribe_alarms_and_conditions(subObject, subType)                  
        # Call ConditionRefresh to get the current conditions with retain = true     
        await conditionType.call_method("0:ConditionRefresh", ua.Variant(machine.sub.subscription_id, ua.VariantType.UInt32))

    
    async def remove_machine_subscription(self, machine):        
        if machine.sub is not None: 
            self.logger.trace("DISCONNECT machine %s.", machine.machineName)
            try:
                self.logger.trace("remove_machine_subscription ns=%s", machine.ns)           
                await machine.sub.delete() 
            except Exception as ex:         
                None
            finally:
                machine.sub = None

        
    async def is_connected(self, namespace, nodeString):        
        self.logger.info('is_connected namespace=%s, nodeString=%s:', namespace, nodeString) 
        isConnected = False
        try:
            # Check if node is reachable
            idx = await self.client.get_namespace_index(namespace)            
            var = self.client.get_node(f"ns={idx};{nodeString}")          
            val = await var.read_display_name()
            if val is not None: 
                isConnected = True
        except Exception as ex:
            # log only often in verbose mode (info)
            self.logger.info('is not connected Info: %s', ex) 
        finally:
            return isConnected


    async def setup_security_and_certificates(self, applicationName):            
        try:  
            theHostname = socket.gethostname()            
            if not os.path.exists("certificate.der"):
                self.logger.trace("setup_certificates")
                gen_certificates("privatekey.pem", "certificate.der", theHostname, applicationName)                           
            # Hint: The client.application_uri must exactly match the SubjectAlternativeName uri in the certificate                      
            self.client.application_uri = get_application_uri(theHostname, applicationName) 
            self.logger.trace("application uri=%s", self.client.application_uri)             
            # Check whether Mode SignAndEncrypt is available      
            endpoints = await self.client.connect_and_get_server_endpoints() 
            for e in endpoints:
                if e.SecurityMode == MessageSecurityMode.SignAndEncrypt:
                    self.logger.trace("set client security string with SignAndEncrypt") 
                    await self.client.set_security_string("Basic256Sha256,SignAndEncrypt,certificate.der,privatekey.pem")
                    break
        except Exception as ex:          
            self.logger.trace('Unexpected error in setup certificates: %s, %s', ex, sys.exc_info()[0])


    async def update_subscriptions(self):
        for machine in self.machines:
            # check node 1 of trumpf namespace
            nodeString = "s=1"
            ns = machine.ns
            if not self.isTrumpfServer: 
                nodeString = "i=2259"
                ns = self.foundationNS
            if await self.is_connected(ns, nodeString):
                if machine.sub is None:                    
                    await self.create_machine_subscription(machine)                            
            else:
                # Reset subscription                
                await self.remove_machine_subscription(machine) 


    async def clean_up_old_connection(self):
        try: 
            self.logger.trace("Clean up old connection.") 
            self.isLastStateConnected = False
            for m in self.machines:
                await self.remove_machine_subscription(m)            
            await self.client.disconnect()
        except:
            None


    async def update_connection(self):
        # Check server connection, server state variable is 2259
        if not await self.is_connected(self.foundationNS, "i=2259"):
            if self.isLastStateConnected: 
                await self.clean_up_old_connection()               
            self.logger.trace("Try to connect to server=%s", self.uri) 
            await self.client.connect()             
            self.isLastStateConnected = True # only set if no exception


    async def run(self):    
        self.logger.trace("run Start")
        await self.setup_security_and_certificates("alarmconverter")
        self.isRunning = True
        while self.isRunning:  
            try:  
                self.logger.trace("...is active")        
                await self.update_connection() # if not possible -> Exception                 
                await self.update_subscriptions()
            except asyncio.CancelledError: # happens on shutdown
                self.logger.trace("MachineAdapter Task cancelled") 
                raise
            except asyncio.TimeoutError:  
                self.logger.trace('Timeout error. Connection not possible: %s', sys.exc_info()[0])
            except Exception as ex:          
                self.logger.trace('Unexpected error: %s, %s', ex, sys.exc_info()[0])
                # only log full exception stack in verbose mode (info)
                self.logger.info('Exception:', exc_info=True)
            finally:
                await asyncio.sleep(10) 


    async def stop(self):
        self.logger.trace("stop")
        self.isRunning = False
        if await self.is_connected(self.foundationNS, "i=2259"):
            for machine in self.machines:
                await self.remove_machine_subscription(machine)
            await self.client.disconnect()
