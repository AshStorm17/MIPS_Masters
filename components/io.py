class MemoryMappedIO:
    def __init__(self, io_base=2000, io_size=50):
        """
        Initialize memory-mapped I/O with a base address and a fixed range for I/O.
        
        :param io_base: The base memory address for memory-mapped I/O.
        :param io_size: The size (in bytes) of the memory-mapped I/O space.
        """
        self.io_base = io_base
        self.io_size = io_size
        self.io_memory = []

    def is_io_address(self, address):
        """
        Check if a given address is in the I/O range.
        
        :param address: The memory address to check.
        :return: True if the address is in the I/O range, False otherwise.
        """
        return self.io_base <= address < self.io_base + self.io_size

    def __str__(self):
        """
        Return the current state of the I/O memory.
        """
        return f"Memory-Mapped I/O State: {self.io_memory}"
