import argparse
from p4utils.mininetlib.network_API import NetworkAPI

default_rule = 'rules/'

def config_network(p4):
    net = NetworkAPI()

    # Network general options
    net.setLogLevel('info')
    net.enableCli()

    # Network definition
    net.addP4Switch('s1',cli_input= default_rule + 's1-commands.txt')
    net.addP4Switch('s2',cli_input= default_rule + 's2-commands.txt')
    net.addP4Switch('s3',cli_input= default_rule + 's3-commands.txt')

    net.setP4SourceAll(p4)

    net.addHost('h1')
    net.addHost('h2')
    net.addHost('h3')

    d = '0ms' #BtAsiaPac
    net.addLink('h1', 's1')
    net.addLink('h2', 's2')
    net.addLink('h3', 's3')
    net.addLink('s2', 's3', delay = d)
    net.addLink('s1', 's3', delay = d)
    net.addLink('s2', 's1', delay = d)

    # Assignment strategy
    #net.mixed()

    net.setBw('s1', 's2', bw = 10)
    net.setBw('s3', 's2', bw = 10)
    net.setBw('s1', 's3', bw = 10)
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
                        type=str, required=False, default='basic.p4')

    return parser.parse_args()


def main():
    args = get_args()
    net = config_network(args.p4)
    net.startNetwork()


if __name__ == '__main__':
    main()
