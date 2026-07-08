#!/usr/bin/env python3

# MIT License

# Copyright (c) 2026 TRUMPF Werkzeugmaschinen GmbH + Co. KG

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

"""OPC UA demo server that emulates a TRUMPF machine tool.

The server loads its address space from MachineNodeTree.xml and then replays
pre-recorded machine data from a record*.json file in an endless loop. The
wait time between two entries equals the difference of their recorded
timestamps, divided by the configured playSpeedFactor. Entries for the
Alarms/Messages node (s=179) are replayed as OPC UA events, all other
entries as plain variable writes.

Endpoint URL, playback speed and record file are configured in
ReplayConfiguration.xml. 
"""

import asyncio
import json
import importlib
import datetime
import os, sys
import re
import asyncua
from asyncua.common import ua_utils
import dateutil
from dateutil.parser import isoparse
from dataclasses import dataclass
from datetime import timedelta, datetime, timezone
from asyncua import ua, Server, Node, uamethod
from xml.dom import minidom
from enum import Enum


# Namespace of the TRUMPF machine interface, registered by importing MachineNodeTree.xml
MACHINE_NAMESPACE = "http://trumpf.com/TRUMPF-Interfaces/"

# Well-known stable NodeIds within that namespace
MACHINE_ROOT_NODE_ID = "1"       # s=1: root object of the machine node tree
ALARM_NODE_ID = "179"            # s=179: Alarms/Messages event node
TC_MACHINE_ALARM_TYPE_ID = 1006  # i=1006: TcMachineAlarmType event type

# Built-in scalar data types (ns=0) that asyncua maps directly to Python values,
# so no dataclass instance needs to be created for them:
# ids 1..12:  Boolean, SByte, Byte, Int16, UInt16, Int32, UInt32, Int64, UInt64, Float, Double, String
# ids 26..29: Number, Integer, UInteger, Enumeration (abstract number types)
_SIMPLE_DATA_TYPE_IDS = frozenset(range(1, 13)) | frozenset(range(26, 30))

# Maps field names as they appear in the recording JSON to the field names of the
# corresponding asyncua dataclass. A value of None means "ignore this JSON field"
# (e.g. nsUrl, which has no counterpart field on the asyncua NodeId dataclass).
JSON_FIELD_TO_UA_FIELD = {"local": "Local", "text": "Text", "id": "Identifier",
                          "nodeId": "Identifier", "nsIdx": "NamespaceIndex", "nsUrl": None}


class NodeTypeInfo:
    def __init__(self):
        self.isSimpleDataType = None
        self.isArray = None
        self.dataTypeName = None
        self.variantType = None


def set_frozen_attr(obj, name, value):
    """Set an attribute on a frozen asyncua dataclass (plain assignment would raise)."""
    object.__setattr__(obj, name, value)


def parse_time_string(timestring):
    """Parse an ISO 8601 timestamp from the recording."""    
    normalized = re.sub(r"(\.\d{6})\d+", r"\1", timestring)
    return isoparse(normalized)


class TypeInfoCache:
    """Determines and caches type information per variable node.

    The introspection (value rank, variant type, data type name) needs several
    address space lookups, so the result is cached by NodeId.
    """

    def __init__(self, server):
        self._server = server
        self._cache = {}

    async def get(self, node):
        if node.nodeid in self._cache:
            return self._cache[node.nodeid]
        newTypeInfo = NodeTypeInfo()
        newTypeInfo.isArray = (await node.read_value_rank()) > 0
        newTypeInfo.variantType = await node.read_data_type_as_variant_type()
        nodeIdDT = await node.read_data_type()
        identifier = nodeIdDT.Identifier
        newTypeInfo.isSimpleDataType = (nodeIdDT.NamespaceIndex == 0) and (identifier in _SIMPLE_DATA_TYPE_IDS)
        if newTypeInfo.isSimpleDataType:
            newTypeInfo.dataTypeName = ua.ObjectIdNames[identifier]
        else:
            dataTypeNode = self._server.get_node(nodeIdDT)
            newTypeInfo.dataTypeName = (await dataTypeNode.read_browse_name()).Name
        self._cache[node.nodeid] = newTypeInfo
        return newTypeInfo


def create_instance_of_complex_data_type_class(nodeTypeInfo, value):
    instance = None
    try:
        if nodeTypeInfo.dataTypeName in ["DateTime", "Time", "UtcTime", "TimeZoneDataType"]: # TIME
            instance = parse_time_string(value)
        else:
            ua_module = importlib.import_module("asyncua.ua")
            myType = getattr(ua_module, nodeTypeInfo.dataTypeName)
            if isinstance(myType, type(Enum)): # Custom ENUM
                instance = value
            else: # CLASS            
                instance = myType()
                for fieldName, fieldValue in value.items():
                    if fieldValue is not None:
                        if fieldName in JSON_FIELD_TO_UA_FIELD:
                            fieldName = JSON_FIELD_TO_UA_FIELD[fieldName]
                        if fieldName is not None: # Ignore fields mapped to None
                            set_frozen_attr(instance, fieldName, fieldValue)
    except Exception as ex:
        print("ComplexDataTypeError:", nodeTypeInfo.dataTypeName, ex)
    return instance


def get_complex_value_instance_object(nodeTypeInfo, value):
    if nodeTypeInfo.isArray:
        return [create_instance_of_complex_data_type_class(nodeTypeInfo, v) for v in value]
    else:
        return create_instance_of_complex_data_type_class(nodeTypeInfo, value)


async def create_field_type_info_dictionary(eventType, typeInfoCache):
    """Collect type information for all fields (properties and variables) of the
    event type and its supertypes, keyed by browse name (sub properties as 'parent/sub')."""
    allTypes = await ua_utils.get_node_supertypes(eventType, includeitself=True, skipbase=False)
    fieldTypeInfos = {}
    allFields = []
    for t in allTypes:
        allFields.extend(await t.get_properties())
        allFields.extend(await t.get_variables())
    for fieldNode in allFields:
        attributeName = (await fieldNode.read_browse_name()).Name
        fieldTypeInfos[attributeName] = await typeInfoCache.get(fieldNode)
        # Collect sub properties
        for subProp in await fieldNode.get_properties():
            subPropName = (await subProp.read_browse_name()).Name
            fieldTypeInfos[f"{attributeName}/{subPropName}"] = await typeInfoCache.get(subProp)
    return fieldTypeInfos


class AlarmReplayer:
    """Replays recorded alarm entries as OPC UA events on the Alarms/Messages node.

    Usage: prepare_event(entry) fills the event generator with the recorded field
    values and returns the recorded event time; trigger() then fires the event.
    """

    def __init__(self, evgen, nsIdx, fieldTypeInfos):
        self._evgen = evgen
        self._nsIdx = nsIdx
        self._fieldTypeInfos = fieldTypeInfos  # event field browse name -> NodeTypeInfo

    @staticmethod
    async def create(server, nsIdx, typeInfoCache):
        machineAlarmType = server.get_node(f"ns={nsIdx};i={TC_MACHINE_ALARM_TYPE_ID}")
        # For ConditionId add NodeId property manually. Necessary till implemented in python asyncua library
        await machineAlarmType.add_property(2, 'NodeId', ua.Variant(VariantType=ua.VariantType.NodeId))
        messagesNode = server.get_node(f"ns={nsIdx};s={ALARM_NODE_ID}")
        fieldTypeInfos = await create_field_type_info_dictionary(machineAlarmType, typeInfoCache)
        evgen = await server.get_event_generator(machineAlarmType, messagesNode)
        return AlarmReplayer(evgen, nsIdx, fieldTypeInfos)

    async def prepare_event(self, entry):
        """Fill the event with the recorded field values, return the recorded event time."""
        try:
            event = self._evgen.event
            for attribute in entry["fieldValues"]:
                name = attribute["field"]["browseName"]["name"]
                # ConditionId is called NodeId in the event object
                if name == "ConditionId":
                    name = "NodeId"
                value = attribute["value"]
                if value is not None:
                    typeInfo = self._fieldTypeInfos[name]
                    if typeInfo.isSimpleDataType:
                        set_frozen_attr(event, name, value)
                    else:
                        set_frozen_attr(event, name, get_complex_value_instance_object(typeInfo, value))
            event.NodeId = ua.StringNodeId(event.NodeId.Identifier) # transform to StringNodeId
            event.EventType = ua.NodeId(event.EventType.Identifier, self._nsIdx) # set EventType correct Namespace
            return event.Time
        except Exception as ex:
            print("prepare_event - Unexpected error:", ex)

    async def trigger(self):
        await self._evgen.trigger() # a new time is set automatically


async def init_all_variables_waiting_for_initial_data(server, topNode):
    statusWaitingInitialData = ua.DataValue(StatusCode=ua.StatusCode(ua.StatusCodes.BadWaitingForInitialData))
    nodeList = await ua_utils.get_node_children(topNode)
    for n in nodeList:
        nodeClass = await n.read_node_class()
        if nodeClass == ua.NodeClass.Variable:
            await n.write_value(statusWaitingInitialData)


@uamethod
def condition_refresh(parent, sub_id):
    None

@uamethod
def condition_refresh2(parent, sub_id, mid):
    None


def register_condition_refresh_mocks(server):
    """Register no-op callbacks for ConditionRefresh/ConditionRefresh2.

    asyncua does not implement ConditionRefresh on the server side, but clients
    call it after subscribing to alarms and should not receive an error.
    """
    isession = server.iserver.isession
    condition_refresh_method = Node(isession, ua.NodeId(ua.ObjectIds.ConditionType_ConditionRefresh))
    isession.add_method_callback(condition_refresh_method.nodeid, condition_refresh)
    condition_refresh2_method = Node(isession, ua.NodeId(ua.ObjectIds.ConditionType_ConditionRefresh2))
    isession.add_method_callback(condition_refresh2_method.nodeid, condition_refresh2)


@dataclass
class ReplayConfig:
    endpointUrl: str
    playSpeedFactor: int
    sourceFileName: str


def load_replay_configuration(path):
    doc = minidom.parse(path)
    execution = doc.getElementsByTagName("execution")[0]
    return ReplayConfig(
        endpointUrl=doc.getElementsByTagName("endpoint")[0].getAttribute("url"),
        playSpeedFactor=int(execution.getAttribute("playSpeedFactor")),
        sourceFileName=execution.getAttribute("sourceFileName"))


async def create_server(config):
    server = Server()
    await server.init()
    await server.load_certificate("server-certificate.der")
    await server.load_private_key("server-privatekey.pem")
    server._application_uri = "urn:ServerHost:TRUMPF:MachineDemoServer"
    server.product_uri = "urn:Demo:TRUMPF:MachineDemoServer"
    server.set_endpoint(config.endpointUrl)
    server.set_server_name("TRUMPF Python Demo Server")
    server.set_security_policy([
            ua.SecurityPolicyType.NoSecurity,
            ua.SecurityPolicyType.Basic256Sha256_SignAndEncrypt])
    return server


async def prepare_address_space(server, typeInfoCache):
    """Import the machine node tree, mark all variables as waiting for initial data
    and set up alarm replay. Returns (namespace index, AlarmReplayer)."""
    await server.import_xml("MachineNodeTree.xml")
    await server.load_data_type_definitions()
    idx = await server.get_namespace_index(MACHINE_NAMESPACE)
    machineNode = server.get_node(f"ns={idx};s={MACHINE_ROOT_NODE_ID}")
    await init_all_variables_waiting_for_initial_data(server, machineNode)
    alarmReplayer = await AlarmReplayer.create(server, idx, typeInfoCache)
    return idx, alarmReplayer


def load_recording(path):
    with open(path) as f:
        return json.load(f)


def compute_wait_seconds(previousTimestamp, currentTimestamp, playSpeedFactor):
    """Wait time between two entries = recorded timestamp difference / playSpeedFactor."""
    if previousTimestamp and currentTimestamp:
        return (currentTimestamp - previousTimestamp).total_seconds() / playSpeedFactor
    return 0.0


async def replay_data_value(server, idx, typeInfoCache, entry):
    """Write the recorded value of one entry to its variable node."""
    node = server.get_node(f"ns={idx};s={entry['nodeId']['id']}")
    value = entry["value"]["value"]
    isEmptyList = (type(value) is list) and (len(value) == 0)
    if value is not None and not isEmptyList:
        nodeTypeInfo = await typeInfoCache.get(node)
        utcnow = datetime.now(timezone.utc)
        myValue = value
        if not nodeTypeInfo.isSimpleDataType:
            myValue = get_complex_value_instance_object(nodeTypeInfo, value)
        # DataValue as workaround to set ServerTimestamp, can be removed when implemented in library
        valueAsVariant = ua.Variant(myValue, VariantType=nodeTypeInfo.variantType)
        datavalue = ua.DataValue(valueAsVariant, SourceTimestamp=utcnow, ServerTimestamp=utcnow)
        # VariantType needed because of new type check in write_value
        await node.write_value(datavalue, varianttype=nodeTypeInfo.variantType)


async def run_replay_loop(server, idx, typeInfoCache, alarmReplayer, recording, playSpeedFactor):
    """Replay the recording in an endless loop: wait the (scaled) recorded time
    difference to the previous entry, then replay the entry as event or value write."""
    while True:
        counter = 0
        previousTimestamp = None
        for entry in recording:
            try:
                counter = counter + 1
                nodeId = entry["nodeId"]["id"]
                print(f"--------------------------\nNodeId={nodeId}, Counter={counter}")
                isAlarm = (nodeId == ALARM_NODE_ID)
                if isAlarm:
                    currentTimestamp = await alarmReplayer.prepare_event(entry)
                else:
                    currentTimestamp = parse_time_string(entry["value"]["serverTimestamp"])
                waitingTime = compute_wait_seconds(previousTimestamp, currentTimestamp, playSpeedFactor)
                previousTimestamp = currentTimestamp
                print(f"Sleep={waitingTime}s, isAlarm={isAlarm}")
                await asyncio.sleep(waitingTime)
                if isAlarm:
                    await alarmReplayer.trigger()
                else:
                    await replay_data_value(server, idx, typeInfoCache, entry)
            except ua.uaerrors.BadNodeIdUnknown:
                print(f"Skipping unknown node: {nodeId} (not in address space)")
            except Exception as ex:
                print("Unexpected error:", nodeId, ex)
        await asyncio.sleep(2) # And redo record file


async def main():
    # set runtime dir to directory of script file
    os.chdir(sys.path[0])

    print(f"Python:       {sys.version}")
    print(f"asyncua:      {asyncua.__version__}")
    print(f"python-dateutil: {dateutil.__version__}")

    config = load_replay_configuration("ReplayConfiguration.xml")
    server = await create_server(config)
    register_condition_refresh_mocks(server)
    typeInfoCache = TypeInfoCache(server)
    idx, alarmReplayer = await prepare_address_space(server, typeInfoCache)
    recording = load_recording(config.sourceFileName)

    async with server:
        await asyncio.sleep(2)
        await run_replay_loop(server, idx, typeInfoCache, alarmReplayer, recording, config.playSpeedFactor)


if __name__ == "__main__":
    asyncio.run(main())
