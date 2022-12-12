## Python Alarm Converter

### Introduction
This is a complete example application which converts OPC UA Alarms and Conditions events to standard OPC UA data items. The application includes a client and a server. The client subscribes to the alarms and the server provides them as data items. It might be interesting if the used client application is not yet able to consume OPC UA events.

The default configuration is for the [PythonMachineDemoServer](../../MachineDemoServer/Python).

A simple example on how to just consume alarms, can be found [here](../../Examples/Python).

It is made as an example to be used with Trumpf machines, but might also be adapted or tested with other OPC UA alarms and conditions servers.

Feel free to use it, adapt it to your needs and contribute back to the open source project. There is no offical TRUMPF support for the OPC UA open source examples and applications.

##### View of converted alarms
![Picture Alarms](doc/alarmConverter.PNG)

### Quickstart
Download python libraries 'asyncua' and 'aioconsole'. Adapt configuration in `machineconfiguration.xml` and execute `alarm_converter.py`.

### Requirements
- Python >= Python 3.7
    - Version >= Python 3.11 is recommended due to startup performance improvements.
- Python opcua-asyncio library >= v1.0.1
- Python aioconsole library

Tested with opcua-asyncio v1.0.1. If it will not run, use exactly that version and create an issue with error description and used library version.

### Description
For each configured machine an OPC UA object with the given machine name is created. That object contains 20 alarm objects which are placeholder slots for upcoming alarms. Each alarm contains data variables, which provide the relevant alarm information.

In case an alarm occurs on the machine, the first unused alarm slot is assigned and the variables are updated with the alarm information. As long as the alarm is pending, the data is available. When the alarm disappears, the variables are reset to empty values.

Furthermore for each machine, there is a variable "AlarmList" which contains the current pending AlarmIdentifiers as a list of strings. On each change (alarm appearing or disappearing), the list is updated.

During execution of the alarm_converter there are console outputs and some console commands which can be entered.

```
---------------------------------------
--> exit     - exit the application      
--> verbose  - set log level to verbose  
--> standard - set log level to standard 
--> config   - show loaded config        
--> show     - show active connections   
--> dir      - show the current directory
---------------------------------------- 
```

### Installation and Execution
With Python installed, the script file can be exuted with `python alarm_converter.py`. As an alternative a fully self contained .exe can be created with PyInstaller.

##### Detailed instruction:
- [Download and install Python](https://www.python.org/downloads/) >= Python 3.7. On installation set checkbox for adding to system path.
- Install opcua-asnycio library >= 1.0.1 and aioconsole library with 
`pip3 install asyncua aioconsole` or upgrade with 
`pip3 install --upgrade asyncua aioconsole`
Behind a company proxy you may need to add the proxy server and trust servers. Search for proxy settings and look for the manual proxy server. 
`pip3 install --trusted-host pypi.org --trusted-host files.pythonhosted.org --proxy=http://username:password@proxyserver:port asyncua aioconsole`

- Get all files and copy them to a folder. Easiest way is to download all files of the github repository. [Download zip](https://github.com/TRUMPF-IoT/OpcUaMachineTools/archive/main.zip). Or use a git client.
- Enter the folder containing alarm_converter.py and execute the server with `python alarm_converter.py`
- On Linux if Python 2.x and Python 3.x are installed execute with `python3 alarm_converter.py`. 


### Configuration

Adapt configuration in `machineconfiguration.xml`.

#### Basic Configuration

| Attribute       | Description |
| --------------  | ----------- |
| machinesServer  | Set the OPC UA server uri of the server providing the alarms |
| isTrumpfServer  | "false" for non trumpf machines. Then alarms will be subscribed on the server node and not on a trumpf specific node. |
| adapterEndpoint | Set the OPC UA server uri the converted alarms will be provided as items |
| traceLevel      | "standard" for normal operation. "verbose" for diagnose purposes. |

#### Machines configuration

For each machine on the trumpf OPC UA gateway add an machine entry.

| Attribute       | Description |
| --------------  | ----------- |
| machineName  | Set the desired name of the OPC UA object containing the converted alarm items  |
| ns  | Set the namespace of the machine |

#### Provided example configurations
- machineconfiguration.xml              --> Configuration for PythonMachineDemoServer
- machineconfiguration_ExampleGateway.xml  --> Configuration example for a Trumpf opc gateway.
- machineconfiguration_QuickstartServer.xml --> Configuration example for opc foundation [AlarmCondition quickstart sample](https://github.com/OPCFoundation/UA-.NETStandard-Samples).


### OPC UA Client for testing
A generic OPC UA client can be used to explore and browse the OPC UA server. A recommended free client is "UaExpert" from UnifiedAutomation. [Download link.](https://www.unified-automation.com/downloads/opc-ua-clients.html)

#### How to view Alarms and conditions
After starting UaExpert and connecting to the server, open the **Event View** with "Document -> Add -> Document Type: Event View".

Drag the "Messages" node to the Configuration section in the Event View. Now you can observe all incoming Events in the Events-Tab and all pending Alarms/Warnings in the Alarms-Tab.


### License
The Python Alarm Converter is licensed under the MIT License.

```
MIT License

Copyright (c) 2022 TRUMPF Werkzeugmaschinen SE + Co. KG

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
