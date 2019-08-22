#!/usr/bin/python
# [pi] byte = bus.read_byte(address) -> [arduino] Wire.onRequest(handler)
import smbus2 as smbus
import json
import time


class TooManyAttempt(Exception):
    def __init__(self, message):
        super().__init__(message)


class I2CClient():

    def __init__(self, address):
        # for RPI version 1, use "bus = smbus.SMBus(0)"
        self.bus = smbus.SMBus(1)
        self.address = address

    def __read(self, action):
        return self.bus.read_i2c_block_data(self.address, action, 32)

    def __write(self, action, data):
        return self.bus.write_i2c_block_data(self.address, action, data)

    def __divide_chunks(self, l, n):
        # looping till length l
        for i in range(0, len(l), n):
            yield l[i:i + n]

    def __part_receive(self, action_write, action_read,
                       part, of, attempt=10, interval=0.25):
        self.__write(action_write, [part, of])
        time.sleep(0.2)  # Seconds
        n = 1
        while n <= attempt:
            data = self.__read(action_read)
            part, of = data[:2]
            data = data[2:]
            body = ""
            for byte in data:
                if byte == 255:
                    break
                body += chr(byte)
            try:
                json_data = json.loads(body.replace('\x00', ''), strict=False)
                if 's' in json_data and json_data['s'] == 'no_end':
                    n += 1
                    time.sleep(interval)
                    continue
            except:
                print ("Body:")
                print (body)
                # No es una respuesta completa, eso quiere decir que esta bien
                pass
            return part, of, body
        raise TooManyAttempt('Too many attempt waiting')

    def long_receive(self, action_write, action_read,
                     attempt=10, interval=0.25):
        part, of, body_str = self.__part_receive(
            action_write, action_read, 1, 1,
            attempt, interval)
        while part != of:
            print (part)
            print (of)
            print ()
            part += 1
            part, of, body = self.__part_receive(
                action_write, action_read, part, of, attempt, interval)
            body_str += body
        # body_str = ""
        return json.loads(body_str.replace('\x00', ''), strict=False)

    # def long_receive(self, actionWrite, actionRead):
    #     self.__write(actionWrite, [1, 1])
    #     time.sleep(0.5)  # Seconds
    #     data = self.__read(actionRead)
    #     part, of = data[:2]
    #     body = data[2:]
    #     while part != of:
    #         part += 1
    #         self.__write(actionWrite, [part, of])
    #         time.sleep(0.5)  # Seconds
    #         data = self.__read(actionRead)
    #         body += data[2:]
    #     body_str = ""
    #     for byte in body:
    #         if byte == 255:
    #             break
    #         body_str += chr(byte)
    #     return json.loads(body_str.replace('\x00', ''), strict=False)

    def receive(self, action, attempt=10, interval=0.25):
        n = 1
        while n <= attempt:
            data = self.__read(action)
            data = data[2:]
            body = ""
            for byte in data:
                if byte == 255:
                    break
                body += chr(byte)
            try:
                json_data = json.loads(body.replace('\x00', ''), strict=False)
                if 's' in json_data and json_data['s'] == 'no_end':
                    n += 1
                    time.sleep(interval)
                    continue
                return json_data
            except:
                print ("Error:")
                print (body)
        raise TooManyAttempt('Too many attempt waiting')

    def send(self, action, body):
        data_bytes = list(body.encode())
        data_bytes = list(self.__divide_chunks(data_bytes, 29))
        of = len(data_bytes)
        if of == 0:
            self.__write(action, [1, 1])
        else:
            part = 0
            for data_b in data_bytes:
                part += 1
                data = [part, of] + data_b
                self.__write(action, data)
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
        time.sleep(0.5)
        return self.long_receive(self.GENERIC_WRITE, self.GENERIC_READ)

    def make_call(self, number):
        body = json.dumps({'n': number}, separators=(',', ':'))
        self.send(self.ACTION_CALL, body)
        time.sleep(1)
        return self.receive(self.RESPONSE_CALL)

    def answer_call(self):
        self.send(self.ACTION_ANSWER, '')
        time.sleep(1)
        return self.receive(self.RESPONSE_ANSWER)

    def hangoff_call(self):
        self.send(self.ACTION_HANGOFF, '')
        time.sleep(1)
        return self.receive(self.RESPONSE_HANGOFF)

    def send_sms(self, number, msg):
        body = json.dumps(
            {'n': number, 'b': msg},
            separators=(',', ':'))
        self.send(self.ACTION_SEND_SMS, body)
        time.sleep(5)
        return self.receive(self.RESPONSE_SEND_SMS, 20)

    def get_sms(self, index):
        body = json.dumps(
            {'i': index},
            separators=(',', ':'))
        self.send(self.ACTION_GET_SMS, body)
        time.sleep(2)
        return self.long_receive(self.GENERIC_WRITE, self.GENERIC_READ, 20)

    def delete_sms(self):
        self.send(self.ACTION_DEL_SMS, '', 20)
        time.sleep(10)
        return self.receive(self.RESPONSE_HANGOFF)

    def get_localization(self):
        self.send(self.ACTION_GET_LOC, '')
        time.sleep(60)
        return self.long_receive(self.GENERIC_WRITE, self.GENERIC_READ)
