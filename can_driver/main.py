#!/usr/bin/env python

from __future__ import print_function

import can
from can.bus import BusState
import sys
from queue import Queue
import os
import argparse
import time
from time import sleep
import datetime
import collections
import struct
import json
import math
import threading
import signal
from ntrip import NTRIPClient
from core import EventBase
import time

class ins401_canfd_driver(EventBase):
    def __init__(self, path, json_setting):
        self.rawdata = []
        self.pkfmt = {}
        self.data_queue = Queue()
        self.id_name = {}
        self.log_files = {}
        self.path = path
        self.bus = can.interface.Bus(bustype='bmcan', channel=0, bitrate=500000, data_bitrate=1000000, tres=True)
        self.bus.state = BusState.ACTIVE
        time.sleep(0.1)
        self.bus = can.interface.Bus(bustype='bmcan', channel=0, bitrate=500000, data_bitrate=1000000, tres=True)
        self.bus.state = BusState.ACTIVE
        time.sleep(0.1)
        self.bus = can.interface.Bus(bustype='bmcan', channel=0, bitrate=500000, data_bitrate=1000000, tres=True)        
        self.bus.state = BusState.ACTIVE
        time.sleep(0.1)
        '''
        print('xxxxxxxxxxxxxxxxxxxxxx', dir(self.bus))
        msg = can.Message(arbitration_id=0x508,
                          data=[0, 25, 0, 1, 3, 1, 4, 1],
                          is_extended_id=False)

        try:
            self.bus.send(msg, timeout=None)
            print("Message sent on {}".format(self.bus.channel_info))
        except can.CanError:
            print("Message NOT sent")        
        '''
        
        with open(json_setting) as json_data:
            self.canfd_setting = json.load(json_data)
        self.id_list = self.canfd_setting["canfd_id"]
    def receive_parse_all(self):
        print('open BUSMUST CAN channel using 500&1000kbps baudrate ...')

        #self.bus.state = BusState.ACTIVE  # or BusState.PASSIVE
        print('waiting for RX CAN messages ...')
        try:
            while True:
                msg = self.bus.recv(1)
                if msg is not None:
                    self.data_queue.put(msg)
        except KeyboardInterrupt:
            pass

    def write_titlebar(self, file, output):
        for value in output['signals']:
            #print(value['name']+'('+value['unit']+')')
            file.write(value['name']+'('+value['unit']+')')
            file.write(",")
        file.write("\n")

    def log(self, output, data):
        if output['name'] not in self.log_files.keys():
            fname_time = time.strftime("%Y_%m_%d_%H_%M_%S", time.localtime()) + '_'
            self.log_files[output['name']] = open(self.path + '/' + fname_time + output['name'] + '.csv', 'w')
            self.write_titlebar(self.log_files[output['name']], output)
        data_trans = []
        for i in range(len(data)):
            try:
                if output['signals'][i]['is_float'] == True:
                    offset = float(output['signals'][i]['offset'])
                    factor = float(output['signals'][i]['factor'])
                else:
                    offset = int(output['signals'][i]['offset'])
                    factor = int(output['signals'][i]['factor'])
            except Exception as e:
                print(e, output['is_float'], type(output['is_float']))
            data_trans.append(data[i]*factor + offset)

        #print(len(output['signals']), len(data_trans), len(data))
        buffer = ''
        if output['name'] == 'INSPVAX':
            buffer = buffer + format(data_trans[0]*9.7803267714, output['signals'][0]['format']) + ","
            buffer = buffer + format(data_trans[1]*9.7803267714, output['signals'][1]['format']) + ","
            buffer = buffer + format(data_trans[2]*9.7803267714, output['signals'][2]['format']) + ","
            buffer = buffer + format(data_trans[3], output['signals'][3]['format']) + ","
            buffer = buffer + format(data_trans[4], output['signals'][4]['format']) + ","
            buffer = buffer + format(data_trans[5], output['signals'][5]['format']) + ","
            buffer = buffer + format(data_trans[6], output['signals'][6]['format']) + ","
            buffer = buffer + format(data_trans[7], output['signals'][7]['format']) + ","
            buffer = buffer + format(data_trans[8], output['signals'][8]['format']) + ","
            buffer = buffer + format(data_trans[9], output['signals'][9]['format']) + ","
            buffer = buffer + format(data_trans[10], output['signals'][10]['format']) + ","
            buffer = buffer + format(data_trans[11], output['signals'][11]['format']) + ","
            buffer = buffer + format(data_trans[12], output['signals'][12]['format']) + ","
            buffer = buffer + format(data_trans[13], output['signals'][13]['format']) + ","
            buffer = buffer + format(data_trans[14], output['signals'][14]['format']) + ","
            buffer = buffer + format(data_trans[15], output['signals'][15]['format']) + ","
            buffer = buffer + format(data_trans[16], output['signals'][16]['format']) + ","            
            buffer = buffer + format(data_trans[17], output['signals'][17]['format']) + ","            
            buffer = buffer + format(data_trans[18], output['signals'][18]['format']) + ","            
            buffer = buffer + format(data_trans[19], output['signals'][19]['format']) + ","            
            buffer = buffer + format(data_trans[20], output['signals'][20]['format']) + ","            
            buffer = buffer + format(data_trans[21], output['signals'][21]['format']) + ","            
            buffer = buffer + format(data_trans[22], output['signals'][22]['format']) + ","
            buffer = buffer + format(data_trans[23], output['signals'][23]['format']) + ","
            buffer = buffer + format(data_trans[24], output['signals'][24]['format']) + ","
            buffer = buffer + format(data_trans[25], output['signals'][25]['format']) + "\n"              

        self.log_files[output['name']].write(buffer)

    def openrtk_unpack_output_packet(self, output, payload):
        fmt = self.pkfmt[output['name']]
        len_fmt = fmt['len_b']
        pack_fmt = fmt['pack']
        #print(list(payload))
        try:
            b = struct.pack(len_fmt, *payload)
            data = struct.unpack(pack_fmt, b)
            # print('time: ',data[10])
            self.log(output, data)
        except Exception as e:
            print("error happened when decode the {0} {1}".format(output['name'], e))

    def parse_output_packet_payload(self, can_id, data):
        output = next((x for x in self.canfd_setting['messages'] if x['id'] == can_id), None)
        if output != None:
            valid_len = output["valid_len"]
            data_hex = [hex(ele) for ele in data]
            
            self.openrtk_unpack_output_packet(output, data[0:valid_len])
        else:
            print('no packet type {0} in json'.format(packet_type))

    def start_pasre(self):
        thread = threading.Thread(target=self.receive_parse_all)
        thread.start()
        thead = threading.Thread(target=self.ntrip_client_thread)
        thead.start()
        self.canfd_id = self.canfd_setting['canfd_id']
        for inode in self.canfd_setting['messages']:
            length = 0
            pack_fmt = '>'
            self.id_name[inode["id"]] = inode["name"]
            for value in inode['signals']:
                if value['type'] == 'float':
                    pack_fmt += 'f'
                    length += 4
                elif value['type'] == 'uint32':
                    pack_fmt += 'I'
                    length += 4
                elif value['type'] == 'int32':
                    pack_fmt += 'i'
                    length += 4
                elif value['type'] == 'int16':
                    pack_fmt += 'h'
                    length += 2
                elif value['type'] == 'uint16':
                    pack_fmt += 'H'
                    length += 2
                elif value['type'] == 'double':
                    pack_fmt += 'd'
                    length += 8
                elif value['type'] == 'int64':
                    pack_fmt += 'q'
                    length += 8
                elif value['type'] == 'uint64':
                    pack_fmt += 'Q'
                    length += 8
                elif value['type'] == 'char':
                    pack_fmt += 'c'
                    length += 1
                elif value['type'] == 'uchar':
                    pack_fmt += 'B'
                    length += 1
                elif value['type'] == 'uint8':
                    pack_fmt += 'B'
                    length += 1
                else:
                    pass
            len_fmt = '{0}B'.format(length)
            fmt_dic = collections.OrderedDict()
            fmt_dic['len'] = length
            fmt_dic['len_b'] = len_fmt
            fmt_dic['pack'] = pack_fmt
            self.pkfmt[inode['name']] = fmt_dic
        while True:
            if self.data_queue.empty():
                time.sleep(0.001)
                continue
            else:
                #'arbitration_id', 'bitrate_switch', 'channel', 'data', 'dlc', 'equals', 'error_state_indicator', 'id_type', 'is_error_frame', 'is_extended_id', 'is_fd', 'is_remote_frame', 'timestamp
                data = self.data_queue.get()
                #print(data.arbitration_id, data.dlc)
                if data.arbitration_id in self.id_list:
                    self.parse_output_packet_payload(data.arbitration_id, data.data)

    def ntrip_client_thread(self):
        self.ntrip_client = NTRIPClient(self.canfd_setting)
        self.ntrip_client.on('base', self.send_base_data)
        self.ntrip_client.run()

    def send_base_data(self, data):
        base_data = list(data)
        all_data_len = len(base_data)
        len_base_data = all_data_len
        index = 0
        data_to_send = [0 for i in range(64)]
        while all_data_len > 0:
            if all_data_len < 62:
                data_len = len_base_data - index
                data_len_l = data_len & 0xff
                data_len_h = (data_len >> 8) & 0xff
                # data_len = struct.pack('>BB', all_data_len - index)
                data_to_send[0:2] = [data_len_h, data_len_l]
                data_to_send[2:] = base_data[index:]
                #data_to_send = base_data[index:]
            else:
                data_len = 62
                data_len_l = data_len & 0xff
                data_len_h = (data_len >> 8) & 0xff
                data_to_send[0:2] = [data_len_h, data_len_l]
                data_to_send[2:] = base_data[index:index+62]
            msg = can.Message(arbitration_id=0x508,
                              data=data_to_send,
                              is_extended_id=False,
                              is_fd=True)
            try:
                self.bus.send(msg, timeout=None)

            except can.CanError:
                print("message cant sent")
            pass
            all_data_len-= 62
            index+= 62
            #print(data_to_send)
            sys.stdout.write("\rsend base data len {0}".format(len_base_data))
            #print('test', len(base_data), all_data_len, index)


def mkdir(file_path):
    if not os.path.exists(file_path):
        os.makedirs(file_path)

def get_utc_day():
	year = int(time.strftime("%Y"))
	month = int(time.strftime("%m"))
	day = int(time.strftime("%d"))
	hour = int(time.strftime("%H"))
	minute = int(time.strftime("%M"))
	second = int(time.strftime("%S"))
	local_time = datetime.datetime(year, month, day, hour, minute, second)
	time_struct = time.mktime(local_time.timetuple())
	utc_st = datetime.datetime.utcfromtimestamp(time_struct)
	
	d1 = datetime.datetime(year, 1, 1)
	utc_sub = utc_st - d1
	utc_str = utc_sub.__str__()
	utc_day_int = int(utc_str.split( )[0])
	utc_day_str = str(utc_day_int + 1)
	return utc_day_str

def kill_app(signal_int, call_back):
    '''Kill main thread
    '''
    os.kill(os.getpid(), signal.SIGTERM)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        json_config = "ins_canfd.json"
    else:
        json_config = sys.argv[1]
    signal.signal(signal.SIGINT, kill_app)
    day = get_utc_day()
    mkpath='./' + day
    path = mkdir(mkpath)    
    canfd_parser = ins401_canfd_driver(mkpath, json_config)
    canfd_parser.start_pasre()
