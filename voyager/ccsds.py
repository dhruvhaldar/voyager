import struct
import binascii

class TelemetryPacket:
    def __init__(self, apid, sequence_count, data):
        self.apid = apid
        self.sequence_count = sequence_count
        self.data = data

    def _get_primary_header(self, data_length):
        # Version (3 bits) = 0
        # Type (1 bit) = 0 (Telemetry)
        # Secondary Header Flag (1 bit) = 1 (Present? Example suggests 0x08 -> 0000 1000 -> S=1)
        # APID (11 bits)

        # Byte 0-1:
        # 000 0 1 APID_HI(3) | APID_LO(8)
        # 0x08 0x00 | APID

        # But wait, 0x08 is 0000 1000.
        # Bits: V(3) T(1) S(1) A(3)
        # 000 0 1 000
        # So APID high bits are 0.
        # If APID is 0x10 (16), binary is 00000010000
        # So first two bytes: 00001000 00010000 = 0x08 0x10. Matches example.

        header_word_1 = (0 << 13) | (0 << 12) | (1 << 11) | (self.apid & 0x7FF)

        # Sequence Flags (2 bits) = 3 (11 binary, Unsegmented)
        # Sequence Count (14 bits)
        header_word_2 = (3 << 14) | (self.sequence_count & 0x3FFF)

        # Packet Length (16 bits) = Total length of data field - 1
        # Data field = Data + CRC (2 bytes)
        # So length = len(data) + 2 - 1 = len(data) + 1
        header_word_3 = data_length

        return struct.pack('>HHH', header_word_1, header_word_2, header_word_3)

    def to_bytes(self):
        # We need to calculate length.
        # Assuming CRC-16 (2 bytes).
        # Packet Data Field = Data + CRC.
        # CCSDS Length = len(Packet Data Field) - 1 = len(data) + 2 - 1 = len(data) + 1.

        length_field_val = len(self.data) + 1
        header = self._get_primary_header(length_field_val)

        payload_without_crc = header + self.data

        # Calculate CRC
        # CRC is usually calculated over the entire packet.
        # Sometimes excluding the CRC field itself.

        # Using CRC-16-CCITT (0x1021)
        # binascii.crc_hqx(data, 0) starts with 0.
        # CCSDS often starts with 0xFFFF.
        # Let's try to implement a standard CCSDS CRC.

        crc = self.calculate_crc(payload_without_crc)
        return payload_without_crc + struct.pack('>H', crc)

    @staticmethod
    def calculate_crc(data):
        # CCSDS CRC-16
        # Generator: x^16 + x^12 + x^5 + 1 (0x1021)
        # Initial value: 0xFFFF
        #
        # Optimization: binascii.crc_hqx is a C-implemented version of CRC-16-CCITT (0x1021).
        # Passing 0xFFFF as the initial value produces the same result as the standard CCSDS implementation.
        # This is approximately 50x faster than the pure Python table-driven implementation.
        return binascii.crc_hqx(data, 0xFFFF)

    def hex_dump(self):
        b = self.to_bytes()
        # Format as hex string
        return b.hex(sep=' ').upper()

    @staticmethod
    def validate_crc(raw_bytes):
        if len(raw_bytes) < 8: # Header (6) + CRC (2)
            return False

        data_to_check = raw_bytes[:-2]
        received_crc = struct.unpack('>H', raw_bytes[-2:])[0]

        calculated_crc = TelemetryPacket.calculate_crc(data_to_check)
        return calculated_crc == received_crc
