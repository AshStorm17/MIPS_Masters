import streamlit as st
from pipeline import MIPSPipeline
from utils.assembler import MIPSAssembler
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
        machine_codes, labels = assembler.assemble(test_instructions)

        st.write("MIPS Assembly to Machine Code Conversion:")
        st.write("-" * 60)
        for machine_code in machine_codes:
            st.write(machine_code)
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
            
            pass
        
        # Clean up the temporary file
        os.remove(file_path)
        os.remove(binary_file_path)
        
if __name__ == "__main__":
    main()
