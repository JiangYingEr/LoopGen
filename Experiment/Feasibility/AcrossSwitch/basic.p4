/* -*- P4_16 -*- */
#include <core.p4>
#include <v1model.p4>

typedef bit<9>  egressSpec_t;
typedef bit<48> macAddr_t;
typedef bit<32> ip4Addr_t;
typedef bit<9>  port_t;


const bit<16> TYPE_IPV4 = 0x800;
const bit<8> UDP_HEADER_LEN = 8;


const port_t CPU_PORT           = 0x4;

const bit<16> ARP_OP_REQ        = 0x0001;
const bit<16> ARP_OP_REPLY      = 0x0002;

const bit<16> TYPE_ARP          = 0x0806;
const bit<16> TYPE_CPU_METADATA = 0x080a;

/*************************************************************************
*********************** H E A D E R S  ***********************************
*************************************************************************/



header ethernet_t {
    macAddr_t dstAddr;
    macAddr_t srcAddr;
    bit<16>   etherType;
}

header cpu_metadata_t {
    bit<8> fromCpu;
    bit<8> switch_id;
    bit<16> origEtherType;
    bit<16> srcPort;
}

header arp_t {
    bit<16> hwType;
    bit<16> protoType;
    bit<8> hwAddrLen;
    bit<8> protoAddrLen;
    bit<16> opcode;
    // assumes hardware type is ethernet and protocol is IP
    macAddr_t srcEth;
    ip4Addr_t srcIP;
    macAddr_t dstEth;
    ip4Addr_t dstIP;
}

header ipv4_t {
    bit<4>    version;
    bit<4>    ihl;
    bit<8>    diffserv;
    bit<16>   totalLen;
    bit<16>   identification;
    bit<3>    flags;
    bit<13>   fragOffset;
    bit<8>    ttl;
    bit<8>    protocol;
    bit<16>   hdrChecksum;
    ip4Addr_t srcAddr;
    ip4Addr_t dstAddr;
}



struct metadata {
    @field_list(0)
    bit<8> switch_id;
    @field_list(0)
    bit<9> ingress_port;
}

struct headers {
    ethernet_t   ethernet;
    cpu_metadata_t    cpu_metadata;
    arp_t        arp;
    ipv4_t       ipv4;

    //ethernet    report_ethernet;
}

/*************************************************************************
*********************** P A R S E R  ***********************************
*************************************************************************/

parser MyParser(packet_in packet,
                out headers hdr,
                inout metadata meta,
                inout standard_metadata_t standard_metadata) {

    state start {
        transition parse_ethernet;
    }

    state parse_ethernet {
        packet.extract(hdr.ethernet);
        transition select(hdr.ethernet.etherType) {
            TYPE_ARP: parse_arp;
            TYPE_CPU_METADATA: parse_cpu_metadata;
            TYPE_IPV4: parse_ipv4;
            default: accept;
        }
    }

    state parse_cpu_metadata {
        packet.extract(hdr.cpu_metadata);
        transition select(hdr.cpu_metadata.origEtherType) {
            TYPE_ARP: parse_arp;
            TYPE_IPV4: parse_ipv4;
            default: accept;
        }
    }

    state parse_arp {
        packet.extract(hdr.arp);
        transition accept;
    }

    state parse_ipv4 {
        packet.extract(hdr.ipv4);
        transition accept;
    }

}

/*************************************************************************
************   C H E C K S U M    V E R I F I C A T I O N   *************
*************************************************************************/

control MyVerifyChecksum(inout headers hdr, inout metadata meta) {
    apply {  }
}


/*************************************************************************
**************  I N G R E S S   P R O C E S S I N G   *******************
*************************************************************************/

control MyIngress(inout headers hdr,
                  inout metadata meta,
                  inout standard_metadata_t standard_metadata) {
    action init_switch_id(bit<8> switch_id){
        meta.switch_id = switch_id;
    }
    action drop() {
        mark_to_drop(standard_metadata);
    }

    action ipv4_forward(egressSpec_t port) {
        standard_metadata.egress_spec = port;
        #hdr.ethernet.srcAddr = hdr.ethernet.dstAddr;
        #hdr.ethernet.dstAddr = dstAddr;
        hdr.ipv4.ttl = hdr.ipv4.ttl - 1;
    }

    action cpu_meta_encap() {
        hdr.cpu_metadata.setValid();
        hdr.cpu_metadata.origEtherType = hdr.ethernet.etherType;
        hdr.cpu_metadata.srcPort = (bit<16>)standard_metadata.ingress_port;
        hdr.ethernet.etherType = TYPE_CPU_METADATA;
        hdr.cpu_metadata.switch_id = meta.switch_id;
    }

    action cpu_meta_decap() {
        hdr.ethernet.etherType = hdr.cpu_metadata.origEtherType;
        hdr.cpu_metadata.setInvalid();
        //standard_metadata.egress_spec = standard_metadata.ingress_port;
    }

    action send_to_cpu() {
        cpu_meta_encap();
        standard_metadata.egress_spec = CPU_PORT;
    }

    action clone_to_cpu() {
        meta.ingress_port = standard_metadata.ingress_port;
        clone_preserving_field_list(CloneType.I2E, 100, 0);
    }

    action resolve_arp(macAddr_t mac) {
        ip4Addr_t dstIP = hdr.arp.dstIP;
        hdr.arp.dstIP = hdr.arp.srcIP;
        hdr.arp.dstEth = hdr.arp.srcEth;
        hdr.arp.srcIP = dstIP;
        hdr.arp.srcEth = mac;
        standard_metadata.egress_spec = standard_metadata.ingress_port;

    }

    table tb_init_switch_id {
        actions = {
            init_switch_id;
            NoAction;
        }
        default_action = NoAction();
    }

    table ipv4_lpm {
        key = {
            //hdr.ipv4.srcAddr: exact;
            hdr.ipv4.dstAddr: exact;
        }
        actions = {
            ipv4_forward;
            drop;
            NoAction;
        }
        size = 1024;
        default_action = drop();
    }

    table tb_arp {
        key = {
            hdr.arp.dstIP: exact;
        }
        actions = {
            resolve_arp;
            send_to_cpu;
        }
        default_action = send_to_cpu();

    }

    table sip_learn {
        key = {
            hdr.ipv4.srcAddr: exact;
            hdr.ipv4.dstAddr: exact;
        }
        actions = {
            NoAction;
            clone_to_cpu;
        }
        default_action = clone_to_cpu;
    }

    apply {
        tb_init_switch_id.apply();
        if (hdr.ipv4.isValid()) {
            sip_learn.apply();
            ipv4_lpm.apply();
        }
    /*
        if (standard_metadata.ingress_port == CPU_PORT) {
            cpu_meta_decap();
            standard_metadata.egress_spec = standard_metadata.ingress_port;
        }
        else if (hdr.arp.isValid() ) {
            tb_arp.apply();
        }
        else if (hdr.ipv4.isValid()) {
            ipv4_lpm.apply();
        }
        */
    }
}

/*************************************************************************
****************  E G R E S S   P R O C E S S I N G   *******************
*************************************************************************/

control MyEgress(inout headers hdr,
                 inout metadata meta,
                 inout standard_metadata_t standard_metadata) {
    apply {
        if (standard_metadata.instance_type == 1){
            hdr.cpu_metadata.setValid();
            hdr.cpu_metadata.origEtherType = hdr.ethernet.etherType;
            hdr.cpu_metadata.srcPort = (bit<16>)meta.ingress_port;
            hdr.ethernet.etherType = TYPE_CPU_METADATA;
            hdr.cpu_metadata.switch_id = meta.switch_id;
            //truncate((bit<32>)19); //ether+cpu header
        }
    }
}

/*************************************************************************
*************   C H E C K S U M    C O M P U T A T I O N   **************
*************************************************************************/

control MyComputeChecksum(inout headers  hdr, inout metadata meta) {
     apply {
        update_checksum(
        hdr.ipv4.isValid(),
            { hdr.ipv4.version,
              hdr.ipv4.ihl,
              hdr.ipv4.diffserv,
              hdr.ipv4.totalLen,
              hdr.ipv4.identification,
              hdr.ipv4.flags,
              hdr.ipv4.fragOffset,
              hdr.ipv4.ttl,
              hdr.ipv4.protocol,
              hdr.ipv4.srcAddr,
              hdr.ipv4.dstAddr },
            hdr.ipv4.hdrChecksum,
            HashAlgorithm.csum16);
    }
}

/*************************************************************************
***********************  D E P A R S E R  *******************************
*************************************************************************/

control MyDeparser(packet_out packet, in headers hdr) {
    apply {

        packet.emit(hdr.ethernet);
        packet.emit(hdr.cpu_metadata);
        packet.emit(hdr.arp);
        packet.emit(hdr.ipv4);
    }
}

/*************************************************************************
***********************  S W I T C H  *******************************
*************************************************************************/

V1Switch(
MyParser(),
MyVerifyChecksum(),
MyIngress(),
MyEgress(),
MyComputeChecksum(),
MyDeparser()
) main;
