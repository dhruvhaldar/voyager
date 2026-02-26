from array import array

class EDAC:
    """
    Error Detection and Correction using Hamming Code.
    Simulates SEC (Single Error Correction) for 8-bit data.
    """

    # Lookup tables for performance
    _ENCODE_TABLE = []
    _DECODE_TABLE = []
    _DECODE_DATA_TABLE = None # Will be array('B')

    # Status codes
    STATUS_OK = 0
    STATUS_CORRECTED = 1

    STATUS_MAP = {
        STATUS_OK: "OK",
        STATUS_CORRECTED: "CORRECTED_SINGLE_BIT_ERROR"
    }

    # We will use a simple Hamming scheme.
    # For 8 data bits (d1..d8), we need 4 parity bits (p1, p2, p4, p8).
    # Total 12 bits.
    # Positions: 1(p1), 2(p2), 3(d1), 4(p4), 5(d2), 6(d3), 7(d4), 8(p8), 9(d5), 10(d6), 11(d7), 12(d8).

    @staticmethod
    def _compute_encode(byte_val):
        """Encodes an 8-bit byte into a 12-bit Hamming code using bitwise operations."""
        # Calculate parity bits directly from byte_val using masks

        # p1 (pos 1): checks 1, 3, 5, 7, 9, 11 (1-based)
        # Data bits at 3, 5, 7, 9, 11 map to input bits 0, 1, 3, 4, 6
        # Mask: (1<<0)|(1<<1)|(1<<3)|(1<<4)|(1<<6) = 0x5B (0101 1011)
        # Use bin().count('1') for compatibility with Python < 3.10
        p1 = bin(byte_val & 0x5B).count('1') & 1

        # p2 (pos 2): checks 2, 3, 6, 7, 10, 11
        # Data bits at 3, 6, 7, 10, 11 map to input bits 0, 2, 3, 5, 6
        # Mask: (1<<0)|(1<<2)|(1<<3)|(1<<5)|(1<<6) = 0x6D (0110 1101)
        p2 = bin(byte_val & 0x6D).count('1') & 1

        # p4 (pos 4): checks 4, 5, 6, 7, 12
        # Data bits at 5, 6, 7, 12 map to input bits 1, 2, 3, 7
        # Mask: (1<<1)|(1<<2)|(1<<3)|(1<<7) = 0x8E (1000 1110)
        p4 = bin(byte_val & 0x8E).count('1') & 1

        # p8 (pos 8): checks 8, 9, 10, 11, 12
        # Data bits at 9, 10, 11, 12 map to input bits 4, 5, 6, 7
        # Mask: (1<<4)|(1<<5)|(1<<6)|(1<<7) = 0xF0 (1111 0000)
        p8 = bin(byte_val & 0xF0).count('1') & 1

        # Construct 12-bit word
        # p1(0), p2(1), d1(2), p4(3), d2(4), d3(5), d4(6), p8(7), d5(8), d6(9), d7(10), d8(11)
        # Input bits mapping to output positions:
        # bit 0 -> pos 2 (<<2)
        # bits 1-3 -> pos 4-6 (<<3)
        # bits 4-7 -> pos 8-11 (<<4)

        encoded = p1 | (p2 << 1) | ((byte_val & 1) << 2) | (p4 << 3) | \
                  ((byte_val & 0x0E) << 3) | (p8 << 7) | ((byte_val & 0xF0) << 4)

        return encoded

    @staticmethod
    def _compute_decode(encoded_val):
        """
        Decodes a 12-bit Hamming code using optimized bitwise operations.
        Returns (decoded_byte, status_code).
        Status code: 0 (OK), 1 (CORRECTED)
        """
        # Calculate parity bits using bit_count on masked values
        # This avoids creating a list of 12 bits and iterating multiple times.

        # c1 checks 1, 3, 5, 7, 9, 11 (1-based) -> indices 0, 2, 4, 6, 8, 10
        # Mask: 0x555 (0101 0101 0101)
        c1 = bin(encoded_val & 0x555).count('1') & 1

        # c2 checks 2, 3, 6, 7, 10, 11 (1-based) -> indices 1, 2, 5, 6, 9, 10
        # Mask: 0x666 (0110 0110 0110)
        c2 = bin(encoded_val & 0x666).count('1') & 1

        # c4 checks 4, 5, 6, 7, 12 (1-based) -> indices 3, 4, 5, 6, 11
        # Mask: 0x878 (1000 0111 1000)
        c4 = bin(encoded_val & 0x878).count('1') & 1

        # c8 checks 8, 9, 10, 11, 12 (1-based) -> indices 7, 8, 9, 10, 11
        # Mask: 0xF80 (1111 1000 0000)
        c8 = bin(encoded_val & 0xF80).count('1') & 1

        syndrome = c1 | (c2 << 1) | (c4 << 2) | (c8 << 3)

        status_code = EDAC.STATUS_OK
        if syndrome != 0:
            status_code = EDAC.STATUS_CORRECTED
            # Flip the error bit
            encoded_val ^= (1 << (syndrome - 1))

        # Extract data bits from (potentially corrected) encoded_val
        # d1..d8 -> pos 3, 5, 6, 7, 9, 10, 11, 12 (1-based)
        # indices 2, 4, 5, 6, 8, 9, 10, 11 (0-based)

        # d1 (bit 2) -> output bit 0 (>>2)
        # d2-d4 (bits 4-6) -> output bits 1-3 (>>3)
        # d5-d8 (bits 8-11) -> output bits 4-7 (>>4)

        d = ((encoded_val >> 2) & 1) | \
            ((encoded_val >> 3) & 0x0E) | \
            ((encoded_val >> 4) & 0xF0)

        return d, status_code

    @classmethod
    def _init_tables(cls):
        """Populates the lookup tables."""
        # Encode table (0-255)
        cls._ENCODE_TABLE = [cls._compute_encode(i) for i in range(256)]

        # Decode table (0-4095)
        cls._DECODE_TABLE = [cls._compute_decode(i) for i in range(4096)]

        # Optimized Decode Data Table (no status codes, byte array)
        cls._DECODE_DATA_TABLE = array('B', [0] * 4096)
        for i in range(4096):
            # Extract just the data part from the existing compute logic
            d, _ = cls._compute_decode(i)
            cls._DECODE_DATA_TABLE[i] = d

    @staticmethod
    def encode(byte_val):
        """Encodes an 8-bit byte into a 12-bit Hamming code using lookup table."""
        # Use table for O(1) performance
        # Mask input to 8 bits to match original behavior and prevent IndexError
        return EDAC._ENCODE_TABLE[byte_val & 0xFF]

    @staticmethod
    def decode_fast(encoded_val):
        """
        Decodes a 12-bit Hamming code using lookup table.
        Returns (decoded_byte, status_code_int).
        """
        # Use table for O(1) performance
        # Mask input to 12 bits to match original behavior and prevent IndexError
        return EDAC._DECODE_TABLE[encoded_val & 0xFFF]

    @staticmethod
    def decode_data_only(encoded_val):
        """
        Decodes a 12-bit Hamming code using optimized array lookup.
        Returns only the decoded byte.
        Faster than decode_fast as it avoids tuple creation and unpacking.
        """
        return EDAC._DECODE_DATA_TABLE[encoded_val & 0xFFF]

    @staticmethod
    def decode(encoded_val):
        """
        Decodes a 12-bit Hamming code using lookup table.
        Returns (decoded_byte, status_string).
        """
        val, status_code = EDAC.decode_fast(encoded_val)
        return val, EDAC.STATUS_MAP[status_code]

# Initialize tables on module import
EDAC._init_tables()
