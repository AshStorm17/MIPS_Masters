import streamlit as st
import pandas as pd
from pipeline import MIPSPipeline
from utils.assembler import MIPSAssembler
from components.alu import signedVal
import tempfile
import os


def main():
    st.title("MIPS Pipeline Simulator")
    st.write("Upload a MIPS assembly file to simulate the pipeline stages.")

    # File uploader for MIPS assembly file
    uploaded_file = st.file_uploader("Choose a MIPS assembly file", type="asm")

    if uploaded_file is not None:
        # Read the uploaded file
        with tempfile.NamedTemporaryFile(delete=False, mode='w', suffix='.asm') as tmp_file:
            tmp_file.write(uploaded_file.getvalue().decode("utf-8"))
            file_path = tmp_file.name

        # Parse and assemble MIPS instructions using the temporary file path
        assembler = MIPSAssembler()
        test_instructions = assembler.parse_asm(file_path)

        # Assemble instructions to machine code
        machine_codes = assembler.assemble_binary(test_instructions)
        format_code = assembler.format_machine_codes(machine_codes)

        st.write("MIPS Assembly to Machine Code Conversion:")
        st.write("-" * 60)
        for code in format_code:
            st.write(code)
        st.write("-" * 60)

        # Save binary code temporarily
        with tempfile.NamedTemporaryFile(delete=False, mode='w') as tmp_file:
            tmp_file.write("\n".join(machine_codes))  # Writing the machine code to the file
            binary_file_path = tmp_file.name

        # Button to run the pipeline
        run_pipeline = st.button("Run Pipeline")

        if run_pipeline:
            # Initialize the MIPS pipeline using the binary file path
            pipeline = MIPSPipeline(binary_file_path)
            st.subheader("MIPS Pipeline Execution (Cycle-by-Cycle):")
            
            # Execute the pipeline cycle-by-cycle
            register_states = pipeline.run_pipeline()
            
            # Convert the list of register states into a DataFrame
            allRegNames = ["$0", "$at", "$v0", "$v1", "$a0", "$a1", "$a2", "$a3", "$t0", "$t1", "$t2", "$t3", "$t4", "$t5", "$t6", "$t7", "$s0", "$s1", "$s2", "$s3", "$s4", "$s5", "$s6", "$s7", "$t8", "$t9", "$k0", "$k1", "$gp", "$sp", "$fp", "$ra"]
            
            register_states_per_cycle = []  # List to hold all register states for each cycle

            # Process each cycle (state) and collect register values
            for i, state in enumerate(register_states):
                # Convert each register value using signedVal
                allRegValues = [signedVal(val) for val in state]
                register_states_per_cycle.append(allRegValues)

            # Create a DataFrame from the collected register states
            register_df = pd.DataFrame(register_states_per_cycle, columns=allRegNames)

            # Split the DataFrame into four parts
            split_register_df = [register_df.iloc[:, i:i+8] for i in range(0, len(allRegNames), 8)]

            st.write("Register States Over Cycles:")

            # Display each part of the register table
            for i, part in enumerate(split_register_df):
                st.write(f"Part {i+1}")
                st.dataframe(part)

            st.write("Pipeline execution completed.")
        
        # Clean up the temporary file
        os.remove(file_path)
        os.remove(binary_file_path)