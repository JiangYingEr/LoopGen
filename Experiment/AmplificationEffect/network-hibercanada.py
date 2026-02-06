import argparse
from p4utils.mininetlib.network_API import NetworkAPI

default_rule = 'rules/'

def config_network(p4):
    net = NetworkAPI()

    # Network general options
    net.setLogLevel('info')
    net.enableCli()

    # Network definition
    net.addP4Switch('s1',cli_input= default_rule + 'hibercanada-s1.txt')
    net.addP4Switch('s2',cli_input= default_rule + 'hibercanada-s2.txt')
    net.addP4Switch('s3',cli_input= default_rule + 'hibercanada-s3.txt')
    net.addP4Switch('s4',cli_input= default_rule + 'hibercanada-s4.txt')
    net.addP4Switch('s5',cli_input= default_rule + 'hibercanada-s4.txt')
    net.addP4Switch('s6',cli_input= default_rule + 'hibercanada-s4.txt')
    net.addP4Switch('s7',cli_input= default_rule + 'hibercanada-s4.txt')
    net.addP4Switch('s8',cli_input= default_rule + 'hibercanada-s4.txt')
    net.addP4Switch('s9',cli_input= default_rule + 'hibercanada-s9.txt')

    net.setP4SourceAll(p4)

    net.addHost('h1')
    net.addHost('h2')
    net.addHost('h3')

    d = '2.1ms' #BtAsiaPac
    net.addLink('h1', 's1')
    net.addLink('h2', 's2')
    net.addLink('h3', 's3')

    net.addLink('s2', 's1', delay = d)
    net.addLink('s2', 's3', delay = d)
    net.addLink('s3', 's4', delay = d)
    net.addLink('s4', 's5', delay = d)
    net.addLink('s5', 's6', delay = d)
    net.addLink('s6', 's7', delay = d)
    net.addLink('s7', 's8', delay = d)
    net.addLink('s8', 's9', delay = d)
    net.addLink('s1', 's9', delay = d)

    # Assignment strategy
    #net.mixed()

    net.setBw('s1', 's2', bw = 10)
    net.setBw('s3', 's2', bw = 10)
    net.setBw('s4', 's3', bw = 10)
    net.setBw('s4', 's5', bw = 10)
    net.setBw('s5', 's6', bw = 10)
    net.setBw('s6', 's7', bw = 10)
    net.setBw('s7', 's8', bw = 10)
    net.setBw('s8', 's9', bw = 10)
    net.setBw('s1', 's9', bw = 10)
    #net.setBw('s1', 'h1', bw = 10)
    #net.setBw('h2', 's2', bw = 10)
    #net.setBw('s3', 'h3', bw = 10)

    net.setIntfIp('h1', 's1', ip='10.0.0.1/24')  # Nodes general options
    net.setIntfIp('h2', 's2', ip='10.0.0.2/24')
    net.setIntfIp('h3', 's3', ip='10.0.0.3/24')
    net.enableCpuPortAll()
    #net.enablePcapDumpAll()
    #net.enableLogAll()

    return net


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--p4', help='p4 src file.',
                        type=str, required=False, default='p4src/int_md.p4')

    return parser.parse_args()


def main():
    args = get_args()
    net = config_network(args.p4)
    net.startNetwork()


if __name__ == '__main__':
    main()
