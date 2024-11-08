## General recommendations

#### To connect a new client to the TRUMPF OPC UA Gateway
- Usage of a self-signed certificate on client side is necessary.
- A connection attempt must be made with the still untrusted client, which will be declined by the OPC UA Proxy / OPC Gateway.
- Afterwards use the TRUMPF OPC UA Proxy / OPC Gateway configuration tool to trust the client.

#### Explore and test the OPC UA interface with UaExpert
- Download and use the generic free OPC UA client [UaExpert](https://www.unified-automation.com/products/development-tools/uaexpert.html).
- OPC UA has two different mechanism to subscribe to data via DATA ITEMS or via EVENTS.
    - For subscriptions to **Data Items** use the "Data Access View" (`UaExpert -> Document -> Add -> Data Access View`).
    - For subscriptions to **Events** use the "Event View" (`UaExpert -> Document -> Add -> Event View`).
- TRUMPF machines, if supported, provide the machine **alarms/messages** via the “OPC UA Alarms and Conditions” Standard, which is based on the OPC UA Events mechanism (see ID 179: Messages).
- Examples on how to consume alarms/messages can be found [here](../Examples/NetCore) and [here](../Examples/Python). 
- To see all alarms/messages from a machine with UaExpert:
    - Drag the Messages node (179: Messages) to the Configuration Area in the Event View.
    - Select “`TcMachineAlarmType`” in the Configuration Area and press “**Apply**” to see all parameters in future alarms (`ConditionType → AckConditionType → AlarmConditionType → …`)
    - Observe the flow of events in the events tab. See the current pending alarms in the alarms tab.
