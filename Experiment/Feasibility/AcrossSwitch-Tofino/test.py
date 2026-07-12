################################################################################
#  INTEL CONFIDENTIAL
#
#  Copyright (c) 2021 Intel Corporation
#  All Rights Reserved.
#
#  This software and the related documents are Intel copyrighted materials,
#  and your use of them is governed by the express license under which they
#  were provided to you ("License"). Unless the License provides otherwise,
#  you may not use, modify, copy, publish, distribute, disclose or transmit this
#  software or the related documents without Intel's prior written permission.
#
#  This software and the related documents are provided as is, with no express or
#  implied warranties, other than those that are expressly stated in the License.
#################################################################################


import ptf.testutils as testutils
from p4testutils.misc_utils import get_logger, get_sw_ports
from bfruntime_client_base_tests import BfRuntimeTest
import bfrt_grpc.client as gc


logger = get_logger()
swports = get_sw_ports()

P4_PROGRAM_NAME = testutils.test_param_get("p4_name") or "loop"
FORWARD_TABLE_NAME = "SwitchIngress.forward"
FORWARD_ACTION_NAME = "SwitchIngress.hit"
FORWARD_EGRESS_PORT = 19


def _pick_ingress_port(excluded_port):
    for port in swports:
        if port != excluded_port:
            return port
    raise RuntimeError(
        "No ingress port available that differs from egress port %d" % excluded_port
    )


def _forward_table_add(table, target, dst_mac, port, counter_bytes=0, counter_pkts=0):
    table.entry_add(
        target,
        [table.make_key([gc.KeyTuple("hdr.ethernet.dst_addr", dst_mac)])],
        [table.make_data(
            [gc.DataTuple("port", port),
             gc.DataTuple("$COUNTER_SPEC_BYTES", counter_bytes),
             gc.DataTuple("$COUNTER_SPEC_PKTS", counter_pkts)],
            FORWARD_ACTION_NAME,
        )],
    )


class ForwardDirectCounterTest(BfRuntimeTest):
    """Validate the direct counter attached to SwitchIngress.forward."""

    def setUp(self):
        BfRuntimeTest.setUp(self, 0, P4_PROGRAM_NAME)

    def runTest(self):
        ig_port = _pick_ingress_port(FORWARD_EGRESS_PORT)
        dmac = "00:11:22:33:44:55"
        smac = "11:33:55:77:99:00"
        pkt = testutils.simple_tcp_packet(eth_dst=dmac, eth_src=smac)
        num_pkts = 3
        pkt_size = len(pkt) + 4
        num_bytes = num_pkts * pkt_size

        bfrt_info = self.interface.bfrt_info_get(P4_PROGRAM_NAME)
        forward_table = bfrt_info.table_get(FORWARD_TABLE_NAME)
        forward_table.info.key_field_annotation_add("hdr.ethernet.dst_addr", "mac")

        target = gc.Target(device_id=0, pipe_id=0xFFFF)
        key = forward_table.make_key([gc.KeyTuple("hdr.ethernet.dst_addr", dmac)])

        logger.info("Programming %s entry for dst MAC %s", FORWARD_TABLE_NAME, dmac)
        _forward_table_add(
            forward_table,
            target,
            dmac,
            FORWARD_EGRESS_PORT,
            counter_bytes=0,
            counter_pkts=0,
        )

        try:
            logger.info(
                "Sending %d matching packet(s) on ingress port %d; loop.p4 hardcodes egress port %d",
                num_pkts,
                ig_port,
                FORWARD_EGRESS_PORT,
            )
            for _ in range(num_pkts):
                testutils.send_packet(self, ig_port, pkt)

            resp = forward_table.entry_get(
                target,
                [key],
                {"from_hw": True},
                forward_table.make_data(
                    [gc.DataTuple("$COUNTER_SPEC_BYTES"),
                     gc.DataTuple("$COUNTER_SPEC_PKTS")],
                    FORWARD_ACTION_NAME,
                    get=True,
                ),
            )

            data_dict = next(resp)[0].to_dict()
            recv_pkts = data_dict["$COUNTER_SPEC_PKTS"]
            recv_bytes = data_dict["$COUNTER_SPEC_BYTES"]

            logger.info(
                "Counter readback packets=%d bytes=%d (expected packets=%d bytes=%d)",
                recv_pkts,
                recv_bytes,
                num_pkts,
                num_bytes,
            )

            assert recv_pkts == num_pkts, (
                "Packet counter mismatch: expected %d got %d"
                % (num_pkts, recv_pkts)
            )
            assert recv_bytes == num_bytes, (
                "Byte counter mismatch: expected %d got %d"
                % (num_bytes, recv_bytes)
            )
        finally:
            logger.info("Deleting %s entry for dst MAC %s", FORWARD_TABLE_NAME, dmac)
            forward_table.entry_del(target, [key])
