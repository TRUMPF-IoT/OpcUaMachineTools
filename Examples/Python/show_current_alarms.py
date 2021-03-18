# MIT License

# Copyright (c) 2021 TRUMPF Werkzeugmaschinen GmbH + Co. KG

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
import os
import sys
import socket
from asyncua import Client
from gen_certificate import gen_certificates, get_application_uri
from asyncua import ua

class SubscriptionCallback:

    def __init__(self):        
        self.pendingConditions = {}
     
    def event_notification(self, event):                                
        # To avoid special event for ConditionRefresh 'Condition refresh started for subscription X.' 
        if (event.NodeId): 
            eventAsDict = self.event_to_dictionary(event)         
            conditionId = event.NodeId.to_string()
            conditionKeys = self.pendingConditions.keys()
            # A condition appears with Retain=True and disappears with Retain=False            
            if event.Retain and not conditionId in conditionKeys:                          
                self.pendingConditions[conditionId] = eventAsDict
            if not event.Retain and conditionId in conditionKeys:
                del self.pendingConditions[conditionId]                 
            print(self.pendingConditions)

    def event_to_dictionary(self, event):
        eventDict = {}        
        eventDict["time"] = event.Time 
        eventDict["identifier"] = event.AlarmIdentifier
        eventDict["source"] = event.SourceName         
        eventDict["type"] = event.SourceName
        eventDict["severity"] = event.Severity
        eventDict["retain"] = event.Retain    
        if type(event.Message) is str:
            eventDict["text"] = event.Message  # Older Trumpf server delivers type string           
        elif type(event.Message) is ua.uatypes.LocalizedText:
            eventDict["text"] = event.Message.Text # Trumpf server with new alarm number system delivers LocalizedText Type
        return eventDict


async def setup_security_and_certificates(client, applicationName):            
    try:  
        theHostname = socket.gethostname()            
        if not os.path.exists("certificate.der"):              
            gen_certificates("privatekey.pem", "certificate.der", theHostname, applicationName)                           
        # Hint: The client.application_uri must exactly match the SubjectAlternativeName uri in the certificate                      
        client.application_uri = get_application_uri(theHostname, applicationName)        
        await client.set_security_string("Basic256Sha256,SignAndEncrypt,certificate.der,privatekey.pem")           
    except Exception as ex:          
        print("Unexpected error in setup security and certificates: ", ex)


async def create_machine_subscription(client, nsIndex):
    # get nodes
    conditionType = client.get_node("ns=0;i=2782")      
    tcMachineAlarmType = client.get_node(f"ns={nsIndex};i=1006")            
    subNode = client.get_node(f"ns={nsIndex};s=179")   

    # subscribe     
    sub = await client.create_subscription(1, SubscriptionCallback())    
    unsubHandle = await sub.subscribe_alarms_and_conditions(subNode, tcMachineAlarmType) 

    # Call ConditionRefresh to get the current conditions with retain = true     
    await conditionType.call_method("0:ConditionRefresh", ua.Variant(sub.subscription_id, ua.VariantType.UInt32))


async def main():
    try:
        machineNamespace = "urn:X0REPLACE0X:TRUMPF:UAInterfaces/http://trumpf.com/TRUMPF-Interfaces/"       
        serverUrl = "opc.tcp://myServer:11878"

        # set runtime dir to directory of script file        
        os.chdir(sys.path[0])  

        # create the opc ua client
        client = Client(serverUrl, 10)  
        await setup_security_and_certificates(client, "exampleApplication")
        await client.connect() 

        nsIndex = await client.get_namespace_index(machineNamespace)
        await create_machine_subscription(client, nsIndex)

        # Output of alarms is in event_notification method in SubscriptionCallback class
        # Wait for some time and watch output
        await asyncio.sleep(100)        
        # Application ends

    except Exception as ex:
        print(ex)
        raise


if __name__ == "__main__":
    # execute if run as a script
    asyncio.run(main())