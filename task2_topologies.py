#!/usr/bin/env python3
import sys
from mininet.net import Mininet
from mininet.cli import CLI
from mininet.node import RemoteController, OVSKernelSwitch
from mininet.topo import Topo
from mininet.topolib import TreeTopo
from mininet.log import setLogLevel, info

class Single13HostsTopo(Topo):
    def build(self, **_opts):
        switch = self.addSwitch('s1')
        for i in range(1, 14):
            host = self.addHost(f'h{i}')
            self.addLink(host, switch)

class Linear10Topo(Topo):
    def build(self, **_opts):
        previous_switch = None

        for i in range(1, 11):
            switch = self.addSwitch(f's{i}')
            host = self.addHost(f'h{i}')

            self.addLink(host, switch)

            if previous_switch is not None:
                self.addLink(previous_switch, switch)

            previous_switch = switch

def create_tree_topology():
    return TreeTopo(depth=4, fanout=5)

def run_topology(topo_type):
    if topo_type == 'single':
        topo = Single13HostsTopo()
        info('*** Criando topologia SINGLE com 13 hosts\n')
    elif topo_type == 'linear':
        topo = Linear10Topo()
        info('*** Criando topologia LINEAR com 10 switches e 10 hosts\n')
    elif topo_type == 'tree':
        topo = create_tree_topology()
        info('*** Criando topologia TREE com depth=4 e fanout=5\n')
    else:
        raise ValueError("Topo inválida. Use: single | linear | tree")

    net = Mininet(
    topo=topo,
    controller=None,
    switch=OVSKernelSwitch,
    autoSetMacs=True,
    autoStaticArp=True,
    build=False   
    )


    info('*** Adicionando controlador remoto (ONOS) em 127.0.0.1:6653\n')

    c0 = net.addController(
        'c0',
        controller=RemoteController,
        ip='127.0.0.1',
        port=6653
    )

    info('*** Construindo rede\n')
    net.build()

    info('*** Iniciando controlador e switches\n')
    c0.start()
    net.start()

    info('*** Configurando switches para OpenFlow13\n')
    for sw in net.switches:
        sw.cmd('ovs-vsctl set Bridge', sw.name, 'protocols=OpenFlow13')

    info('*** Testando conectividade\n')

    if topo_type == 'tree':
        info('*** Testando conectividade parcial (3 testes apenas)\n')
        h1 = net.get('h1')
        h312 = net.get('h312')
        h625 = net.get('h625')

        net.ping([h1, h312])
        net.ping([h1, h625])
        net.ping([h312, h625])
    else:
        info('*** Executando pingAll() completo\n')
        net.pingAll()

    info('*** Rede em execução. Use comandos no ONOS (devices, flows, hosts)\n')
    info('*** e o CLI do Mininet para testes adicionais.\n')

    CLI(net)

    info('*** Parando a rede\n')
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')

    if len(sys.argv) != 2:
        print("Uso: sudo python3 task2_topologies.py [single|linear|tree]")
        sys.exit(1)

    topology_type = sys.argv[1].lower()
    run_topology(topology_type)
