#!/usr/bin/env python3

from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet, ethernet

AUTH_ETHER_TYPE = 0x88B5
PROTECTED_MAC = "00:00:00:00:00:08"
AUTH_PASSWORD = "letmein"


class SimpleSwitch13Auth(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(SimpleSwitch13Auth, self).__init__(*args, **kwargs)

        self.mac_to_port = {
            "0000000000000001": {"00:00:00:00:00:01": 1},
            "0000000000000002": {"00:00:00:00:00:02": 1},
            "0000000000000003": {"00:00:00:00:00:03": 1},
        }

        self.edge_port = 1
        self.pending_auth = {}  # { (dpid, mac): {'in_port': port, 'msg': msg} }
        self.auth_passed = set()

        self.logger.info("=== SimpleSwitch13Auth_Fixed started ===")
        self.logger.info("Protected MAC: %s", PROTECTED_MAC)

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        dp = ev.msg.datapath
        parser = dp.ofproto_parser
        ofp = dp.ofproto

        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofp.OFPP_CONTROLLER,
                                          ofp.OFPCML_NO_BUFFER)]
        self.add_flow(dp, 0, match, actions)
        self.logger.info("Installed table-miss on %s", format(dp.id, "d").zfill(16))

    def add_flow(self, dp, priority, match, actions, buffer_id=None):
        parser = dp.ofproto_parser
        ofp = dp.ofproto
        inst = [parser.OFPInstructionActions(ofp.OFPIT_APPLY_ACTIONS, actions)]
        if buffer_id:
            mod = parser.OFPFlowMod(datapath=dp, buffer_id=buffer_id,
                                    priority=priority, match=match,
                                    instructions=inst)
        else:
            mod = parser.OFPFlowMod(datapath=dp, priority=priority,
                                    match=match, instructions=inst)
        dp.send_msg(mod)

    def send_auth_request(self, dp, port, mac_addr):
        parser = dp.ofproto_parser
        ofp = dp.ofproto
        ctrl_mac = "00:00:00:00:00:AA"

        eth = ethernet.ethernet(dst=mac_addr, src=ctrl_mac, ethertype=AUTH_ETHER_TYPE)
        pkt = packet.Packet()
        pkt.add_protocol(eth)
        pkt.add_protocol(b"AUTH_REQ")
        pkt.serialize()

        actions = [parser.OFPActionOutput(port)]
        out = parser.OFPPacketOut(datapath=dp, buffer_id=ofp.OFP_NO_BUFFER,
                                  in_port=ofp.OFPP_CONTROLLER,
                                  actions=actions, data=pkt.data)
        dp.send_msg(out)
        self.logger.info("[Auth] Sent AUTH_REQ to %s (port=%d)", mac_addr, port)

    def verify_and_allow(self, dp, src_mac, in_port, msg):
        parser = dp.ofproto_parser
        ofp = dp.ofproto
        dpid = format(dp.id, "d").zfill(16)

        self.mac_to_port.setdefault(dpid, {})
        self.mac_to_port[dpid][src_mac] = in_port
        self.auth_passed.add((dpid, src_mac))
        self.logger.info("[Auth] %s verified OK on %s port=%s", src_mac, dpid, in_port)

        orig_pkt = packet.Packet(msg.data)
        eth = orig_pkt.get_protocols(ethernet.ethernet)[0]
        dst_mac = eth.dst

        if dst_mac in self.mac_to_port[dpid]:
            out_port = self.mac_to_port[dpid][dst_mac]
        else:
            out_port = ofp.OFPP_FLOOD

        match = parser.OFPMatch(in_port=in_port, eth_src=src_mac, eth_dst=dst_mac)
        actions = [parser.OFPActionOutput(out_port)]
        self.add_flow(dp, 1, match, actions)

        if out_port != ofp.OFPP_FLOOD:
            reverse_match = parser.OFPMatch(in_port=out_port, eth_src=dst_mac, eth_dst=src_mac)
            reverse_actions = [parser.OFPActionOutput(in_port)]
            self.add_flow(dp, 1, reverse_match, reverse_actions)

        data = msg.data if msg.buffer_id == ofp.OFP_NO_BUFFER else None
        out = parser.OFPPacketOut(datapath=dp, buffer_id=msg.buffer_id,
                                  in_port=in_port, actions=actions, data=data)
        dp.send_msg(out)
        self.logger.info("[Auth] Released first packet from %s -> %s (out_port=%s)", src_mac, dst_mac, out_port)

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        msg = ev.msg
        dp = msg.datapath
        parser = dp.ofproto_parser
        ofp = dp.ofproto
        in_port = msg.match["in_port"]

        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocols(ethernet.ethernet)[0]
        src, dst, eth_type = eth.src, eth.dst, eth.ethertype
        dpid = format(dp.id, "d").zfill(16)
        self.mac_to_port.setdefault(dpid, {})

        if eth_type == AUTH_ETHER_TYPE:
            raw = msg.data[14:] if len(msg.data) > 14 else b""
            if raw.startswith(b"AUTH_RESP:"):
                password = raw.split(b":", 1)[1].decode(errors="ignore")
                key = (dpid, PROTECTED_MAC)
                if key in self.pending_auth and password == AUTH_PASSWORD:
                    ctx = self.pending_auth.pop(key)
                    self.verify_and_allow(dp, PROTECTED_MAC, ctx["in_port"], ctx["msg"])
                else:
                    self.logger.info("[Auth] AUTH_RESP password mismatch or no pending entry")
            return

        if src == PROTECTED_MAC and in_port == self.edge_port:
            key = (dpid, src)
            if (dpid, src) in self.auth_passed:
                pass
            elif key not in self.pending_auth:
                self.pending_auth[key] = {"in_port": in_port, "msg": msg}
                self.send_auth_request(dp, in_port, src)
                self.logger.info("[Auth] %s pending auth on %s", src, dpid)
                return
            else:
                self.logger.info("[Auth] %s auth already pending on %s", src, dpid)
                return

        self.mac_to_port[dpid][src] = in_port

        if dst in self.mac_to_port[dpid]:
            out_port = self.mac_to_port[dpid][dst]
        else:
            out_port = ofp.OFPP_FLOOD

        actions = [parser.OFPActionOutput(out_port)]

        if out_port != ofp.OFPP_FLOOD:
            match = parser.OFPMatch(in_port=in_port, eth_src=src, eth_dst=dst)
            if msg.buffer_id != ofp.OFP_NO_BUFFER:
                self.add_flow(dp, 1, match, actions, msg.buffer_id)
                return
            else:
                self.add_flow(dp, 1, match, actions)

        data = msg.data if msg.buffer_id == ofp.OFP_NO_BUFFER else None
        out = parser.OFPPacketOut(datapath=dp, buffer_id=msg.buffer_id,
                                  in_port=in_port, actions=actions, data=data)
        dp.send_msg(out)

