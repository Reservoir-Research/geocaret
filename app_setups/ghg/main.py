"""Set up of the reservoir and catchment delineation application workflow.

   To be called directly or via CLI.
"""
import setup_inputs
import setup_outputs

# Set up event handlers for tasks

# * Set up input data

if __name__ == '__main__':
    setup_inputs.main()
    setup_outputs.main()
