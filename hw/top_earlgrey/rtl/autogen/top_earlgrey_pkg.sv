// Copyright lowRISC contributors.
// Licensed under the Apache License, Version 2.0, see LICENSE for details.
// SPDX-License-Identifier: Apache-2.0

package top_earlgrey_pkg;

  // Base addresses of all peripherals.
  parameter logic [31:0] TOP_EARLGREY_UART_BASE_ADDR = 32'h40000000;
  parameter logic [31:0] TOP_EARLGREY_GPIO_BASE_ADDR = 32'h40010000;
  parameter logic [31:0] TOP_EARLGREY_SPI_DEVICE_BASE_ADDR = 32'h40020000;
  parameter logic [31:0] TOP_EARLGREY_FLASH_CTRL_BASE_ADDR = 32'h40030000;
  parameter logic [31:0] TOP_EARLGREY_RV_TIMER_BASE_ADDR = 32'h40080000;
  parameter logic [31:0] TOP_EARLGREY_AES_BASE_ADDR = 32'h40110000;
  parameter logic [31:0] TOP_EARLGREY_HMAC_BASE_ADDR = 32'h40120000;
  parameter logic [31:0] TOP_EARLGREY_RV_PLIC_BASE_ADDR = 32'h40090000;
  parameter logic [31:0] TOP_EARLGREY_PINMUX_BASE_ADDR = 32'h40070000;
  parameter logic [31:0] TOP_EARLGREY_PADCTRL_BASE_ADDR = 32'h40160000;
  parameter logic [31:0] TOP_EARLGREY_ALERT_HANDLER_BASE_ADDR = 32'h40130000;
  parameter logic [31:0] TOP_EARLGREY_PWRMGR_BASE_ADDR = 32'h400A0000;
  parameter logic [31:0] TOP_EARLGREY_RSTMGR_BASE_ADDR = 32'h400B0000;
  parameter logic [31:0] TOP_EARLGREY_CLKMGR_BASE_ADDR = 32'h400C0000;
  parameter logic [31:0] TOP_EARLGREY_NMI_GEN_BASE_ADDR = 32'h40140000;
  parameter logic [31:0] TOP_EARLGREY_USBDEV_BASE_ADDR = 32'h40150000;
  parameter logic [31:0] TOP_EARLGREY_SENSOR_CTRL_BASE_ADDR = 32'h40170000;
  parameter logic [31:0] TOP_EARLGREY_OTBN_BASE_ADDR = 32'h50000000;

  // Enumeration for DIO pins.
  typedef enum {
    TopEarlgreyDioPinUsbdevDn = 0,
    TopEarlgreyDioPinUsbdevDp = 1,
    TopEarlgreyDioPinUsbdevD = 2,
    TopEarlgreyDioPinUsbdevSuspend = 3,
    TopEarlgreyDioPinUsbdevTxModeSe = 4,
    TopEarlgreyDioPinUsbdevDnPullup = 5,
    TopEarlgreyDioPinUsbdevDpPullup = 6,
    TopEarlgreyDioPinUsbdevSe0 = 7,
    TopEarlgreyDioPinUsbdevSense = 8,
    TopEarlgreyDioPinUartTx = 9,
    TopEarlgreyDioPinUartRx = 10,
    TopEarlgreyDioPinSpiDeviceSdo = 11,
    TopEarlgreyDioPinSpiDeviceSdi = 12,
    TopEarlgreyDioPinSpiDeviceCsb = 13,
    TopEarlgreyDioPinSpiDeviceSck = 14,
    TopEarlgreyDioPinCount = 15
  } top_earlgrey_dio_pin_e;

  // TODO: Enumeration for PLIC Interrupt source peripheral.
  // TODO: Enumeration for PLIC Interrupt Ids.

endpackage
