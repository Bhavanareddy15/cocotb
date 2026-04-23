
class AXI4LiteModel:
    def __init__(self):
        self.registers = {i: 0 for i in range(32)}  # mirrors slave register file

    def write(self, addr, data):
        if addr < 32:
            self.registers[addr] = data

    def read(self, addr):
        if addr < 32:
            return self.registers[addr]
        return None   # out of bounds