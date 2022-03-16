## Python OPC UA Client Examples

### Introduction
 
Everything is provided as open source to provide examples on how to work and program with OPC UA. For the open source tools and examples there is no official TRUMPF support. Feel free to participate.

### Requirements
* Python >= Python 3.7
* Python opcua-asyncio library >= 0.9.14

### Examples

#### Generate certificate - gen_certificate.py
Library used in all examples to create the certificate if not yet created.

#### Show pending alarms - show_current_alarms.py
Example client to show the alarms and messages via OPC UA Alarms and Conditions.


### Installation and Execution
With Python installed, the script file can be exuted with `python exampleName.py`. As an alternative a fully self contained .exe can be created with PyInstaller.

##### Detailed instruction:
* [Download and install Python](https://www.python.org/downloads/) >= Python 3.7. On installation set checkbox for adding to system path.
* Install opcua-asnycio library >= 0.9.14 with 
`pip3 install asyncua` or upgrade with `pip3 install --upgrade asyncua`
Behind a company proxy you may need to add the proxy server and trust servers. Search for proxy settings and look for the manual proxy server. 
`pip3 install --trusted-host pypi.org --trusted-host files.pythonhosted.org --proxy=http://username:password@proxyserver:port asyncua`

* Download all files and copy them to a folder. Easiest way is to download all files of the github repository. [Download zip](https://github.com/TRUMPF-IoT/OpcUaMachineTools/archive/main.zip). 
* Enter the folder containing the examples and execute the client example with `python exampleName.py`
* On Linux if Python 2.x and Python 3.x are installed execute with `python3 exampleName.py`. 

To create a self contained .exe on Windows which can be used on systems without Python installed:
* Install PyInstaller with: `pip3 install pyinstaller`
* Comment out line `os.chdir(sys.path[0])` if it exists in python file. 
* Switch to folder and execute `pyinstaller.exe --onefile exampleName.py`. The result is in the "dist" directory.


### License
The Python OPC UA Client examples are licensed under the MIT License.
