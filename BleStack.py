import subprocess
import itertools
import threading


class BleScanner(threading.Thread):
    def __init__(self, process_beacon):
        threading.Thread.__init__(self)
        self.process_beacon = process_beacon
        self.active = False

    def run(self):

        # hcitool lescan --duplicates
        # hcidump --raw
        cmd_scan = "hcitool lescan --duplicates"
        subprocess.Popen(cmd_scan, shell=True, stdout=subprocess.PIPE)

        cmd_dump = "hcidump --raw"
        proc = subprocess.Popen(cmd_dump, shell=True, stdout=subprocess.PIPE)

        while self.active:
            line = proc.stdout.readline()
            if line != '':
                # print line.rstrip()
                tokens = line.split()
                if tokens[0] == '>' and tokens[6] == '00' and tokens[14] == '04':
                    mac_address = tokens[13]+":"+tokens[12]+":"+tokens[11]+":"+tokens[10]+":"+tokens[9]+":"+tokens[8]
                    ip_address = str(int(tokens[15], 16)) + "."+str(int(tokens[16], 16))\
                        + "." + str(int(tokens[17], 16)) + "."+str(int(tokens[18], 16))
                    rssi = int(tokens[19], 16)-256
                    human_name = ''
                    name_line = proc.stdout.readline()
                    if name_line != '':
                        print name_line.rstrip()
                        name_tokens = name_line.split()
                        if name_tokens[0] == '>' and name_tokens[6] == '04':
                            token_list = []
                            for token in itertools.islice(name_tokens, 17, None):
                                token_list.append(token)
                            if int(name_tokens[14], 16) > 6:
                                cnt_in_nextline = int(name_tokens[14], 16) - 6
                                name_line = proc.stdout.readline()
                                print name_line.rstrip()
                                name_tokens = name_line.split()
                                for token in itertools.islice(name_tokens, None, cnt_in_nextline):
                                    token_list.append(token)
                            elif int(name_tokens[14], 16) < 6:
                                del token_list[-1]
                            for token in token_list:
                                human_name += chr(int(token, 16))
                    self.process_beacon(mac_address, ip_address, rssi, human_name)
                elif len(tokens) >= 14 and tokens[0] == '>' and tokens[14] == '03':
                    mac_address = tokens[13]+":"+tokens[12]+":"+tokens[11]+":"+tokens[10]+":"+tokens[9]+":"+tokens[8]
                    rssi = int(tokens[18], 16)-256
                    self.process_beacon(mac_address, '', rssi, "SensorTag")


    def start(self):
        self.active = True
        super(BleScanner, self).start()

    def stop(self):
        self.active = False


def set_beacon(ip_address):
    # cmd = "hcitool -i hci0 cmd 0x08 0x0008 04 C0 A8 02 37"
    ip_tokens = ip_address.split(".")

    hex_ip_string = ''
    for token in ip_tokens:
        hex_repr = "%0.2X" % int(token)
        hex_ip_string += " " + hex_repr
        # print hex
    # print hexIpString

    cmd = "hcitool -i hci0 cmd 0x08 0x0008 04" + hex_ip_string
    # print cmd
    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    proc.wait()
    # hcitool -i hci0 cmd 0x08 0x0008 04 C0 A8 02 37


def start_beacon():
    cmd = "hciconfig hci0 leadv"
    subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)


def stop_beacon():
    cmd = "hciconfig hci0 noleadv"
    subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
