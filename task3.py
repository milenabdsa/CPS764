#!/usr/bin/env python3

import sys
import argparse
from mininet.net import Mininet
from mininet.cli import CLI
from mininet.node import RemoteController, OVSKernelSwitch
from mininet.topo import Topo
from mininet.topolib import TreeTopo
from mininet.log import setLogLevel, info

class SingleTopo(Topo):
    def __init__(self, hosts=2, **opts):
        self.num_hosts = hosts
        super().__init__(**opts)

    def build(self, **_opts):
        switch = self.addSwitch('s1')
        for i in range(1, self.num_hosts + 1):
            host = self.addHost(f'h{i}')
            self.addLink(host, switch)

class LinearTopo(Topo):
    def __init__(self, length=2, **opts):
        self.length = length
        super().__init__(**opts)

    def build(self, **_opts):
        previous_switch = None
        for i in range(1, self.length + 1):
            switch = self.addSwitch(f's{i}')
            host = self.addHost(f'h{i}')
            self.addLink(host, switch)
            if previous_switch is not None:
                self.addLink(previous_switch, switch)
            previous_switch = switch

def create_tree_topology(depth, fanout):
    return TreeTopo(depth=depth, fanout=fanout)

def quick_tests(net, topo_type, args):
    if topo_type == 'single':
        try:
            h1, h2 = net.get('h1', 'h2')
            net.ping([h1, h2])
        except KeyError:
            pass
    elif topo_type == 'linear':
        try:
            h1 = net.get('h1')
            h_last = net.get(f'h{args.length}')
            net.ping([h1, h_last])
        except KeyError:
            pass
    elif topo_type == 'tree':
        if len(net.hosts) >= 2:
            h1 = net.hosts[0]
            h_last = net.hosts[-1]
            net.ping([h1, h_last])

def run_topology(args):
    topo_type = args.type

    if topo_type == 'single':
        topo = SingleTopo(hosts=args.hosts)
    elif topo_type == 'linear':
        topo = LinearTopo(length=args.length)
    elif topo_type == 'tree':
        topo = create_tree_topology(depth=args.depth, fanout=args.fanout)
    else:
        raise ValueError("Tipo inválido")

    net = Mininet(
        topo=topo,
        controller=None,
        switch=OVSKernelSwitch,
        autoSetMacs=True,
        autoStaticArp=True,
        build=False
    )

    c0 = net.addController(
        'c0',
        controller=RemoteController,
        ip='127.0.0.1',
        port=6653
    )

    net.build()
    c0.start()
    net.start()

    for sw in net.switches:
        sw.cmd('ovs-vsctl set Bridge', sw.name, 'protocols=OpenFlow13')

    quick_tests(net, topo_type, args)

    CLI(net)
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')

    parser = argparse.ArgumentParser()
    parser.add_argument('--type', choices=['single', 'linear', 'tree'], required=True)
    parser.add_argument('--hosts', type=int, default=13)
    parser.add_argument('--length', type=int, default=10)
    parser.add_argument('--depth', type=int, default=4)
    parser.add_argument('--fanout', type=int, default=5)

    args = parser.parse_args()
    run_topology(args)
