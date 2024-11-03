import pandas as pd
import random
from datetime import datetime, timedelta

# Constants
statuses = ["Approved", "In Progress", "Alerts", "Pending Approval", "Rejected"]
races = ["Malay", "Chinese", "Indian", "Thai", "Vietnamese", "Filipino", "Burman", "Khmer", "Other"]
nationalities = ["Malaysian", "Singaporean", "Indonesian", "Thai", "Vietnamese", "Filipino", "Burmese"]
occupations = ["Engineer", "Doctor", "Teacher", "Lawyer", "Artist", "Nurse", "Scientist", "Manager", "Accountant"]
income_ranges = [(30000, 50000), (50001, 100000), (100001, 200000), (200001, 500000)]
risk_levels = ["Low", "Medium", "High"]

# List of realistic names from various Southeast Asian countries
first_names = ["Ahmad", "Siti", "Mohamed", "Aishah", "Daniel", "Fatimah", 
               "Ryan", "Nur", "Zain", "Rina", "Nguyen", "Tao", "Ayu", 
               "Juan", "Maria", "Sophea", "Lai", "Khin"]
last_names = ["Ali", "Chong", "Kumar", "Tan", "Abdullah", "Mohd", 
              "Omar", "Lim", "Hernandez", "Santos", "Ng", "Yap", "Mala", "Soe"]

# Possible activity stages
activity_stages = [
    "Application Submitted",
    "Verification Started",
    "Initial Review Completed",
    "Request for Additional Information",
    "User Responded with Additional Information",
    "Final Review Completed",
    "Verification Completed",
    "Notification Sent to User"
]

# Function to create dummy data
def create_dummy_data(num_rows):
    data = []
    for i in range(num_rows):
        applicant_id = f"APP{i+1:03}"
        applicant_date = datetime.now() - timedelta(days=random.randint(1, 30), hours=random.randint(0, 23), minutes=random.randint(0, 59))
        full_name = f"{random.choice(first_names)} {random.choice(last_names)}"
        status = random.choice(statuses)
        rating_score = random.randint(1, 10)
        additional_remarks = random.choice([
            "All documents are complete.", 
            "Pending verification of income details.", 
            "Additional documents required.", 
            "Awaiting user response.", 
            "-"
        ])
        dob = datetime.now() - timedelta(days=random.randint(18 * 365, 65 * 365))
        gender = random.choice(["Male", "Female"])
        race = random.choice(races)
        nationality = random.choice(nationalities)
        address = f"{random.randint(1, 100)}, Jalan {random.choice(['Merdeka', 'Jaya', 'Setia', 'Pahlawan'])}, {random.choice(['Kuala Lumpur', 'Bangkok', 'Hanoi', 'Jakarta', 'Manila'])}"
        employment_status = random.choice(["Employed", "Unemployed", "Self-employed"])
        occupation = random.choice(occupations)
        annual_income = random.randint(*random.choice(income_ranges))
        net_worth = round(annual_income * random.uniform(1, 5))
        attempts = random.randint(1, 5)
        time_taken = random.randint(30, 120)
        source_of_funds = random.choice(["Savings", "Loan", "Gift", "Inheritance", "Income"])
        risk_level = random.choice(risk_levels)
        compliance_probability = random.randint(0, 100)

        # Randomly determine how far along the application is
        current_stage_index = random.randint(0, len(activity_stages) - 1)
        activity_feed = []
        for stage_index in range(current_stage_index + 1):
            timestamp = applicant_date + timedelta(hours=stage_index)
            activity_feed.append(f"{activity_stages[stage_index]} - {timestamp.strftime('%Y-%m-%d %H:%M')}")

        # Fill in the remaining stages as "N/A"
        for stage in activity_stages[current_stage_index + 1:]:
            activity_feed.append(f"{stage} - N/A")

        data.append([
            applicant_id, 
            applicant_date.strftime('%Y-%m-%d %H:%M'),
            full_name, 
            status, 
            rating_score, 
            additional_remarks, 
            dob.strftime('%Y-%m-%d'),
            gender, 
            race, 
            nationality, 
            address, 
            employment_status, 
            occupation, 
            annual_income, 
            net_worth, 
            attempts, 
            time_taken, 
            source_of_funds, 
            risk_level, 
            compliance_probability,
            "\n".join(activity_feed)
        ])
    
    return data

# Create DataFrame
columns = [
    "Applicant ID", "Application Date", "Full Name", "Status", "Rating Score",
    "Additional Remarks", "Date of Birth", "Gender", "Race", "Nationality", 
    "Address", "Employment Status", "Occupation", "Annual Income (RM)", 
    "Net Worth (RM)", "Attempt of Application", "Time Taken (minutes)", 
    "Source of Funds", "Risk Level", "Compliance Probability", "Activity Feed"
]

dummy_data = create_dummy_data(50)
df = pd.DataFrame(dummy_data, columns=columns)

# Save to Excel
df.to_excel("dummy_applicant_data.xlsx", index=False)
print("Dummy data saved to 'dummy_applicant_data.xlsx'.")
