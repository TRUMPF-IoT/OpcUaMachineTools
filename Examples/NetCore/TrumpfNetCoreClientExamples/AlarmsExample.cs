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

using Opc.Ua;
using Opc.Ua.Client;
using System;
using System.Collections.Generic;

namespace TrumpfNetCoreClientExamples
{
    class AlarmsExample
    {
        NodeId mTcMachineAlarmTypeId;
        // Dictionary of all currently pending/existing alarms
        Dictionary<NodeId, TcMachineAlarm> mPendingAlarms = new Dictionary<NodeId, TcMachineAlarm>();

        public void Start(BaseClient client)
        {
            Session session = client.ClientSession;
            ushort customNamespaceIndex = (ushort)session.NamespaceUris.GetIndex("http://trumpf.com/TRUMPF-Interfaces/");
            mTcMachineAlarmTypeId = new NodeId(1006, customNamespaceIndex);           

            // declate callback.
            var monitoredItem_Notification = new MonitoredItemNotificationEventHandler(MonitoredItem_Notification);

            // create a subscription for alarm events
            Subscription sub = new Subscription(session.DefaultSubscription) { PublishingInterval = 1000, MaxNotificationsPerPublish = 1000 };

            // Define the events which shall be monitored
            var monItem = new MonitoredItem(sub.DefaultItem)
            {
                StartNodeId = new NodeId("179", customNamespaceIndex),   // messages node
                NodeClass = NodeClass.Object,
                AttributeId = Attributes.EventNotifier, // for events
                SamplingInterval = 0,                   // 0 for events
                QueueSize = UInt32.MaxValue,
                Filter = CreateEventFilter(customNamespaceIndex)
            };

            // set up callback for notifications.
            monItem.Notification += monitoredItem_Notification;
            sub.AddItem(monItem);

            session.AddSubscription(sub);
            sub.Create();

            // Currently no effect on trumpf python demo server
            // Usually necessary to get the refresh of events for the currently pending alarms
            RefreshMessages(sub);
        }

        private void RefreshMessages(Subscription sub)
        {
            sub.Session.Call(ObjectTypeIds.ConditionType, MethodIds.ConditionType_ConditionRefresh, new Variant(sub.Id));
        }


        private EventFilter CreateEventFilter(ushort myCustomNamespaceIndex)
        {
            // For very generic filter creations, not easy to understand:
            // https://github.com/OPCFoundation/UA-.NETStandard-Samples/blob/master/Workshop/AlarmCondition/Client/FilterDefinition.cs
            // https://github.com/OPCFoundation/UA-.NETStandard-Samples/blob/master/Samples/ClientControls.Net4/Common/FilterDeclaration.cs

            var eventFilter = new EventFilter();

            // Select Clause -> Deliver those Attributes in the event
            eventFilter.AddSelectClause(ObjectTypeIds.BaseEventType, "EventType", Attributes.Value);
            eventFilter.AddSelectClause(ObjectTypeIds.BaseEventType, "Message", Attributes.Value);
            eventFilter.AddSelectClause(ObjectTypeIds.BaseEventType, "SourceName", Attributes.Value);
            eventFilter.AddSelectClause(ObjectTypeIds.BaseEventType, "Severity", Attributes.Value);
            eventFilter.AddSelectClause(ObjectTypeIds.BaseEventType, "Time", Attributes.Value);
            eventFilter.AddSelectClause(ObjectTypeIds.ConditionType, "Retain", Attributes.Value);
            eventFilter.AddSelectClause(ObjectTypeIds.AlarmConditionType, "0:ActiveState/Id", Attributes.Value);
            eventFilter.AddSelectClause(ObjectTypeIds.ConditionType, string.Empty, Attributes.NodeId); // ConditionId
            eventFilter.AddSelectClause(mTcMachineAlarmTypeId, $"{myCustomNamespaceIndex}:AlarmIdentifier", Attributes.Value);

            // Where Clause -> Only deliver events of the specified type
            ContentFilter whereClause = new ContentFilter();
            LiteralOperand operandType = new LiteralOperand();
            operandType.Value = new Variant(mTcMachineAlarmTypeId);
            ContentFilterElement elementFirstType = whereClause.Push(FilterOperator.OfType, operandType);

            return eventFilter;
        }        

        private void MonitoredItem_Notification(MonitoredItem monitoredItem, MonitoredItemNotificationEventArgs e)
        {
            EventFieldList notification = e.NotificationValue as EventFieldList;
            if (notification != null)
            {
                var eType = monitoredItem.GetEventType(notification);
                if (eType.NodeId == mTcMachineAlarmTypeId)
                {
                    NodeId conditionId = (NodeId)notification.EventFields[7].Value;
                    // Alternative: 
                    // bool retain = (bool)monitoredItem.GetFieldValue(notification, ObjectTypeIds.ConditionType, "Retain");
                    bool retain = (bool)notification.EventFields[5].Value;
                    // New Alarm
                    if (retain && !mPendingAlarms.ContainsKey(conditionId))
                    {
                        object m = notification.EventFields[1].Value;
                        // Older Trumpf server delivers type string   
                        string message = m is string ? (string)m : ((LocalizedText)m).Text;
                        var alarm = new TcMachineAlarm
                        {                            
                            EventType = (NodeId)notification.EventFields[0].Value,
                            Message = message, 
                            SourceName = (string)notification.EventFields[2].Value,
                            Severity = (ushort)notification.EventFields[3].Value,
                            Time = (DateTime)notification.EventFields[4].Value,
                            Retain = retain,
                            ActiveStateId = (bool)notification.EventFields[6].Value,
                            AlarmIdentifier = (string)notification.EventFields[8].Value
                        };
                        mPendingAlarms[conditionId] = alarm;
                    }
                    // Alarm does not exist any more
                    if (!retain && mPendingAlarms.ContainsKey(conditionId))
                    {
                        mPendingAlarms.Remove(conditionId);
                    }

                    if (mPendingAlarms.Count > 0)
                    {
                        Console.WriteLine("==================================================================================");
                        foreach (var kvp in mPendingAlarms)
                        {
                            Console.WriteLine(kvp.Value.ToString());
                        }
                        Console.WriteLine("==================================================================================");
                    }
                }
            }
        }
        private class TcMachineAlarm
        {
            public NodeId EventType { get; set; }
            public string Message { get; set; }
            public string SourceName { get; set; }
            public ushort Severity { get; set; }
            public DateTime Time { get; set; }
            public bool Retain { get; set; }
            public bool ActiveStateId { get; set; }
            public string AlarmIdentifier { get; set; }
            public override string ToString()
            {
                return $"{Time} {AlarmIdentifier} {Message} {SourceName} {Severity}";
            }
        }
    }
}
