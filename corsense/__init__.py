from bluepy.btle import *

class csDelegate(DefaultDelegate):
    def __init__(self):
        DefaultDelegate.__init__(self)

    def handleNotification(self, cHandle, packet):
        data = self.convert_to_integer(packet)
        flag = data[0]
        self.check_data_format(flag, data)

    @staticmethod
    def convert_to_integer(d):
        return [ord(d[i]) for i in range(len(d))]

    @staticmethod
    def check_data_format(flag, data):
        uint8_bit = 0
        rr_bit = 16  # in decimal - 00010000 (5th bit)
        ee_bit = 8  # in decimal - 00001000 (4th bit)
        index = 0

        # HR format
        if flag & uint8_bit == 0:
            # hr_value = data[1]
            index += 2
            uint8 = True

        else:
            index += 1
            uint8 = False

        # ee_exit availability
        if flag & ee_bit != 0:
            # ee_value = data[index] + (data[index + 1] << 8)
            index += 2

        rr_list = []

        # rr_exit availability
        if flag & rr_bit != 0:

            rr_exit = True
            while index < len(data):
                rr_value = data[index] + (data[index + 1] << 8)
                rr_value = (float(rr_value) / 1024) * 1000  # convert to ms
                index += 2
                rr_list.append(rr_value)
                print('RR List: ' + str(rr_list))
        else:
            rr_exit = False


class corSense:
    def __init__(self):
        # TODO: search for the correct ID based on corSense name
        self.per = Peripheral("08:7c:be:cd:32:28", ADDR_TYPE_PUBLIC)

    def retrieveUUID(self):
        self.cccid = AssignedNumbers.client_characteristic_configuration
        self.hrid = AssignedNumbers.heart_rate
        self.hrmid = AssignedNumbers.heart_rate_measurement


cs = corSense()
print(type(cs.per))
# cs = Peripheral("08:7c:be:cd:32:28", ADDR_TYPE_PUBLIC)

# debug
print("CorSense has been connected")

# Retrieve required UUID
cs.retrieveUUID()

try:
    # set callback for notifications
    cs.per.setDelegate(csDelegate())

    # enable notifications for heart rate measurements
    en_notify = b"\x01\x00"
    notify = cs.per.getCharacteristics(uuid=str(cs.hrmid))[0]
    notify_handle = notify.getHandle() + 1

    cs.per.writeCharacteristic(notify_handle, en_notify, withResponse=True)

    while True:
        if cs.per.waitForNotifications(2):
            continue

finally:
    cs.per.disconnect()

