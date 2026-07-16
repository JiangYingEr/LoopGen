import argparse
import sys
sys.path.append('/home/p4/p4utils')
from p4utils.mininetlib.cli import P4CLI
import time
from p4utils.mininetlib.network_API import NetworkAPI

import threading

def run_command_before_start(net):
    #while True
    time.sleep(10)
    net.execScript("p4switch_stop s1", reboot = False)
    #c = P4CLI(net)
    #c.do_p4switch_stop("s1")
    with open("./test.txt", 'w') as f:
        f.write("test")
    #net.stopNetwork()


default_rule = 'rules/'

def config_network(p4):
    net = NetworkAPI()

    # Network general options
    net.setLogLevel('info')
    net.enableCli()

    #net.execScript('python3 controlloer.py s1 &', reboot=True)
    #net.execScript('python3 controlloer.py s2 &', reboot=True)
    #net.execScript('python3 controlloer.py s3 &', reboot=True)

    net.addP4Switch('s1',cli_input=default_rule + 's1.txt')
    net.addP4Switch('s2',cli_input=default_rule + 's2.txt')
    net.addP4Switch('s3',cli_input=default_rule + 's3.txt')

    net.setP4SourceAll(p4)

    net.addHost('h1')
    net.addHost('h2')
    net.addHost('h3')


    net.addLink('h1', 's1')
    net.addLink('h2', 's2')
    net.addLink('h3', 's3')

    net.addLink('s1', 's2',delay='50ms')
    net.addLink('s2', 's3',delay='50ms')
    net.addLink('s1', 's3',delay='50ms')

    net.setIntfIp('h1', "s1", "10.0.0.1/24")
    net.setIntfMac("h1", "s1", "00:00:00:00:00:01")

    net.setIntfIp("h2", "s2", "10.0.0.2/24")
    net.setIntfMac("h2", "s2", "00:00:00:00:00:02")

    net.setIntfIp("h3", "s3", "10.0.0.3/24")
    net.setIntfMac("h3", "s3", "00:00:00:00:00:03")

    # Assignment strategy
    #net.mixed()
    net.setDelayAll(50)
    # Nodes general options
    net.enableCpuPortAll()
    #net.enablePcapDumpAll()
    #net.enableLogAll()
    net.setBwAll(10)

    return net


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--p4', help='p4 src file.',
                        type=str, required=False, default='basic.p4')

    return parser.parse_args()


def main():
    args = get_args()
    net = config_network(args.p4)
    #command_thread = threading.Thread(target=run_command_before_start, args=(net,))
    #command_thread.start()
    #net.execScript("p4switch_stop s1", reboot = True)
    net.startNetwork()

    #net.startNetworkInBackground()

    #net.interact()

    #time.sleep(10)
    #c = P4CLI(net)
    #c.do_p4switch_stop("s1")
    #command_thread.join()



if __name__ == '__main__':
    main()
