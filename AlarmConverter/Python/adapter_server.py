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
from asyncua import Server, ua
from datetime import datetime


ALARM_PARAMETERS = {
    "AlarmIdentifier":
        { "type": ua.VariantType.String,  "default": "", "eventKey": "identifier", "trumpfOnly": True },
    "ConditionName": 
        { "type": ua.VariantType.String,  "default": "", "eventKey": "name", "trumpfOnly": False },
    "SourceName":
        { "type": ua.VariantType.String,  "default": "", "eventKey": "source", "trumpfOnly": False },
    "Text":
        { "type": ua.VariantType.String,  "default": "", "eventKey": "text", "trumpfOnly": False },
    "Severity":
        { "type": ua.VariantType.UInt16,  "default": 0, "eventKey": "severity", "trumpfOnly": False },
    "Time":
        { "type": ua.VariantType.DateTime,  "default": datetime(1900,1,1), "eventKey": "time", "trumpfOnly": False },                          
}

class AdapterServer:

    def __init__(self, endpointUri, sourceIsTrumpf):
        self.logger = logging.getLogger(__name__)
        self.server = Server()
        self.sourceIsTrumpf = sourceIsTrumpf
        self.endpointUri = endpointUri
        self.isRunning = False
        self.hasStopped = False
        self.idx = None


    async def initialize(self):        
        self.logger.trace("Initializing Server. Please wait.") 
        await self.server.init()
        self.server.set_endpoint(self.endpointUri)
        self.server.set_server_name("AlarmConverterServer")
        # set all possible endpoint policies for clients to connect through
        self.server.set_security_policy([ua.SecurityPolicyType.NoSecurity,])
        # setup our own namespace        
        ns = "http://trumpf.com/alarmconverter/"
        self.idx = await self.server.register_namespace(ns)          


    async def run(self):
        # starting!
        self.isRunning = True
        self.hasStopped = False
        async with self.server:
            self.logger.trace("Server started!")        
            while self.isRunning: # Todo Variable to check if to stop              
                await asyncio.sleep(1)
            self.hasStopped = True


    async def stop(self):
        self.isRunning = False
        while not self.hasStopped:           
            await asyncio.sleep(0.25)
        self.logger.trace("Server stopped!")


    async def add_machine(self, machineName):      
        machineNode = await self.server.nodes.objects.add_object(ua.NodeId(machineName, self.idx), machineName)  
        # Add array variable for list of active alarm identifiers      
        await machineNode.add_variable(ua.NodeId(f"{machineName}.AlarmList", self.idx), "AlarmList", 
                                       ua.Variant([], ua.VariantType.String, is_array=True))
        # Add 20 alarm slots with variables
        for i in range(0,20):
            alarmId = f"Alarm{i}"
            alarmNode = await machineNode.add_object(ua.NodeId(f"{machineName}.{alarmId}", self.idx), alarmId) 
            for key,v in ALARM_PARAMETERS.items():
                if not v["trumpfOnly"] or ( v["trumpfOnly"] and self.sourceIsTrumpf ):
                    await alarmNode.add_variable(ua.NodeId(f"{machineName}.{alarmId}.{key}", self.idx), key, v["default"], v["type"])


    async def update_alarm_list(self, machineName, pendingAlarms):          
        node = self.server.get_node(ua.NodeId(f"{machineName}.AlarmList", self.idx))
        identifiers = [x["identifier"] for x in pendingAlarms.values()]
        await node.write_value(identifiers, ua.VariantType.String) 


    async def update_alarm_values(self, machineName, slotNumber, eventAsDict):      
        alarmId = f"Alarm{slotNumber}"
        for key,v in ALARM_PARAMETERS.items():
            if not v["trumpfOnly"] or ( v["trumpfOnly"] and self.sourceIsTrumpf ):
                node = self.server.get_node(ua.NodeId(f"{machineName}.{alarmId}.{key}", self.idx))
                newValue = eventAsDict[v["eventKey"]]
                await node.write_value(newValue, v["type"]) 


    async def reset_alarm_values(self, machineName, slotNumber, eventAsDict):      
        # reset to default values
        for key,v in ALARM_PARAMETERS.items():
            if not v["trumpfOnly"] or ( v["trumpfOnly"] and self.sourceIsTrumpf ):
                eventAsDict[v["eventKey"]] = v["default"] 
        await self.update_alarm_values(machineName, slotNumber, eventAsDict)

