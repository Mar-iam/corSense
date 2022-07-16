import bluepy.btle as btle
from bluepy.btle import Scanner, DefaultDelegate, AssignedNumbers
import numpy


class corsense():
    def __init__(self):
        self.running = True
        self.device = None
        self.device_info = None
        self.cccid = None
        self.hrid = None
        self.hrmid = None
        self.delegate = corsense.csDelegate()
        self.plot = None

    def set_plot_func(self, func):
        self.plot = func

    def scan(self):
        scanner = Scanner().withDelegate(self.delegate)
        devices = scanner.scan()
        for dev in devices:
            # print("Device: %s (%s), RSSI=%d dB" % (dev.addr, dev.addrType, dev.rssi))
            for (adType, desc, value) in dev.getScanData():
                # print("   %s = %s" % (desc, value))
                if desc == "Short Local Name" and value == 'CorSense A-00529':
                    self.device_info = dev
                    print("CorSense has been found!")
                    return True
        return False

    def connect(self, addr=None, addr_type=None):
        if addr is None:
            addr = self.device_info.addr
            addr_type = self.device_info.addrType
        elif addr_type is None:
            addr_type = btle.ADDR_TYPE_RANDOM

        try:
            self.device = btle.Peripheral(addr, addr_type)
            print('CorSense has been connected')
            return True
        except btle.BTLEException:
            return False

    def get_corsense_services(self):
        self.cccid = AssignedNumbers.client_characteristic_configuration
        self.hrid = AssignedNumbers.heart_rate
        self.hrmid = AssignedNumbers.heart_rate_measurement

    def enable_notifications(self):
        # enable notifications for heart rate measurements
        en_notify = b"\x01\x00"
        notify = self.device.getCharacteristics(uuid=str(self.hrmid))[0]
        notify_handle = notify.getHandle() + 1

        self.device.writeCharacteristic(notify_handle, en_notify, withResponse=True)

    def initialize(self):
        if self.device is None:
            while True:
                if self.scan():
                    break

            self.connect()

        self.get_corsense_services()
        self.enable_notifications()
        self.device.withDelegate(self.delegate)

        self.run()

    def run(self):
        while self.running:
            if self.device.waitForNotifications(1.0):
                continue

        self.device.disconnect()

    def stop(self):
        self.running = False

    def rr(self):
        return self.delegate.vals

    class csDelegate(DefaultDelegate):
        def __init__(self):
            DefaultDelegate.__init__(self)
            self.vals = [0, 0]

        def handleNotification(self, data):
            self.set_vals(data)

        @staticmethod
        def get_rr(index, data):
            rr_list = []
            while index < len(data):
                rr_cur = data[index] + (data[index + 1] << 8)
                rr_cur = (float(rr_cur) / 1024) * 1000  # convert to ms
                index += 2
                rr_list.append(rr_cur)

                print('RR List: ' + str(rr_list), index)
            return rr_list

        def set_vals(self, data):
            flag = data[0]
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

            # rr_exit availability
            if flag & rr_bit != 0:
                rr_exit = True
                self.vals = self.get_rr(index, data)


            else:
                rr_exit = False


if __name__ == "__main__":
    cs = corsense()
    cs.initialize()