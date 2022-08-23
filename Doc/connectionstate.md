## How to determine the connection state of a machine aggregated in the OPC UA gateway

####Possibility 1 (recommended):
Subscribe to an item in the namespace of the machine which always has a value. For example FeedrateOverride (s=33). If the callback delivers a value and the StatusCode is Good (0x00000000), the machine is connected. If the callback delivers another StatusCode, for example BadOutOfService (0x808D0000) or BadConnectionClosed (0x80AE0000), then the machine should be regarded as disconnected.

####Possibility 2:
Subscribe to a special ServerStatus variable in the OPC UA gateway for each machine. The node id of the ServerStatus is ```ns=1;s=OpcUaServers.{connectionName}.ServerStatus```. If the value is "Connected", then the machine is connected. If the value is not "Connected", then the machine is disconnected. That method will not work with the OPC UA retrofit cube.

ServerStatus browse path:
Objects -> DeviceSet -> OPC UA Servers -> {ConnectionName} -> Diagnostics -> ServerStatus