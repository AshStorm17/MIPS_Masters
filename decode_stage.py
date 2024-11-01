import multiprocessing
from components.registers import Registers
from instructions import Instruction
from fetch_stage import FetchTest

class DecodeTest:
    def __init__(self, IF_ID, ID_EX):
        self.IF_ID = IF_ID  # Queue for fetched instructions
        self.ID_EX = ID_EX  # Queue for decoded instructions
        self.registers = Registers(initialise=True)  # Initialize registers

    def decode_stage(self):
        """Simulate decode stage and display output."""
        while True:
            if not self.IF_ID.empty():
                fetched_data = self.IF_ID.get()

                # Check for end signal
                if fetched_data is None:  # If None is received, break the loop
                    break

                IR = fetched_data['IR']
                opcode = int(IR[:6], 2)
    
                # Create the instruction object based on opcode
                if opcode == 0:
                    inst_type = 0  # R-type
                elif opcode in [2, 3]:
                    inst_type = 2  # J-type
                else:
                    inst_type = 1  # I-type
                
                inst = Instruction(type=inst_type, instruction=IR)
                fields = inst.get_fields()

                # Prepare the data to send to the ID_EX stage
                id_ex_data = {
                    'instruction': inst,
                    'PC': fetched_data['PC'],
                    'RS': self.registers.read(int(fields['rs'], 2)),  # Read value of RS register
                }

                # Handle I-type immediate value and sign extension
                if inst.type == 1:  # I-type instruction
                    immediate = int(IR[16:], 2)  # Immediate is bits 16-31
                    if (immediate & 0x8000):  # Sign extend if negative
                        immediate |= 0xFFFF0000
                    id_ex_data['Immediate'] = immediate
                
                # Handle J-type instruction
                if inst.type == 2:  # J-type instruction
                    id_ex_data['Address'] = int(IR[6:], 2)  # Convert address to decimal

                # Create a dictionary with the mapped values
                decoded_values = {
                    'Instruction': id_ex_data['instruction'],
                    'PC': id_ex_data['PC'],
                    'RS': id_ex_data['RS'],
                }

                # Include RT only for R-type and J-type instructions
                if inst.type == 0 or inst.type == 2:  # R-type or J-type
                    id_ex_data['RT'] = self.registers.read(int(fields['rt'], 2))  # Read RT register
                    decoded_values['RT'] = id_ex_data['RT']
                
                # Add Immediate or Address if they exist
                if 'Immediate' in id_ex_data:
                    decoded_values['Immediate'] = id_ex_data['Immediate']
                if 'Address' in id_ex_data:
                    decoded_values['Address'] = id_ex_data['Address']

                # Send the decoded values to the ID_EX queue
                self.ID_EX.put(decoded_values)
                print("Decoded instruction:", decoded_values)

def run_pipeline(file_path):
    # Create multiprocessing Queues for the IF_ID and ID_EX stages
    IF_ID = multiprocessing.Queue()
    ID_EX = multiprocessing.Queue()
    
    # Create and start the FetchTest process
    fetch_test = FetchTest(file_path, IF_ID)
    fetch_process = multiprocessing.Process(target=fetch_test.fetch_stage)
    fetch_process.start()

    # Create DecodeTest instance and run the decode stage
    decode_test = DecodeTest(IF_ID, ID_EX)

    # Run the decode stage in a separate process
    decode_process = multiprocessing.Process(target=decode_test.decode_stage)
    decode_process.start()

    # Wait for the fetch process to finish
    fetch_process.join()
    
    # After fetching is done, signal the decode stage to stop
    IF_ID.put(None)  # Signal that no more instructions will be fetched

    # Wait for the decode process to finish
    decode_process.join()

if __name__ == "__main__":
    run_pipeline(file_path="assets/binary.txt")
