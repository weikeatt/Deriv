import solara
import pandas as pd
import random
from datetime import datetime, timedelta
from pathlib import Path

# Create a sample DataFrame with 50 rows of dummy data
num_rows = 50
data = {
    "Applicant ID": pd.Series(range(1000, 1000 + num_rows)),
    "Application Date": [datetime.now() - timedelta(days=i) for i in range(num_rows)],
    "Full Name": [f"Applicant {i + 1}" for i in range(num_rows)],
    "Status": pd.Series(random.choices(
        ["Approved", "Pending Approval", "Rejected", "In Progress", "Alerts"],
        k=num_rows
    )),
    "Rating Score": pd.Series(random.choices(range(1, 10), k=num_rows)),
    "Details": ["Details here" for _ in range(num_rows)],
}

df = pd.DataFrame(data)

@solara.component
def Page():
    solara.Style(Path("custom.css"))
    selected_page, set_selected_page = solara.use_state("Admin")

    # State for filter text
    filter_text, set_filter_text = solara.use_state("")
    # State for checkbox to include approved status
    include_approved, set_include_approved = solara.use_state(True)
    # State for last updated time
    last_updated, set_last_updated = solara.use_state(datetime.now().strftime("%Y-%m-%d %H:%M"))

    # Create the top bar
    with solara.AppBar():
        solara.Markdown("The Think Tank")

    # Create the sidebar
    with solara.Sidebar():
        solara.Markdown(f"**Last Updated:**<br> {last_updated} (UTC+8)")
        solara.Markdown("## Pages")
        with solara.Column():
            solara.Button("Admin", on_click=lambda: set_selected_page("Admin"))
            solara.Button("Reporting", on_click=lambda: set_selected_page("Reporting"))
            solara.Button("Analytics", on_click=lambda: set_selected_page("Analytics"))

    with solara.Column(style={"marginLeft": "200px"}):
        if selected_page == "Admin":
            # Calculate counts for each status
            status_counts = df['Status'].value_counts()

            # Create a container for the cards
            with solara.Div(style={"display": "flex", "flexWrap": "wrap", "gap": "10px"}):
                card_data = [
                    {"title": "Approved", "symbol": "✅", "color": "green", "borderColor": "green", "number": status_counts.get("Approved", 0), "info": "Total number of approved applications"},
                    {"title": "In Progress", "symbol": "🔄", "color": "orange", "borderColor": "orange", "number": status_counts.get("In Progress", 0), "info": "Total number of applications currently being processed."},
                    {"title": "Alerts", "symbol": "⚠️", "color": "darkred", "borderColor": "darkred", "number": status_counts.get("Alerts", 0), "info": "Total number of applications that are suspicious"},
                    {"title": "Pending Approval", "symbol": "⏳", "color": "blue", "borderColor": "blue", "number": status_counts.get("Pending Approval", 0), "info": "Total number of applications awaiting approval"},
                    {"title": "Rejected", "symbol": "❌", "color": "red", "borderColor": "red", "number": status_counts.get("Rejected", 0), "info": "Total number of rejected applications"},
                ]

                # Keep the original order of cards
                for card in card_data:
                    card_style = {
                        "border": f"2px solid {card['borderColor']}",
                        "borderRadius": "5px",
                        "padding": "8px",
                        "flex": "1 1 150px",
                        "cursor": "pointer",
                        "height": "100px",
                        "position": "relative"
                    }

                    with solara.Div(style=card_style):
                        with solara.Tooltip(solara.Markdown(card['info']), color="white"):
                            solara.Div("ℹ️", style={"position": "absolute", "top": "8px", "right": "8px", "fontSize": "16px", "color": "gray", "cursor": "pointer"})

                        with solara.Div(style={"display": "flex", "alignItems": "center"}):
                            solara.Div(card["symbol"], style={"color": card["color"], "fontSize": "40px", "marginRight": "10px"})
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
                                    style={"flex": "1", "maxWidth": "280px", "minWidth": "200px"}  # Set max and min widths
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

                            column_hover, set_column_hover = solara.use_state(None)
                            solara.DataFrame(sorted_df, on_column_header_hover=set_column_hover, items_per_page=10)




                solara.Div(style={"width": "1px", "backgroundColor": "black", "margin": "0 10px"}) # Middle split line

                with solara.lab.Tabs():
                    with solara.lab.Tab("Applicant Information", icon_name="mdi-information", style="font-weight: bold"):
                        with solara.Div(style={"display": "flex", "alignItems": "flex-start", "gap": "20px", "margin": "10px 0"}):
                            default_image_path = Path("default_profile_picture.jpg")
                            profile_image_path = Path("profile_picture.jpg")
                            final_image_path = profile_image_path if profile_image_path.exists() else default_image_path

                            with solara.Div(style={"border": "2px solid #ccc", "borderRadius": "10px", "padding": "5px", "display": "inline-block", "boxShadow": "0 2px 5px rgba(0, 0, 0, 0.2)"}):
                                solara.Image(final_image_path)

                                # Photo Matched box
                                with solara.Div(style={"width": "130px", "height": "22px", "backgroundColor": "green", "borderRadius": "5px", "display": "flex", "alignItems": "center", "justifyContent": "center", "marginTop": "2px"}):
                                    solara.Markdown("**PHOTO MATCHED**", style={"margin": "0", "color": "white", "fontWeight": "bold"})

                                # IC Verified box
                                with solara.Div(style={"width": "130px", "height": "22px", "backgroundColor": "green", "borderRadius": "5px", "display": "flex", "alignItems": "center", "justifyContent": "center", "marginTop": "5px"}):
                                    solara.Markdown("**IC VERIFIED**", style={"margin": "0", "color": "white", "fontWeight": "bold"})



                            with solara.Div(style={"display": "flex", "flexDirection": "column", "border": "1px solid #ccc", "borderRadius": "5px", "padding": "10px", "backgroundColor": "#f9f9f9"}):
                                solara.Markdown(f"**Applicant ID:** {df['Applicant ID'].iloc[0]}")
                                solara.Markdown(f"**Full Name:** {df['Full Name'].iloc[0]}")
                                solara.Markdown(f"**Date of Birth & Gender:** {df['Date of Birth'].iloc[0] if 'Date of Birth' in df else 'N/A'} | {df['Gender'].iloc[0] if 'Gender' in df else 'N/A'}")
                                solara.Markdown(f"**Race & Nationality:** {df['Race'].iloc[0] if 'Race' in df else 'N/A'} | {df['Nationality'].iloc[0] if 'Nationality' in df else 'N/A'}")
                                solara.Markdown(f"**Address:** {df['Address'].iloc[0] if 'Address' in df else 'N/A'}")
                                solara.Markdown(f"**Employment Status & Occupation:** {df['Employment Status'].iloc[0] if 'Employment Status' in df else 'N/A'} | {df['Occupation'].iloc[0] if 'Occupation' in df else 'N/A'}")
                                solara.Markdown(f"**Annual Income (RM) & Net Worth (RM):** {df['Annual Income'].iloc[0] if 'Annual Income' in df else 'N/A'} | {df['Net Worth'].iloc[0] if 'Net Worth' in df else 'N/A'}")
                                solara.Markdown(f"**Attempt of Application & Time Taken:** {df['Attempt of Application'].iloc[0] if 'Attempt of Application' in df else 'N/A'} | {df['Time Taken'].iloc[0] if 'Time Taken' in df else 'N/A'}")
                                solara.Markdown(f"**Source of Funds:** {df['Source of Funds'].iloc[0] if 'Source of Funds' in df else 'N/A'}")

                            with solara.Div(style={"display": "flex", "flexDirection": "column", "gap": "10px", "marginLeft": "10px"}):
                                new_box_data = [
                                    {"title": "Rating Score", "value": df['Rating Score'].iloc[0]},
                                    {"title": "Risk Level", "value": "Low"},
                                    {"title": "Compliance Probability", "value": "85%"},
                                ]

                                for item in new_box_data:
                                    with solara.Div(style={"border": "1px solid #ccc", "borderRadius": "5px", "padding": "10px", "backgroundColor": "#f0f0f0"}):
                                        solara.Markdown(f"**{item['title']}:** {item['value']}")

                        with solara.Div(style={"display": "flex", "alignItems": "center", "gap": "10px", "marginTop": "10px"}):
                            admin_comments, set_admin_comments = solara.use_state("")
                            solara.InputText(label="Enter comments", value=admin_comments, on_value=set_admin_comments, continuous_update=True, style={"flex": "1"})

                            solara.Button("Approve", 
                                          on_click=lambda: handle_approval(df['Applicant ID'].iloc[0], admin_comments),
                                          style={"backgroundColor": "green", "color": "white"})
                            solara.Button("Reject", 
                                          on_click=lambda: handle_rejection(df['Applicant ID'].iloc[0], admin_comments),
                                          style={"backgroundColor": "red", "color": "white"})

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

def handle_approval(applicant_id, comments):
    # Logic for approving the application
    print(f"Application {applicant_id} approved with comments: {comments}")

def handle_rejection(applicant_id, comments):
    # Logic for rejecting the application
    print(f"Application {applicant_id} rejected with comments: {comments}")

# To run the Page component in your app as needed