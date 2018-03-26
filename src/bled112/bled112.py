#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import signal
import logging
import urllib2
import json
import time
import ble_codes
import util
import multiprocessing as mp
from util import current_milli_time

# ----------------------------------------
# BLE state machine definitions
# ----------------------------------------
BLE_STATE_STANDBY = 0
BLE_STATE_SCANNING = 1
BLE_STATE_ADVERTISING = 2
BLE_STATE_CONNECTING = 3
BLE_STATE_CONNECTED_MASTER = 4
BLE_STATE_CONNECTED_SLAVE = 5

PROCESS_STATE_STOPPED = 0
PROCESS_STATE_RUNNING = 1
DEBUG = True
POWERBENCH = False
IBEACON = False


class Step(object):
    def __init__(self, time='', ble_operation='advertising', adv_data='', short_name='',
                 sr_data='', long_name='', major='', minor='', adv_channels='', adv_interval_min='',
                 adv_interval_max='', gap_discoverable_mode='', connection_interval_min='',
                 connection_interval_max='', slave_latency='', supervision_timeout='', gap_connectable_mode=''):
        self.time = time
        self.ble_operation = ble_operation
        self.adv_data = adv_data
        self.short_name = short_name
        # default BLE stack value: 140942474c69622055314131502033382e344e4657
        self.sr_data = sr_data
        self.long_name = long_name
        self.major = major
        self.minor = minor
        self.adv_interval_min = adv_interval_min
        self.adv_interval_max = adv_interval_max
        self.adv_channels = adv_channels
        self.gap_discoverable_mode = gap_discoverable_mode
        self.gap_connectable_mode = gap_connectable_mode
        self.connection_interval_min = connection_interval_min
        self.connection_interval_max = connection_interval_max
        self.slave_latency = slave_latency
        self.supervision_timeout = supervision_timeout


class Peripheral(object):
    def __init__(self, logger, steps, port_name, baud_rate="38400",
                 packet_mode=False, gap_role='broadcaster', gatt_role='server',
                 adv_data=[
                     0x08,  # field length
                     # field type 0x08=shortname
                     0x08,
                     0x42, 0x4c, 0x45, 0x76, 0x61, 0x00, 0x00,  # adv name
                     0x02,  # field length
                     0x01,  # BGLIB_GAP_AD_TYPE_FLAGS --> field type # data (0x02 | 0x04 = 0x06, # general discoverable + BLE only, no BR+EDR)
                     0x06,
                     0x03,  # field length
                     0xFF,  # BGLIB_GAP_AD_TYPE_SERVICES_128BIT_ALL, field type
                     0xDD, 0xDD],
                 short_name='BLEva',
                 sr_data=[
                     # 0x06, # field length
                     # 0x09, # BGLIB_GAP_AD_TYPE_LOCALNAME_COMPLETE
                     # 0x43, 0x4c, 0x45, 0x76, 0x61
                 ],
                 long_name='',
                 major=0x200, minor=0x200, adv_channels=0x07,
                 adv_interval_min=0x200, adv_interval_max=0x200,
                 gap_discoverable_mode=ble_codes.gap_discoverable_mode[
                     'gap_user_data'],
                 gap_connectable_mode=ble_codes.gap_connectable_mode[
                     'gap_scannable_non_connectable'],
                 connection_interval_min=7.5, connection_interval_max=30,
                 slave_latency=0, supervision_timeout=250
                 ):
        self.logger = logger
        self.port_name = port_name
        self.baud_rate = baud_rate
        self.packet_mode = packet_mode
        self.gap_role = gap_role
        self.gatt_role = gatt_role
        self.steps = steps
        self.adv_data = adv_data
        self.short_name = short_name
        self.sr_data = sr_data
        self.long_name = long_name
        self.major = major
        self.minor = minor
        self.adv_channels = adv_channels
        self.adv_interval_min = adv_interval_min
        self.adv_interval_max = adv_interval_max
        self.ble_state = None
        self.process_state = None
        self.gap_discoverable_mode = gap_discoverable_mode
        self.gap_connectable_mode = gap_connectable_mode
        self.sr_data = sr_data
        self.connection_interval_min = connection_interval_min
        self.connection_interval_max = connection_interval_max
        self.slave_latency = slave_latency
        self.supervision_timeout = supervision_timeout

    def start_benchmark(self):
        '''
        start benchmark
        '''
        import bglib
        self.bg = bglib.BGLib()
        import serial
        print self.port_name
        self.ser = serial.Serial(port=self.port_name, baudrate=38400, timeout=1)
        self.register_handlers()
        self.setup()
        self.process_state = PROCESS_STATE_RUNNING
        for step in self.steps:
            self.set(step)
            self.logger.info('Starting next Step')
            self.run()
            t0 = current_milli_time()
            print "step time " + str(step.time)
            print "t0 " + str(t0)
            while current_milli_time() - t0 < step.time and self.process_state == PROCESS_STATE_RUNNING:
                # catch all incoming data
                self.bg.check_activity(self.ser)
                # don't burden the CPU
                time.sleep(0.001)
                # if for some reason, we end up in standby, benchmark fails
                if self.ble_state == BLE_STATE_STANDBY:
                    raise Exception("We are in standby, but we should not be!")
            t1 = current_milli_time()
            print "t1 " + str(t1)
            print "diff " + str(t1 - t0)
            self.standby()
        self.stop()  # close serial connection after benchmark

    def setup(self):
        '''
        setups a device and puts it in standby at beginning of benchmark
        '''
        self.logger.info('Setting up BLEva...')
        self.bg.packet_mode = self.packet_mode
        # self.ser = serial.Serial(port=self.port_name, baudrate=self.baud_rate, timeout=1)
        self.logger.debug('flushing input')
        self.ser.flushInput()
        self.logger.debug('flushing output')
        self.ser.flushOutput()
        # disconnect if we are connected already
        self.logger.debug('disconnecting in case we are connected')
        self.bg.send_command(self.ser, self.bg.ble_cmd_connection_disconnect(0))
        self.bg.check_activity(self.ser, 1)

        # stop advertising if we are advertising already
        self.logger.debug('stop advertising in case we are still')
        # 0 gap_non_discoverable, 0 gap_non_connectable
        self.bg.send_command(self.ser, self.bg.ble_cmd_gap_set_mode(0, 0))
        self.bg.check_activity(self.ser, 1)

        # stop scanning if we are scanning already
        # This command ends the current GAP discovery procedure and stop the scanning
        # of advertising devices
        self.logger.debug('stop scanning in case we are still')
        self.bg.send_command(self.ser, self.bg.ble_cmd_gap_end_procedure())
        self.bg.check_activity(self.ser, 1)

        # now we must be in STANDBY state
        # TODO here notify phone that we are ready
        self.ble_state = BLE_STATE_STANDBY
        self.logger.debug('BLEva is in STANDBY now.')

    def standby(self):
        '''
         puts device in standby between steps or at the end of benchmark
        '''
        # disconnect if we are connected already
        self.logger.debug('disconnecting in case we are connected')
        self.bg.send_command(self.ser, self.bg.ble_cmd_connection_disconnect(0))
        self.bg.check_activity(self.ser, 1)

        # stop advertising if we are advertising already
        self.logger.debug('stop advertising in case we are still')
        # 0 gap_non_discoverable, 0 gap_non_connectable
        self.bg.send_command(self.ser, self.bg.ble_cmd_gap_set_mode(0, 0))
        self.bg.check_activity(self.ser, 1)

        # stop scanning if we are scanning already
        # This command ends the current GAP discovery procedure and stop the scanning
        # of advertising devices
        self.logger.debug('stop scanning in case we are still')
        self.bg.send_command(self.ser, self.bg.ble_cmd_gap_end_procedure())
        self.bg.check_activity(self.ser, 1)

        # now we must be in STANDBY state
        # TODO here notify phone that we are ready
        self.ble_state = BLE_STATE_STANDBY
        self.logger.debug('BLEva is in STANDBY now.')

    def set(self, step):
        '''
        Prepares the run of a new step by setting its parameters
        '''
        if step.ble_operation != "":
            self.ble_operation = step.ble_operation
        if step.adv_data != "":
            self.adv_data = step.adv_data
        if step.short_name != "":
            self.short_name = step.short_name
        if step.sr_data != "":
            self.sr_data = step.sr_data
        if step.long_name != "":
            self.long_name = step.long_name
        if step.major != "":
            self.major = step.major
        if step.minor != "":
            self.minor = step.minor
        if step.adv_interval_min != "":
            self.adv_interval_min = step.adv_interval_min
        if step.adv_interval_max != "":
            self.adv_interval_max = step.adv_interval_max
        if step.adv_channels != "":
            self.adv_channels = step.adv_channels
        if step.gap_discoverable_mode != "":
            self.gap_discoverable_mode = step.gap_discoverable_mode
        if step.gap_connectable_mode != "":
            self.gap_connectable_mode = step.gap_connectable_mode
        if step.connection_interval_min != "":
            self.connection_interval_min = step.connection_interval_min
        if step.connection_interval_max != "":
            self.connection_interval_max = step.connection_interval_max
        if step.slave_latency != "":
            self.slave_latency = step.slave_latency
        if step.supervision_timeout != "":
            self.supervision_timeout = step.supervision_timeout

    def run(self):
        '''
        set all parameters on the device (e.g., for a new step)
        '''
        if self.ble_state != BLE_STATE_STANDBY:
            raise

        self.logger.debug('set advertisement parameters')
        # This is just to tweak channels, radio...
        self.bg.send_command(self.ser, self.bg.ble_cmd_gap_set_adv_parameters(
            int(self.adv_interval_min * 0.625), int(self.adv_interval_max * 0.625), self.adv_channels))
        self.bg.check_activity(self.ser, 1)

        # 4 means custom user data in advertisment packet
        if self.gap_discoverable_mode == ble_codes.gap_discoverable_mode['gap_user_data']:  # TODO, use always user_data
            self.logger.debug('Setting user defined advertising data.')
            if self.short_name != "":
                print "setting advertisement"
                self.adv_data[2:9] = util.get_char_array(self.short_name)[0:7]
                logging.debug('Advertising Data: %s', self.adv_data)
                print self.adv_data
            self.bg.send_command(self.ser,
                                 self.bg.ble_cmd_gap_set_adv_data(0, self.adv_data))
            self.bg.check_activity(self.ser, 1)
            if self.long_name != "":
                self.sr_data = [
                    0x0F,  # field length
                    0x09,  # BGLIB_GAP_AD_TYPE_LOCALNAME_COMPLETE
                    0x42, 0x4c, 0x45, 0x76, 0x61, 0x6c, 0x75, 0x61, 0x74, 0x69, 0x6f, 0x6e, 0x00, 0x00
                ]
                print "setting scan response"
                print self.long_name
                self.sr_data[2:16] = util.get_char_array(self.long_name)[0:14]
                logging.debug('Advertising Data: %s', self.sr_data)
                print self.sr_data
            else:
                self.sr_data = []
            # NOTE SR is not necessary
            if self.sr_data != "":
                self.bg.send_command(self.ser,
                                     self.bg.ble_cmd_gap_set_adv_data(1, self.sr_data))
                self.bg.check_activity(self.ser, 1)

        # start advertising as discoverable
        # ibeacon was 0x84, 0x03
        self.logger.debug('Entering advertising mode.')
        self.bg.send_command(self.ser, self.bg.ble_cmd_gap_set_mode(
            self.gap_discoverable_mode, self.gap_connectable_mode))
        self.bg.check_activity(self.ser, 1)

        # set state to advertising
        self.ble_state = BLE_STATE_ADVERTISING
        self.logger.debug('BLEva is in BLE_STATE_ADVERTISING now.')

    def stop(self):
        '''
        stop thread
        '''
        print "stop"
        self.standby()
        print "standby"
        self.ser.close()
        print "closed"

    # --------------------------------------------------------------------------
    # Event Handlers
    # --------------------------------------------------------------------------
    def handler_on_timeout(self, sender, args):
        '''
        Gets called when we send a command but we don't get a response back e.g.
        '''
        self.logger.debug('handler_on_timeout: %s', args)
        # might want to try the following lines to reset, though it probably
        # wouldn't work at this point if it's already timed out:
        self.bg.send_command(self.ser, self.bg.ble_cmd_system_reset(0))
        self.ble_state = BLE_STATE_STANDBY
        self.logger.debug('BLEva is in STANDBY now.')

    # NOTE not needed as we are not in enhanced broadcasting mode,
    # This will never get called
    def handler_ble_evt_gap_scan_response(self, sender, args):
        """
        Handler to print scan responses with a timestamp (this only works when
        discoverable mode is set to enhanced broadcasting 0x80/0x84)
        """

    def handler_ble_evt_connection_status(self, sender, args):
        '''
        This gets called when a client has just been connected to us.
        We need to check if we already know it, potentially check if it is blacklisted etc...
        Then we set it as our active client.
        '''
        self.logger.debug('handler_ble_evt_connection_status: %s', args)
        self.logger.info('Connection Status has changed')

        # self.connection_interval_min=640
        # self.connection_interval_max=1280
        # self.slave_latency=0
        # self.supervision_timeout=3600
        #  {'latency': 0, 'connection': 0, 'conn_interval': 39, 'flags': 5, 'timeout': 2000, 'address': [216, 96, 156, 121, 224, 248], 'address_type': 0, 'bonding': 255}
        #  {'latency': 0, 'connection': 0, 'conn_interval': 6, 'flags': 9, 'timeout': 2000, 'address': [216, 96, 156, 121, 224, 248], 'address_type': 0, 'bonding': 255}
        # check if connection status flags are 5 (bit0=connection_connected + bit2=connection completed)
        if (args['flags'] & 0x05) == 0x05:
            self.ble_state = BLE_STATE_CONNECTED_SLAVE
            self.logger.debug('BLEva is in BLE_STATE_CONNECTED_SLAVE now.')
            if self.connection_interval_min != "":
                print self.connection_interval_min
                print self.connection_interval_max
                print self.supervision_timeout
                connection = args['connection']
                print "Requesting to upgrade connection"
                self.logger.debug('Requesting to upgrade connection')
                # self.bg.send_command(self.ser, self.bg.ble_cmd_connection_update(
                    # connection, 6, 24, 0, 25))
                self.bg.send_command(self.ser, self.bg.ble_cmd_connection_update(
                    connection, self.connection_interval_min / 1.25,
                    self.connection_interval_max / 1.25, self.slave_latency / 1.25,
                    self.supervision_timeout / 10))
        elif (args['flags'] & 0x09) == 0x09:
            self.logger.debug('BLEva connection parameters have been changed by master.')
            if self.connection_interval_min != "":
                if not self.connection_interval_min * 1.25 <= args['conn_interval'] <= self.connection_interval_max * 1.25:
                    self.logger.warning('Master set intervals outside our desired region :(')
                if not self.supervision_timeout * 10 == args['timeout']:
                    self.logger.warning('Master set timeout outside our desired region :(')
                if not self.slave_latency * 1.25 == args['latency']:
                    self.logger.warning('Master set slave latency outside our desired region :(')
        else:
            self.logger.warning('Connection was not correctly established!')

    def handler_ble_evt_connection_disconnected(self, sender, args):
        '''
        A client has just disconnected from us
        '''
        self.logger.debug('handler_ble_evt_connection_disconnected: %s', args)
        if args['reason'] == 0x213:
            self.logger.debug('User on the remote device terminated the connection')

        # We need to advertise ourselves again as a slave
        self.bg.send_command(self.ser, self.bg.ble_cmd_gap_set_mode(
            self.gap_discoverable_mode, self.gap_connectable_mode))

        # we can now set state to advertise again
        self.ble_state = BLE_STATE_ADVERTISING
        self.logger.debug('BLEva is in BLE_STATE_ADVERTISING now.')
        self.process_state = PROCESS_STATE_STOPPED

    def handler_ble_rsp_gap_set_mode(self, senser, args):
        '''
        GAP mode has been set in response to
        self.bg.ble_cmd_gap_set_mode
        '''
        self.logger.debug('handler_ble_rsp_gap_set_mode: %s', args)
        if args["result"] != 0:
            self.logger.warning('ble_rsp_gap_set_mode FAILED\n Re-running setup()')
            self.setup()
        else:
            self.logger.debug('GAP mode sucessfully set')

    def handler_ble_evt_attributes_value(self, sender, args):
        '''
        Gets called when an attribute has been written by a client
        {'connection': 0, 'handle': 25, 'reason': 2, 'value': [1], 'offset': 0}
        '''
        self.logger.debug('handler_ble_evt_attributes_value: %s', args)
        client_con = args['connection']
        self.bg.send_command(self.ser, self.bg.ble_cmd_attributes_user_write_response(client_con, 0))

    def handler_ble_evt_attributes_user_read_request(self, sender, args):
        '''
        This is called whenever a client reads an attribute that has the user type
        enabled. We then serve the data dynamically. Each packet payload is 22 Bytes.
        Whenever a client is receiving 22 bytes, the client needs to issue another
        read request on the same atttribute as long as all the data is received
        (This can be concludes when we receive less than 22 bytes)
        'connection': connection, 'handle': handle, 'offset': offset, 'maxsize': maxsize
        '''
        self.logger.debug('handler_ble_evt_attributes_user_read_request: %s', args)
        client_con = args['connection']  # --> we should not care about connection No for identification
        # as we only can have one single client connected at the same time
        # for feedback if previous write has been suceeded
        value = [0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01,
                 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01]
        self.bg.send_command(self.ser, self.bg.ble_cmd_attributes_user_read_response(client_con, 0, value))

    def handler_ble_rsp_connection_update(self, sender, args):
        '''
            Gets called as a result of us trying to upgrade an existing connection.
        '''
        self.logger.debug('handler_ble_rsp_connection_update: %s', args)
        if args['result'] != 0:
            self.logger.warning('Upgrading od connection failed, resetting BLEva')
            self.bg.send_command(self.ser, self.bg.ble_cmd_system_reset(0))
            self.ble_state = BLE_STATE_STANDBY
            self.logger.debug('BLEva is in STANDBY now.')

    def handler_ble_evt_attributes_status(self, sender, args):
        '''
            Gets called when a client enables notification or indication
        '''
        self.logger.debug('handler_ble_evt_attributes_status: %s', args)

    def handler_ble_rsp_attributes_read(self, sender, args):
        self.logger.debug('handler_ble_rsp_attributes_read: %s', args)

    def handler_ble_rsp_attributes_user_read_response(self, sender, args):
        self.logger.debug('handler_ble_rsp_attributes_user_read_response: %s', args)

    def handler_ble_rsp_attributes_write(self, sender, args):
        self.logger.debug('handler_ble_rsp_attributes_write: %s', args)

    def handler_ble_rsp_attributes_user_write_response(self, sender, args):
        self.logger.debug('handler_ble_rsp_attributes_user_write_response: %s', args)

    def handler_ble_rsp_attributes_read_type(self, sender, args):
        self.logger.debug('handler_ble_rsp_attributes_read_type: %s', args)

    def handler_ble_evt_attclient_indicated(self, sender, args):
        self.logger.debug('handler_ble_evt_attclient_indicated: %s', args)

    # gracefully exit without a big exception message if possible
    # FIXME should flush our buffers here
    def handler_ctrl_c(self, signal, frame):
        self.standby()
        print "BLEva shut down"
        exit(0)

    def register_handlers(self):
        self.logger.debug('registering handlers...')
        self.bg.on_timeout += self.handler_on_timeout
        self.bg.ble_evt_gap_scan_response += self.handler_ble_evt_gap_scan_response
        self.bg.ble_evt_connection_disconnected += self.handler_ble_evt_connection_disconnected
        self.bg.ble_evt_connection_status += self.handler_ble_evt_connection_status
        self.bg.ble_rsp_attributes_read += self.handler_ble_rsp_attributes_read
        self.bg.ble_rsp_attributes_user_read_response += self.handler_ble_rsp_attributes_user_read_response
        self.bg.ble_rsp_attributes_write += self.handler_ble_rsp_attributes_write
        self.bg.ble_rsp_attributes_user_write_response += self.handler_ble_rsp_attributes_user_write_response
        self.bg.ble_rsp_attributes_read_type += self.handler_ble_rsp_attributes_read_type
        self.bg.ble_evt_attclient_indicated += self.handler_ble_evt_attclient_indicated
        self.bg.ble_evt_attributes_value += self.handler_ble_evt_attributes_value
        self.bg.ble_evt_attributes_user_read_request += self.handler_ble_evt_attributes_user_read_request
        self.bg.ble_rsp_gap_set_mode += self.handler_ble_rsp_gap_set_mode
        self.bg.ble_rsp_connection_update += self.handler_ble_rsp_connection_update
        signal.signal(signal.SIGINT, self.handler_ctrl_c)


def getBenchmark(url):
    try:
        r = urllib2.urlopen(url).read()
    except Exception:
        return ""
    return r


def main():
    parser = argparse.ArgumentParser(description='''Starts a BLEva Gateway
            service on the device.''', epilog='''Note: This requires a BLED112
            dongle from Bluegiga.''')
    parser.add_argument('-u', '--url', help='''URL of BLEva server''', required=True)
    parser.add_argument('-d', '--debug', help='Debug level (0-4)', type=int,
                        default=20, choices=[10, 20, 30, 40, 50])
    args = parser.parse_args()
    url = args.url
    print url
    tty_paths = util.get_tty_paths()
    FORMAT = '%(asctime)s - %(name)s - %(processName)s - %(levelname)s - %(message)s'
    logging.basicConfig(format=FORMAT, filename='bled112.log')
    logger = logging.getLogger('BLEva')
    logger.setLevel(args.debug)
    import multiprocessing_logging
    multiprocessing_logging.install_mp_handler()
    logger.info('\n--------------------')
    logger.info('BLEva has started')
    logger.info('\n--------------------')
    while True:
        logger.info('\n--------------------')
        logger.info('BLEva is waiting for new benchmark')
        print "BLEva is waiting for new benchmarks"
        b = getBenchmark(url + '/benchmark')
        print b
        if b != '':
            logger.info('BLEva received new benchmark')
            print "got new benchmark"
            j = json.loads(b)
            instances = []
            for dongle in j['dongles']:
                gap_role = dongle['gap_role']
                gatt_role = dongle['gatt_role']
                replicas = dongle['replicas']
                print replicas
                logger.debug("Replicas: " + str(replicas))
                if replicas > len(tty_paths):
                    raise Exception("Too few dongles connected.")
                for replica in xrange(0, replicas):
                    if gap_role in ['broadcaster', 'peripheral']:
                        a = dongle['steps']
                        steps = []
                        for v in a:
                            s = Step()
                            s.time = v['time']
                            print "json time " + str(['time'])
                            s.ble_operation = v['ble_operation']
                            # s.adv_data = map(ord, v['adv_data'][2:].decode("hex"))
                            # s.short_name = util.pad_truncate(s.short_name, 5)
                            # s.long_name = util.pad_truncate(s.long_name, 12)
                            s.long_name = v['long_name']
                            if replica < 10:
                                s.short_name = v['short_name'] + str(0) + str(replica)
                                if s.long_name != "":
                                    s.long_name = v['long_name'] + str(0) + str(replica)
                            else:
                                s.short_name = v['short_name'] + str(replica)
                                if s.long_name != "":
                                    s.long_name = v['long_name'] + str(replica)
                            s.short_name = util.pad_truncate(s.short_name, 7)
                            if s.long_name != "":
                                s.long_name = util.pad_truncate(s.long_name, 14)
                            logger.debug("Replica Short Name: " + s.short_name)
                            logger.debug("Replica Long Name: " + s.long_name)
                            s.major = int(v['major'], 0)  # NOTE base=0 guesses base from string
                            s.minor = int(v['minor'], 0)
                            s.adv_interval_min = int(v['adv_interval_min'], 0)
                            s.adv_interval_max = int(v['adv_interval_max'], 0)
                            s.adv_channels = int(v['adv_channels'], 0)
                            s.gap_discoverable_mode = ble_codes.gap_discoverable_mode[v['gap_discoverable_mode']]
                            s.gap_connectable_mode = ble_codes.gap_connectable_mode[v['gap_connectable_mode']]
                            if "connection_interval_min" in v:
                                s.connection_interval_min = v["connection_interval_min"]
                            if "connection_interval_max" in v:
                                s.connection_interval_max = v["connection_interval_max"]
                            if "slave_latency" in v:
                                s.slave_latency = v["slave_latency"]
                            if "supervision_timeout" in v:
                                s.supervision_timeout = v["supervision_timeout"]
                            steps.append(s)
                        peripheral = Peripheral(logger=logger, steps=steps, port_name=tty_paths[replica], gap_role=gap_role, gatt_role=gatt_role)
                        instances.append(peripheral)
            logger.info('BLEva is starting benchmark now')
            print "BLEva is starting benchmark now"
            processes = []
            logger.debug('Telling Phone to start')
            print "notifying phone"
            urllib2.urlopen(url + '/benchmark/sync/dongle').read()
            print "done notified"
            if not IBEACON:
                for i in instances:
                    print i
                    p = mp.Process(target=i.start_benchmark, name=i.steps[0].short_name)
                    p.start()
                    processes.append(p)
                for p in processes:
                    p.join()
            else:
                time.sleep(40)
            print "finished one benchmark"
            logger.info('BLEva finished one benchmark')  # FIXME fix logger to also log spawned processes
        if b == '':
            print "BLEva server not available, sleeping a while and try again."
            logger.info('BLEva server not available, sleeping a while and try again.')  # FIXME fix logger to also log spawned processes
            time.sleep(10)  # sleep and then try again until server is available
if __name__ == '__main__':
    main()
