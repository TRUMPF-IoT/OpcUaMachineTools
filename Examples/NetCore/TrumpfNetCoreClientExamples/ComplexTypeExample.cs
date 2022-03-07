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

using Newtonsoft.Json;
using Opc.Ua;
using Opc.Ua.Client;
using Opc.Ua.Client.ComplexTypes;
using System;
using System.IO;
using System.Threading;

namespace TrumpfNetCoreClientExamples
{
    class ComplexTypeExample
    {
        public void Start(BaseClient client)
        {
            Session session = client.ClientSession;
            ushort customNamespaceIndex = (ushort)session.NamespaceUris.GetIndex("http://trumpf.com/TRUMPF-Interfaces/");

            // Load necessary complex types as types. Here struct TsSheetTechnology i=3002
            var complexTypeSystem = new ComplexTypeSystem(session);
            ExpandedNodeId sheetTechType = new ExpandedNodeId(3002, customNamespaceIndex);
            Type systemType1 = complexTypeSystem.LoadType(sheetTechType).Result;
            // Alternative auto load all types, but takes some seconds
            // complexTypeSystem.Load()

            NodeId sheetTechListId = new NodeId("147", customNamespaceIndex); // 147 SheetTechnologyList

            for (int i = 0; i < 20; i++)
            {
                // If session.ReadValue is used then exception needs to be handled for certain statuscode
                // Better allways use session.Read(...) with UaNetStandard SDK
                DataValue dv = ReadSingleValue(session, sheetTechListId);
                if (dv.StatusCode == 0)
                {
                    // Data as a json
                    var jsonEncoder = new JsonEncoder(session.MessageContext, false);
                    jsonEncoder.WriteDataValue("TsSheetTech", dv);
                    var textbuffer = jsonEncoder.CloseAndReturnText();
                    string intendedJson = JsonIntend(textbuffer);
                    Console.WriteLine(intendedJson);

                    // Data as a struct
                    var sheetTechListValue = (ExtensionObject[])dv.Value;
                    BaseComplexType sheetTech = (BaseComplexType)sheetTechListValue[0].Body;
                    TsSheetTech st = new TsSheetTech(sheetTech); // Fill struct or class
                }
                else
                {
                    Console.WriteLine($"Error on reading value. StatusCode={dv.StatusCode}");
                }
                Thread.Sleep(3000);
            }
        }

        public static DataValue ReadSingleValue(Session session, NodeId readId)
        {
            ReadValueIdCollection nodesToRead = new ReadValueIdCollection();
            ReadValueId nodeToRead = new ReadValueId();
            nodeToRead.NodeId = readId;
            nodeToRead.AttributeId = Attributes.Value;
            nodesToRead.Add(nodeToRead);

            // read all values.
            DataValueCollection results = null;
            DiagnosticInfoCollection diagnosticInfos = null;

            session.Read(
                        null,
                        0,
                        TimestampsToReturn.Both,
                        nodesToRead,
                        out results,
                        out diagnosticInfos);

            ClientBase.ValidateResponse(results, nodesToRead);
            ClientBase.ValidateDiagnosticInfos(diagnosticInfos, nodesToRead);

            return results[0];
        }

        public static string JsonIntend(string json)
        {
            using (var stringReader = new StringReader(json))
            using (var stringWriter = new StringWriter())
            {
                var jsonReader = new JsonTextReader(stringReader);
                var jsonWriter = new JsonTextWriter(stringWriter) { Formatting = Formatting.Indented };
                jsonWriter.WriteToken(jsonReader);
                return stringWriter.ToString();
            }
        }
    }
}
