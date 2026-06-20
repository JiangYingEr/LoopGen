from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_4
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet
from ryu.lib.packet import ether_types


class SimpleSwitch14(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_4.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(SimpleSwitch14, self).__init__(*args, **kwargs)
        self.mac_to_port = {}

        # Static MAC Table
        s1_dpid = format(1, "d").zfill(16)
        s2_dpid = format(2, "d").zfill(16)
        s3_dpid = format(3, "d").zfill(16)

        self.mac_to_port.setdefault(s1_dpid, {})
        self.mac_to_port.setdefault(s2_dpid, {})
        self.mac_to_port.setdefault(s3_dpid, {})

        # S1
        self.mac_to_port[s1_dpid]["00:00:00:00:00:01"] = 1
        self.mac_to_port[s1_dpid]["00:00:00:00:00:02"] = 2
        self.mac_to_port[s1_dpid]["00:00:00:00:00:03"] = 3

        # S2
        self.mac_to_port[s2_dpid]["00:00:00:00:00:01"] = 2
        self.mac_to_port[s2_dpid]["00:00:00:00:00:02"] = 1
        self.mac_to_port[s2_dpid]["00:00:00:00:00:03"] = 3

        # S3
        self.mac_to_port[s3_dpid]["00:00:00:00:00:01"] = 3
        self.mac_to_port[s3_dpid]["00:00:00:00:00:02"] = 2
        self.mac_to_port[s3_dpid]["00:00:00:00:00:03"] = 1
        
        self.logger.info("STATIC MAC TABLE LOADED: No flooding will occur for H1/H2/H3.")

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        # install table-miss flow entry
        #
        # We specify NO BUFFER to max_len of the output action due to
        # OVS bug. At this moment, if we specify a lesser number, e.g.,
        # 128, OVS will send Packet-In with invalid buffer_id and
        # truncated packet data. In that case, we cannot output packets
        # correctly.  The bug has been fixed in OVS v2.1.0.
        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,
                                          ofproto.OFPCML_NO_BUFFER)]
        self.add_flow(datapath, 0, match, actions)

    def add_flow(self, datapath, priority, match, actions):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,
                                             actions)]

        mod = parser.OFPFlowMod(datapath=datapath, priority=priority,
                                match=match, instructions=inst)
        datapath.send_msg(mod)

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        in_port = msg.match['in_port']

        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocols(ethernet.ethernet)[0]

        if eth.ethertype == ether_types.ETH_TYPE_LLDP:
            # ignore lldp packet
            return

        #ignore IPv6
        #if eth.ethertype == 0x86dd:
        #    return

        dst = eth.dst
        src = eth.src

        dpid = datapath.id
        self.mac_to_port.setdefault(dpid, {})

        self.logger.info("packet in %s %s %s %s", dpid, src, dst, in_port)

        # learn a mac address to avoid FLOOD next time.
        self.mac_to_port[dpid][src] = in_port

        if dst in self.mac_to_port[dpid]:
            out_port = self.mac_to_port[dpid][dst]
        else:
            out_port = ofproto.OFPP_FLOOD

        actions = [parser.OFPActionOutput(out_port)]

        # install a flow to avoid packet_in next time
        if out_port != ofproto.OFPP_FLOOD:
            match = parser.OFPMatch(in_port=in_port, eth_dst=dst, eth_src=src)
            self.add_flow(datapath, 1, match, actions)

        data = None
        if msg.buffer_id == ofproto.OFP_NO_BUFFER:
            data = msg.data

        out = parser.OFPPacketOut(datapath=datapath, buffer_id=msg.buffer_id,
                                  in_port=in_port, actions=actions, data=data)
        datapath.send_msg(out)
