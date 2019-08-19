#!/usr/bin/python
# [pi] byte = bus.read_byte(address) -> [arduino] Wire.onRequest(handler)
import smbus as smbus
import json
import time


class I2CClient():

    def __init__(self, address):
        # for RPI version 1, use "bus = smbus.SMBus(0)"
        self.bus = smbus.SMBus(1)
        self.address = address

    def __read(self, action):
        return self.bus.read_i2c_block_data(self.address, action)

    def __write(self, action, data):
        return self.bus.write_i2c_block_data(self.address, action, data)

    def __divide_chunks(self, l, n):
        # looping till length l
        for i in range(0, len(l), n):
            yield l[i:i + n]

    def long_receice(self, actionWrite, actionRead):
        self.__write(actionWrite, [1, 1])
        time.sleep(0.5)  # Seconds
        data = self.__read(actionRead)
        part, of = data[:2]
        body = data[2:]
        while part != of:
            part += 1
            self.__write(actionWrite, [part, of])
            time.sleep(0.5)  # Seconds
            data = self.__read(actionRead)
            body += data[2:]
        return body

    def receice(self, action):
        data = self.__read(action)
        return data[2:]

    def send(self, action, body):
        data_bytes = list(body.encode())
        data_bytes = list(self.__divide_chunks(data_bytes, 29))
        of = len(data_bytes)
        for i in range(of):
            part = i + 1
            data = [part, of] + data_bytes[i]
            self.write(action, data)
            time.sleep(0.5)  # Seconds


class GSMClient(I2CClient):
    ACTION_CALL = 1
    ACTION_ANSWER = 2
    ACTION_HANGOFF = 3
    ACTION_SEND_SMS = 4
    ACTION_GET_SMS = 5
    ACTION_DEL_SMS = 6
    ACTION_GET_LOC = 7
    ACTION_GET_STA = 10  # STATUS

    RESPONSE_CALL = 11
    RESPONSE_ANSWER = 12
    RESPONSE_HANGOFF = 13
    RESPONSE_SEND_SMS = 14
    # RESPONSE_GET_SMS = 15
    RESPONSE_DEL_SMS = 16
    # RESPONSE_GET_LOC = 17
    # RESPONSE_GET_STA = 20

    GENERIC_WRITE = 30
    GENERIC_READ = 31

    def get_status(self):
        self.send(self.ACTION_GET_STA, '')
        time.sleep(1)
        return self.long_receice(self.GENERIC_WRITE, self.GENERIC_READ)

    def make_call(self, number):
        body = json.dumps({'n': number}, separators=(',', ':'))
        self.send(self.ACTION_CALL, body)
        time.sleep(5)
        return self.receice(self.RESPONSE_CALL)

    def answer_call(self, number):
        self.send(self.ACTION_ANSWER, '')
        time.sleep(5)
        return self.receice(self.RESPONSE_ANSWER)

    def hangoff_call(self, number):
        self.send(self.ACTION_HANGOFF, '')
        time.sleep(5)
        return self.receice(self.RESPONSE_HANGOFF)

    def send_sms(self, number, msg):
        body = json.dumps(
            {'n': number, 'b': msg},
            separators=(',', ':'))
        self.send(self.ACTION_SEND_SMS, body)
        time.sleep(20)
        return self.receice(self.RESPONSE_SEND_SMS)

    def get_sms(self, index):
        body = json.dumps(
            {'i': index},
            separators=(',', ':'))
        self.send(self.ACTION_GET_SMS, body)
        time.sleep(5)
        return self.long_receice(self.GENERIC_WRITE, self.GENERIC_READ)

    def delete_smss(self, number):
        self.send(self.ACTION_DEL_SMS, '')
        time.sleep(20)
        return self.receice(self.RESPONSE_HANGOFF)

    def get_localization(self):
        self.send(self.ACTION_GET_LOC, '')
        time.sleep(60)
        return self.long_receice(self.GENERIC_WRITE, self.GENERIC_READ)
