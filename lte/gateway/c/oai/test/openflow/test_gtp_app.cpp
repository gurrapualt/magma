/*
 * Licensed to the OpenAirInterface (OAI) Software Alliance under one or more
 * contributor license agreements.  See the NOTICE file distributed with
 * this work for additional information regarding copyright ownership.
 * The OpenAirInterface Software Alliance licenses this file to You under
 * the terms found in the LICENSE file in the root of this source tree.
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 *-------------------------------------------------------------------------------
 * For more information about the OpenAirInterface (OAI) Software Alliance:
 *      contact@openairinterface.org
 */
#include <string.h>
#include <gtest/gtest.h>
#include <fluid/of10msg.hh>
#include <fluid/of13msg.hh>
#include "GTPApplication.h"
#include "openflow_mocks.h"

using ::testing::_;
using ::testing::AllOf;
using ::testing::Test;
using namespace fluid_msg;
using namespace openflow;

namespace {

/**
 * Test fixture that instantiates an openflow controller for testing.
 */
class GTPApplicationTest : public ::testing::Test {
 protected:
  static constexpr const char* TEST_GTP_MAC            = "1.2.3.4.5.6";
  static const uint32_t TEST_GTP_PORT                  = 123;
  static const uint32_t TEST_MTR_PORT                  = 1155;
  static const uint32_t TEST_INTERNAL_SAMPLING_POR     = 1156;
  static const uint32_t TEST_INTERNAL_SAMPLING_FWD_TBL = 201;
  static const uint32_t TEST_UPLINK_PORT               = of13::OFPP_LOCAL;

 protected:
  virtual void SetUp() {
    gtp_app = new GTPApplication(
        TEST_GTP_MAC, TEST_GTP_PORT, TEST_MTR_PORT, TEST_INTERNAL_SAMPLING_POR,
        TEST_INTERNAL_SAMPLING_FWD_TBL, TEST_UPLINK_PORT);
    messenger = std::shared_ptr<MockMessenger>(new MockMessenger());

    controller = std::unique_ptr<OpenflowController>(
        new OpenflowController("127.0.0.1", 6666, 2, false, messenger));
    controller->register_for_event(gtp_app, openflow::EVENT_ADD_GTP_TUNNEL);
    controller->register_for_event(gtp_app, openflow::EVENT_DELETE_GTP_TUNNEL);
  }

  virtual void TearDown() {
    controller = NULL;
    messenger  = NULL;
    delete gtp_app;
  }

 protected:
  std::unique_ptr<OpenflowController> controller;
  std::shared_ptr<MockMessenger> messenger;
  GTPApplication* gtp_app;
};

// Matchers for flow modifications

MATCHER_P(CheckTableId, table_id, "") {
  auto msg = static_cast<of13::FlowMod*>(&arg);
  return msg->table_id() == table_id;
}

MATCHER_P(CheckInPort, port_num, "") {
  auto msg = static_cast<of13::FlowMod*>(&arg);
  auto in_port =
      static_cast<of13::InPort*>(msg->get_oxm_field(of13::OFPXMT_OFB_IN_PORT));
  return in_port->value() == port_num;
}

MATCHER_P(CheckTunnelId, tunnel_id, "") {
  auto msg       = static_cast<of13::FlowMod*>(&arg);
  auto tun_field = static_cast<of13::TUNNELId*>(
      msg->get_oxm_field(of13::OFPXMT_OFB_TUNNEL_ID));
  return tun_field->value() == tunnel_id;
}

MATCHER_P(CheckIPv4Dst, ip, "") {
  auto msg        = static_cast<of13::FlowMod*>(&arg);
  auto ipv4_field = static_cast<of13::IPv4Dst*>(
      msg->get_oxm_field(of13::OFPXMT_OFB_IPV4_DST));
  return ipv4_field->value().getIPv4() == ip.s_addr;
}

MATCHER_P(CheckArpTpa, ip, "") {
  auto msg = static_cast<of13::FlowMod*>(&arg);
  auto ipv4_field =
      static_cast<of13::ARPTPA*>(msg->get_oxm_field(of13::OFPXMT_OFB_ARP_TPA));
  return ipv4_field->value().getIPv4() == ip.s_addr;
}

MATCHER_P(CheckEthType, eth_type, "") {
  auto msg            = static_cast<of13::FlowMod*>(&arg);
  auto eth_type_field = static_cast<of13::EthType*>(
      msg->get_oxm_field(of13::OFPXMT_OFB_ETH_TYPE));
  return eth_type_field->value() == eth_type;
}

MATCHER_P(CheckCommandType, command_type, "") {
  auto msg = static_cast<of13::FlowMod*>(&arg);
  return msg->command() == command_type;
}

MATCHER_P(CheckIPv4Src, ip, "") {
  auto msg        = static_cast<of13::FlowMod*>(&arg);
  auto ipv4_field = static_cast<of13::IPv4Src*>(
      msg->get_oxm_field(of13::OFPXMT_OFB_IPV4_SRC));
  return ipv4_field->value().getIPv4() == ip.s_addr;
}

MATCHER_P(CheckIPv4Proto, ip_proto, "") {
  auto msg        = static_cast<of13::FlowMod*>(&arg);
  auto ipv4_field = static_cast<of13::IPProto*>(
      msg->get_oxm_field(of13::OFPXMT_OFB_IP_PROTO));
  return ipv4_field->value() == ip_proto;
}

MATCHER_P(CheckTcpDstPort, tcp_port, "") {
  auto msg = static_cast<of13::FlowMod*>(&arg);
  auto tcp_port_field =
      static_cast<of13::TCPDst*>(msg->get_oxm_field(of13::OFPXMT_OFB_TCP_DST));
  return tcp_port_field->value() == tcp_port;
}

MATCHER_P(CheckTcpSrcPort, tcp_port, "") {
  auto msg = static_cast<of13::FlowMod*>(&arg);
  auto tcp_port_field =
      static_cast<of13::TCPSrc*>(msg->get_oxm_field(of13::OFPXMT_OFB_TCP_SRC));
  return tcp_port_field->value() == tcp_port;
}

/*
 * Test that tunnel flows are added when an add tunnel event is sent.
 * This only tests the flow matchers for now, because it is not easy to verify
 * the actions with the libfluid framework
 */
TEST_F(GTPApplicationTest, TestAddTunnel) {
  struct in_addr ue_ip;
  ue_ip.s_addr = inet_addr("0.0.0.1");
  struct in_addr enb_ip;
  enb_ip.s_addr    = inet_addr("0.0.0.2");
  uint32_t in_tei  = 1;
  uint32_t out_tei = 2;
  char imsi[]      = "001010000000013";
  int vlan = 0;
  AddGTPTunnelEvent add_tunnel(ue_ip, vlan, enb_ip, in_tei, out_tei, imsi);
  // Uplink
  EXPECT_CALL(
      *messenger,
      send_of_msg(
          AllOf(
              CheckTableId(0), CheckInPort(TEST_GTP_PORT),
              CheckTunnelId(in_tei), CheckCommandType(of13::OFPFC_ADD)),
          _))
      .Times(1);
  // downlink
  EXPECT_CALL(
      *messenger, send_of_msg(
                      AllOf(
                          CheckTableId(0), CheckInPort(of13::OFPP_LOCAL),
                          CheckEthType(0x0800), CheckIPv4Dst(ue_ip),
                          CheckCommandType(of13::OFPFC_ADD)),
                      _))
      .Times(1);
  EXPECT_CALL(
      *messenger,
      send_of_msg(
          AllOf(
              CheckTableId(0), CheckInPort(TEST_MTR_PORT), CheckEthType(0x0800),
              CheckIPv4Dst(ue_ip), CheckCommandType(of13::OFPFC_ADD)),
          _))
      .Times(1);

  EXPECT_CALL(
      *messenger, send_of_msg(
                      AllOf(
                          CheckTableId(0), CheckInPort(of13::OFPP_LOCAL),
                          CheckEthType(0x0806), CheckArpTpa(ue_ip),
                          CheckCommandType(of13::OFPFC_ADD)),
                      _))
      .Times(1);
  EXPECT_CALL(
      *messenger,
      send_of_msg(
          AllOf(
              CheckTableId(0), CheckInPort(TEST_MTR_PORT), CheckEthType(0x0806),
              CheckArpTpa(ue_ip), CheckCommandType(of13::OFPFC_ADD)),
          _))
      .Times(1);

  controller->dispatch_event(add_tunnel);
}

/*
 * Test that tunnel flows are deleted when a delete tunnel event is sent
 */
TEST_F(GTPApplicationTest, TestDeleteTunnel) {
  struct in_addr ue_ip;
  ue_ip.s_addr    = inet_addr("0.0.0.1");
  uint32_t in_tei = 1;
  DeleteGTPTunnelEvent del_tunnel(ue_ip, in_tei);
  // Uplink
  EXPECT_CALL(
      *messenger,
      send_of_msg(
          AllOf(
              CheckTableId(0), CheckInPort(TEST_GTP_PORT),
              CheckTunnelId(in_tei), CheckCommandType(of13::OFPFC_DELETE)),
          _))
      .Times(1);
  // downlink
  EXPECT_CALL(
      *messenger, send_of_msg(
                      AllOf(
                          CheckTableId(0), CheckInPort(of13::OFPP_LOCAL),
                          CheckEthType(0x0800), CheckIPv4Dst(ue_ip),
                          CheckCommandType(of13::OFPFC_DELETE)),
                      _))
      .Times(1);
  EXPECT_CALL(
      *messenger,
      send_of_msg(
          AllOf(
              CheckTableId(0), CheckInPort(TEST_MTR_PORT), CheckEthType(0x0800),
              CheckIPv4Dst(ue_ip), CheckCommandType(of13::OFPFC_DELETE)),
          _))
      .Times(1);

  EXPECT_CALL(
      *messenger, send_of_msg(
                      AllOf(
                          CheckTableId(0), CheckInPort(of13::OFPP_LOCAL),
                          CheckEthType(0x0806), CheckArpTpa(ue_ip),
                          CheckCommandType(of13::OFPFC_DELETE)),
                      _))
      .Times(1);

  EXPECT_CALL(
      *messenger,
      send_of_msg(
          AllOf(
              CheckTableId(0), CheckInPort(TEST_MTR_PORT), CheckEthType(0x0806),
              CheckArpTpa(ue_ip), CheckCommandType(of13::OFPFC_DELETE)),
          _))
      .Times(1);

  controller->dispatch_event(del_tunnel);
}

/*
 * Test that tunnel flows are added when an add tunnel event
 * is sent with dl_flow.
 */
TEST_F(GTPApplicationTest, TestAddTunnelDlFlow) {
  struct in_addr ue_ip;
  ue_ip.s_addr = inet_addr("0.0.0.1");
  struct in_addr enb_ip;
  enb_ip.s_addr    = inet_addr("0.0.0.2");
  uint32_t in_tei  = 1;
  uint32_t out_tei = 2;
  char imsi[]      = "001010000000013";
  struct ipv4flow_dl dl_flow;
  uint32_t dl_flow_precedence = 0;
  int vlan = 0;

  dl_flow.dst_ip.s_addr = inet_addr("0.0.0.3");
  dl_flow.src_ip.s_addr = inet_addr("0.0.0.4");
  dl_flow.tcp_dst_port  = 33;
  dl_flow.tcp_src_port  = 44;
  dl_flow.ip_proto      = 6;  // TCP
  dl_flow.set_params =
      SRC_IPV4 | DST_IPV4 | TCP_SRC_PORT | TCP_DST_PORT | IP_PROTO;

  AddGTPTunnelEvent add_tunnel(
      ue_ip, vlan, enb_ip, in_tei, out_tei, imsi, &dl_flow, dl_flow_precedence);
  // Uplink
  EXPECT_CALL(
      *messenger,
      send_of_msg(
          AllOf(
              CheckTableId(0), CheckInPort(TEST_GTP_PORT),
              CheckTunnelId(in_tei), CheckCommandType(of13::OFPFC_ADD)),
          _))
      .Times(1);
  // downlink
  EXPECT_CALL(
      *messenger,
      send_of_msg(
          AllOf(
              CheckTableId(0), CheckInPort(of13::OFPP_LOCAL),
              CheckEthType(0x0800), CheckIPv4Dst(dl_flow.dst_ip),
              CheckIPv4Src(dl_flow.src_ip), CheckIPv4Proto(dl_flow.ip_proto),
              CheckTcpDstPort(dl_flow.tcp_dst_port),
              CheckTcpSrcPort(dl_flow.tcp_src_port),
              CheckCommandType(of13::OFPFC_ADD)),
          _))
      .Times(1);
  EXPECT_CALL(
      *messenger,
      send_of_msg(
          AllOf(
              CheckTableId(0), CheckInPort(TEST_MTR_PORT), CheckEthType(0x0800),
              CheckIPv4Dst(dl_flow.dst_ip), CheckIPv4Src(dl_flow.src_ip),
              CheckIPv4Proto(dl_flow.ip_proto),
              CheckTcpDstPort(dl_flow.tcp_dst_port),
              CheckTcpSrcPort(dl_flow.tcp_src_port),
              CheckCommandType(of13::OFPFC_ADD)),
          _))
      .Times(1);

  EXPECT_CALL(
      *messenger, send_of_msg(
                      AllOf(
                          CheckTableId(0), CheckInPort(of13::OFPP_LOCAL),
                          CheckEthType(0x0806), CheckArpTpa(ue_ip),
                          CheckCommandType(of13::OFPFC_ADD)),
                      _))
      .Times(1);
  EXPECT_CALL(
      *messenger,
      send_of_msg(
          AllOf(
              CheckTableId(0), CheckInPort(TEST_MTR_PORT), CheckEthType(0x0806),
              CheckArpTpa(ue_ip), CheckCommandType(of13::OFPFC_ADD)),
          _))
      .Times(1);

  controller->dispatch_event(add_tunnel);
}

/*
 * Test that tunnel flows are deleted when a delete tunnel event
 * is sent with dl_flow
 */
TEST_F(GTPApplicationTest, TestDeleteTunnelDlFlow) {
  struct in_addr ue_ip;
  ue_ip.s_addr    = inet_addr("0.0.0.1");
  uint32_t in_tei = 1;
  struct ipv4flow_dl dl_flow;

  dl_flow.dst_ip.s_addr = inet_addr("0.0.0.3");
  dl_flow.src_ip.s_addr = inet_addr("0.0.0.4");
  dl_flow.tcp_dst_port  = 33;
  dl_flow.tcp_src_port  = 44;
  dl_flow.ip_proto      = 6;  // TCP
  dl_flow.set_params =
      SRC_IPV4 | DST_IPV4 | TCP_SRC_PORT | TCP_DST_PORT | IP_PROTO;

  DeleteGTPTunnelEvent del_tunnel(ue_ip, in_tei, &dl_flow);
  // Uplink
  EXPECT_CALL(
      *messenger,
      send_of_msg(
          AllOf(
              CheckTableId(0), CheckInPort(TEST_GTP_PORT),
              CheckTunnelId(in_tei), CheckCommandType(of13::OFPFC_DELETE)),
          _))
      .Times(1);
  // downlink
  EXPECT_CALL(
      *messenger,
      send_of_msg(
          AllOf(
              CheckTableId(0), CheckInPort(of13::OFPP_LOCAL),
              CheckEthType(0x0800), CheckIPv4Dst(dl_flow.dst_ip),
              CheckIPv4Src(dl_flow.src_ip), CheckIPv4Proto(dl_flow.ip_proto),
              CheckTcpDstPort(dl_flow.tcp_dst_port),
              CheckTcpSrcPort(dl_flow.tcp_src_port),
              CheckCommandType(of13::OFPFC_DELETE)),
          _))
      .Times(1);
  EXPECT_CALL(
      *messenger,
      send_of_msg(
          AllOf(
              CheckTableId(0), CheckInPort(TEST_MTR_PORT), CheckEthType(0x0800),
              CheckIPv4Dst(dl_flow.dst_ip), CheckIPv4Src(dl_flow.src_ip),
              CheckIPv4Proto(dl_flow.ip_proto),
              CheckTcpDstPort(dl_flow.tcp_dst_port),
              CheckTcpSrcPort(dl_flow.tcp_src_port),
              CheckCommandType(of13::OFPFC_DELETE)),
          _))
      .Times(1);

  EXPECT_CALL(
      *messenger, send_of_msg(
                      AllOf(
                          CheckTableId(0), CheckInPort(of13::OFPP_LOCAL),
                          CheckEthType(0x0806), CheckArpTpa(ue_ip),
                          CheckCommandType(of13::OFPFC_DELETE)),
                      _))
      .Times(1);

  EXPECT_CALL(
      *messenger,
      send_of_msg(
          AllOf(
              CheckTableId(0), CheckInPort(TEST_MTR_PORT), CheckEthType(0x0806),
              CheckArpTpa(ue_ip), CheckCommandType(of13::OFPFC_DELETE)),
          _))
      .Times(1);

  controller->dispatch_event(del_tunnel);
}

int main(int argc, char** argv) {
  ::testing::InitGoogleTest(&argc, argv);
  return RUN_ALL_TESTS();
}

}  // namespace
