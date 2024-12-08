#!/usr/bin/python3
import gpiod
import time
import threading
from logzero import logger

DEFAULT_LINE_MAP = {
   'JETSON_NANO': {
       3: 'J3', 5: 'J2', 7: 'BB0', 8: 'G0', 10: 'G1', 11: 'G2', 12: 'J7',
       13: 'B6', 15: 'Y2', 16: 'DD0', 18: 'B7', 19: 'C0', 21: 'C1',
       22: 'B5', 23: 'C2', 24: 'C3', 26: 'C4', 27: 'B5', 28: 'C2',
       29: 'S5', 31: 'Z0', 32: 'V0', 33: 'E6', 35: 'J4', 36: 'G3',
       37: 'B4', 38: 'J5', 40: 'J6'
   }
}

DEFAULT_GPIOD_CONSUMER = 'hx711'

class HX711:
   def get_line_no(self, pin_no):
       if not pin_no in self.line_map:
           raise RuntimeError(f"pin:{pin_no} is not found in line map.")
       line_str = self.line_map[pin_no]
       offset = int(line_str[-1])
       address = line_str[:-1]
       address_num = ord(address[0]) - ord('A')
       if len(address) == 2:
           address_num += ord('Z') - ord('A') + 1
       return address_num * 8 + offset

   def __init__(self, dout, pd_sck, gain=128, mutex=False, chip=None,
                line_map_name='JETSON_NANO', custome_line_map=None):
       self.line_map = None
       if line_map_name in DEFAULT_LINE_MAP:
           self.line_map = DEFAULT_LINE_MAP[line_map_name]
       elif custome_line_map:
           self.line_map = custome_line_map
       else:
           raise RuntimeError(f"line_map_name={line_map_name} not found")

       self.chip = chip
       if self.chip is None:
           self.chip = gpiod.Chip("0", gpiod.Chip.OPEN_BY_NUMBER)
       self.PD_SCK = self.chip.get_line(self.get_line_no(pd_sck))
       self.DOUT = self.chip.get_line(self.get_line_no(dout))
       self.mutex_flag = mutex
       if self.mutex_flag:
           self.readLock = threading.Lock()
       
       self.PD_SCK.request(consumer=DEFAULT_GPIOD_CONSUMER, type=gpiod.LINE_REQ_DIR_OUT)
       self.DOUT.request(consumer=DEFAULT_GPIOD_CONSUMER, type=gpiod.LINE_REQ_DIR_IN)
       
       self.GAIN = 0
       self.REFERENCE_UNIT = 1
       self.REFERENCE_UNIT_B = 1
       self.OFFSET = 1.0
       self.OFFSET_B = 1.0
       self.lastVal = 0.0

       self.byte_format = 'MSB'
       self.bit_format = 'MSB'

       self.set_gain(gain)
       time.sleep(0.1)

   def convertFromTwosComplement24bit(self, inputValue):
       return -(inputValue & 0x800000) + (inputValue & 0x7fffff)

   def is_ready(self):
       return self.DOUT.get_value() == 0

   def set_gain(self, gain):
       if gain == 128:
           self.GAIN = 1
       elif gain == 64:
           self.GAIN = 3
       elif gain == 32:
           self.GAIN = 2
       self.PD_SCK.set_value(0)
       self.readRawBytes()

   def get_gain(self):
       if self.GAIN == 1: return 128
       if self.GAIN == 3: return 64
       if self.GAIN == 2: return 32
       return 0

   def readNextBit(self):
       self.PD_SCK.set_value(1)
       self.PD_SCK.set_value(0)
       return self.DOUT.get_value()

   def readNextByte(self):
       byteValue = 0
       for x in range(8):
           if self.bit_format == 'MSB':
               byteValue <<= 1
               byteValue |= self.readNextBit()
           else:
               byteValue >>= 1
               byteValue |= self.readNextBit() * 0x80
       return byteValue

   def readRawBytes(self):
       if self.mutex_flag:
           self.readLock.acquire()

       while not self.is_ready():
           pass

       firstByte = self.readNextByte()
       secondByte = self.readNextByte()
       thirdByte = self.readNextByte()

       for i in range(self.GAIN):
           self.readNextBit()

       if self.mutex_flag:
           self.readLock.release()          

       if self.byte_format == 'LSB':
           return [thirdByte, secondByte, firstByte]
       else:
           return [firstByte, secondByte, thirdByte]

   def read_long(self):
       dataBytes = self.readRawBytes()
       logger.debug(dataBytes)
       twosComplementValue = (dataBytes[0] << 16) + (dataBytes[1] << 8) + dataBytes[2]
       logger.debug(f"Twos: 0x{twosComplementValue:06x}")
       signedIntValue = self.convertFromTwosComplement24bit(twosComplementValue)
       self.lastVal = signedIntValue
       return int(signedIntValue)

   def read_average(self, times=3):
       if times <= 0:
           raise ValueError("HX711()::read_average(): times must >= 1!!")
       if times == 1:
           return self.read_long()
       if times < 5:
           return self.read_median(times)
       valueList = []
       for x in range(times):
           valueList.append(self.read_long())
       valueList.sort()
       trimAmount = int(len(valueList) * 0.2)
       valueList = valueList[trimAmount:-trimAmount]
       return sum(valueList) / len(valueList)

   def read_median(self, times=3):
       if times <= 0:
           raise ValueError("HX711::read_median(): times must be greater than zero!")
       if times == 1:
           return self.read_long()
       valueList = []
       for x in range(times):
           valueList.append(self.read_long())
       valueList.sort()
       if (times & 0x1) == 0x1:
           return valueList[len(valueList) // 2]
       else:
           midpoint = len(valueList) // 2
           return sum(valueList[midpoint:midpoint+2]) / 2.0

   def get_value(self, times=3):
       return self.get_value_A(times)

   def get_value_A(self, times=3):
       return self.read_median(times) - self.get_offset_A()

   def get_value_B(self, times=3):
       g = self.get_gain()
       self.set_gain(32)
       value = self.read_median(times) - self.get_offset_B()
       self.set_gain(g)
       return value

   def get_weight(self, times=3):
       return self.get_weight_A(times)

   def get_weight_A(self, times=3):
       value = self.get_value_A(times)
       value = value / self.REFERENCE_UNIT
       return value

   def get_weight_B(self, times=3):
       value = self.get_value_B(times)
       value = value / self.REFERENCE_UNIT_B
       return value

   def tare(self, times=15):
       value = self.read_average(times)
       self.set_offset(value)
       return value

   def tare_A(self, times=15):
       value = self.read_average(times)
       self.set_offset_A(value)
       return value

   def tare_B(self, times=15):
       backupGain = self.get_gain()
       self.set_gain(32)
       value = self.read_average(times)
       self.set_offset_B(value)
       self.set_gain(backupGain)
       return value

   def set_reading_format(self, byte_format="LSB", bit_format="MSB"):
       if byte_format == "LSB":
           self.byte_format = byte_format
       elif byte_format == "MSB":
           self.byte_format = byte_format
       else:
           raise ValueError("Unrecognised byte_format: \"%s\"" % byte_format)
       if bit_format == "LSB":
           self.bit_format = bit_format
       elif bit_format == "MSB":
           self.bit_format = bit_format
       else:
           raise ValueError("Unrecognised bitformat: \"%s\"" % bit_format)

   def set_offset(self, offset):
       self.OFFSET = offset

   def set_offset_A(self, offset):
       self.OFFSET = offset

   def set_offset_B(self, offset):
       self.OFFSET_B = offset

   def get_offset(self):
       return self.OFFSET

   def get_offset_A(self):
       return self.OFFSET

   def get_offset_B(self):
       return self.OFFSET_B

   def set_reference_unit(self, reference_unit):
       self.REFERENCE_UNIT = reference_unit

   def set_reference_unit_A(self, reference_unit):
       self.REFERENCE_UNIT = reference_unit

   def set_reference_unit_B(self, reference_unit):
       self.REFERENCE_UNIT_B = reference_unit

   def get_reference_unit(self):
       return self.REFERENCE_UNIT

   def get_reference_unit_A(self):
       return self.REFERENCE_UNIT

   def get_reference_unit_B(self):
       return self.REFERENCE_UNIT_B

   def power_down(self):
       if self.mutex_flag:
           self.readLock.acquire()
       self.PD_SCK.set_value(0)
       self.PD_SCK.set_value(1)
       time.sleep(0.0001)
       if self.mutex_flag:
           self.readLock.release()

   def power_up(self):
       if self.mutex_flag:
           self.readLock.acquire()
       self.PD_SCK.set_value(0)
       time.sleep(0.0001)
       if self.mutex_flag:
           self.readLock.release()
       if self.get_gain() != 128:
           self.readRawBytes()

   def reset(self):
       self.power_down()
       self.power_up()
