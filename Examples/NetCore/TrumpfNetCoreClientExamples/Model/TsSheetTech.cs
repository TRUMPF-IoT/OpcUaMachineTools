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

using Opc.Ua.Client.ComplexTypes;

namespace TrumpfNetCoreClientExamples
{
    public struct TsSheetTech
    {
        public string DatasetName; 
        public double SheetDimensionX;
        public double SheetDimensionY;
        public double Thickness;
        public int Type;
        public int ScratchFree;
        public int MagazinePositionClamp1;
        public int MagazinePositionClamp2;
        public int MagazinePositionClamp3;
        public int MagazinePositionClamp4;
        public int MagazinePositionClamp5;
        public int MagazinePositionClamp6;
        public double XLength;
        public double YLength;
        public string Grade;
        public double Density;
        public int DynamicLevel;
        public string MaterialGroup;
        public int ScratchFreeDieOn;
        public int AdvancedEvaporateSwitch;

        public TsSheetTech(BaseComplexType sheetTech)
        {
            DatasetName = (string)sheetTech["DatasetName"];
            SheetDimensionX = (double)sheetTech["SheetDimensionX"];
            SheetDimensionY = (double)sheetTech["SheetDimensionY"];
            Thickness = (double)sheetTech["Thickness"];
            Type = (int)sheetTech["Type"];
            ScratchFree = (int)sheetTech["ScratchFree"];
            MagazinePositionClamp1 = (int)sheetTech["MagazinePositionClamp1"];
            MagazinePositionClamp2 = (int)sheetTech["MagazinePositionClamp2"];
            MagazinePositionClamp3 = (int)sheetTech["MagazinePositionClamp3"];
            MagazinePositionClamp4 = (int)sheetTech["MagazinePositionClamp4"];
            MagazinePositionClamp5 = (int)sheetTech["MagazinePositionClamp5"];
            MagazinePositionClamp6 = (int)sheetTech["MagazinePositionClamp6"];
            XLength = (double)sheetTech["XLength"];
            YLength = (double)sheetTech["YLength"];
            Grade = (string)sheetTech["Grade"];
            Density = (double)sheetTech["Density"];
            DynamicLevel = (int)sheetTech["DynamicLevel"];
            MaterialGroup = (string)sheetTech["MaterialGroup"];
            ScratchFreeDieOn = (int)sheetTech["ScratchFreeDieOn"];
            AdvancedEvaporateSwitch = (int)sheetTech["AdvancedEvaporateSwitch"];
        }
    }
}
