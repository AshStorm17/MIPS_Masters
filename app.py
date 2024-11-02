import streamlit as st
from components.registers import Registers
from components.alu import ALU
from components.memory import Memory
from instructions import Instruction
from MIPS_parser import MIPSParser
from MIPSPipeline import MIPSPipeline  # Assuming MIPSPipeline class is in a separate file

# Initialize MIPS Pipeline with a default file
mips_pipeline = MIPSPipeline(file_path="assets/binary.txt")

# Sidebar for controls
st.sidebar.title("MIPS Processor Pipeline Controls")
run_pipeline = st.sidebar.button("Run Entire Pipeline")
step_pipeline = st.sidebar.button("Step Pipeline")
reset_pipeline = st.sidebar.button("Reset Pipeline")

# Pipeline state headers
st.title("MIPS Processor Pipeline Simulator")

# Display pipeline stages
st.header("Pipeline Stages")
st.subheader("Fetch Stage")
fetch_stage_text = st.empty()
st.subheader("Decode Stage")
decode_stage_text = st.empty()
st.subheader("Execute Stage")
execute_stage_text = st.empty()
st.subheader("Memory Access Stage")
memory_access_stage_text = st.empty()
st.subheader("Write-Back Stage")
write_back_stage_text = st.empty()

# Display registers and memory state
st.header("Registers")
register_display = st.empty()
st.header("Memory")
memory_display = st.empty()

# Display PC and hazard management
st.header("Program Counter (PC)")
pc_display = st.empty()

# Function to update each stage display
def update_stages(pipeline):
    fetch_stage_text.text(f"Fetch: {pipeline.IF_ID if not pipeline.IF_ID.empty() else 'Idle'}")
    decode_stage_text.text(f"Decode: {pipeline.ID_EX if not pipeline.ID_EX.empty() else 'Idle'}")
    execute_stage_text.text(f"Execute: {pipeline.EX_MEM if not pipeline.EX_MEM.empty() else 'Idle'}")
    memory_access_stage_text.text(f"Memory Access: {pipeline.MEM_WB if not pipeline.MEM_WB.empty() else 'Idle'}")
    write_back_stage_text.text(f"Write Back: Completed" if pipeline.write_done.is_set() else "Write Back: Idle")

# Function to update register and memory states
def update_components(pipeline):
    register_display.text(str(pipeline.registers.reg))
    memory_display.text(str(pipeline.memory.data))
    pc_display.text(f"PC: {pipeline.PC.value}")

# Execute Pipeline Steps
if run_pipeline:
    mips_pipeline.run_pipeline()
    update_components(mips_pipeline)
elif step_pipeline:
    # Run the pipeline step-by-step and update displays
    if not mips_pipeline.fetch_stage():
        st.write("Program has completed execution.")
    else:
        update_components(mips_pipeline)
        update_stages(mips_pipeline)
elif reset_pipeline:
    # Re-initialize the pipeline for a fresh start
    mips_pipeline = MIPSPipeline(file_path="assets/binary.txt")
    st.write("Pipeline has been reset.")
    update_components(mips_pipeline)
