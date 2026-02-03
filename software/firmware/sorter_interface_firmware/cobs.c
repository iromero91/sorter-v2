/*
 * Sorter Interface Firmware - Consistent Overhead Byte Stuffing (COBS) Functions
 * Copyright (C) 2017-2026 Jose I Romero
 * 
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 * 
 * The above copyright notice and this permission notice shall be included in
 * all copies or substantial portions of the Software.
 * 
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE 
 * SOFTWARE.
*/

#include "cobs.h"

/**
 * \brief In-place COBS encoding for short packets
 * 
 * Based on the algorith described by Jason Sachs at https://www.embeddedrelated.com/showarticle/113.php
 * The packet must be less than 253 bytes long and start with a "phantom" 0 byte.
 * 
 * @param data Pointer to the data buffer to encode (must start with 0 byte).
 * @param length Length of the data buffer in bytes. (including the intial 0 byte)
 */

int COBS_short_encode_inplace(char* data, int length) {
    uint8_t *counter = (uint8_t *)data;
    if (data[0] != 0) return -1; // First byte must be 0
    if (length > 253) return -1; // Too long for this function
    *counter = 1;
    for (int i = 1; i < length; i++) {
        if (data[i] == 0) {
            counter = (uint8_t *)&data[i];
            *counter = 1;
        } else {
            (*counter)++;
        }
    }
    return 0;
}

/**
 * \brief In-place COBS decoding for short packets
 * 
 * Based on the algorith described by Jason Sachs at https://www.embeddedrelated.com/showarticle/113.php
 * The packet must be less than 253 bytes long.
 * 
 * @param data Pointer to the data buffer to decode.
 * @param length Length of the data buffer in bytes.
 */
int COBS_short_decode_inplace(char* data, int length) {
    if (length > 253) return -1; // Too long for this function
    int index = 0;
    // Replace each counter byte with 0, then skip ahead by the counter value to remove the next 0
    while (index < length) {
        uint8_t counter = (uint8_t)data[index];
        data[index] = 0;
        index += counter;
    }
    return 0;
}