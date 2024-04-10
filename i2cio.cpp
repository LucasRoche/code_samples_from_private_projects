#include "i2cio.h"

// This file contains functions to handle low level I/O for the i2c bus
// Read and write are done byte by byte with the read() and write() functions
// The read_block and write_block functions are wrappers to read/write multiple bytes to/from a buffer using the read/write function
// The machine uses the i2c device 1, with addresses in the range [0x50 : 0x57]
// The i2c is used to communicate with the cartridges EEPROM, on which are stored product informations

// Global file descriptor used to talk to the I2C bus:
static int i2c_fd = -1;

// Default RPi B device name for the I2C bus exposed on GPIO2,3 pins (GPIO2=SDA, GPIO3=SCL):
const char *i2c_fname = "/dev/i2c-0";

// Returns a new file descriptor for communicating with the I2C bus:
int i2c_init(void) {
    if ((i2c_fd = open(i2c_fname, O_RDWR | O_NONBLOCK)) < 0) {
        char err[200];
        sprintf(err, "open('%s') in i2c_init", i2c_fname);
        LogParser::writeLog("I2C", Q_FUNC_INFO, "Error opening i2c device " + QString::fromLatin1(i2c_fname) + " : " + QString::fromLatin1(strerror(errno)), LOGLEVEL::ERROR);
        return -1;
    }

    // NOTE we do not call ioctl with I2C_SLAVE here because we always use the I2C_RDWR ioctl operation to do
    // writes, reads, and combined write-reads. I2C_SLAVE would be used to set the I2C slave address to communicate
    // with. With I2C_RDWR operation, you specify the slave address every time. There is no need to use normal write()
    // or read() syscalls with an I2C device which does not support SMBUS protocol. I2C_RDWR is much better especially
    // for reading device registers which requires a write first before reading the response.

    return i2c_fd;
}

void i2c_close(void) {
    close(i2c_fd);
}

// Write to an I2C slave device's register:
int i2c_write(uint8_t slave_addr, uint8_t reg, uint8_t data) {
    int retval;
    uint8_t outbuf[2];

    struct i2c_msg msgs[1];
    struct i2c_rdwr_ioctl_data msgset[1];

    outbuf[0] = reg;
    outbuf[1] = data;

    msgs[0].addr = slave_addr;
    msgs[0].flags = 0;
    msgs[0].len = 2;
    msgs[0].buf = outbuf;

    msgset[0].msgs = msgs;
    msgset[0].nmsgs = 1;

    if (ioctl(i2c_fd, I2C_RDWR, &msgset) < 0) {
        LogParser::writeLog("I2C", Q_FUNC_INFO, "Write error in ioctl(I2C_RDRW). Address : 0x" + QString::number(slave_addr, 16) + ". Register : 0x" + QString::number(reg, 16)+ ". Error : " +QString::number(errno) + " " + QString::fromLatin1(strerror(errno)), LOGLEVEL::ERROR);
        return -1;
    }

    return 0;
}

// Write a block of len bytes on i2c slave at address slave_addr, register reg from the data input buffer
int i2c_write_block(uint8_t slave_addr, uint8_t reg, uint8_t *data, size_t len){
    int returnValue = 0;
    for(size_t i = 0; i < len; i++){
        returnValue += i2c_write(slave_addr, reg+i, data[i]);
        usleep(5000);
    }
    return returnValue;
}


// Read the given I2C slave device's register and return the read value in `*result`:
int i2c_read(uint8_t slave_addr, uint8_t reg, uint8_t *result) {
    int retval;
    uint8_t outbuf[1], inbuf[1];
    struct i2c_msg msgs[2];
    struct i2c_rdwr_ioctl_data msgset[1];

    msgs[0].addr = slave_addr;
    msgs[0].flags = 0;
    msgs[0].len = 1;
    msgs[0].buf = outbuf;

    msgs[1].addr = slave_addr;
    msgs[1].flags = I2C_M_RD;
    msgs[1].len = 1;
    msgs[1].buf = inbuf;

    msgset[0].msgs = msgs;
    msgset[0].nmsgs = 2;

    outbuf[0] = reg;

    inbuf[0] = 0;

    *result = 0;
    if (ioctl(i2c_fd, I2C_RDWR, &msgset) < 0) {
        if(errno != ERRNO_EEPROM_NOT_DETECTED){ // errno 121 = eeprom not detected, do not print error in this function to avoid spamming the log file when some cartridges slot are free
            LogParser::writeLog("I2C", Q_FUNC_INFO, "Read error in ioctl(I2C_RDRW). Address : 0x" + QString::number(slave_addr, 16) + ". Register : 0x" + QString::number(reg, 16)+ ". Error : " +QString::number(errno) + " " + QString::fromLatin1(strerror(errno)), LOGLEVEL::ERROR);

        }
        return -errno;
    }

    *result = inbuf[0];
    return 0;
}

//Read a block of "len" bytes of the i2c device at address "slave_addr", on register "reg", and store the data in "inBuffer"
//On success, returns 0
//On error, returns the number of byte reads that failed, and store the errno for each failed read in the input buffer
int i2c_read_block(uint8_t slave_addr, uint8_t reg, uint8_t *inBuffer, size_t len){
   int retVal = 0;
   int numberOfErrors = 0;
   for(size_t i = 0; i < len; i++){
       retVal = i2c_read(slave_addr, reg+i, &inBuffer[i]);
       if(retVal < 0){
           inBuffer[i] = static_cast<uint8_t>(-retVal);
           numberOfErrors++;
       }
   }
   return -numberOfErrors;
}
