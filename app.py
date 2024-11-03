import streamlit as st
from MIPSPipeline import MIPSPipeline
from utils.assembler import MIPSAssembler, parse_asm
import tempfile
import os

def main():
    st.title("MIPS Pipeline Simulator")
    st.write("Upload a MIPS assembly file to simulate the pipeline stages.")

    # File uploader for MIPS assembly file
    uploaded_file = st.file_uploader("Choose a MIPS assembly file", type="asm")

    if uploaded_file is not None:
        # Read the uploaded file
        asm_code = uploaded_file.read().decode("utf-8")
        
        # Parse and assemble MIPS instructions
        assembler = MIPSAssembler()
        instructions = asm_code.splitlines()
        
        # Assemble each instruction and collect binary code
        binary_code = []
        st.subheader("Assembly to Binary Conversion")
        for instruction in instructions:
            if instruction.strip() and not instruction.strip().startswith('#'):
                try:
                    hex_code, binary = assembler.assemble(instruction)
                    binary_code.append(binary)
                    st.write(f"{instruction:<25} -> {hex_code:<12} {binary}")
                except ValueError as e:
                    st.write(f"Error in instruction '{instruction}': {e}")
        
        # Combine binary code into one string (if needed for the pipeline)
        binary_code_str = "\n".join(binary_code)
        
        # Save binary code temporarily
        with tempfile.NamedTemporaryFile(delete=False, mode='w') as tmp_file:
            tmp_file.write(binary_code_str)
            file_path = tmp_file.name

        # Initialize and run MIPS pipeline
        pipeline = MIPSPipeline(file_path)

        if st.button("Run Simulation"):
            st.write("Running pipeline simulation...")
            
            # Run the pipeline
            pipeline.run_pipeline()
            
            # Display initial and final state of registers
            st.subheader("Initial Register State")
            st.write(pipeline.registers.reg)
            
            st.subheader("Final Register State")
            st.write(pipeline.registers.reg)
            
            # Display register states after each instruction
            st.subheader("Register States After Each Instruction")
            for i, state in enumerate(pipeline.register_states):
                st.write(f"**Instruction {i+1}**")
                st.write(state)
                st.write("---")  # Divider for clarity
            
        # Clean up temporary file after use
        os.remove(file_path)

if __name__ == "__main__":
    main()
