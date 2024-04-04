## Remarks
- Signal documentation
    - *Sampling rate / Trigger* and *Initial condition* are relevant for the initial signal state after machine restart.
    - The *"Trigger"* defines the moment the signal is updated. Until a signal is updated for the first time after restarting the machine, the signal is in state "BadOutOfService" or in state "BadWaitingForInitialData".
- The OPC UA standard defines two ways to receive data. Both are used by TRUMPF.
    - Data Items which can be read or subscribed to.
    - Events which can be subscribed to.
- Events
    - Events can be subscribed on object nodes whose attribute "EventNotifier" is set to "SubscribeToEvents".
    - The OPC UA Alarms and Conditions ([OPC 10000-9: UA Part 9: Alarms and Conditions](https://reference.opcfoundation.org/Core/Part9/v105/docs/)) standard is based on events.
    - In the TRUMPF address space, alarm events can be subscribed on ID 179. Other object nodes are defined to provide certain events, for example ID 444: SheetLoadingFinished.
    - Events can be viewed in UaExpert by adding a new document tab with Document->Add->Event view.


## Guidelines


- Do not hardcode **namespace indexes**. Resolve namespace index from namespace URI before accessing it. Read section "[Node Namespace](https://opclabs.doc-that.com/files/onlinedocs/PicoOpc/1.0/BrowserHelp/Node%20Identification.html)".
- To support **complex data types** like structs, use the automatic mechanisms of your SDK to auto create the necessary classes and types. For example complexTypeSystem.Load() in the opc foundation .NET SDK. In the future, defined structs might be extended via inheritance. To stay compatible, the auto type mechanisms must be used.
    Example of complex type:
    ```
    TsPositionOffset
    {
        double XOffset;
        double YOffset;
        double ZOffset;
        doubl XRotation;
        double YRotation;
        double ZRotation;
    }
    ```
- Node hierarchy might be reorganised in a future TRUMPF OPC UA interface release. Do **not rely on (i.e. hardcode) node hierarchy**. 
    - Access the nodes programmatically using nodeIDs OR
    - Browse for ObjectType and dynamically resolve node IDs if possible.
- Do not depend on browse names or display names for signals that are not part of the OPC UA companion specifications. They may be changed in future TRUMPF OPC UA interface releases. The node IDs will remain stable.
- There is no guarantee that all signals related to the same trigger (e.g. program started) will be updated on the same millisecond and with the exact same timestamp.
- Nodes can remain without a value until the first trigger event. Until then the OPC UA status code is "BadWaitingForInitialData 0x80320000" or "BadOutOfService 0x808D0000". That is a standard response. (When certain nodes are set at a certain trigger, they remain uninitialized until the first trigger event occurs.)





 

    