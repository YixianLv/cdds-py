import pytest
import time
import threading

from cyclonedds.core import Listener, Qos, Policy
from cyclonedds.util import duration



# Adapted from OSPL tests
def test_on_data_available(manual_setup, hitpoint):
    class L(Listener):
        def on_data_available(self, _):
            hitpoint.hit()

    dr = manual_setup.dr(listener=L())
    manual_setup.dw().write(manual_setup.msg)

    assert hitpoint.was_hit()

"""
def test_on_inconsistent_topic(self):
'''
from: osplo/testsuite/dbt/api/dcps/c99/utest/listener/code/listener_utests.c

It's not that easy for OpenSplice to generate inconsistent_topic
events. However, it is build on top of SAC and it works on that
language binding. We can assume that this test succeeds when
the other listener test pass as well...

So, we will just check that the listener's actually got installed
'''
    topic_name = 'ST_on_inconsistent_topic'
    event = threading.Event()

    gci = ddsutil.get_dds_classes_from_idl(self.idl_path, self.shape_type_name)
#         gci2 = ddsutil.get_dds_classes_from_idl(self.idl_path, self.shape_type_name + '2')

    class L(Listener):
        def on_inconsistent_topic(self, topic, status):
            print('on_inconsistent_topic triggered: topic name = {}, total_count = {}, total_change_count = {}'
                .format(topic.get_name(), status.total_coutn, status.total_change_count))
            event.set()

    dp1 = DomainParticipant(listener=L())

    self.assertIsNotNone(dp1.listener, "DomainParticipant Listener was not set")

    t1 = gci.register_topic(dp1, topic_name, listener=L())

    self.assertIsNotNone(t1.listener, "Topic Listener was not set")

#         t2qos = Qos([DurabilityQosPolicy(DDSDurabilityKind.PERSISTENT)])
#         try:
#             t2 = gci2.register_topic(dp2, topic_name, qos=None)
#             self.fail("expected this topic registeration to fail")
#         except DDSException as e:
#             pass
#         
#         try:
#             self.assertTrue(self.event.wait(self.time_out),'Did not receive on_inconsistent_topic')
#         finally:
#             pass
"""


def test_data_available_listeners(manual_setup, hitpoint_factory):
    hpf = hitpoint_factory

    class MyListener(Listener):
        def __init__(self):
            super().__init__()
            self.hitpoint_data_available = hpf()
            self.hitpoint_pub_matched = hpf()
            self.hitpoint_sub_matched = hpf()

        def on_data_available(self, reader):
            self.hitpoint_data_available.hit()

        def on_publication_matched(self, writer,status):
            self.hitpoint_pub_matched.hit()

        def on_subscription_matched(self, reader, status):
            self.hitpoint_sub_matched.hit()

    domain_participant_listener = MyListener()
    manual_setup.dp.listener = domain_participant_listener

    publisher_listener = MyListener()
    publisher = manual_setup.pub(listener=publisher_listener)

    subscriber_listener = MyListener()
    subscriber = manual_setup.sub(listener=subscriber_listener)

    datawriter_listener = MyListener()
    datawriter = manual_setup.dw(listener=datawriter_listener)

    datareader_listener = MyListener()
    datareader = manual_setup.dr(listener=datareader_listener)

    datawriter.write(manual_setup.msg)

    #  Assertions, _only_ datawriter should publication match,
    # _only_ datareader should subscriber match and receive data

    assert datawriter_listener.hitpoint_pub_matched.was_hit()
    assert datareader_listener.hitpoint_sub_matched.was_hit()
    assert datareader_listener.hitpoint_data_available.was_hit()

    assert domain_participant_listener.hitpoint_pub_matched.was_not_hit()
    assert domain_participant_listener.hitpoint_sub_matched.was_not_hit()
    assert domain_participant_listener.hitpoint_data_available.was_not_hit()

    assert publisher_listener.hitpoint_pub_matched.was_not_hit()
    assert publisher_listener.hitpoint_sub_matched.was_not_hit()
    assert publisher_listener.hitpoint_data_available.was_not_hit()

    assert subscriber_listener.hitpoint_pub_matched.was_not_hit()
    assert subscriber_listener.hitpoint_sub_matched.was_not_hit()
    assert subscriber_listener.hitpoint_data_available.was_not_hit()

    assert datawriter_listener.hitpoint_sub_matched.was_not_hit()
    assert datawriter_listener.hitpoint_data_available.was_not_hit()

    assert datareader_listener.hitpoint_pub_matched.was_not_hit()


def test_on_offered_deadline_missed(manual_setup, hitpoint):
    class MyListener(Listener):
        def on_offered_deadline_missed(self, writer, status):
            hitpoint.hit(data=time.time())

    wqos = Qos(Policy.Deadline(duration(milliseconds=200)))
    dw = manual_setup.dw(qos=wqos, listener=MyListener())
    dr = manual_setup.dr()

    write_time = time.time()
    dw.write(manual_setup.msg)

    assert hitpoint.was_hit()
    delay = hitpoint.data - write_time
    assert delay >= 0.2  # seconds


def test_on_offered_incompatible_qos(manual_setup, hitpoint):
    class MyListener(Listener):
        def on_offered_incompatible_qos(self, writer, status):
            hitpoint.hit()

    wqos = Qos(Policy.Durability.Volatile)
    rqos = Qos(Policy.Durability.Transient)

    wr = manual_setup.dw(qos=wqos, listener=MyListener())
    rd = manual_setup.dr(qos=rqos)

    wr.write(manual_setup.msg)

    assert hitpoint.was_hit()


def test_liveliness(manual_setup, hitpoint_factory):
    handler = hitpoint_factory()
    alive = hitpoint_factory()
    notalive = hitpoint_factory()

    class MyListenerWriter(Listener):
        def on_liveliness_lost(self, writer, status):
            handler.hit(data=time.time())

    class MyListenerReader(Listener):
        def on_liveliness_changed(self, reader, status):
            if status.alive_count == 1:
                alive.hit(data=status.alive_count_change)
            else:
                notalive.hit(data=status.alive_count_change)

    qos = Qos(
        Policy.Liveliness.ManualByTopic(duration(seconds=0.2)),
        Policy.Ownership.Exclusive
    )

    manual_setup.tp(qos=qos)
    manual_setup.dr(listener=MyListenerReader())
    datawriter = manual_setup.dw(listener=MyListenerWriter())

    write_time = time.time()
    datawriter.write(manual_setup.msg)

    assert handler.was_hit()
    assert handler.data - write_time >= 0.2
    assert alive.was_hit() and alive.data == 1
    assert notalive.was_hit() and notalive.data == -1


def test_on_requested_deadline_missed(manual_setup, hitpoint):
    class MyListener(Listener):
        def on_requested_deadline_missed(self, reader, status):
            hitpoint.hit(data=time.time())

    qos = Qos(Policy.Deadline(duration(seconds=0.2)))
    wr = manual_setup.dw(qos=qos)
    manual_setup.dr(qos=qos, listener=MyListener())
    
    write_time = time.time()
    wr.write(manual_setup.msg)

    assert hitpoint.was_hit()
    assert hitpoint.data - write_time >= 0.2


"""
def test_on_requested_incompatible_qos(self):
    handlerTriggered = threading.Event()
    saved_status = None
    class L(Listener):
        def on_requested_incompatible_qos(self, reader, status):
            nonlocal saved_status
            saved_status = status
            handlerTriggered.set()

    dp = DomainParticipant()

    topic_name = 'ST_test_on_requested_incompatible_qos'

    gci = ddsutil.get_dds_classes_from_idl(self.idl_path, self.shape_type_name)

    t = gci.register_topic(dp, topic_name)

    wqos = Qos(policies=[
            DurabilityQosPolicy(DDSDurabilityKind.VOLATILE)
        ])
    rqos = Qos(policies=[
            DurabilityQosPolicy(DDSDurabilityKind.TRANSIENT)
        ])
    wr = dp.create_datawriter(t, wqos)
    rd = dp.create_datareader(t,rqos, L())

    ShapeType = gci.get_class('ShapeType')
    Inner = gci.get_class('Inner_Shapes')

    data = ShapeType(color='GREEN', x=22, y=33, z=44, t=Inner(foo=55))

    wr.write(data)
    self.assertTrue(handlerTriggered.wait(self.time_out), 'Event not triggered')
    self._check_status(saved_status, RequestedIncompatibleQosStatus, [
        Info('total_count', int), 
        Info('total_count_change', int), 
        Info('last_policy_id', QosPolicyId), 
        ])

def test_on_sample_rejected(self):
    handlerTriggered = threading.Event()
    saved_status = None
    class L(Listener):
        def on_sample_rejected(self, reader, status):
            nonlocal saved_status
            saved_status = status
            handlerTriggered.set()

    dp = DomainParticipant()

    topic_name = 'ST_on_sample_rejected'

    gci = ddsutil.get_dds_classes_from_idl(self.idl_path, self.shape_type_name)

    t = gci.register_topic(dp, topic_name)

    qos = Qos(policies=[
            ResourceLimitsQosPolicy(max_samples=1)
        ])

    wr = dp.create_datawriter(t)
    rd = dp.create_datareader(t, qos, L())

    ShapeType = gci.get_class('ShapeType')
    Inner = gci.get_class('Inner_Shapes')

    data1 = ShapeType(color='GREEN', x=22, y=33, z=44, t=Inner(foo=55))
    data2 = ShapeType(color='BLUE', x=222, y=233, z=244, t=Inner(foo=255))

    wr.write(data1)
    self.assertFalse(handlerTriggered.is_set(), 'Event already triggered')
    wr.write(data2)
    self.assertTrue(handlerTriggered.wait(self.time_out), 'Event not triggered')
    self._check_status(saved_status, SampleRejectedStatus, [
        Info('total_count', int), 
        Info('total_count_change', int), 
        Info('last_reason', DDSSampleRejectedStatusKind), 
        Info('last_instance_handle', int), 
        ])

def test_on_sample_lost(self):
    handlerTriggered = threading.Event()
    saved_status = None

    class L(Listener):
        def on_sample_lost(self, reader, status):
            nonlocal saved_status
            saved_status = status
            handlerTriggered.set()

    qos = Qos(policies=[
        DestinationOrderQosPolicy(DDSDestinationOrderKind.BY_SOURCE_TIMESTAMP)
        ])

    dp = DomainParticipant()

    topic_name = 'ST_on_sample_lost'

    gci = ddsutil.get_dds_classes_from_idl(self.idl_path, self.shape_type_name)

    t = gci.register_topic(dp, topic_name)

    wr = dp.create_datawriter(t, qos)
    rd = dp.create_datareader(t, qos, L())

    ShapeType = gci.get_class('ShapeType')
    Inner = gci.get_class('Inner_Shapes')

    data1 = ShapeType(color='GREEN', x=22, y=33, z=44, t=Inner(foo=55))

    t1 = DDSTime(1000,0)
    t2 = DDSTime(1001,0)
    # write out-of-order samples
    wr.write_ts(data1, t2)
    rd.take()
    wr.write_ts(data1, t1)
    self.assertTrue(handlerTriggered.wait(self.time_out), 'Event not triggered')
    self._check_status(saved_status, SampleLostStatus, [
        Info('total_count', int), 
        Info('total_count_change', int), 
        ])
"""