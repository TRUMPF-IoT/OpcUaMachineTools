> [!NOTE]
> Specific signals might or might not be available on a machine, depending on technology, age and software release version.

### Monitoring basic machine status

| ID            | Description | OPC UA Signal Package | OPC Mechanism |
| ------------- | ------------| --------------------- | ------------- |
| `ID 4 [Running]` | Indicates that the production plan on the machine is active. | Production Status Interface V3.0 | DATA ITEM |
| `ID 32 [Name]` | Current active program name. | Production Status Interface V2.0 | DATA ITEM |
| `ID 33 [FeedrateOverride]` | Indicates that the production plan on the machine is active. | Production Status Interface V2.0 | DATA ITEM |
| `ID 35.Running` | Basic program state. All Boolean. Active state is True. | Production Status Interface V2.0 | DATA ITEM |
| `ID 35.Stopped` | |  | |
| `ID 35.Aborted` | |  | |
| `ID 35.Ended`   | |  | |
| `ID 275 [ProgramState]` | Alternative to ID35.x, basic program state as Enum. | Production Status Interface V2.1 | DATA ITEM |

### Getting machine alarms and error messages

| ID            | Description | OPC UA Signal Package | OPC Mechanism |
| ------------- | ------------| --------------------- | ------------- |
| `ID 179 [Messages]` | Machine alarm/messages events. Node used to register for events of type `TcMachineAlarmType`. | Production Status Interface V2.0 | EVENT |

### Reading parts and material related information

| ID            | Description | OPC UA Signal Package | OPC Mechanism |
| ------------- | ------------| --------------------- | ------------- |
| `ID 145 [PartsInProgramList]` | Total count of parts on current sheet of current active program. If program is finished with state “Ended”, those parts can be counted as produced parts. | Material Flow Interface V1.0 | DATA ITEM |
| `ID 147 [SheetTechnologyList]` | Parameters of sheet used in current active program. | Material Flow Interface V1.0 | DATA ITEM |
| `ID 443 [PartUnloadingFinished]` | This node sends events of types: `PartUnloadingFinishedEventType`; Trigger: At successful part unload | Material Flow Interface V2.0 | EVENT |
| `ID 444 [SheetLoadingFinished]` | This node sends events of types: `SheetLoadingFinishedEventType`; Trigger: Loading of a sheet is finished | Material Flow Interface V2.0 | EVENT |
| `ID 445 [SheetUnloadingFinished]` | This node sends events of types: `SheetUnloadingFinishedEventType`; Trigger: Unloading of a sheet is finished | Material Flow Interface V2.0 | EVENT |
| `ID 455 [PartUnloadingStarted]` | This node sends events of types: `PartUnloadingStartedEventType`; Trigger: At successful start of part unload | Material Flow Interface V2.0 | EVENT |

### Other interesting signals

| ID            | Description | OPC UA Signal Package | OPC Mechanism |
| ------------- | ------------| --------------------- | ------------- |
| `ID 59 [NetBeamOnTime]` | The accumulated total laser beam on time of the current active or last executed program until the next program is started. | Production Status Interface V2.0 | DATA ITEM |
| `ID 69 [EmergencyStop]` | Signals that an emergency stop is active. | Production Status Interface V2.0 | DATA ITEM |
| `ID 73 ... ID 77 [LightBarriers]` | The safety circuit for light barrier #1 has been interrupted. | Production Status Interface V2.0 | DATA ITEM |
| `ID 330 [LaserTechnologyList]` | Laser processing parameters in current active program. | Process Parameters Interface V1.0 | DATA ITEM |
| `ID 343 [WorkpiecePositionOffset]` | Offset of the workpiece position related to the programmed zero point. | Material Flow Interface V1.0 | DATA ITEM |
| `ID 345 [PalletPosition]` | Position of machine pallets A and B. Signal change when the pallet end position is reached. Status Undefined when pallet in motion and on change preparation position (pallet B outside and bottom, pallet A outside and top, pallet A and B outside and top). | Material Flow Interface V1.0 | DATA ITEM |



