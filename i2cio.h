#ifndef I2CIO_H
#define I2CIO_H

#include "logs/logparser.h"
#include <stdio.h>
#include <string.h>
#include <fcntl.h>
#include <stdint.h>
#include <sys/ioctl.h>
#include <termios.h>
#include <unistd.h>
#include <cstdio>
#include <cstdlib>
#include <fcntl.h>
#include <linux/i2c.h>
#include <iostream>

#include <linux/i2c-dev.h>

#define ERRNO_EEPROM_NOT_DETECTED 6

extern const char *i2c_fname;

int i2c_init(void);
void i2c_close(void);
int i2c_write(uint8_t slave_addr, uint8_t reg, uint8_t data);
int i2c_read(uint8_t slave_addr, uint8_t reg, uint8_t *result);
int i2c_read_block(uint8_t slave_addr, uint8_t reg, uint8_t *inBuffer, size_t len);
int i2c_write_block(uint8_t slave_addr, uint8_t reg, uint8_t *data, size_t len);

#endif // I2CIO_H
