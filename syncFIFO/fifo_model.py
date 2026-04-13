class FifoModel:
    def __init__(self, depth):
        self.depth  = depth
        self.buffer = []

    def write(self, data):
        if not self.full():
            self.buffer.append(data)

    def read(self):
        if not self.empty():
            return self.buffer.pop(0)

    def full(self):
        return len(self.buffer) == self.depth

    def empty(self):
        return len(self.buffer) == 0