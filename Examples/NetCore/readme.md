## .NET Core OPC UA Client Examples

### Introduction
Everything is provided as open source to provide examples on how to work and program with OPC UA. For the open source tools and examples there is no official TRUMPF support. Feel free to participate and contribute.

### Requirements
- .Net Core 3.1
- OPCFoundation [.NetStandard](https://github.com/OPCFoundation/UA-.NETStandard) OPC UA nuget packages
    - OPCFoundation.NetStandard.Opc.Ua.Client.Debug
    - OPCFoundation.NetStandard.Opc.Ua.Client.ComplexTypes.Debug

### Configuration

The basic configuration for applications using the OPCFoundation .NetStandard SDK is done within the Config.xml file of the application. Here it is Opc.Ua.BasicClient.Config.xml. 

The server endpoint is configured in Program.cs via the endpointURL. The default URL is the setting for the TRUMPF Python Demo Server.

#### Certificate handling
Getting some knowledge about certificate handling is necessary. Ignoring the topic will not lead to success.

During a connection attempt client and server exchange certificates. A connection is only established if both sides  have accepted/trusted the certificates of each other.

*How does the .NetStandard Client gets his client certificate?*
-> If there is no self signed client certificate yet, a certificate is auto created during ```await application.CheckApplicationInstanceCertificate```. 

*Where is the storage location of certificates?*
-> The storage locations are defined in Opc.Ua.BasicClient.Config.xml. On Windows, X509Store and CurrentUser\My lead to the windows certificate store. The client certificate (ApplicationCertificate) can be viewed or deleted with the Windows Certificate Management Console (certmgr.msc). If there are issues, try to run the client with admin credentials or configure a different certificate store in the xml. 

Auto acceptance of server certificates can also be activated in the xml config. Accepting a server certificate is done by moving the certificate into the trusted folder. Initially a server certificate is stored in the rejected folder.

### Examples

Run an example by uncommenting in Program.cs. The examples can be run in conjunction with the TRUMPF Python Demo Server.

**AlarmsExample**

Shows how to consume Alarms and Conditions and how to determine the currently pending alarms.

**ComplexTypeExample**

Shows how to read items with complex data types using the complex type system.


### License
The .NET Core OPC UA Client examples are licensed under the MIT License.
