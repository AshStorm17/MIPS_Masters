import multiprocessing

class HazardManager:
    def __init__(self, registers):
        # Track pipeline register destination fields for hazard detection
        self.ex_mem_reg_dst = None  # Register destination in EX/MEM stage
        self.mem_wb_reg_dst = None  # Register destination in MEM/WB stage
        self.ex_mem_forwarding_data = None  # ALU result from EX/MEM stage
        self.mem_wb_forwarding_data = None  # Data from MEM/WB stage

        self.registers = registers
        self.stall_signal = multiprocessing.Event()
    
    def update_stage_data(self, ex_mem_reg_dst, ex_mem_forwarding_data, mem_wb_reg_dst, mem_wb_forwarding_data):
        """Update EX/MEM and MEM/WB stage destination registers and data."""
        self.ex_mem_reg_dst = ex_mem_reg_dst
        self.ex_mem_forwarding_data = ex_mem_forwarding_data
        self.mem_wb_reg_dst = mem_wb_reg_dst
        self.mem_wb_forwarding_data = mem_wb_forwarding_data

    def check_data_hazard(self, rs, rt, ex_mem_data, mem_wb_data):
        """
        Check for data hazards and determine forwarding paths
        Returns: (forward_a, forward_b)
        forward_a/b: 0 (no forwarding), 1 (from MEM), 2 (from WB)
        """
        forward_a = 0  # For rs
        forward_b = 0  # For rt
        
        # EX/MEM hazard
        if ex_mem_data and 'RegDst' in ex_mem_data:
            if rs == ex_mem_data['RegDst'] and rs != 0:
                forward_a = 1
            if rt == ex_mem_data['RegDst'] and rt != 0:
                forward_b = 1
                
        # MEM/WB hazard
        elif mem_wb_data and 'RegDst' in mem_wb_data:
            if rs == mem_wb_data['RegDst'] and rs != 0:
                forward_a = 2
            if rt == mem_wb_data['RegDst'] and rt != 0:
                forward_b = 2
                
        return forward_a, forward_b

    def get_forwarded_value(self, reg_num, forward_signal, ex_mem_data, mem_wb_data):
        """Get the forwarded value based on forwarding signal"""
        if forward_signal == 0:
            return self.registers.read(reg_num)
        elif forward_signal == 1 and ex_mem_data:
            return ex_mem_data['ALU_result']
        elif forward_signal == 2 and mem_wb_data:
            if 'Mem_data' in mem_wb_data:
                return mem_wb_data['Mem_data']
            return mem_wb_data['ALU_result']
        return None
    
    def reset(self):
        """Reset hazard and forwarding flags for a new cycle."""
        self.stall_signal.clear()
        self.ex_mem_reg_dst = None
        self.mem_wb_reg_dst = None
        self.ex_mem_forwarding_data = None
        self.mem_wb_forwarding_data = None
        