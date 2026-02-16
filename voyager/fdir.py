class EDAC:
    """
    Error Detection and Correction using Hamming Code.
    Simulates SEC (Single Error Correction) for 8-bit data.
    """

    # Lookup tables for performance
    _ENCODE_TABLE = []
    _DECODE_TABLE = []

    # Internal status codes
    _STATUS_OK = 0
    _STATUS_CORRECTED = 1

    _STATUS_MAP = {
        _STATUS_OK: "OK",
        _STATUS_CORRECTED: "CORRECTED_SINGLE_BIT_ERROR"
    }

    # We will use a simple Hamming scheme.
    # For 8 data bits (d1..d8), we need 4 parity bits (p1, p2, p4, p8).
    # Total 12 bits.
    # Positions: 1(p1), 2(p2), 3(d1), 4(p4), 5(d2), 6(d3), 7(d4), 8(p8), 9(d5), 10(d6), 11(d7), 12(d8).

    @staticmethod
    def _compute_encode(byte_val):
        """Encodes an 8-bit byte into a 12-bit Hamming code."""
        d = [
            (byte_val >> 0) & 1, # d1 (pos 3) - LSB of input
            (byte_val >> 1) & 1, # d2 (pos 5)
            (byte_val >> 2) & 1, # d3 (pos 6)
            (byte_val >> 3) & 1, # d4 (pos 7)
            (byte_val >> 4) & 1, # d5 (pos 9)
            (byte_val >> 5) & 1, # d6 (pos 10)
            (byte_val >> 6) & 1, # d7 (pos 11)
            (byte_val >> 7) & 1, # d8 (pos 12) - MSB
        ]

        # Calculate parity bits
        # p1 (pos 1): check 1, 3, 5, 7, 9, 11
        p1 = d[0] ^ d[1] ^ d[3] ^ d[4] ^ d[6]

        # p2 (pos 2): check 2, 3, 6, 7, 10, 11
        p2 = d[0] ^ d[2] ^ d[3] ^ d[5] ^ d[6]

        # p4 (pos 4): check 4, 5, 6, 7, 12
        p4 = d[1] ^ d[2] ^ d[3] ^ d[7]

        # p8 (pos 8): check 8, 9, 10, 11, 12
        p8 = d[4] ^ d[5] ^ d[6] ^ d[7]

        # Construct 12-bit word
        # p1 p2 d1 p4 d2 d3 d4 p8 d5 d6 d7 d8
        encoded = (p1 << 0) | (p2 << 1) | (d[0] << 2) | (p4 << 3) | \
                  (d[1] << 4) | (d[2] << 5) | (d[3] << 6) | (p8 << 7) | \
                  (d[4] << 8) | (d[5] << 9) | (d[6] << 10) | (d[7] << 11)

        return encoded

    @staticmethod
    def _compute_decode(encoded_val):
        """
        Decodes a 12-bit Hamming code.
        Returns (decoded_byte, status_code).
        Status code: 0 (OK), 1 (CORRECTED)
        """
        # Extract bits
        bits = [(encoded_val >> i) & 1 for i in range(12)]
        # Positions are 1-based in Hamming theory, but 0-based index here.
        # pos 1 -> bits[0], pos 2 -> bits[1], etc.

        # Recalculate parity
        # c1 checks 1, 3, 5, 7, 9, 11
        c1 = bits[0] ^ bits[2] ^ bits[4] ^ bits[6] ^ bits[8] ^ bits[10]

        # c2 checks 2, 3, 6, 7, 10, 11
        c2 = bits[1] ^ bits[2] ^ bits[5] ^ bits[6] ^ bits[9] ^ bits[10]

        # c4 checks 4, 5, 6, 7, 12
        c4 = bits[3] ^ bits[4] ^ bits[5] ^ bits[6] ^ bits[11]

        # c8 checks 8, 9, 10, 11, 12
        c8 = bits[7] ^ bits[8] ^ bits[9] ^ bits[10] ^ bits[11]

        syndrome = c1 | (c2 << 1) | (c4 << 2) | (c8 << 3)

        status_code = EDAC._STATUS_OK
        if syndrome != 0:
            # Single bit error at position 'syndrome'
            status_code = EDAC._STATUS_CORRECTED

            # Flip the bit
            # syndrome is 1-based index
            encoded_val ^= (1 << (syndrome - 1))

            # Re-extract bits after correction
            bits = [(encoded_val >> i) & 1 for i in range(12)]

        # Extract data bits
        # d1..d8 -> pos 3, 5, 6, 7, 9, 10, 11, 12
        # indices 2, 4, 5, 6, 8, 9, 10, 11

        d = 0
        d |= bits[2] << 0
        d |= bits[4] << 1
        d |= bits[5] << 2
        d |= bits[6] << 3
        d |= bits[8] << 4
        d |= bits[9] << 5
        d |= bits[10] << 6
        d |= bits[11] << 7

        return d, status_code

    @classmethod
    def _init_tables(cls):
        """Populates the lookup tables."""
        # Encode table (0-255)
        cls._ENCODE_TABLE = [cls._compute_encode(i) for i in range(256)]

        # Decode table (0-4095)
        cls._DECODE_TABLE = [cls._compute_decode(i) for i in range(4096)]

    @staticmethod
    def encode(byte_val):
        """Encodes an 8-bit byte into a 12-bit Hamming code using lookup table."""
        # Use table for O(1) performance
        # Mask input to 8 bits to match original behavior and prevent IndexError
        return EDAC._ENCODE_TABLE[byte_val & 0xFF]

    @staticmethod
    def decode(encoded_val):
        """
        Decodes a 12-bit Hamming code using lookup table.
        Returns (decoded_byte, status).
        """
        # Use table for O(1) performance
        # Mask input to 12 bits to match original behavior and prevent IndexError
        val, status_code = EDAC._DECODE_TABLE[encoded_val & 0xFFF]
        return val, EDAC._STATUS_MAP[status_code]

# Initialize tables on module import
EDAC._init_tables()
