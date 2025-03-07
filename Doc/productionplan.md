## How to add orders to the production plan of the machine

There is no OPC UA method. Orders are added to the production plan via the file interface LST or TPP.

## Definitions for cutting machines

Since different parts are nested to one sheet, there might be a 1:1 or 1:N relationship to customer orders, depending on the company process.

##### Machine: ProgramName
The Program describes how to cut one sheet metal.

##### Machine: ProductionOrderIdentifier [TruTops Boost: Manufacturing order description]
The ProductionOrder defines a concrete production task. A ProductionOrder defines the task to cut a Program n-times and defines a name for the task, the ProductionOrderIdentifier. Apart from the program count other additional parameters, like the sequence number for loading and unloading, can be set in the ProductionOrder.

##### Machine: ProductionPackageName [TruTops Boost: Job no., Job name]
The third level of aggreagation is the ProductionPackage. It can be used to combine several ProductionOrders and give them a common name, the ProductionPackageName. For example to relate several ProductionOrders to an assembly group.

##### Machine: Production plan
The production plan is the "playlist" on the machine and consists of production orders, which might be grouped to production packages.


## Production plan functionalities via LST file:

Production orders can be appended to the production plan of the machine using a FERTIGUNG_AUFTRAG_TMP section in the LST file.


```
BEGIN_FERTIGUNG_AUFTRAG_TMP
C
ZA,MM,6
MM,AT,1,  10,1,1,,'Jobname'                           ,,'',T
MM,AT,1,  20,1,1,,'FertAuftrBez'                      ,,'',T
MM,AT,1,  30,1,1,,'FertStatus'                        ,,'',T
MM,AT,1,  40,1,1,,'Programmname'                      ,,'',T
MM,AT,1,  50,1,1,,'SollAnzahl'                        ,,'',Z
MM,AT,1,  60,1,1,,'IstAnzahl'                         ,,'',Z
C
ZA,DA,2
DA,'JOB43','JOB43_1','0','JOB43_1',1,0
DA,'JOB47','JOB47_1','0','JOB47_1',4,0
C
ENDE_FERTIGUNG_AUFTRAG_TMP

```

| Id    | Name            | Comments               |
| ----- | ----------------| ---------------------  |
| 10    | JobName, ProductionPackageName |         |
| 20    | ManufacturingOrder, ProductionOrderIdentifier | Must be unique in the production plan. |
| 30    | ManufacturingStatus, ProductionOrderState    | (optional) 0=Released, 9=Disabled |
| 40    | ProgramName     |
| 50    | TargetQuantitiy | Number of sheet metal program runs.
| 60    | CurrentQuantity | (optional) default=0

If a LST containing a FERTIGUNG_AUFRAG_TMP section is imported, the production plan gets filled. The FERTIUNG_AUFTRAG_TMP section can exist in addition to the program in the LST or as the sole entry.

#### Activate FERTIGUNG_AUFTRAG_TMP section in TruTops Boost

To auto generate the section, set the **Transfer type** to "Production Package" in the workplace settings of a machine in HomeZone.

![Transfer type](transferType.png)


## Production plan functionalities via TPP file:

TPP files can be imported on TRUMPF cutting machines. With TPP files, production orders can be appended to the production plan of the machine. Their content is XML and the file ending must be .tpp. TPP is an abbreviation for "TRUMPF Production Package".

Example TPP files:
- [examplePackage1.tpp](Attachments/examplePackage1.tpp)
- [examplePackage2.tpp](Attachments/examplePackage2.tpp)

XML schema file:
- [JobOrders.xsd](Attachments/JobOrders.xsd)

| XML-Object Name    | Description       | Attributes           |
| ------------------ | ------------------| -------------------  |
| Jobs               | List of Jobs       |                     |
| Job                | Collection of production orders and their sequence in the production plan.       | JobName        |
| DeviceOrderChain   | Not in useage any more. But each device order must be embedded into a DeviceOrderChain element.      |         |
| DeviceOrder        | Production order at 2D-cutting machines. Defines a production order for a device. The desired "work plan" is defined via the SequenceListId. It defines whether loading/unloading/processing/sorting steps are executed or not. | ProgName, SequenceListId, DesiredQuantity, CurrentQuantity, State          |
| Description       | Production order description.       |           |
| Comment           | Additional comment for the production order.      |           |
| Store             | Defines the storage data: which raw material should be fetched from where, on which pallets the finished parts should be unloaded. Platforms or double carts are also referred to as "storage facilities".      |           |
| Process           | Defines a process: For which storage station(s) the data record applies: Raw material, scrap skeleton, maxi parts, emergency, sorting parts, machine pallet, system pallet for machine pallet, scrap.    | LocationTypeProperty  |
| Group            | Additional grouping feature if several data records have to be kept apart for a LocationTypeProperty. Example: When sorting small parts, several pallets can be used on several stations at the same time.     | LocationTypePropertyGroup, OneLocationTypePropertyGroupRequired          |
| Data           | Defines the pallet, the material or the stock group type to be requested. Or the location at which a function is to be carried out.      | Sequence, Quantity, RequestType, RequestValue, RequestValue2           |
| SortMaster / SortData     | Settings for 2D-Laser sorting device SortMaster.     | SortMode, CleanPallet, RetryCount   |
| OrderSettings           | Settings of production orders.      | SortingEnabled, CleanPalletEnabled, StopForManualUnloadEnabled, EmptyPalletOrderStartEnabled, PalletChangerUseMode             |
| PartOrderInformation | Defines the relationship between the parts in the DeviceOrders and the customer orders. (Which part belongs to which customer).      | SequenceInPartInformation, CustomerOrder, Operation           |
| ProductionOrder        | Production order at 3D-cutting and tube machines.     | Name, OrderType, OrderValueText, CurrentQuantity, DesiredQuantity, MaxQuantity, State, ContinuousMachining            |

If a machine supports the OPC UA interface package MCI V01.00.00, the current production plan can be exported in TPP format via the OPC UA method: `ID 331: GetProductionPlanAsTPP`