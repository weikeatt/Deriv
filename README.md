# Applicant Management System

This project is an Applicant Management System built using Python and the Solara framework. It provides a user-friendly interface for managing applicants' data, including features for approval, rejection, and tracking application progress.

## Table of Contents
- [Installation](#installation)
- [Usage](#usage)
  - [Step 1: Generate Applicants' Data](#step-1-generate-applicants-data)
  - [Step 2: Run the Application](#step-2-run-the-application)
- [File Structure](#file-structure)

## Installation📦

To install the required library, run:

```bash
pip install solara
```
## Usage📋
### Step 1: Generate Applicants' Data

Run the following command to generate sample applicant data:

```bash
python generate_data.py
```

### Step 2: Run the Application

After generating the data, run the application using:

```bash
solara run sol.py
```

## File Structure📁

```
/Deriv
│
├── custom.css                   # Custom CSS to override Solara's default styles
├── default_profile_picture.jpg  # Default profile picture for applicants
├── generate_data.py             # Script to generate dummy applicants' data
├── main.py                      # Basic solution with dummy data
└── sol.py                       # Main application with generated data and full features
```
