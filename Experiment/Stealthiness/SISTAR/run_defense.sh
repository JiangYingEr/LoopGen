#!/bin/bash

echo ">>> Start configuring S1 defense..."

echo "Setting Thresholds to 50 PPS..."
simple_switch_CLI --thrift-port 9090 <<< "register_write MyIngress.threshold_register32 7 50"
simple_switch_CLI --thrift-port 9090 <<< "register_write MyIngress.threshold_register32 8 50"

simple_switch_CLI --thrift-port 9090 <<< "table_clear MyIngress.DDoS_ternary"

echo "Adding Drop Rules..."
simple_switch_CLI --thrift-port 9090 <<< "table_add MyIngress.DDoS_ternary MyIngress.drop 0x1&&&0xff => 1"
simple_switch_CLI --thrift-port 9090 <<< "table_add MyIngress.DDoS_ternary MyIngress.drop 0x2&&&0xff => 1"
simple_switch_CLI --thrift-port 9090 <<< "table_add MyIngress.DDoS_ternary MyIngress.drop 0x3&&&0xff => 1"

echo ">>> Configuration S1 Done. Current Rules:"
simple_switch_CLI --thrift-port 9090 <<< "table_dump MyIngress.DDoS_ternary"
