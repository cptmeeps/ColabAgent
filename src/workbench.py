# @title Workbench

# workbench.py: Module to execute multiple chains using a Google

from typing import Dict, Any, List
import pandas as pd

DEBUG = True

class Workbench:
    """Manages execution of multiple chains using a Google Sheet template"""

    def __init__(self, sheet_url: str):
        self.sheet = GoogleSheet(sheet_url)
        self.chain_manager = ChainManager()

    def execute_all_chains(self):
        """Execute all chains specified in the input tab"""
        # Read input tab
        input_df = self.sheet.read_to_dataframe()
        print(input_df)

        # Write headers to output tab
        headers = ['chain_url', 'chain_input', 'chain_output']
        self.sheet.update_values('output!A1:C1', [headers])

        # Process each chain
        for _, row in input_df.iterrows():
            chain_url = row['chain_url']
            chain_input = row['chain_input']

            if DEBUG:
                print(f"Executing chain: {chain_url}")
                print(f"chain_input: {chain_input}")

            # Create and execute chain
            self.chain_manager = ChainManager()
            self.chain_manager.load_chain(chain_url)
            self.chain_manager.add_to_context("chain_input", chain_input)

            result = self.chain_manager.execute()
            chain_output = result.get('chain_output')

            if DEBUG:
                print(f"Output: {chain_output}")
            # Prepare results data
            output_data = {
                'chain_url': chain_url,
                'chain_input': chain_input,
                'chain_output': [chain_output]
            }

            # Determine the next available row in the output tab
            current_output = self.sheet.get_values('output!A:C')
            next_row = len(current_output) + 1

            # Update the output tab with results
            range_name = f'output!A{next_row}:C{next_row}'
            self.sheet.update_values(range_name, [list(output_data.values())])

if __name__ == "__main__":
    sheet_url = "https://docs.google.com/spreadsheets/d/1oGhppbHko50B-AR9qGtqtinwIvmQqY1M3iLOExaKm-Q/edit?gid=0#gid=0"
    workbench = Workbench(sheet_url)
    workbench.execute_all_chains()