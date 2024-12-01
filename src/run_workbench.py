# @title Run Workbench
# @markdown Please enter your Workbench Google Sheet URL and click the **Run Workbench** button:

workbench_sheet_url = ""  # @param {type:"string"}

# Import the necessary library
import ipywidgets as widgets


# Define the function to run when the button is clicked
def run_workbench(button):
    workbench = Workbench(workbench_sheet_url)
    workbench.execute_all_chains()
    print(f"Workbench Sheet URL set to: {workbench_sheet_url}")
    print("Workbench is now running...")

# Create the button
# Create the button with custom size and styling
run_button = widgets.Button(
    description='Run Workbench',
    disabled=False,
    button_style='', 
    tooltip='Click to run the workbench',
    icon='check',
    layout=widgets.Layout(
        width='200px', 
        height='40px'  
    ),
    style=widgets.ButtonStyle(
        font_weight='bold',
        text_color='white',
        button_color='#2ecc71'
    )
)

# Attach the function to the button
run_button.on_click(run_workbench)

# Display the button
display(run_button)