#!/usr/bin/env python3

# MIT License

# Copyright (c) 2022 TRUMPF Werkzeugmaschinen SE + Co. KG

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import asyncio
import logging
import custom_logger
import os 
import sys
from machines_adapter_client import MachinesAdapterClient
from adapter_server import AdapterServer
from aioconsole import ainput
from xml.dom import minidom


async def interactive(machinesAdapter):
    while True:
        print('---------------------------------------')
        print('--> exit     - exit the application')
        print('--> verbose  - set log level to verbose')
        print('--> standard - set log level to standard')
        print('--> config   - show loaded config')
        print('--> show     - show active connections')
        print('--> dir      - show the current directory')
        print('----------------------------------------')
        line = await ainput("")
        if line == 'dir': 
            print(f"DIRECTORY --- [{sys.path[0]}]")
        elif line == 'verbose':
            print("LOG LEVEL --- [Set log level to verbose.]")
            custom_logger.set_level('verbose')
        elif line == 'standard':
            print("LOG LEVEL --- [Set log level to standard.]")
            custom_logger.set_level('standard')
        elif line == 'config':
            print(f"CONFIG --- URL=[{machinesAdapter.uri}]")
        elif line == 'show':
            for m in machinesAdapter.machines:
                if m.sub is not None:
                    print(f"CONNECTED     --- [{m.ns}]")
                else:
                    print(f"NOT CONNECTED --- [{m.ns}]")
        elif line == 'exit':
            print("EXIT --- [Exit application.]")
            break


async def main():
    # set runtime dir to directory of script file
    os.chdir(sys.path[0])    
    custom_logger.setup_logging("./logs/", "logger.log")
    logger = logging.getLogger(__name__)
    
    try:
        logger.trace("Directory=%s", sys.path[0])

        # Read configuration XML Document
        doc = minidom.parse("machineconfiguration.xml")                           
        custom_logger.set_level(doc.documentElement.getAttribute("traceLevel") )
       
        # Create and start server
        isTrumpfServer = doc.documentElement.getAttribute("isTrumpfServer") == "true"
        endpointUri = doc.documentElement.getAttribute("adapterEndpoint")
        adapterServer = AdapterServer(endpointUri, isTrumpfServer)
        await adapterServer.initialize()    
        asyncio.create_task(adapterServer.run())

        # Add machines and start adapter 
        machines = doc.getElementsByTagName("machine")
        uri = doc.documentElement.getAttribute("machinesServer")
        machinesAdapter = MachinesAdapterClient(uri, adapterServer, isTrumpfServer)        
        logger.trace("Add Machines.")
        for m in machines:  
            await machinesAdapter.add_machine(m.getAttribute("machineName"), m.getAttribute("ns"))        
        asyncio.create_task(machinesAdapter.run())

        # wait for everything is set up
        await asyncio.sleep(10) 

        # here code stops until user types exit
        await interactive(machinesAdapter)

        # exit        
        await machinesAdapter.stop()
        await adapterServer.stop()

    except Exception:
        logger.exception("Exception")


if __name__ == "__main__":
    # execute if run as a script
    asyncio.run(main())
