## Python Machine Demo Server

### Introduction
This is a **demo server** which is intended to provide a first impression regarding the address space, data types, some exemplary signals and events of OPC UA signals on TRUMPF machines. To achieve this the demo server is capable of replaying a set of prerecorded signals in a loop.
The demo server is not exactly the same as the OPC UA server on the machines, but it is pretty similar in many regards. 

Be aware that some signals of the example set might not be available on certain machine types or are only available on newer machine generations. Also signals can be part of different OPC UA interface packages, i.e. licensable machine options, which will influence availability on concrete machine instances in the field.
 
Do not rely on details of the demo server!
 
Everything is provided as open source to provide examples on how to work and program with OPC UA. For the open source tools and examples there is no official TRUMPF support. Feel free to participate.


### Specialities of the demo server
The demo server provides two endpoints, one without security policy and one with security policy type *Basic256Sha256*. In contrast, the TRUMPF OPC UA proxy only provides the secure *Basic256Sha256* endpoint.

Furthermore the demo server just accepts any client certificate and does not perform any checks regarding the content or structure of the certificate. The TRUMPF OPC UA proxy is much more restrictive in those regards.

Alarms and Conditions can only be subscribed on the "Messages" node. The ConditionRefresh Method for Alarms and Conditions is not supported by the demo server. (How to view Alarms and Conditions see the UaExpert example at the bottom of the page)



### Requirements
- Python >= Python 3.7
- Python opcua-asyncio library >= 0.9.95

Tested with 0.9.95. If it will not run, use exactly that version and create an issue with error description and used library version.

### Installation and Execution
With Python installed, the script file can be exuted with `python PythonMachineDemoServer.py`. As an alternative a fully self contained .exe can be created with PyInstaller.

##### Detailed instruction:
- [Download and install Python](https://www.python.org/downloads/) >= Python 3.7. On installation set checkbox for adding to system path.
- Install opcua-asnycio library >= 0.9.95 with 
`pip3 install asyncua` or upgrade with `pip3 install --upgrade asyncua`
Behind a company proxy you may need to add the proxy server and trust servers. Search for proxy settings and look for the manual proxy server. 
`pip3 install --trusted-host pypi.org --trusted-host files.pythonhosted.org --proxy=http://username:password@proxyserver:port asyncua`

- Download all files and copy them to a folder. Easiest way is to download all files of the github repository. [Download zip](https://github.com/TRUMPF-IoT/OpcUaMachineTools/archive/main.zip). 
- Enter the folder containing PythonMachineDemoServer.py and execute the server with `python PythonMachineDemoServer.py`
- On Linux if Python 2.x and Python 3.x are installed execute with `python3 PythonMachineDemoServer.py`. 

To create a self contained .exe on Windows which can be used on systems without Python installed:
- Install PyInstaller with: `pip3 install pyinstaller`
- Comment out line `os.chdir(sys.path[0])` in PythonMachineDemoServer.py. That can cause issues. 
- Switch to folder and execute `pyinstaller.exe --onefile PythonMachineDemoServer.py`. The result is in the "dist" directory.

### Configuration
Basic configuration is done via **ReplayConfiguration.xml**. The following configurations can be done:
- "url" defines the endpoint URL where the clients connect to.
- "sourceFileName" defines the file with prerecorded signals.
- "playSpeedFactor" defines the time multiplier in replaying the signals.

### OPC UA Client
A generic OPC UA client can be used to explore and browse the OPC UA server. A recommended free client is "UaExpert" from UnifiedAutomation. [Download link.](https://www.unified-automation.com/downloads/opc-ua-clients.html)

#### How to view Alarms and conditions
After starting UaExpert and connecting to the server, open the **Event View** with "Document -> Add -> Document Type: Event View".

Drag the "Messages" node to the Configuration section in the Event View. Now you can observe all incoming Events in the Events-Tab and all pending Alarms/Warnings in the Alarms-Tab.


### License
The Python Machine Demo Server is licensed under the MIT License.
