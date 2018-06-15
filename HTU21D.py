from microbit import *

class HTU21D:
    def __init__(self):
        self.HTDU21D_ADDRESS           = 0x40
        self.TRIGGER_TEMP_MEASURE_HOLD = 0xE3
        self.TRIGGER_HUMD_MEASURE_HOLD = 0xE5
        self.SHIFTED_DIVISOR           = (2**8 + 2**5 + 2**4 + 1)<<15
        self.READ_USER_REG             = 0xE7
        self.WRITE_USER_REG            = 0xE6
        self.SOFT_RESET                = 0xFE
        
        self.RH12_TEMP14 = 0b00000000
        self.RH08_TEMP12 = 0b00000001
        self.RH10_TEMP13 = 0b10000000
        self.RH11_TEMP11 = 0b10000001
        
    def readTemp(self):
        buf = bytes([self.TRIGGER_TEMP_MEASURE_HOLD])
        i2c.write(self.HTDU21D_ADDRESS, buf) 
                  
        msb, lsb, crc = i2c.read(self.HTDU21D_ADDRESS, 3)
        crcResult     = self.__check_crc(msb, lsb, crc)
        raw           = (msb<<8 | lsb) & 0xfffc
        temp          = -46.85 + 175.72 * raw / 65536.0
        
        return temp if crcResult == 0 else crcResult
        
    def readHumid(self):
        buf = bytes([self.TRIGGER_HUMD_MEASURE_HOLD])
        i2c.write(self.HTDU21D_ADDRESS, buf) 
                  
        msb, lsb, crc = i2c.read(self.HTDU21D_ADDRESS, 3)
        crcResult     = self.__check_crc(msb, lsb, crc)
        raw           = (msb<<8 | lsb) & 0xfffc
        humid         = -6.0 + 125.0 * raw / 65536.0
        
        return humid if crcResult == 0 else crcResult
        
    def __check_crc(self, msb, lsb, crc):
        divisor   = self.SHIFTED_DIVISOR
        remainder = msb<<16 | lsb<<8 | crc
        
        for i in range(23, 7, -1):
            if remainder & 1<<i:
                remainder ^= divisor
             
            divisor >>= 1
            
        return 0 if remainder == 0 else 999
    
    def readUserRegister(self):
        buf = bytes([self.READ_USER_REG])
        i2c.write(self.HTDU21D_ADDRESS, buf)
        
        return i2c.read(self.HTDU21D_ADDRESS, 1)
        
    def setResolution(self, resolution):
        userRegister = self.readUserRegister()[0]
        userRegister &= 0b01111110
        resolution   &= 0b10000001
        userRegister |= resolution
        
        buf = bytes([self.WRITE_USER_REG, userRegister])
        i2c.write(self.HTDU21D_ADDRESS, buf)
        
    def softReset(self):
        buf = bytes([self.SOFT_RESET])
        i2c.write(self.HTDU21D_ADDRESS, buf)

##############
# how to use #
##############
if __name__ == "__main__":
    HTU = HTU21D()
    
    #HTU.softReset() # To soft-reset the HTU21D, uncomment this line.
    
    #HTU.setResolution(HTU.RH12_TEMP14) # You can select one of the four resolutions.
    #HTU.setResolution(HTU.RH08_TEMP12)
    #HTU.setResolution(HTU.RH10_TEMP13)
    #HTU.setResolution(HTU.RH11_TEMP11)
    while True:
        #print(HTU.readUserRegister()) # To serial.print the user register, uncomment this line.
        
        temp  = HTU.readTemp()
        humid = HTU.readHumid()
        print("%.1f C, %.1f %%" % (temp, humid))
        sleep(1000)
