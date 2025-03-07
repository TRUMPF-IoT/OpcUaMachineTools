<?xml version="1.0" encoding="UTF-8"?>
<TrumpfProductionPackage xmlns="http://www.trumpf.com/xmlns/cadcam/TRUMPFMasterfile-1.0" xmlns:fmc="http://www.trumpf.com/xmlns/cadcam/FMC-1.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="TrumpfMasterfile.xsd">
  <fmcc xmlns="">
    <source>
      <fmc:Jobs xsi:schemaLocation="http://www.trumpf.com/xmlns/cadcam/FMC-1.0 JobOrders.xsd">
        <fmc:Job JobName="*">
          <fmc:DeviceOrderChain>
            <fmc:DeviceOrder ProgName="N14_1" SequenceListId="80" CurrentQuantity="0" DesiredQuantity="8" State="ENABLED">
              <fmc:Description><![CDATA[N14_1]]></fmc:Description>
              <fmc:Comment />
              <fmc:OrderSettings>
                <fmc:OrderData CleanPalletEnabled="false" PalletChangerUseMode="A_AND_B" SortingEnabled="false" />
              </fmc:OrderSettings>
            </fmc:DeviceOrder>
          </fmc:DeviceOrderChain>
          <fmc:DeviceOrderChain>
            <fmc:DeviceOrder ProgName="FLAT_KEY_EAV" SequenceListId="1" CurrentQuantity="1" DesiredQuantity="5" State="ENABLED">
              <fmc:Description><![CDATA[FLAT_KEY_EAV]]></fmc:Description>
              <fmc:Comment />
              <fmc:OrderSettings>
                <fmc:OrderData CleanPalletEnabled="false" PalletChangerUseMode="UNDEFINED" SortingEnabled="false" />
              </fmc:OrderSettings>
            </fmc:DeviceOrder>
          </fmc:DeviceOrderChain>
          <fmc:DeviceOrderChain>
            <fmc:DeviceOrder ProgName="CARTRIDGE_HOLDER" SequenceListId="80" CurrentQuantity="0" DesiredQuantity="1" State="BLOCKED">
              <fmc:Description><![CDATA[CARTRIDGE_HOLDER]]></fmc:Description>
              <fmc:Comment />
              <fmc:OrderSettings>
                <fmc:OrderData CleanPalletEnabled="false" PalletChangerUseMode="A_AND_B" SortingEnabled="false" />
              </fmc:OrderSettings>
            </fmc:DeviceOrder>
          </fmc:DeviceOrderChain>
        </fmc:Job>
      </fmc:Jobs>
    </source>
  </fmcc>
</TrumpfProductionPackage>