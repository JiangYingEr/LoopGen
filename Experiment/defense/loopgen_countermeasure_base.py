import time
from typing import Dict, List, Optional, Sequence, Tuple

from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.lib.packet import ethernet
from ryu.lib.packet import ether_types
from ryu.lib.packet import packet
from ryu.ofproto import ofproto_v1_3

try:
    from ryu.topology import event as topo_event
    from ryu.topology.api import get_link
except ImportError:  # pragma: no cover - depends on local ryu install
    topo_event = None
    get_link = None


class LoopGenCountermeasureBase(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    # Subclasses override these knobs to reproduce different countermeasures.
    APP_NAME = "loopgen_base"
    ENABLE_LOOP_DETECTION = False
    MIN_UPDATE_INTERVAL_SEC: Optional[float] = None
    TRACE_HOP_LIMIT = 32

    # Static host placement used by the LoopGen reproduction topology.
    STATIC_HOST_PORTS = {
        1: {
            "00:00:00:00:00:01": 1,
            "00:00:00:00:00:02": 2,
            "00:00:00:00:00:03": 3,
        },
        2: {
            "00:00:00:00:00:01": 2,
            "00:00:00:00:00:02": 1,
            "00:00:00:00:00:03": 3,
        },
        3: {
            "00:00:00:00:00:01": 3,
            "00:00:00:00:00:02": 2,
            "00:00:00:00:00:03": 1,
        },
    }

    # Fallback topology for LoopGen_topo.py when Ryu link discovery is not enabled.
    FALLBACK_SWITCH_LINKS = {
        (1, 2): 2,
        (2, 2): 1,
        (2, 3): 3,
        (3, 2): 2,
        (3, 3): 1,
        (1, 3): 3,
    }

    def __init__(self, *args, **kwargs):
        super(LoopGenCountermeasureBase, self).__init__(*args, **kwargs)
        self.mac_to_port: Dict[int, Dict[str, int]] = {
            dpid: dict(ports) for dpid, ports in self.STATIC_HOST_PORTS.items()
        }
        self.switch_links: Dict[Tuple[int, int], int] = dict(self.FALLBACK_SWITCH_LINKS)
        self.last_update_time: Dict[str, float] = {}
        self.logger.info(
            "[%s] loaded static MAC table for H1/H2/H3; loop_detection=%s, min_update_interval=%s",
            self.APP_NAME,
            self.ENABLE_LOOP_DETECTION,
            self.MIN_UPDATE_INTERVAL_SEC,
        )

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER, ofproto.OFPCML_NO_BUFFER)]
        self.add_flow(datapath, priority=0, match=match, actions=actions)

    def add_flow(self, datapath, priority, match, actions, buffer_id=None):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        instructions = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, actions)]
        if buffer_id is not None:
            mod = parser.OFPFlowMod(
                datapath=datapath,
                buffer_id=buffer_id,
                priority=priority,
                match=match,
                instructions=instructions,
            )
        else:
            mod = parser.OFPFlowMod(
                datapath=datapath,
                priority=priority,
                match=match,
                instructions=instructions,
            )
        datapath.send_msg(mod)

    def _refresh_topology_from_ryu(self) -> None:
        if get_link is None:
            return

        try:
            links = get_link(self, None)
        except Exception as exc:  # pragma: no cover - defensive around controller runtime
            self.logger.debug("[%s] topology refresh failed: %s", self.APP_NAME, exc)
            return

        if not links:
            return

        refreshed = dict(self.FALLBACK_SWITCH_LINKS)
        for link in links:
            refreshed[(link.src.dpid, link.src.port_no)] = link.dst.dpid
        self.switch_links = refreshed

    def _trace_implied_forwarding_loop(
        self,
        address: str,
        proposed_dpid: int,
        proposed_port: int,
    ) -> Tuple[bool, List[Tuple[int, int]]]:
        # Build the hypothetical address-learning database for this address only.
        address_locations: Dict[int, int] = {}
        for dpid, mac_table in self.mac_to_port.items():
            if address in mac_table:
                address_locations[dpid] = mac_table[address]
        address_locations[proposed_dpid] = proposed_port

        if len(address_locations) < 2:
            return False, []

        for start_dpid in address_locations:
            visited_index: Dict[Tuple[int, int], int] = {}
            path: List[Tuple[int, int]] = []
            current_dpid = start_dpid

            for _ in range(self.TRACE_HOP_LIMIT):
                current_port = address_locations.get(current_dpid)
                if current_port is None:
                    break

                location = (current_dpid, current_port)
                if location in visited_index:
                    cycle_path = path[visited_index[location]:] + [location]
                    return True, cycle_path

                visited_index[location] = len(path)
                path.append(location)

                next_dpid = self.switch_links.get(location)
                if next_dpid is None:
                    break
                current_dpid = next_dpid
            else:
                # The paper suggests treating overlong traces as inconsistent.
                return True, path

        return False, []

    def _accept_learning_update(
        self,
        dpid: int,
        src: str,
        in_port: int,
        now: float,
    ) -> Tuple[bool, str]:
        start_time = time.time()
        if self.MIN_UPDATE_INTERVAL_SEC is not None:
            last_time = self.last_update_time.get(src)
            if last_time is not None and now - last_time < self.MIN_UPDATE_INTERVAL_SEC:
                return False, (
                    f"rapid location update for {src}: delta={now - last_time:.6f}s "
                    f"< {self.MIN_UPDATE_INTERVAL_SEC:.6f}s"
                )
            
        if self.ENABLE_LOOP_DETECTION:
            self._refresh_topology_from_ryu()
            detected, cycle_path = self._trace_implied_forwarding_loop(src, dpid, in_port)
            if detected:
                return False, f"loop detected for {src}: implied path {cycle_path}"

        self.mac_to_port.setdefault(dpid, {})[src] = in_port
        self.last_update_time[src] = now
        end_time = time.time()
        cost_time_ms = (end_time-start_time)*1000
        print(f"[{self.__class__.__name__}] Defense Algorithm Time Cost per Execution: {cost_time_ms:.4f} ms")
        return True, "accepted"

    def _resolve_output_port(self, dpid: int, dst: str, ofproto) -> int:
        mac_table = self.mac_to_port.setdefault(dpid, {})
        return mac_table.get(dst, ofproto.OFPP_FLOOD)

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        in_port = msg.match["in_port"]

        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocols(ethernet.ethernet)[0]
        if eth.ethertype == ether_types.ETH_TYPE_LLDP:
            return

        src = eth.src
        dst = eth.dst
        dpid = datapath.id

        accepted, reason = self._accept_learning_update(
            dpid=dpid,
            src=src,
            in_port=in_port,
            now=time.time(),
        )
        if accepted:
            self.logger.info(
                "[%s] packet in dpid=%s src=%s dst=%s in_port=%s (learned)",
                self.APP_NAME,
                dpid,
                src,
                dst,
                in_port,
            )
        else:
            self.logger.warning(
                "[%s] blocked learning update dpid=%s src=%s in_port=%s: %s",
                self.APP_NAME,
                dpid,
                src,
                in_port,
                reason,
            )

        out_port = self._resolve_output_port(dpid, dst, ofproto)
        actions = [parser.OFPActionOutput(out_port)]

        if out_port != ofproto.OFPP_FLOOD:
            match = parser.OFPMatch(in_port=in_port, eth_dst=dst, eth_src=src)
            if msg.buffer_id != ofproto.OFP_NO_BUFFER:
                self.add_flow(datapath, priority=1, match=match, actions=actions, buffer_id=msg.buffer_id)
                return
            self.add_flow(datapath, priority=1, match=match, actions=actions)

        data = None
        if msg.buffer_id == ofproto.OFP_NO_BUFFER:
            data = msg.data
        out = parser.OFPPacketOut(
            datapath=datapath,
            buffer_id=msg.buffer_id,
            in_port=in_port,
            actions=actions,
            data=data,
        )
        datapath.send_msg(out)

    if topo_event is not None:
        @set_ev_cls(topo_event.EventSwitchEnter)
        def _switch_enter_handler(self, ev):
            self._refresh_topology_from_ryu()

        @set_ev_cls(topo_event.EventLinkAdd)
        def _link_add_handler(self, ev):
            self._refresh_topology_from_ryu()

        @set_ev_cls(topo_event.EventLinkDelete)
        def _link_delete_handler(self, ev):
            self._refresh_topology_from_ryu()
