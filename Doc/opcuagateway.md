## How to access the data / signals of different machines aggregated in the OPC UA Gateway

All machines are aggregated via different OPC UA Namespaces. Each machine gets a unique namespace prefix. To access the data of a desired machine, first connect to the OPC UA gateway, then determine the corresponding namespace index using the unique namespace URI of that machine.

With the obtained namespace index and the node identifiers, all data items / signals of the machine can be accessed.

#### Namespaces schema for TRUMPF machines:
- ```urn:X0REPLACE0X:TRUMPF:UAInterfaces/http://trumpf.com/TRUMPF-Interfaces/```

Just replace *"X0REPLACE0X"* with the *hostname* of the TRUMPF machine.

##### Possible usage of the namespace URIs:
- For example in the configuration of your OPC UA client software which items shall be subscribed. Configuration should always contain the namespace URI and never the namespace index.
- In your programming SDK usually there is a method which returns the namespace index e.g. ```session.NamespaceUris.GetIndex(machineNamespace)``` or ```client.get_namespace_index(machineNamespace)```
- Each OPC UA server has a standard node "NamespaceArray". That node can be read to get the list of all namespace URIs with their corresponding index. It can always be accessed via namespace index 0 and integer identifier 2255.

##### General remarks:
After connecting to any OPC UA server the first step is to resolve the desired namespace URI to the namespace index. In OPC UA there is no guarantee that namespace indices will stay the same between new client sessions or restarts of the server. 

Therefore configuration files must never contain namespace indices. They must contain the namespace URIs. For example if there is a configuration file for subscriptions, each node must be referenced via a combination of namespace URI and identifier.

If your vendor only allows to configure namespace indices and not namespace URIs, please tell them to allow URIs.

###### Example bad configuration:
```ns=5;i=33```

###### Example good configuration:
```ns=urn:X0REPLACE0X:TRUMPF:UAInterfaces/http://trumpf.com/TRUMPF-Interfaces/;i=33```

The only fixed and reserved namespace is the namespace for the URI ```http://opcfoundation.org/UA/```, it's index is always 0.
