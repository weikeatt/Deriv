import solara
import pandas as pd
from datetime import datetime
from pathlib import Path

# Load data from Excel file
excel_file_path = "applicant_data.xlsx"  # Specify your Excel file path here
df = pd.read_excel(excel_file_path)

# Ensure the DataFrame contains the expected columns
required_columns = ["Applicant ID", "Application Date", "Full Name", "Status", "Details"]
if not all(col in df.columns for col in required_columns):
    raise ValueError(f"The Excel file must contain the following columns: {required_columns}")

# Convert 'Application Date' to datetime if it is not already
df['Application Date'] = pd.to_datetime(df['Application Date'], errors='coerce')

# Function to save updates to the Excel file
def save_updates():
    df.to_excel(excel_file_path, index=False)

def handle_approval(applicant_id, comments):
    # Update the applicant's status to 'Approved' and add comments
    global df  # Access the global DataFrame
    df.loc[df['Applicant ID'] == applicant_id, 'Status'] = 'Approved'
    df.loc[df['Applicant ID'] == applicant_id, 'Details'] = comments

    # Write the updated DataFrame back to the Excel file
    save_updates()
    print(f"Application {applicant_id} approved with comments: {comments}")

def handle_rejection(applicant_id, comments):
    # Update the applicant's status to 'Rejected' and add comments
    global df  # Access the global DataFrame
    df.loc[df['Applicant ID'] == applicant_id, 'Status'] = 'Rejected'
    df.loc[df['Applicant ID'] == applicant_id, 'Details'] = comments

    # Write the updated DataFrame back to the Excel file
    save_updates()
    print(f"Application {applicant_id} rejected with comments: {comments}")


@solara.component
def Page():
    # Load custom CSS for styling
    solara.Style(Path("custom.css"))
    
    # State management
    selected_page, set_selected_page = solara.use_state("Admin")  # Tracks the currently selected page

    # Filter state for searching applicants
    filter_text, set_filter_text = solara.use_state("")  # Text input for filtering
    include_approved, set_include_approved = solara.use_state(True)  # Checkbox to include approved applicants
    last_updated, set_last_updated = solara.use_state(datetime.now().strftime("%Y-%m-%d %H:%M"))  # Timestamp for last update

    # State for selected applicant and admin comments
    selected_applicant, set_selected_applicant = solara.use_state(None)  # Currently selected applicant ID
    admin_comments, set_admin_comments = solara.use_state("")  # Comments entered by the admin
    show_confirmation, set_show_confirmation = solara.use_state(False)  # State for showing confirmation popup

    # Clear comments when the selected applicant changes
    solara.use_effect(
        lambda: set_admin_comments(""),  # Reset comments field
        [selected_applicant]  # Dependency: triggers when selected_applicant changes
    )

    # State for pagination
    current_page, set_current_page = solara.use_state(0)  # Tracks the current page for applicant listings


    # Create the top navigation bar
    with solara.AppBar():
        solara.Markdown("The Think Tank")


    # Create the sidebar for navigation and information display
    with solara.Sidebar():
        # Display the last updated timestamp
        solara.Markdown(f"**Last Updated:**<br> {last_updated} (UTC+8)")

        # Section header for page navigation
        solara.Markdown("## Pages")

        # Column layout for navigation buttons
        with solara.Column():
            # Button for navigating to the Admin page
            solara.Button("Admin", on_click=lambda: set_selected_page("Admin"))

            # Button for navigating to the Reporting page
            solara.Button("Reporting", on_click=lambda: set_selected_page("Reporting"))

            # Button for navigating to the Analytics page
            solara.Button("Analytics", on_click=lambda: set_selected_page("Analytics"))


    # Create a main content area with a specified left margin
    with solara.Column(style={"marginLeft": "200px"}):
        # Check if the selected page is "Admin"
        if selected_page == "Admin":
            # Calculate counts for each application status
            status_counts = df['Status'].value_counts()

            # Create a container for the status cards
            with solara.Div(style={"display": "flex", "flexWrap": "wrap", "gap": "10px"}):
                # Define card data for each status
                card_data = [
                    {"title": "Approved", "symbol": "✅", "color": "green", "borderColor": "green", "number": status_counts.get("Approved", 0), "info": "Total number of approved applications"},
                    {"title": "In Progress", "symbol": "🔄", "color": "orange", "borderColor": "orange", "number": status_counts.get("In Progress", 0), "info": "Total number of applications currently being processed."},
                    {"title": "Alerts", "symbol": "⚠️", "color": "darkred", "borderColor": "darkred", "number": status_counts.get("Alerts", 0), "info": "Total number of applications that are suspicious"},
                    {"title": "Pending Approval", "symbol": "⏳", "color": "blue", "borderColor": "blue", "number": status_counts.get("Pending Approval", 0), "info": "Total number of applications awaiting approval"},
                    {"title": "Rejected", "symbol": "❌", "color": "red", "borderColor": "red", "number": status_counts.get("Rejected", 0), "info": "Total number of rejected applications"},
                ]

                # Loop through each card data entry to create the cards
                for card in card_data:
                    # Define styles for each card
                    card_style = {
                        "border": f"2px solid {card['borderColor']}",
                        "borderRadius": "5px",
                        "padding": "8px",
                        "flex": "1 1 150px",  # Flex properties for responsiveness
                        "cursor": "pointer",
                        "height": "100px",
                        "position": "relative"
                    }

                    # Create the card container
                    with solara.Div(style=card_style):
                        # Add a tooltip with information about the card
                        with solara.Tooltip(solara.Markdown(card['info']), color="white"):
                            # Information icon in the top right corner
                            solara.Div("ℹ️", style={"position": "absolute", "top": "8px", "right": "8px", "fontSize": "16px", "color": "gray", "cursor": "pointer"})

                        # Layout for the card content
                        with solara.Div(style={"display": "flex", "alignItems": "center"}):
                            # Display the status symbol
                            solara.Div(card["symbol"], style={"color": card["color"], "fontSize": "40px", "marginRight": "10px"})
                            
                            # Column layout for title and count
                            solara.Div(
                                style={"display": "flex", "flexDirection": "column"},
                                children=[
                                    solara.Markdown(f"**{card['title']}**", style={"color": card["color"], "fontSize": "18px", "fontWeight": "bold"}),
                                    solara.Markdown(f"{card['number']}", style={"fontSize": "24px", "fontWeight": "bold"})
                                ]
                            )


            # Split section below cards
            with solara.Div(style={"marginTop": "0px", "display": "flex"}):
                with solara.lab.Tabs():  # Create tabs for the application section
                    with solara.lab.Tab("Application Table", icon_name="mdi-table", style="font-weight: bold"):
                        with solara.Div(style={"display": "flex", "flexDirection": "column", "flex": "1"}):
                            # Search input and checkbox
                            with solara.Div(style={"display": "flex", "alignItems": "center", "gap": "10px"}):
                                solara.InputText(
                                    label="Search by ID, Name or Status",
                                    value=filter_text,
                                    on_value=set_filter_text,
                                    continuous_update=True,
                                    style={"flex": "1", "maxWidth": "280px", "minWidth": "200px"}
                                )
                                solara.Checkbox(label="Include Approved Applications", value=include_approved, on_value=set_include_approved)

                            # Filter the DataFrame based on input
                            filtered_df = df[
                                (include_approved | (df['Status'] != "Approved")) & 
                                (
                                    df['Applicant ID'].astype(str).str.contains(filter_text, case=False) |
                                    df['Full Name'].str.contains(filter_text, case=False) |
                                    df['Status'].str.contains(filter_text, case=False)
                                )
                            ]

                            sorted_df = filtered_df.sort_values(by="Application Date", ascending=True)
                            sorted_df['Application Date'] = sorted_df['Application Date'].dt.strftime('%Y-%m-%d %H:%M')

                            # Pagination setup
                            items_per_page = 5
                            start_idx = current_page * items_per_page
                            end_idx = start_idx + items_per_page
                            paginated_df = sorted_df.iloc[start_idx:end_idx]

                            # Total items and pages
                            total_items = len(sorted_df)
                            total_pages = (total_items - 1) // items_per_page + 1

                            # Display paginated DataFrame as clickable buttons
                            for _, row in paginated_df.iterrows():
                                button_style = {
                                    "margin": "5px",
                                    "padding": "10px",
                                    "border": "1px solid #ccc",
                                    "borderRadius": "5px",
                                    "cursor": "pointer",
                                    "backgroundColor": "#f9f9f9",
                                    "width": "100%",
                                    "textAlign": "left",
                                    "display": "flex",
                                    "alignItems": "center"
                                }

                                solara.Button(
                                    label=f"Applicant ID: {row['Applicant ID']} | Name: {row['Full Name']} | Status: {row['Status']}",
                                    style=button_style,
                                    on_click=lambda applicant_id=row['Applicant ID']: (set_selected_applicant(applicant_id))
                                )

                            # Pagination controls
                            with solara.Div(style={"display": "flex", "justifyContent": "space-between", "marginTop": "10px"}):
                                solara.Button(
                                    label="Previous",
                                    on_click=lambda: set_current_page(max(current_page - 1, 0)),
                                    disabled=current_page == 0
                                )

                                solara.Markdown(f"Page {current_page + 1} of {total_pages} | Total Applications: {total_items}")

                                solara.Button(
                                    label="Next",
                                    on_click=lambda: set_current_page(min(current_page + 1, total_pages - 1)),
                                    disabled=end_idx >= total_items
                                )



                solara.Div(style={"width": "1px", "backgroundColor": "black", "margin": "0 10px"})  # Divider

                with solara.lab.Tabs():
                    with solara.lab.Tab("Applicant Information", icon_name="mdi-information", style="font-weight: bold"):
                        # Check if an applicant is selected
                        if selected_applicant is not None:
                            applicant_info = df[df['Applicant ID'] == selected_applicant].iloc[0]
                            
                            with solara.Div(style={"display": "flex", "alignItems": "flex-start", "gap": "20px", "margin": "10px 0"}):
                                # Profile image handling
                                default_image_path = Path("default_profile_picture.jpg")
                                profile_image_path = Path("profile_picture.jpg")
                                final_image_path = profile_image_path if profile_image_path.exists() else default_image_path

                                with solara.Div(style={
                                    "border": "1px solid #ddd",
                                    "borderRadius": "8px",
                                    "padding": "8px",
                                    "display": "inline-block",
                                    "boxShadow": "0 1px 5px rgba(0, 0, 0, 0.1)",
                                    "backgroundColor": "#fff",
                                    "maxWidth": "250px"  # Set a smaller max width
                                }):
                                    solara.Image(final_image_path)  # Display profile image

                                    # Status color mapping
                                    status_color_map = {
                                        "APPROVED": "green",
                                        "IN PROGRESS": "orange",
                                        "ALERTS": "darkred",
                                        "PENDING APPROVAL": "blue",
                                        "REJECTED": "red"
                                    }

                                    current_status = applicant_info['Status'].upper()  # Retrieve current status
                                    background_color = status_color_map.get(current_status, "gray")
                                    status_box_style = {
                                        "height": "25px",
                                        "backgroundColor": background_color,
                                        "borderRadius": "4px",
                                        "display": "flex",
                                        "alignItems": "center",
                                        "justifyContent": "center",
                                        "marginTop": "5px",
                                        "color": "white",
                                        "fontWeight": "bold",
                                        "fontSize": "12px"  # Smaller font size
                                    }
                                    with solara.Div(style=status_box_style):
                                        solara.Markdown(f"**{current_status}**", style={"margin": "0", "color": "white"})

                                    # Displaying status indicators
                                    for status_text in ["PHOTO MATCHED", "IC VERIFIED"]:
                                        is_matched = applicant_info[status_text]  # 1 or 0
                                        color = "green" if is_matched == 1 else "red"

                                        # Status boxes
                                        status_styles = {
                                            "height": "25px",
                                            "backgroundColor": color,
                                            "borderRadius": "4px",
                                            "display": "flex",
                                            "alignItems": "center",
                                            "justifyContent": "center",
                                            "marginTop": "5px",
                                            "color": "white",
                                            "fontWeight": "bold",
                                            "fontSize": "12px"
                                        }
                                        with solara.Div(style=status_styles):
                                            solara.Markdown(f"**{status_text}**", style={"margin": "0", "color": "white"})

                                    # Info boxes layout
                                    with solara.Div(style={"display": "flex", "flexDirection": "column", "gap": "5px", "marginTop": "10px"}):
                                        new_box_data = [
                                            {"title": "Rating Score", "value": applicant_info['Rating Score']},
                                            {"title": "Risk Level", "value": applicant_info['Risk Level']},
                                            {"title": "Compliance Probability", "value": applicant_info['Compliance Probability']},
                                        ]

                                        for item in new_box_data:
                                            with solara.Div(style={
                                                "border": "1px solid #ddd",
                                                "borderRadius": "4px",
                                                "padding": "5px",
                                                "backgroundColor": "#f9f9f9",
                                                "boxShadow": "0 1px 3px rgba(0, 0, 0, 0.1)"
                                            }):
                                                solara.Markdown(f"**{item['title']}:** {item['value']}", style={
                                                    "margin": "0",
                                                    "fontSize": "12px"  # Smaller font size
                                                })



                                # Display the applicant information based on the selected applicant
                                with solara.Div(style={"display": "flex", "flexDirection": "column", "border": "1px solid #ccc", "borderRadius": "5px", "padding": "10px", "backgroundColor": "#f9f9f9"}):
                                    solara.Markdown(f"**Applicant ID:** {applicant_info['Applicant ID']}")
                                    solara.Markdown(f"**Full Name:** {applicant_info['Full Name']}")
                                    solara.Markdown(f"**Date of Birth & Gender:** {applicant_info.get('Date of Birth', 'N/A')} | {applicant_info.get('Gender', 'N/A')}")
                                    solara.Markdown(f"**Address:** {applicant_info.get('Address', 'N/A')}")
                                    solara.Markdown(f"**Race & Nationality:** {applicant_info.get('Race', 'N/A')} | {applicant_info.get('Nationality', 'N/A')}")
                                    solara.Markdown(f"**Employment Status & Occupation:** {applicant_info.get('Employment Status', 'N/A')} | {applicant_info.get('Occupation', 'N/A')}")
                                    solara.Markdown(f"**Annual Income (RM) & Net Worth (RM):** {applicant_info.get('Annual Income (RM)', 'N/A')} | {applicant_info.get('Net Worth (RM)', 'N/A')}")
                                    solara.Markdown(f"**Attempt of Application & Time Taken:** {applicant_info.get('Attempt of Application', 'N/A')} | {applicant_info.get('Time Taken (minutes)', 'N/A')}")
                                    solara.Markdown(f"**Source of Funds:** {applicant_info.get('Source of Funds', 'N/A')}")

                        # here
                        if selected_applicant is not None:
                            with solara.Div(style={"display": "flex", "alignItems": "center", "gap": "10px", "marginTop": "10px"}):
                                solara.InputText(label="Enter comments", value=admin_comments, on_value=set_admin_comments, continuous_update=True, style={"flex": "1"})

                                solara.Button("Approve", 
                                              on_click=lambda: (
                                                  handle_approval(selected_applicant, admin_comments),
                                                  set_show_confirmation(True),
                                                  set_admin_comments(""),  # Clear comments field
                                                  set_selected_applicant(None)  # Optionally clear selected applicant
                                              ),
                                              style={"backgroundColor": "green", "color": "white"})
                                
                                solara.Button("Reject", 
                                              on_click=lambda: (
                                                  handle_rejection(selected_applicant, admin_comments),
                                                  set_show_confirmation(True),
                                                  set_admin_comments(""),  # Clear comments field
                                                  set_selected_applicant(None)  # Optionally clear selected applicant
                                              ),
                                              style={"backgroundColor": "red", "color": "white"})

                        # Confirmation message
                        if show_confirmation:
                            with solara.Div(style={"marginTop": "10px", "padding": "10px", "backgroundColor": "#e0ffe0", "border": "1px solid green", "borderRadius": "5px"}):
                                solara.Markdown("**Saved!** Your changes have been recorded.")
                            
                            # Optionally, add a button to dismiss the confirmation message
                            solara.Button("OK", on_click=lambda: set_show_confirmation(False))


                    with solara.lab.Tab("Activity Feed", icon_name="mdi-calendar-clock", style="font-weight: bold"):
                        # Define the stages, their statuses, and timestamps
                        stages = [
                            ("Application Submitted", "completed", "2024-11-01 10:00"),
                            ("Verification Started", "completed", "2024-11-01 11:00"),
                            ("Initial Review Completed", "completed", "2024-11-01 12:00"),
                            ("Request for Additional Information", "in_progress", "2024-11-01 13:00"),
                            ("User Responded with Additional Information", "not_reached", "N/A"),
                            ("Final Review Completed", "not_reached", "N/A"),
                            ("Verification Completed", "not_reached", "N/A"),
                            ("Notification Sent to User", "not_reached", "N/A"),
                        ]

                        # Display each stage with appropriate icons and timestamps
                        with solara.Div(style={"padding": "20px", "fontFamily": "Arial"}):
                            for stage, status, timestamp in stages:
                                if status == "completed":
                                    icon = "✅"  # Green check mark for completed stages
                                elif status == "in_progress":
                                    icon = "⏳"  # Hourglass for in-progress stages
                                else:
                                    icon = "⚪"  # No color circle for not yet reached stages

                                solara.Markdown(f"<span style='font-size: 15px;'>{icon} **{stage}** - *{timestamp}*")


        elif selected_page == "Reporting":
            solara.Markdown("## Reporting Page")

        elif selected_page == "Analytics":
            solara.Markdown("## Analytics Page")
