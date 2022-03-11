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

class ins401_canfd_driver:
    def __init__(self, path, json_setting):
        self.rawdata = []
        self.pkfmt = {}
        self.data_queue = Queue()
        self.id_name = {}
        self.log_files = {}
        self.path = path
        print('xxxxxxxxxxxxxxx', self.path)
        with open(json_setting) as json_data:
            self.canfd_setting = json.load(json_data)
        self.id_list = self.canfd_setting["canfd_id"]
    def receive_parse_all(self):
        print('Open BUSMUST CAN channel using 500kbps baudrate ...')
        bus = can.interface.Bus(bustype='bmcan', channel=0, bitrate=500000, data_bitrate=1000000, tres=True)
        bus.state = BusState.ACTIVE  # or BusState.PASSIVE
        print('Waiting for RX CAN messages ...')
        try:
            while True:
                msg = bus.recv(1)
                if msg is not None:
                    #print(msg)
                    #print(list(msg.data))
                    self.data_queue.put(msg)
        except KeyboardInterrupt:
            pass

    def write_titlebar(self, file, output):
        for value in output['signals']:
            print(value['name']+'('+value['unit']+')')
            file.write(value['name']+'('+value['unit']+')')
            file.write(",")
        file.write("\n")

    def log(self, output, data):
        print('lllllllllllllllllllllog')
        if output['name'] not in self.log_files.keys():
            self.log_files[output['name']] = open(self.path + '/' + output['name'] + '.csv', 'w')
            self.write_titlebar(self.log_files[output['name']], output)
        data_trans = []
        for i in range(len(data)):
            offset = float(output['signals'][i]['offset'])
            factor = float(output['signals'][i]['factor'])
            data_trans.append(data[i]*factor + offset)
        print(data_trans, len(data))
        print(data_trans[0]*9.7803267714, data_trans[1]*9.7803267714, data_trans[2]*9.7803267714)
        '''
        buffer = ''
        if output['name'] == 'INSPVAX':
            buffer = buffer + format(data[0], output['payload'][0]['format']) + ","
            buffer = buffer + format(data[1], output['payload'][1]['format']) + ","
            buffer = buffer + format(data[2], output['payload'][2]['format']) + ","
            buffer = buffer + format(data[3], output['payload'][3]['format']) + ","
            buffer = buffer + format(data[4], output['payload'][4]['format']) + ","
            buffer = buffer + format(data[5], output['payload'][5]['format']) + ","
            buffer = buffer + format(data[6], output['payload'][6]['format']) + ","
            buffer = buffer + format(data[7], output['payload'][7]['format']) + "\n"
        '''
        '''
        buffer = ''
        if output['name'] == 's1':
            buffer = buffer + format(data[0], output['payload'][0]['format']) + ","
            buffer = buffer + format(data[1], output['payload'][1]['format']) + ","
            buffer = buffer + format(data[2], output['payload'][2]['format']) + ","
            buffer = buffer + format(data[3], output['payload'][3]['format']) + ","
            buffer = buffer + format(data[4], output['payload'][4]['format']) + ","
            buffer = buffer + format(data[5], output['payload'][5]['format']) + ","
            buffer = buffer + format(data[6], output['payload'][6]['format']) + ","
            buffer = buffer + format(data[7], output['payload'][7]['format']) + "\n"

            ff_buffer = '$GPIMU,'
            ff_buffer = ff_buffer + format(data[0], output['payload'][0]['format']) + ","
            ff_buffer = ff_buffer + format(data[1], output['payload'][1]['format']) + "," + "    ,"
            ff_buffer = ff_buffer + format(data[2], output['payload'][2]['format']) + ","
            ff_buffer = ff_buffer + format(data[3], output['payload'][3]['format']) + ","
            ff_buffer = ff_buffer + format(data[4], output['payload'][4]['format']) + ","
            ff_buffer = ff_buffer + format(data[5], output['payload'][5]['format']) + ","
            ff_buffer = ff_buffer + format(data[6], output['payload'][6]['format']) + ","
            ff_buffer = ff_buffer + format(data[7], output['payload'][7]['format']) + "\n"
            self.f_process.write(ff_buffer)

            e_buffer = ''
            e_buffer = e_buffer + format(data[0], output['payload'][0]['format']) + ","
            e_buffer = e_buffer + format(data[1], output['payload'][1]['format']) + "," + "    ,"
            e_buffer = e_buffer + format(data[2], output['payload'][2]['format']) + ","
            e_buffer = e_buffer + format(data[3], output['payload'][3]['format']) + ","
            e_buffer = e_buffer + format(data[4], output['payload'][4]['format']) + ","
            e_buffer = e_buffer + format(data[5], output['payload'][5]['format']) + ","
            e_buffer = e_buffer + format(data[6], output['payload'][6]['format']) + ","
            e_buffer = e_buffer + format(data[7], output['payload'][7]['format']) + "\n"
            self.f_imu.write(e_buffer)
        '''
    def openrtk_unpack_output_packet(self, output, payload):
        fmt = self.pkfmt[output['name']]
        len_fmt = fmt['len_b']
        pack_fmt = fmt['pack']
        input('')
        print(list(payload))
        try:
            b = struct.pack(len_fmt, *payload)
            data = struct.unpack(pack_fmt, b)
            print(data)
            self.log(output, data)
        except Exception as e:
            print("error happened when decode the {0} {1}".format(output['name'], e))

    def parse_output_packet_payload(self, can_id, data):
        output = next((x for x in self.canfd_setting['messages'] if x['id'] == can_id), None)
        if output != None:
            valid_len = output["valid_len"]
            self.openrtk_unpack_output_packet(output, data[0:valid_len])
        else:
            print('no packet type {0} in json'.format(packet_type))

    def start_pasre(self):
        thread = threading.Thread(target=self.receive_parse_all)
        thread.start()
        self.canfd_id = self.canfd_setting['canfd_id']
        for inode in self.canfd_setting['messages']:
            length = 0
            pack_fmt = '>'
            print(inode["id"], inode["name"])
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
            len_fmt = '{0}B'.format(length)
            fmt_dic = collections.OrderedDict()
            fmt_dic['len'] = length
            fmt_dic['len_b'] = len_fmt
            fmt_dic['pack'] = pack_fmt
            self.pkfmt[inode['name']] = fmt_dic
        print(self.id_name)
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
