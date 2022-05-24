##How to connect to different machines via the OPC UA Gateway

All machines are aggregated via different OPC UA Namespaces. Each machine gets a unique namespace prefix. After connecting to the OPC UA gateway the first step is to get the corresponding namespace index for a desired machine using the namespace URI of the machine.

With the namespace index and the node identifiers, all items of the machine can be accessed.

####Namespaces for TRUMPF machines:
- ```urn:X0REPLACE0X:TRUMPF:UAInterfaces/http://trumpf.com/TRUMPF-Interfaces/```

Just replace "X0REPLACE0X" with the ID of the machine.

#####Possible usages of the namespace URIs:
- For example in the configuration of your OPC UA client software which items shall be subscribed. Configuration should allways contain the namespace URI and never the namespace index for a namespace URI.
- In your programming SDK usually there is a method which returns the namespace index e.g. ```session.NamespaceUris.GetIndex(machineNamespace)``` or ```client.get_namespace_index(machineNamespace)```
- Each OPC UA server has a standard node "NamespaceArray". That node can be read to get the list of all namespace URIs with their corresponding index. It can allways be accessed via namespace index 0 and integer identifier 2255.

#####General remarks:
After connecting to any OPC UA server the first step is to resolve the desired namespace URI to the namespace index. In OPC UA there is no guarantee that namespace indices will stay the same between restarts of the server. 

Therefore configuration files must never contain namespace indices. They must contain the namespace URIs. For example if there is configuration file which defines which nodes shall be subscribed to, the configuration for each node must be the combination of namespace URI and identifier.

If your vendor only supplies a configuration with the possibility to enter namespace indices instead of namespace URIs, please tell him to correct his mistake.

######Example bad configuration:
```ns=5;i=33```

######Example good configuration:
```ns="urn:X0REPLACE0X:TRUMPF:UAInterfaces/http://trumpf.com/TRUMPF-Interfaces/";i=33```

The only fixed and reserved namespace is the namespace for the URI ```http://opcfoundation.org/UA/```, it allways is index 0.
