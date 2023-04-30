import random
import socket
import argparse
import struct
import heapq
import json
import threading
import datetime
import time
import sys

ROUTETRACE_PCT = b'R'
ACK_PCT = b'A'
HELLO_PCT = b'H'
LINKSTATE_PCT = b'L'

HEADER_FORMAT = '!4sH4sHHcII'
HEADER_LENGTH = struct.calcsize(HEADER_FORMAT)
topology = {}


def readtopology(topology_file):
    """
    Read the file and store a node, and it's neighbor nodes in a dictionary.
    And print it

    :param topology_file:
    :return: a dictionary containing all the interconnection
    """

    print("Topology:")
    with open(topology_file, 'r') as f:
        for line in f:
            nodes = line.strip().split()
            nodeslist = nodes[1:len(nodes)]
            topology[nodes[0]] = nodeslist
    with open(topology_file, 'r') as f:
            contents = f.read()
            print(contents)

    return topology


def dijkstra(topology, start_IP, start_port):
    """
    Store the distance between our start node and every other nodes in a dict
    eg: {'1.0.0.0,1': 0, '2.0.0.0,2': 1, '3.0.0.0,3': 1, '4.0.0.0,4': 2, '5.0.0.0,5': 2}
    Also store the next node to visit to get to each node

    :param topology: dictionary of nodes and their neighbors with costs
    :param start_IP: IP address of starting node
    :param start_port: port number of starting node
    :return: tuple of (distances, next_nodes)
    """
    start_node = start_IP + "," + str(start_port)
    # Initialize distances and next_nodes dictionaries
    distances = {node: float('inf') for node in topology}
    distances[start_node] = 0
    next_nodes = {node: None for node in topology}

    # Initialize heap with start node
    heap = [(0, start_node)]

    # Iterate over heap
    while heap:
        (current_dist, current_node) = heapq.heappop(heap)
        if current_dist > distances[current_node]:
            continue
        for neighbor in topology[current_node]:
            neighbor_dist = current_dist + 1  # Assuming all edges have weight 1
            if neighbor_dist < distances[neighbor]:
                distances[neighbor] = neighbor_dist
                next_nodes[neighbor] = current_node if distances[neighbor]!= 1 else neighbor
                heapq.heappush(heap, (neighbor_dist, neighbor))
    return distances, next_nodes


def generate_forwarding_table(topology, myIP, myPort):
    distances, next_hop = dijkstra(topology, myIP, myPort)
    table_str = "Fowarding Table: \n"
    for node, next in next_hop.items():
        table_str += node + " " + (next if next else "None") + "\n"
    return table_str

def createroutes():
    return

def forwardpacket(data):
    """
    determine whether to forward a packet and where to forward a packet received by an emulator
    in the network.

    :return:
    """
    src_ip, src_port, dst_ip, dst_port, TTL, pct_type, seq_num, length = struct.unpack(
        HEADER_FORMAT, data[:HEADER_LENGTH])

    if pct_type == ROUTETRACE_PCT:
        print()
    elif pct_type == HELLO_PCT:
        print()
    elif pct_type == LINKSTATE_PCT:
        print()

    return


def buildForwardTable():
    """
    use the forward search algorithm to compute a forwarding table based on the topology it
    collected from LinkStateMessage.

    :return:
    """
    distances, next_hop = dijkstra(topology, myIP, myPort)
    table_str = "Fowarding Table: \n"
    for node, next in next_hop.items():
        table_str += node + " " + (next if next else "None") + "\n"
    return table_str


# def send_message_periodically():
#     # Set up socket
#     s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#
#     # Send message periodically
#     while True:
#         message = b"Hello, World!"
#         s.sendto(message, (host, port))
#         time.sleep(1)  # Wait 1 second before sending next message


# def routing(packet, ftable, logfile):
#     """Routing the packet
#
#     :param packet: the packet we need to route
#     :param ftable: the forwarding table
#     :param logfile: the log file
#     :return: None
#     """
#     #print('routing')
#     # unpack the packet
#     pp, src_ip, src_port, dest_ip, dest_port, outer_len, ptype, pseq_num, plength \
#         = struct.unpack(HEADER_FORMAT, packet[:HEADER_LENGTH])
#     dest_ip = socket.gethostbyaddr(socket.inet_ntoa(dest_ip))[0]
#     parts = dest_ip.split(".")
#     dest_ip = parts[0]
#     dest_port = socket.ntohs(dest_port)
#     destination = (dest_ip, dest_port)
#     #print('routing')
#     #print(destination)
#     # check if the destination is in the forwarding table
#     if destination not in ftable:
#         print('notmatch')
#         log("NOMATCH", packet, logfile)
#         return
#     # add the packet to the queue
#     #print('routing')
#     queueing(packet, ftable, logfile)
#     return

def send_packet(packet, ftable, logfile):
    """Send the packet

    :param packet: the packet we need to send
    :param ftable: the forwarding table
    :param logfile: the log file
    :return: None
    """
    # unpack the packet
    # sock_send = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    pp, src_ip, src_port, dest_ip, dest_port, outer_len, ptype, pseq_num, plength \
        = struct.unpack(HEADER_FORMAT, packet[:26])
    dest_ip = socket.gethostbyaddr(socket.inet_ntoa(dest_ip))[0]
    parts = dest_ip.split(".")
    dest_ip = parts[0]
    dest_port = socket.ntohs(dest_port)
    destination = (dest_ip, dest_port)
    # check if the packet is lost
    if ftable[destination]['loss_probability'] > random.randint(0, 100):
        return
    # send the packet
    addr = socket.gethostbyname(ftable[destination]['next_hop'][0])
    port = ftable[destination]['next_hop'][1]
    # print(socket.ntohl(pseq_num))
    sock.sendto(packet, (addr, port))
    # print('send packet to', ftable[destination]['next_hop'])
    global packet_delay_signal
    packet_delay_signal = 0
    return


if __name__ == '__main__':
    # parse the arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--port", type=int,
                        help="the port of the emulator")
    parser.add_argument("-f", "--filename", type=str,
                        help="The name of the file containing the topology structure")

    args = parser.parse_args()

    port = args.port
    file = args.filename
    topology = readtopology(file)
    # print(topology)
    # print(json.dumps(topology, indent=4))
    # print("\n")

    # create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    myIP_name = socket.gethostname()
    myIP = socket.gethostbyname(myIP_name)
    sock.bind((myIP, port))

    # For debug, please delete
    myIP = "1.0.0.0"
    port = 1

    # Set up timer for periodic hello messages
    hello_timer = threading.Timer(3.0, lambda: s.sendto(b"Hello", (myIP, port)))

    # Keep track of nodes and last hello message time
    nodes = {}
    last_hello = {}

    # Generate the forwarding table
    forwarding_table = generate_forwarding_table(topology, myIP, port)
    print(forwarding_table)

    # # Generate the shortest path table for each node
    # generate_path_table(topology, myIP, port)


    # Start a thread to send "hello" message periodically
    # socket_thread = threading.Thread(target=send_message_periodically)
    # socket_thread.start()




    # Receive packet from network in a non-blocking way
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
    sock.setblocking(0)

    # build the forwarding table

    # Recive packet from network
