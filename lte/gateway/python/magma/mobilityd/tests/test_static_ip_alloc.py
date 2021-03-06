"""
Copyright 2020 The Magma Authors.

This source code is licensed under the BSD-style license found in the
LICENSE file in the root directory of this source tree.

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import ipaddress
import unittest
from typing import Optional

from lte.protos.mconfig.mconfigs_pb2 import MobilityD
from magma.mobilityd.ip_descriptor import IPDesc, IPType
from magma.mobilityd.ip_address_man import IPAddressManager, \
    IPNotInUseError, MappingNotFoundError
from magma.mobilityd.tests.test_multi_apn_ip_alloc import MockedSubscriberDBStub
from magma.mobilityd.uplink_gw import InvalidVlanId


class StaticIPAllocationTests(unittest.TestCase):
    """
    Test class for the Mobilityd Static IP Allocator
    """
    RECYCLING_INTERVAL_SECONDS = 1

    def _new_ip_allocator(self, recycling_interval):
        """
        Creates and sets up an IPAllocator with the given recycling interval.
        """
        config = {
            'recycling_interval': recycling_interval,
            'persist_to_redis': False,
            'redis_port': 6379,
        }
        mconfig = MobilityD(ip_allocator_type=MobilityD.IP_POOL,
                            static_ip_enabled=True)

        self._allocator = IPAddressManager(recycling_interval=recycling_interval,
                                           subscriberdb_rpc_stub=MockedSubscriberDBStub(),
                                           config=config,
                                           mconfig=mconfig)
        self._allocator.add_ip_block(self._block)

    def setUp(self):
        self._block = ipaddress.ip_network('192.168.0.0/28')
        self._new_ip_allocator(self.RECYCLING_INTERVAL_SECONDS)

    def tearDown(self):
        MockedSubscriberDBStub.clear_subs()

    def check_type(self, sid: str, type: IPType):
        ip_desc = self._allocator.sid_ips_map[sid]
        self.assertEqual(ip_desc.type, type)

    def check_gw_info(self, vlan: Optional[int], gw_ip: str, gw_mac: Optional[str]):
        gw_info_ip = self._allocator._dhcp_gw_info.get_gw_ip(vlan)
        self.assertEqual(gw_info_ip, gw_ip)
        gw_info_mac = self._allocator._dhcp_gw_info.get_gw_mac(vlan)
        self.assertEqual(gw_info_mac, gw_mac)

    def test_get_ip_for_subscriber(self):
        """ test get_ip_for_sid without any assignment """
        sid = 'IMSI11'
        ip0, _ = self._allocator.alloc_ip_address(sid)

        ip0_returned = self._allocator.get_ip_for_sid(sid)

        # check if retrieved ip is the same as the one allocated
        self.assertEqual(ip0, ip0_returned)
        self.check_type(sid, IPType.IP_POOL)

    def test_get_ip_for_subscriber_with_apn(self):
        """ test get_ip_for_sid with static IP """
        apn = 'magma'
        imsi = 'IMSI110'
        sid = imsi + '.' + apn
        assigned_ip = '1.2.3.4'
        MockedSubscriberDBStub.add_sub(sid=imsi, apn=apn, ip=assigned_ip)

        ip0, _ = self._allocator.alloc_ip_address(sid)
        ip0_returned = self._allocator.get_ip_for_sid(sid)

        # check if retrieved ip is the same as the one allocated
        self.assertEqual(ip0, ip0_returned)
        self.assertEqual(ip0, ipaddress.ip_address(assigned_ip))
        self.check_type(sid, IPType.STATIC)

    def test_get_ip_for_subscriber_with_different_apn(self):
        """ test get_ip_for_sid with different APN assigned ip"""
        apn = 'magma'
        imsi = 'IMSI110'
        sid = imsi + '.' + apn
        assigned_ip = '1.2.3.4'
        MockedSubscriberDBStub.add_sub(sid=imsi, apn="xyz", ip=assigned_ip)

        ip0, _ = self._allocator.alloc_ip_address(sid)
        ip0_returned = self._allocator.get_ip_for_sid(sid)

        # check if retrieved ip is the same as the one allocated
        self.assertEqual(ip0, ip0_returned)
        self.assertNotEqual(ip0, ipaddress.ip_address(assigned_ip))
        self.check_type(sid, IPType.IP_POOL)

    def test_get_ip_for_subscriber_with_wildcard_apn(self):
        """ test wildcard apn"""
        apn = 'magma'
        imsi = 'IMSI110'
        sid = imsi + '.' + apn
        assigned_ip = '1.2.3.4'
        MockedSubscriberDBStub.add_sub(sid=imsi, apn="*", ip=assigned_ip)

        ip0, _ = self._allocator.alloc_ip_address(sid)
        ip0_returned = self._allocator.get_ip_for_sid(sid)

        # check if retrieved ip is the same as the one allocated
        self.assertEqual(ip0, ip0_returned)
        self.assertEqual(ip0, ipaddress.ip_address(assigned_ip))
        self.check_type(sid, IPType.STATIC)

    def test_get_ip_for_subscriber_with_wildcard_and_exact_apn(self):
        """ test IP assignement from multiple  APNs"""
        apn = 'magma'
        imsi = 'IMSI110'
        sid = imsi + '.' + apn
        assigned_ip = '1.2.3.4'
        assigned_ip_wild = '22.22.22.22'
        MockedSubscriberDBStub.add_sub(sid=imsi, apn="*", ip=assigned_ip_wild)
        MockedSubscriberDBStub.add_sub_ip(sid=imsi, apn=apn, ip=assigned_ip)

        ip0, _ = self._allocator.alloc_ip_address(sid)
        ip0_returned = self._allocator.get_ip_for_sid(sid)

        # check if retrieved ip is the same as the one allocated
        self.assertEqual(ip0, ip0_returned)
        self.assertEqual(ip0, ipaddress.ip_address(assigned_ip))
        self.check_type(sid, IPType.STATIC)

    def test_get_ip_for_subscriber_with_invalid_ip(self):
        """ test invalid data from DB """
        apn = 'magma'
        imsi = 'IMSI110'
        sid = imsi + '.' + apn
        assigned_ip = '1.2.3.hh'
        MockedSubscriberDBStub.add_sub(sid=imsi, apn=apn, ip=assigned_ip)

        ip0, _ = self._allocator.alloc_ip_address(sid)
        ip0_returned = self._allocator.get_ip_for_sid(sid)

        # check if retrieved ip is the same as the one allocated
        self.assertEqual(ip0, ip0_returned)
        self.assertNotEqual(str(ip0), assigned_ip)
        self.check_type(sid, IPType.IP_POOL)

    def test_get_ip_for_subscriber_with_multi_apn_but_no_match(self):
        """ test IP assignment from multiple  APNs"""
        apn = 'magma'
        imsi = 'IMSI110'
        sid = imsi + '.' + apn
        assigned_ip = '1.2.3.4'
        assigned_ip_wild = '22.22.22.22'
        MockedSubscriberDBStub.add_sub(sid=imsi, apn="abc", ip=assigned_ip_wild)
        MockedSubscriberDBStub.add_sub_ip(sid=imsi, apn="xyz", ip=assigned_ip)

        ip0, _ = self._allocator.alloc_ip_address(sid)
        ip0_returned = self._allocator.get_ip_for_sid(sid)

        # check if retrieved ip is the same as the one allocated
        self.assertEqual(ip0, ip0_returned)
        self.assertNotEqual(ip0, ipaddress.ip_address(assigned_ip))
        self.check_type(sid, IPType.IP_POOL)

    def test_get_ip_for_subscriber_with_incomplete_sub(self):
        """ test IP assignment from subscriber without non_3gpp config"""
        apn = 'magma'
        imsi = 'IMSI110'
        sid = imsi + '.' + apn
        MockedSubscriberDBStub.add_incomplete_sub(sid=imsi)

        ip0, _ = self._allocator.alloc_ip_address(sid)
        ip0_returned = self._allocator.get_ip_for_sid(sid)

        # check if retrieved ip is the same as the one allocated
        self.assertEqual(ip0, ip0_returned)
        self.check_type(sid, IPType.IP_POOL)

    def test_get_ip_for_subscriber_with_wildcard_no_apn(self):
        """ test wildcard apn"""
        imsi = 'IMSI110'
        sid = imsi
        assigned_ip = '1.2.3.4'
        MockedSubscriberDBStub.add_sub(sid=imsi, apn="*", ip=assigned_ip)

        ip0, _ = self._allocator.alloc_ip_address(sid)
        ip0_returned = self._allocator.get_ip_for_sid(sid)

        # check if retrieved ip is the same as the one allocated
        self.assertEqual(ip0, ip0_returned)
        self.assertEqual(ip0, ipaddress.ip_address(assigned_ip))
        self.check_type(sid, IPType.STATIC)

    def test_get_ip_for_subscriber_with_apn_dot(self):
        """ test get_ip_for_sid with static IP """
        apn = 'magma.ipv4'
        imsi = 'IMSI110'
        sid = imsi + '.' + apn
        assigned_ip = '1.2.3.4'
        MockedSubscriberDBStub.add_sub(sid=imsi, apn=apn, ip=assigned_ip)

        ip0, _ = self._allocator.alloc_ip_address(sid)
        ip0_returned = self._allocator.get_ip_for_sid(sid)

        # check if retrieved ip is the same as the one allocated
        self.assertEqual(ip0, ip0_returned)
        self.assertEqual(ip0, ipaddress.ip_address(assigned_ip))
        self.check_type(sid, IPType.STATIC)

    def test_get_ip_for_subscriber_with_wildcard_and_no_exact_apn(self):
        """ test IP assignement from multiple  APNs"""
        apn = 'magma'
        imsi = 'IMSI110'
        sid = imsi + '.' + apn
        assigned_ip = '1.2.3.4'
        assigned_ip_wild = '22.22.22.22'
        MockedSubscriberDBStub.add_sub(sid=imsi, apn="*", ip=assigned_ip_wild)
        MockedSubscriberDBStub.add_sub_ip(sid=imsi, apn="xyz", ip=assigned_ip)

        ip0, _ = self._allocator.alloc_ip_address(sid)
        ip0_returned = self._allocator.get_ip_for_sid(sid)

        # check if retrieved ip is the same as the one allocated
        self.assertEqual(ip0, ip0_returned)
        self.assertEqual(ip0, ipaddress.ip_address(assigned_ip_wild))
        self.check_type(sid, IPType.STATIC)

    def test_get_ip_for_subscriber_with_wildcard_and_exact_apn_no_ip(self):
        """ test IP assignement from multiple  APNs"""
        apn = 'magma'
        imsi = 'IMSI110'
        sid = imsi + '.' + apn
        assigned_ip_wild = '22.22.22.22'
        MockedSubscriberDBStub.add_sub(sid=imsi, apn="*", ip=assigned_ip_wild)
        MockedSubscriberDBStub.add_sub_ip(sid=imsi, apn=apn, ip=None)

        ip0, _ = self._allocator.alloc_ip_address(sid)
        ip0_returned = self._allocator.get_ip_for_sid(sid)

        # check if retrieved ip is the same as the one allocated
        self.assertEqual(ip0, ip0_returned)
        self.assertEqual(ip0, ipaddress.ip_address(assigned_ip_wild))
        self.check_type(sid, IPType.STATIC)

    def test_get_ip_for_subscriber_with_apn_with_gw(self):
        """ test get_ip_for_sid with static IP """
        apn = 'magma'
        imsi = 'IMSI110'
        sid = imsi + '.' + apn
        assigned_ip = '1.2.3.4'
        gw_ip = "1.2.3.1"
        gw_mac = "11:22:33:11:77:28"
        MockedSubscriberDBStub.add_sub(sid=imsi, apn=apn, ip=assigned_ip,
                                       gw_ip=gw_ip, gw_mac=gw_mac)

        ip0, _ = self._allocator.alloc_ip_address(sid)
        ip0_returned = self._allocator.get_ip_for_sid(sid)

        # check if retrieved ip is the same as the one allocated
        self.assertEqual(ip0, ip0_returned)
        self.assertEqual(ip0, ipaddress.ip_address(assigned_ip))
        self.check_type(sid, IPType.STATIC)
        self.check_gw_info(None, gw_ip, gw_mac)

    def test_get_ip_for_subscriber_with_only_wildcard_apn_gw(self):
        """ test wildcard apn"""
        apn = 'magma'
        imsi = 'IMSI110'
        sid = imsi + '.' + apn
        assigned_ip = '1.2.3.4'
        gw_ip = "1.2.3.100"
        gw_mac = "11:22:33:11:77:81"
        MockedSubscriberDBStub.add_sub(sid=imsi, apn="*", ip=assigned_ip,
                                       gw_ip=gw_ip, gw_mac=gw_mac)

        ip0, _ = self._allocator.alloc_ip_address(sid)
        ip0_returned = self._allocator.get_ip_for_sid(sid)

        # check if retrieved ip is the same as the one allocated
        self.assertEqual(ip0, ip0_returned)
        self.assertEqual(ip0, ipaddress.ip_address(assigned_ip))
        self.check_type(sid, IPType.STATIC)

    def test_get_ip_for_subscriber_with_apn_with_gw_vlan(self):
        """ test get_ip_for_sid with static IP """
        apn = 'magma'
        imsi = 'IMSI110'
        sid = imsi + '.' + apn
        assigned_ip = '1.2.3.4'
        gw_ip = "1.2.3.1"
        gw_mac = "11:22:33:11:77:44"
        vlan = "200"
        MockedSubscriberDBStub.add_sub(sid=imsi, apn=apn, ip=assigned_ip,
                                       gw_ip=gw_ip, gw_mac=gw_mac, vlan=vlan)

        ip0, _ = self._allocator.alloc_ip_address(sid)
        ip0_returned = self._allocator.get_ip_for_sid(sid)

        # check if retrieved ip is the same as the one allocated
        self.assertEqual(ip0, ip0_returned)
        self.assertEqual(ip0, ipaddress.ip_address(assigned_ip))
        self.check_type(sid, IPType.STATIC)
        self.check_gw_info(vlan, gw_ip, gw_mac)

    def test_get_ip_for_subscriber_with_apn_with_gw_invalid_ip(self):
        """ test get_ip_for_sid with static IP """
        apn = 'magma'
        imsi = 'IMSI110'
        sid = imsi + '.' + apn
        assigned_ip = '1.2.3.4'
        gw_ip = "1.2.3.1333"
        gw_mac = "11:22:33:11:77:76"
        vlan = "200"
        MockedSubscriberDBStub.add_sub(sid=imsi, apn=apn, ip=assigned_ip,
                                       gw_ip=gw_ip, gw_mac=gw_mac, vlan=vlan)

        ip0, _ = self._allocator.alloc_ip_address(sid)
        ip0_returned = self._allocator.get_ip_for_sid(sid)

        # check if retrieved ip is the same as the one allocated
        self.assertEqual(ip0, ip0_returned)
        self.assertEqual(ip0, ipaddress.ip_address(assigned_ip))
        self.check_type(sid, IPType.STATIC)
        self.check_gw_info(vlan, None, None)

    def test_get_ip_for_subscriber_with_apn_with_gw_nul_ip(self):
        """ test get_ip_for_sid with static IP """
        apn = 'magma'
        imsi = 'IMSI110'
        sid = imsi + '.' + apn
        assigned_ip = '1.2.3.4'
        gw_ip = ""
        gw_mac = "11:22:33:11:77:45"
        vlan = "200"
        MockedSubscriberDBStub.add_sub(sid=imsi, apn=apn, ip=assigned_ip,
                                       gw_ip=gw_ip, gw_mac=gw_mac, vlan=vlan)

        ip0, _ = self._allocator.alloc_ip_address(sid)
        ip0_returned = self._allocator.get_ip_for_sid(sid)

        # check if retrieved ip is the same as the one allocated
        self.assertEqual(ip0, ip0_returned)
        self.assertEqual(ip0, ipaddress.ip_address(assigned_ip))
        self.check_type(sid, IPType.STATIC)
        self.check_gw_info(vlan, None, None)

    def test_get_ip_for_subscriber_with_apn_with_gw_nul_mac(self):
        """ test get_ip_for_sid with static IP """
        apn = 'magma'
        imsi = 'IMSI110'
        sid = imsi + '.' + apn
        assigned_ip = '1.2.3.24'
        gw_ip = "1.2.3.55"
        gw_mac = None
        vlan = "200"
        MockedSubscriberDBStub.add_sub(sid=imsi, apn=apn, ip=assigned_ip,
                                       gw_ip=gw_ip, gw_mac=gw_mac, vlan=vlan)

        ip0, _ = self._allocator.alloc_ip_address(sid)
        ip0_returned = self._allocator.get_ip_for_sid(sid)

        # check if retrieved ip is the same as the one allocated
        self.assertEqual(ip0, ip0_returned)
        self.assertEqual(ip0, ipaddress.ip_address(assigned_ip))
        self.check_type(sid, IPType.STATIC)
        self.check_gw_info(vlan, gw_ip, "")

    def test_get_ip_for_subscriber_with_wildcard_apn_gw(self):
        """ test wildcard apn"""
        apn = 'magma'
        imsi = 'IMSI110'
        sid = imsi + '.' + apn
        assigned_ip = '1.2.3.4'
        gw_ip = "1.2.3.100"
        gw_mac = "11:22:33:11:77:81"
        vlan = "300"

        MockedSubscriberDBStub.add_sub(sid=imsi, apn=apn, ip=assigned_ip,
                                       gw_ip=gw_ip, gw_mac=gw_mac, vlan=vlan)

        wildcard_assigned_ip = "20.20.20.20"
        wildcard_gw_ip = "1.2.7.7"
        wildcard_gw_mac = "11:22:33:88:77:99"
        wildcard_vlan = "400"

        MockedSubscriberDBStub.add_sub_ip(sid=imsi, apn="*", ip=wildcard_assigned_ip,
                                          gw_ip=wildcard_gw_ip, gw_mac=wildcard_gw_mac,
                                          vlan=wildcard_vlan)

        ip0, _ = self._allocator.alloc_ip_address(sid)
        ip0_returned = self._allocator.get_ip_for_sid(sid)

        # check if retrieved ip is the same as the one allocated
        self.assertEqual(ip0, ip0_returned)
        self.assertEqual(ip0, ipaddress.ip_address(assigned_ip))
        self.check_type(sid, IPType.STATIC)
        self.check_gw_info(vlan, gw_ip, gw_mac)
        self.check_gw_info(wildcard_vlan, None, None)

    def test_get_ip_for_subscriber_with_apn_with_gw_invalid_vlan(self):
        """ test get_ip_for_sid with static IP """
        apn = 'magma'
        imsi = 'IMSI110'
        sid = imsi + '.' + apn
        assigned_ip = '1.2.3.4'
        gw_ip = "1.2.3.1"
        gw_mac = "11:22:33:11:77:44"
        vlan = "20000"
        MockedSubscriberDBStub.add_sub(sid=imsi, apn=apn, ip=assigned_ip,
                                       gw_ip=gw_ip, gw_mac=gw_mac, vlan=vlan)

        with self.assertRaises(InvalidVlanId):
            ip0, _ = self._allocator.alloc_ip_address(sid)
