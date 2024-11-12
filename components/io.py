class MemoryMappedIO:
    def __init__(self, io_base=0x10000000, io_size=0x10):
        """
        Initialize memory-mapped I/O with a base address and a fixed range for I/O.
        
        :param io_base: The base memory address for memory-mapped I/O.
        :param io_size: The size (in bytes) of the memory-mapped I/O space.
        """
        self.io_base = io_base
        self.io_size = io_size
        self.io_memory = {}

    def is_io_address(self, address):
        """
        Check if a given address is in the I/O range.
        
        :param address: The memory address to check.
        :return: True if the address is in the I/O range, False otherwise.
        """
        return self.io_base <= address < self.io_base + self.io_size

    def read_io(self, address):
        """
        Simulate reading from a memory-mapped I/O address.
        
        :param address: The memory address to read from.
        :return: The value at the I/O address, or 0 if uninitialized.
        """
        if not self.is_io_address(address):
            raise ValueError(f"Address {hex(address)} is not within the I/O range.")
        return self.io_memory.get(address, 0)

    def write_io(self, address, value):
        """
        Simulate writing to a memory-mapped I/O address.
        
        :param address: The memory address to write to.
        :param value: The value to write to the address.
        """
        if not self.is_io_address(address):
            raise ValueError(f"Address {hex(address)} is not within the I/O range.")
        self.io_memory[address] = value
        print(f"I/O write at {hex(address)}: {value}")

    def __str__(self):
        """
        Return the current state of the I/O memory.
        """
        io_state = {hex(addr): val for addr, val in self.io_memory.items()}
        return f"Memory-Mapped I/O State: {io_state}"
