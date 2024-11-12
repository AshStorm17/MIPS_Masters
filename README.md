# MIPS_Masters

## MIPS Pipeline Simulator
A MIPS Pipeline Simulator built with Python and Streamlit that allows users to upload MIPS assembly files and simulate the execution of a pipeline. The simulator provides a cycle-by-cycle view of the register values, showing how the MIPS assembly instructions execute in stages.

## Features
- **File Upload**: Upload a MIPS assembly (.asm) file for simulation.
- **MIPS Assembly to Machine Code**: Converts MIPS assembly instructions to binary machine code.
- **Cycle-by-Cycle Execution**: Simulates each pipeline stage and shows register values for each cycle.
- **Interactive Register Viewer**: View register states in the Streamlit sidebar by selecting specific cycles.

## Project Structure
- **`pipeline`**: Contains `MIPSPipeline` class to handle cycle-by-cycle execution.
- **`parser`**: Contains the `MIPSParser` class to parse the machine code.
- **`utils`**: Holds the `MIPSAssembler` for parsing and converting MIPS assembly to machine code.
- **`components`**: Includes `ALU`, `Registers` and `Memory` that is components for handling MIPS instructions.
- **`app.py`**: The Streamlit app that serves as the user interface and controller for the simulation.

## Requirements
Install dependencies with:
```
pip install -r requirements.txt
```

## Usage
To use streamlit
```
streamlit run app.py
```
