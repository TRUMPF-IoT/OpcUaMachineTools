// MIT License

// Copyright (c) 2022 TRUMPF Werkzeugmaschinen GmbH + Co. KG

// Permission is hereby granted, free of charge, to any person obtaining a copy
// of this software and associated documentation files (the "Software"), to deal
// in the Software without restriction, including without limitation the rights
// to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
// copies of the Software, and to permit persons to whom the Software is
// furnished to do so, subject to the following conditions:

// The above copyright notice and this permission notice shall be included in all
// copies or substantial portions of the Software.

// THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
// IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
// FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
// AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
// LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
// OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
// SOFTWARE.

namespace TrumpfNetCoreClientExamples
{
    class Program
    {
        static void Main(string[] args)
        {
            string endpointURL = "opc.tcp://localhost:50000";
            BaseClient client = new BaseClient(endpointURL);
            client.InitConnection().Wait();

            // -------------------------------------------
            // Uncomment the example you want to run
            // -------------------------------------------

            // Example how to consume machine alarms/messages
            AlarmsExample alarmsExample = new AlarmsExample();
            alarmsExample.Start(client);

            // Example how to read a complex type
            //ComplexTypeExample complexExample = new ComplexTypeExample();
            //complexExample.Start(client);

            client.WaitForExit();
        }
    }
}
