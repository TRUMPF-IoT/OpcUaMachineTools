<?xml version="1.0" encoding="UTF-8"?>
<TrumpfProductionPackage xmlns="http://www.trumpf.com/xmlns/cadcam/TRUMPFMasterfile-1.0"
    xmlns:fmc="http://www.trumpf.com/xmlns/cadcam/FMC-1.0"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="TrumpfMasterfile.xsd">
    <fmcc xmlns="">
        <source>
            <fmc:Jobs xsi:schemaLocation="http://www.trumpf.com/xmlns/cadcam/FMC-1.0 JobOrders.xsd">
                <fmc:Job JobName="ONLY_MAXI_NEW">
                    <fmc:DeviceOrderChain>
                        <fmc:DeviceOrder ProgName="ONLY_MAXI_NEW_1" SequenceListId="3" CurrentQuantity="3" DesiredQuantity="5" State="ENABLED">
                            <fmc:Description><![CDATA[ONLY_MAXI_NEW_1]]></fmc:Description>
                            <fmc:Comment />
                            <fmc:Store>
                                <fmc:Process LocationTypeProperty="SUPPLY_LOCATION">
                                    <fmc:Group LocationTypePropertyGroup="0">
                                        <fmc:Data Sequence="1" RequestType="STOCK_NAME_ON_CARRIER_TYPE" RequestValue="00100500" />
                                    </fmc:Group>
                                </fmc:Process>
                                <fmc:Process LocationTypeProperty="GRID_LOCATION">
                                    <fmc:Group LocationTypePropertyGroup="0">
                                        <fmc:Data Sequence="1" RequestType="PALLET_NUMBER" RequestValue="105" />
                                    </fmc:Group>
                                </fmc:Process>
                                <fmc:Process LocationTypeProperty="MAXI_LOCATION">
                                    <fmc:Group LocationTypePropertyGroup="0">
                                        <fmc:Data Sequence="1" RequestType="STOCK_GROUP_TYPE" RequestValue="SPml" />
                                    </fmc:Group>
                                </fmc:Process>
                            </fmc:Store>
                            <fmc:OrderSettings>
                                <fmc:OrderData CleanPalletEnabled="false" PalletChangerUseMode="ONLY_A" SortingEnabled="false" />
                            </fmc:OrderSettings>
                        </fmc:DeviceOrder>
                    </fmc:DeviceOrderChain>
                </fmc:Job>
                <fmc:Job JobName="ONLY_LO_UNLO_NEW">
                    <fmc:DeviceOrderChain>
                        <fmc:DeviceOrder ProgName="ONLY_LO_UNLO_NEW_1" SequenceListId="80" CurrentQuantity="0" DesiredQuantity="10" State="BLOCKED">
                            <fmc:Description><![CDATA[ONLY_LO_UNLO_NEW_1]]></fmc:Description>
                            <fmc:Comment />
                            <fmc:OrderSettings>
                                <fmc:OrderData CleanPalletEnabled="true" PalletChangerUseMode="A_AND_B" SortingEnabled="false" />
                            </fmc:OrderSettings>
                        </fmc:DeviceOrder>
                    </fmc:DeviceOrderChain>
                </fmc:Job>
            </fmc:Jobs>
        </source>
    </fmcc>
</TrumpfProductionPackage>