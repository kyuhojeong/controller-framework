from ControllerModule import ControllerModule
from ipoplib import gen_uid


class AddressMapper(ControllerModule):

    def __init__(self, CFxHandle, paramDict):

        super(AddressMapper, self).__init__()
        self.CFxHandle = CFxHandle
        self.CMConfig = paramDict
        self.uid_ip_table = {}

    def initialize(self):

        # Populating the uid_ip_table with all the IPv4 addresses
        # and the corresponding UIDs in the /16 subnet
        parts = self.CMConfig["ip4"].split(".")
        ip_prefix = parts[0] + "." + parts[1] + "."
        for i in range(0, 255):
            for j in range(0, 255):
                ip = ip_prefix + str(i) + "." + str(j)
                uid = gen_uid(ip)
                self.uid_ip_table[uid] = ip

        logCBT = self.CFxHandle.createCBT(initiator='AddressMapper',
                                          recipient='Logger',
                                          action='info',
                                          data="AddressMapper Loaded")
        self.CFxHandle.submitCBT(logCBT)

    def processCBT(self, cbt):

        if(cbt.action == 'ADD_MAPPING'):

            try:
                # cbt.data is a dict with uid and ip keys
                self.uid_ip_table[cbt.data['uid']] = cbt.data['ip']
            except KeyError:

                logCBT = self.CFxHandle.createCBT(initiator='AddressMapper',
                                                  recipient='Logger',
                                                  action='warning',
                                                  data="Invalid ADD_MAPPING"
                                                  " Configuration")
                self.CFxHandle.submitCBT(logCBT)

        elif(cbt.action == 'DEL_MAPPING'):

            self.uid_ip_table.pop(cbt.data)  # Remove mapping if it exists

        elif(cbt.action == 'RESOLVE'):

            # Modify the CBT with the response data and send it back
            cbt.action = 'RESOLVE_RESP'

            # If mapping exists, return IP else return None
            cbt.data = self.uid_ip_table.get(cbt.data)

            # Swap inititator and recipient
            cbt.initiator, cbt.recipient = cbt.recipient, cbt.initiator

            self.CFxHandle.submitCBT(cbt)

        elif(cbt.action == 'REVERSE_RESOLVE'):

            # Modify the CBT with the response data and send it back
            cbt.action = 'REVERSE_RESOLVE_RESP'
            ip = cbt.data
            cbt.data = None
            # Iterate through all items in dict for reverse lookup
            for key, value in self.uid_ip_table.items():
                if(value == ip):
                    cbt.data = key
                    break

            # Swap inititator and recipient
            cbt.initiator, cbt.recipient = cbt.recipient, cbt.initiator

            self.CFxHandle.submitCBT(cbt)

        else:
            logCBT = self.CFxHandle.createCBT(initiator='AddressMapper',
                                              recipient='Logger',
                                              action='warning',
                                              data="AddressMapper: "
                                              "Invalid CBT received"
                                              " from " + cbt.initiator)
            self.CFxHandle.submitCBT(logCBT)

    def timer_method(self):
        pass

    def terminate(self):
        pass
