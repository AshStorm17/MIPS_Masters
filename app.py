import streamlit as st
import pandas as pd
from pipeline import MIPSPipeline
from utils.assembler import MIPSAssembler
from components.alu import signedVal
import tempfile
import os


def cleanup_files(file_path, binary_file_path):
    # Clean up the temporary files
    if file_path:
        os.remove(file_path)
    if binary_file_path:
        os.remove(binary_file_path)

def main_2():
    st.title("MIPS Pipeline Simulator")
    st.write("Choose an option to simulate the pipeline stages:")

    # Option to upload MIPS assembly file
    upload_option = st.radio("Select an option", ("Upload MIPS file", "Enter MIPS code"))
    file_path = None
    binary_file_path = None

    if upload_option == "Upload MIPS file":
        # File uploader for MIPS assembly file
        uploaded_file = st.file_uploader("Choose a MIPS assembly file", type="asm")

        if uploaded_file is not None:
            # Read the uploaded file
            with tempfile.NamedTemporaryFile(delete=False, mode='w', suffix='.asm') as tmp_file:
                tmp_file.write(uploaded_file.getvalue().decode("utf-8"))
                file_path = tmp_file.name
    else:
        # Text area for MIPS assembly code
        mips_code = st.text_area("Enter MIPS Assembly Code", height=200)

        if mips_code:
            # Write the MIPS code to a temporary file
            with tempfile.NamedTemporaryFile(delete=False, mode='w', suffix='.asm') as tmp_file:
                tmp_file.write(mips_code)
                file_path = tmp_file.name

    # # Initialize session state for assembly completion
    # if "assembled" not in st.session_state:
    #     st.session_state.assembled = False

    # assemble_button = st.button("Assemble")

    # if assemble_button and file_path:
    #     assembler = MIPSAssembler()
    #     test_instructions = assembler.parse_asm(file_path)

    #     # Assemble instructions to machine code
    #     machine_codes = assembler.assemble_binary(test_instructions)
    #     format_code = assembler.format_machine_codes(machine_codes)

    #     # Display the MIPS Assembly to Machine Code Conversion
    #     st.write("MIPS Assembly to Machine Code Conversion:")
    #     st.write("-" * 60)
    #     for code in format_code:
    #         st.write(code)
    #     st.write("-" * 60)
    #     # Set assembled flag to True
    #     st.session_state.assembled = True
    #     # Save binary code temporarily
    #     with tempfile.NamedTemporaryFile(delete=False, mode='w') as tmp_file:
    #         tmp_file.write("\n".join(machine_codes))  # Writing the machine code to the file
    #         binary_file_path = tmp_file.name
        
    # print(st.session_state.assembled,'-----',binary_file_path)
    # if st.session_state.assembled and binary_file_path: 
    if st.button("Run Pipeline"):
        # Initialize the MIPS pipeline using the binary file path
        assembler = MIPSAssembler()
        test_instructions = assembler.parse_asm(file_path)

        # Assemble instructions to machine code
        machine_codes = assembler.assemble_binary(test_instructions)
        format_code = assembler.format_machine_codes(machine_codes)

        # Display the MIPS Assembly to Machine Code Conversion
        st.write("MIPS Assembly to Machine Code Conversion:")
        st.write("-" * 60)
        for code in format_code:
            st.write(code)
        st.write("-" * 60)
        # Set assembled flag to True
        st.session_state.assembled = True
        # Save binary code temporarily
        with tempfile.NamedTemporaryFile(delete=False, mode='w') as tmp_file:
            tmp_file.write("\n".join(machine_codes))  # Writing the machine code to the file
            binary_file_path = tmp_file.name
        pipeline = MIPSPipeline(binary_file_path)
        st.subheader("MIPS Pipeline Execution (Cycle-by-Cycle):")

        # Execute the pipeline cycle-by-cycle
        register_states = pipeline.run_pipeline()

        # Convert the list of register states into a DataFrame
        all_reg_names = ["$0", "$at", "$v0", "$v1", "$a0", "$a1", "$a2", "$a3",
                        "$t0", "$t1", "$t2", "$t3", "$t4", "$t5", "$t6", "$t7",
                        "$s0", "$s1", "$s2", "$s3", "$s4", "$s5", "$s6", "$s7",
                        "$t8", "$t9", "$k0", "$k1", "$gp", "$sp", "$fp", "$ra"]
        register_states_per_cycle = []

        # Process each cycle (state) and collect register values
        for i, state in enumerate(register_states):
            # Convert each register value using signedVal
            all_reg_values = [signedVal(val) for val in state]
            register_states_per_cycle.append(all_reg_values)

        # Create a DataFrame from the collected register states
        register_df = pd.DataFrame(register_states_per_cycle, columns=all_reg_names)

        # Display the register states over cycles
        st.write("Register States Over Cycles:")

        # Split the DataFrame into tabs for better readability
        num_tabs = 4
        tab_names = [f"Registers {i+1}-{i+8}" for i in range(0, len(all_reg_names), 8)]
        tabs = st.tabs(tab_names)

        for i, tab in enumerate(tabs):
            with tab:
                st.dataframe(register_df.iloc[:, i*8:(i+1)*8])

        st.write("Pipeline execution completed.")

        # Clean up the temporary files
        cleanup_files(file_path, binary_file_path)


if __name__ == "__main__":
    main_2()
