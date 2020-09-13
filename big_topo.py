#!/usr/bin/python

from threading import Thread
from mininet.net import Mininet
from mininet.node import Controller, RemoteController, UserSwitch
from mininet.cli import CLI
from mininet.link import Intf, TCULink
from mininet.log import setLogLevel, info
from mininet.topo import Topo
from mininet.clean import cleanup
from time import sleep
import argparse, traceback

HOSTS = 11

class Project(Topo):
    def __init__(self):
        Topo.__init__(self)



        hosts = dict()

        for i in range(HOSTS):
            h = 'h' + str(i+1)
            s = 's' + str(i+1)
            hosts[h] = self.addHost(h)
            hosts[s] = self.addSwitch(s)
            self.addLink(h, s, cls=TCULink)

        self.addLink(hosts['h1'], hosts['s1'], cls=TCULink)

        for i in range(HOSTS-1):
            self.addLink(hosts['s' + str(i+2)], hosts['s1'], cls=TCULink)

def start_server(server):
    pass
    #server.sendCmd('python3 server.py')

def start_client(client, index):
    client.sendCmd('tcpreplay -i h%s-eth0 -l 0 client%s.pcap' % (index, index))
    print(client.waiting)


if __name__ == '__main__':
    setLogLevel('info')

    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--manual", help="manual mininet", action="store_true")
    args = parser.parse_args()

    ryu = RemoteController('ame', ip='172.16.100.9', port=6633)

    try:
        all_set = False

        while not all_set:
            topo = Project()
            cleanup()
            net = Mininet(
                topo=topo,
                controller=ryu,
                switch=UserSwitch,
                autoSetMacs=True,
            )
            print("------- RESTARTANDO: ")
            net.start()
            response = net.waitConnected(3)
            print ("------- CONECTADOS: ", response)
            ryu.start()
            percentage = net.pingAll()
            response = net.waitConnected(3)
            percentage = net.pingAll()
            print("------- CONECTADOS: ", response)
            if response or int(percentage) == 0:
                print ("------- PORCENTAGEM DE PING: ", response)
                all_set = True
            else:
                net.stop()
                cleanup()
                print('-------- PARANDO O RYU')
                ryu.stop()


        clients = []
        server = net.getNodeByName('h1')
        server.setMAC('00:00:00:00:00:01')

        if not args.manual:
            start_server(server)
            for i in range(1, HOSTS):
                start_client(
                    net.getNodeByName(
                        'h' + str(i+1)
                    ),
                    str(i+1)
                )


    except Exception as e:
        print("Houve um erro, stopando...", traceback.printexc())
        net.stop()

    try:
        while net.getNodeByName('h2').waiting:
            sleep(5)
            print('Running.')
    except:
        net.stop()

    if args.manual:
        CLI(net)

    cleanup()

    #CLI(net)
#
    #net.stop()

# Allows the file to be imported using `mn --custom <filename> --topo minimal`
topos = {
    'mytopo': Project
}
