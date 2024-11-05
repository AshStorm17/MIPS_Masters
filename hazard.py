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

    def check_data_hazard(self, rs, rt):
        """
        Check for data hazards in the decode and execute stages.
        Returns: (forward_a, forward_b, stall)
        forward_a/b: 0 (no forwarding), 1 (from EX), 2 (from MEM)
        stall: Boolean indicating if the pipeline should stall.
        """
        forward_a = 0  # Forwarding option for rs
        forward_b = 0  # Forwarding option for rt
        stall = False

        # Check EX/MEM forwarding possibility
        if self.ex_mem_reg_dst is not None:
            if rs == self.ex_mem_reg_dst and rs != 0:
                forward_a = 1
            if rt == self.ex_mem_reg_dst and rt != 0:
                forward_b = 1

        # Check MEM/WB forwarding possibility if EX/MEM not used
        if self.mem_wb_reg_dst is not None:
            if forward_a == 0 and rs == self.mem_wb_reg_dst and rs != 0:
                forward_a = 2
            if forward_b == 0 and rt == self.mem_wb_reg_dst and rt != 0:
                forward_b = 2

        # Hazard requiring stall: Check for load-use data hazard
        if self.ex_mem_reg_dst == rs or self.ex_mem_reg_dst == rt:
            stall = True  # Stall for load-use hazards only

        return forward_a, forward_b, stall

    def get_forwarded_value(self, reg_num, forward_signal):
        """Get the forwarded value based on the forwarding signal."""
        if forward_signal == 1:
            return self.ex_mem_forwarding_data
        elif forward_signal == 2:
            return self.mem_wb_forwarding_data
        return None
    
    def reset(self):
        """Reset hazard and forwarding flags for a new cycle."""
        self.stall_signal.clear()
        self.ex_mem_reg_dst = None
        self.mem_wb_reg_dst = None
        self.ex_mem_forwarding_data = None
        self.mem_wb_forwarding_data = None
        