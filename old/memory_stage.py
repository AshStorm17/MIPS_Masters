import multiprocessing
from components.memory import Memory

class MemoryTest:
    def __init__(self, EX_MEM):
        self.memory = Memory()  # Instantiate memory
        self.EX_MEM = EX_MEM  # Receive the EX/MEM pipeline register data
        self.MEM_WB = {}  # MEM/WB pipeline register to store memory stage results

    def mem_stage(self):
        """Simulate memory stage and display output."""
        inst = self.EX_MEM.get('instruction')

        if inst['type'] == 1 and inst['op'][:3] == "100":  # Load instruction
            address = self.EX_MEM['ALU_result']
            mem_data = "".join(self.memory.load_byte(address + i) for i in range(4))  # Load 4 bytes
            self.MEM_WB['Mem_data'] = mem_data
            self.MEM_WB['RegDst'] = self.EX_MEM['RD']
        
        elif inst['type'] == 1 and inst['op'][:3] == "101":  # Store instruction
            address = self.EX_MEM['ALU_result']
            store_data = self.EX_MEM['RT']
            for i in range(4):
                self.memory.store(store_data[i*8:(i+1)*8], address + i)  # Store each byte individually

        else:  # No memory access, pass ALU result
            self.MEM_WB['ALU_result'] = self.EX_MEM['ALU_result']
            self.MEM_WB['RegDst'] = self.EX_MEM['RD']
        
        self.MEM_WB['instruction'] = inst
        print("Memory Stage:", self.MEM_WB)


# Separate testing script for the memory stage
if __name__ == "__main__":
    # Example EX_MEM dictionary for testing
    EX_MEM = {
        'instruction': {
            'type': 1,
            'op': "100011",  # Example opcode for a load instruction
            'rt': '00010'  # Example target register
        },
        'ALU_result': 1024,  # Example memory address
        'RD': 2  # Example register destination
    }

    # Create and run MemoryTest instance
    memory_test = MemoryTest(EX_MEM)
    memory_test.mem_stage()
