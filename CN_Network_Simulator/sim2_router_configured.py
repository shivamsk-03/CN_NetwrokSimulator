import time

class Hub:
    def __init__(self):
        self.connectedDevices = []
        self.connectedSwitches = []
        self.connectedBridges = []
        self.tokenAvailable = True

    def connectDevice(self, device):
        self.connectedDevices.append(device)
        device.connectToHub(self)

    def connectSwitch(self, switch):
        self.connectedSwitches.append(switch)
        switch.connectToHub(self)

    def connectBridge(self, bridge):
        self.connectedBridges.append(bridge)
        bridge.connectToHub(self)

    def broadcastMessage(self, sender, receiver, message):
        print("---- Broadcasting Message via Hub ----")
        for device in self.connectedDevices:
            if device == receiver:
                device.receiveMessage(message)
            else:
                device.receiveMessage("Message rejected: " + message)

        relayedSwitches = []
        for switch in self.connectedSwitches:
            if switch.isPortConnected(sender) and switch.isPortConnected(receiver):
                if self.tokenAvailable and switch.hasToken():
                    switch.relayMessage(sender, receiver, message)
                    relayedSwitches.append(switch)
                else:
                    print("Token not available in the switch.")

        if not relayedSwitches:
            print("Message rejected in the switch.")

        for bridge in self.connectedBridges:
            if bridge.isDeviceConnected(sender) and bridge.isDeviceConnected(receiver):
                bridge.relayMessage(sender, receiver, message)
            else:
                print("Message rejected in the bridge.")

    def passToken(self):
        self.tokenAvailable = True
        print("Token passed to the next device.")


class Device:
    def __init__(self, id, ipAddress):
        self.id = id
        self.ipAddress = ipAddress
        self.hub = None
        self.hasReceivedMessage = False

    def sendMessage(self, receiver, message, flow_control):
        if flow_control == '1':
            self.sendStopAndWaitMessage(receiver, message)
        elif flow_control == '2':
            self.sendSlidingWindowMessage(receiver, message)
        else:
            print("Invalid flow control protocol.")

    def sendStopAndWaitMessage(self, receiver, message):
        self.hasReceivedMessage = False
        print("---- Stop-and-Wait Protocol ----")
        print("Sending message:", message)
        print("Receiver:", receiver.id)
        receiver.receiveMessage(message)
        while not self.hasReceivedMessage:
            print("Waiting for ACK...")
            time.sleep(1)
            self.receiveStopAndWaitAck()

    def sendSlidingWindowMessage(self, receiver, message):
        self.hasReceivedMessage = False
        print("---- Sliding Window Protocol ----")
        print("Sending message:", message)
        print("Receiver:", receiver.id)
        receiver.receiveMessage(message)
        while not self.hasReceivedMessage:
            print("Waiting for ACK...")
            time.sleep(1)
            self.receiveSlidingWindowAck()

    def receiveMessage(self, message):
        self.hasReceivedMessage = True
        print("Device", self.id, "received message:", message)

    def receiveStopAndWaitAck(self):
        print("ACK received.")
        self.hasReceivedMessage = True

    def receiveSlidingWindowAck(self):
        print("ACK received.")
        self.hasReceivedMessage = True

    def connectToHub(self, hub):
        self.hub = hub

    def getId(self):
        return self.id

    def hasReceived(self):
        return self.hasReceivedMessage


class Switch:
    def __init__(self, id):
        self.id = id
        self.connectedPorts = []
        self.hub = None
        self.tokenAvailable = False

    def connectPort(self, port):
        self.connectedPorts.append(port)

    def connectToHub(self, hub):
        self.hub = hub

    def isPortConnected(self, device):
        for port in self.connectedPorts:
            if port.getConnectedDevice() == device:
                return True
        return False

    def hasToken(self):
        return self.tokenAvailable

    def relayMessage(self, sender, receiver, message):
        relayed = False
        for port in self.connectedPorts:
            if port.getConnectedDevice() == receiver:
                port.getConnectedDevice().receiveMessage("[Relayed] " + message)
                relayed = True
        if not relayed:
            print("Message rejected in the switch.")

        for port in self.connectedPorts:
            if port.getConnectedDevice() != receiver and port.getConnectedDevice() != sender:
                port.getConnectedDevice().receiveMessage("Message rejected: " + message)

        self.tokenAvailable = False


class Port:
    def __init__(self, connectedDevice):
        self.connectedDevice = connectedDevice

    def getConnectedDevice(self):
        return self.connectedDevice


class Bridge:
    def __init__(self, id):
        self.id = id
        self.connectedDevices = []
        self.hub = None

    def connectDevice(self, device):
        self.connectedDevices.append(device)

    def connectToHub(self, hub):
        self.hub = hub

    def isDeviceConnected(self, device):
        return device in self.connectedDevices

    def relayMessage(self, sender, receiver, message):
        for device in self.connectedDevices:
            if device == receiver:
                device.receiveMessage("[Relayed] " + message)
            else:
                device.receiveMessage("Message rejected: " + message)


class Router:
    def __init__(self):
        self.routingTable = {}

    def addRoute(self, destination, switch):
        self.routingTable[destination] = switch

    def getRoutingTable(self):
        return self.routingTable


# Create devices
device1 = Device(1, "192.168.0.1")
device2 = Device(2, "192.168.0.2")
device3 = Device(3, "192.168.0.3")
device4 = Device(4, "192.168.0.4")
device5 = Device(5, "192.168.0.5")

# Create switch
switch = Switch(1)

# Create bridge
bridge = Bridge(1)

# Create hub
hub = Hub()

# Create router
router = Router()

# Add routes to the router
router.addRoute("192.168.0.1", switch)
router.addRoute("192.168.0.2", switch)
router.addRoute("192.168.0.3", switch)
router.addRoute("192.168.0.4", switch)
router.addRoute("192.168.0.5", switch)

# Connect devices to hub
hub.connectDevice(device1)
hub.connectDevice(device2)
hub.connectDevice(device3)
hub.connectDevice(device4)
hub.connectDevice(device5)

# Connect switch to hub
hub.connectSwitch(switch)

# Connect bridge to hub
hub.connectBridge(bridge)

# Connect devices to switch
switch.connectPort(Port(device1))
switch.connectPort(Port(device2))
switch.connectPort(Port(device3))
switch.connectPort(Port(device4))
switch.connectPort(Port(device5))

# Simulate broadcasting message via hub
print("---- Broadcasting Message via Hub ----")
print("Available devices: 1, 2, 3, 4, 5")
senderId = int(input("Enter sender device ID: "))
receiverId = int(input("Enter receiver device ID: "))
message = input("Enter message: ")

sender = None
receiver = None

for device in hub.connectedDevices:
    if device.getId() == senderId:
        sender = device
    if device.getId() == receiverId:
        receiver = device

if sender is not None and receiver is not None:
    hub.broadcastMessage(sender, receiver, message)
else:
    print("Invalid device ID.")

# Display routing table
print("---- Routing Table ----")
routingTable = router.getRoutingTable()
for destination, switch in routingTable.items():
    print("Destination:", destination, "Switch:", switch.id)
