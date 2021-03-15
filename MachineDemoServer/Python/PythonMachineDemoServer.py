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
import json
import importlib
import datetime
import os, sys
from asyncua.common import ua_utils
from dateutil.parser import isoparse
from datetime import timedelta, datetime
from asyncua import ua, Server
from xml.dom import minidom
from enum import Enum

_nodeIdToTypeInfoDict = {}
_attributeNameToTypeInfoDict = {}
_complexTypeNameMapping = {"local":"Local", "text":"Text", "id":"Identifier", 
                           "nodeId":"Identifier", "nsIdx":"NamespaceIndex"} 

class NodeTypeInfo:
    def __init__(self):
        self.isSimpleDataType = None
        self.isArray = None
        self.dataTypeName = None


def create_instance_of_complex_data_type_class(nodeTypeInfo, value):
    global _complexTypeNameMapping 
    instance = None
    try:        
        if nodeTypeInfo.dataTypeName in ["DateTime", "Time", "UtcTime", "TimeZoneDataType"]: # TIME
            instance = isoparse(value)
        else:            
            ua_module = importlib.import_module("asyncua.ua")
            myType = getattr(ua_module, nodeTypeInfo.dataTypeName)            
            if isinstance(myType, type(Enum)): # Custom ENUM            
                instance = value            
            else: # CLASS
                # Attentention with NodeId types, 
                # Per default TwoByteNodeIds are created without NamespaceIndex -> Maybe needs to be corrected
                instance = myType()                            
                for name,value in value.items():        
                    if value is not None:
                        if name in _complexTypeNameMapping:
                            name = _complexTypeNameMapping[name]
                        setattr(instance, name, value)  # set value   
    except Exception as ex:
        print("ComplexDataTypeError:", nodeTypeInfo.dataTypeName, ex)    
    return instance


def get_complex_value_instance_object(nodeTypeInfo, value):  
    if nodeTypeInfo.isArray:
        return [create_instance_of_complex_data_type_class(nodeTypeInfo,v) for v in value]
    else:
        return create_instance_of_complex_data_type_class(nodeTypeInfo, value)


async def get_type_information(server, node):
    global _nodeIdToTypeInfoDict
    if node.nodeid in _nodeIdToTypeInfoDict:
        return _nodeIdToTypeInfoDict[node.nodeid]
    else:
        newTypeInfo = NodeTypeInfo()
        newTypeInfo.isArray = (await node.read_value_rank()) > 0   
        nodeIdDT = await node.read_data_type()
        isNs0 = (nodeIdDT.NamespaceIndex == 0)  
        id = nodeIdDT.Identifier    
        newTypeInfo.isSimpleDataType = isNs0 and ((id < 13) or (id > 25 and id < 30)) # ua.ObjectIds
        if newTypeInfo.isSimpleDataType:  
            newTypeInfo.dataTypeName = ua.ObjectIdNames[id]          
        else:
            dataTypeNode = server.get_node(nodeIdDT)
            newTypeInfo.dataTypeName = (await dataTypeNode.read_browse_name()).Name  
        _nodeIdToTypeInfoDict[node.nodeid] = newTypeInfo
        return newTypeInfo


async def create_attribute_name_to_type_info_dictionary(server, etype):    
    allTypes = await ua_utils.get_node_supertypes(etype, includeitself=True, skipbase=False)
    fieldTypeInfos= {}
    allFields = []
    for t in allTypes:        
        allFields.extend(await t.get_properties())      
        allFields.extend(await t.get_variables())
    for fieldNode in allFields:
        attributeName = (await fieldNode.read_browse_name()).Name        
        fieldTypeInfos[attributeName] = await get_type_information(server, fieldNode)
        # Collect sub properties
        for subProp in await fieldNode.get_properties():
            subPropName = (await subProp.read_browse_name()).Name
            newName = f"{attributeName}/{subPropName}"
            fieldTypeInfos[newName] = await get_type_information(server, subProp)
    return fieldTypeInfos


async def create_machine_alarm(evgen, nsIdx, entry):
    global _attributeNameToTypeInfoDict
    try:  
        event = evgen.event   
        for attribute in entry["fieldValues"]:
            name = attribute["field"]["browseName"]["name"]
            # ConditionId is called NodeId in the event object
            if name == "ConditionId":
                name = "NodeId"
            value = attribute["value"]  
            if value is not None:
                typeInfo = _attributeNameToTypeInfoDict[name]
                if typeInfo.isSimpleDataType:                    
                    setattr(event, name, value)  # set value
                else:
                    complexValue = get_complex_value_instance_object(typeInfo, value) 
                    setattr(event, name, complexValue) # set value
        event.NodeId = ua.StringNodeId(event.NodeId.Identifier) # transform to StringNodeId 
        event.EventType = ua.NodeId(event.EventType.Identifier, nsIdx) # set EventType correct Namespace
        return event.Time
    except Exception as ex:
        print("create_machine_alarm - Unexpected error:", ex)


async def prepare_for_machine_alarms(server, nsIdx):
    global _attributeNameToTypeInfoDict
    machineAlarmType = server.get_node(f"ns={nsIdx};i=1006")                
    # For ConditionId add NodeId property manually. Necessary till implemented in python asyncua library
    await machineAlarmType.add_property(2, 'NodeId', ua.Variant(varianttype=ua.VariantType.NodeId))
    messagesNode = server.get_node(f"ns={nsIdx};s=179")                
    _attributeNameToTypeInfoDict = await create_attribute_name_to_type_info_dictionary(server, machineAlarmType)
    return await server.get_event_generator(machineAlarmType, messagesNode)


async def init_all_variables_waiting_for_initial_data(topNode):
    statusWaitingInitialData = ua.DataValue(status=ua.StatusCode(ua.StatusCodes.BadWaitingForInitialData)) 
    nodeList = await ua_utils.get_node_children(topNode)
    for n in nodeList:
        nodeClass = await n.read_node_class()
        if nodeClass == ua.NodeClass.Variable:              
            await n.write_value(statusWaitingInitialData)


async def main():
    # set runtime dir to directory of script file
    os.chdir(sys.path[0]) 

    # Read configuration XML Document
    doc = minidom.parse("ReplayConfiguration.xml")
    playSpeedFactor = int(doc.getElementsByTagName("execution")[0].getAttribute("playSpeedFactor"))  
    sourceFileName = doc.getElementsByTagName("execution")[0].getAttribute("sourceFileName")
    endpoint = doc.getElementsByTagName("endpoint")[0].getAttribute("url")   

    server = Server()
    await server.init()
    await server.load_certificate("server-certificate.der")
    await server.load_private_key("server-privatekey.pem")
    server._application_uri = "urn:ServerHost:TRUMPF:MachineDemoServer"
    server.product_uri = "urn:Demo:TRUMPF:MachineDemoServer"
    server.set_endpoint(endpoint)
    server.set_server_name("TRUMPF Python Demo Server")          
    server.set_security_policy([
            ua.SecurityPolicyType.NoSecurity,
            ua.SecurityPolicyType.Basic256Sha256_SignAndEncrypt])   
    await server.import_xml("MachineNodeTree.xml")    
    await server.load_type_definitions()    
    idx = await server.get_namespace_index("http://trumpf.com/TRUMPF-Interfaces/")

    # Prepare tree                                         
    machineNode = server.get_node(f"ns={idx};s=1")      
    await init_all_variables_waiting_for_initial_data(machineNode) 
    evgen = await prepare_for_machine_alarms(server, idx)  

    # Load record json
    with open(sourceFileName) as f: 
        hdaJson = json.load(f)

    async with server:  
        await asyncio.sleep(2)                                                                       
        while True:
            counter = 0
            previousTimestamp = None
            currentTimestamp = None
            for entry in hdaJson:
                try:
                    counter = counter + 1                    
                    nodeId = entry["nodeId"]["id"]   
                    print(f"--------------------------\nNodeId={nodeId}, Counter={counter}")            
                    isAlarm = (nodeId == "179")
                    timeDiff = timedelta(0)  
                    if isAlarm:
                        currentTimestamp = await create_machine_alarm(evgen, idx, entry)   
                    else:
                        currentTimestamp = isoparse(entry["value"]["serverTimestamp"])    
                    if previousTimestamp and currentTimestamp:    
                        timeDiff = currentTimestamp - previousTimestamp                  
                    previousTimestamp = currentTimestamp
                    waitingTime = timeDiff.total_seconds() / playSpeedFactor                  
                    print(f"Sleep={waitingTime}s, isAlarm={isAlarm}")
                    await asyncio.sleep(waitingTime)
                    if isAlarm:
                        await evgen.trigger() # a new time is set automatically
                    else:  
                        node = server.get_node(f"ns={idx};s={nodeId}")                                                                             
                        value = entry["value"]["value"]
                        isEmptyList = (type(value) is list) and (len(value) == 0)
                        if value is not None and not isEmptyList:
                            nodeTypeInfo = await get_type_information(server, node)
                            datavalue = ua.DataValue()
                            if nodeTypeInfo.isSimpleDataType: 
                                # DataValue as workaround to set ServerTimestamp
                                # DataValue can be removed when library is auto setting ServerTimestamp
                                datavalue = ua.DataValue(value)                                                
                            else:
                                complexValue = get_complex_value_instance_object(nodeTypeInfo, value)                              
                                datavalue = ua.DataValue(complexValue)                                
                            datavalue.SourceTimestamp = datetime.utcnow()
                            datavalue.ServerTimestamp = datetime.utcnow()                                                          
                            await node.write_value(datavalue) 
                except Exception as ex:
                    print("Unexpected error:", nodeId, ex)
            await asyncio.sleep(2) # And redo record file   

if __name__ == "__main__":
    asyncio.run(main())

