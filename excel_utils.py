"""
Excel processing utilities
"""
import pandas as pd
from datetime import datetime
from typing import List, Dict, Tuple


def validate_excel_data(df: pd.DataFrame) -> Tuple[pd.DataFrame, List[str]]:
    """
    Validate and clean Excel data
    Returns: (cleaned_dataframe, list_of_errors)
    """
    errors = []
    required_columns = ['name', 'dob', 'dojo', 'belt', 'day', 'gender']
    valid_belts = ['white', 'yellow', 'blue', 'purple', 'green', 'brown', 'black']
    
    # Gender normalization tokens (case- and whitespace-insensitive)
    male_tokens = ['male', 'm', 'boy', 'b']
    female_tokens = ['female', 'f', 'girl', 'g']
    
    # Day normalization tokens (case-insensitive)
    saturday_tokens = ['sat', 'saturday']
    sunday_tokens = ['sun', 'sunday']
    
    # Check for required columns (case-insensitive)
    df.columns = df.columns.str.lower().str.strip()
    
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        errors.append(f"Missing required columns: {', '.join(missing_columns)}")
        return df, errors
    
    # Remove rows with all NaN values
    df = df.dropna(how='all')
    
    # Clean and validate each row
    valid_rows = []
    skipped_rows = []  # Track which rows were skipped with reasons
    
    for idx, row in df.iterrows():
        row_num = idx + 2  # Excel row number (accounting for header)
        skip_reason = None
        
        # Validate name
        if pd.isna(row['name']) or str(row['name']).strip() == '':
            skip_reason = f"Row {row_num}: Missing name"
        
        # Validate and parse DOB
        if not skip_reason:
            if pd.isna(row['dob']):
                skip_reason = f"Row {row_num}: Missing DOB"
            else:
                try:
                    if isinstance(row['dob'], str):
                        # Try to parse date string
                        dob = pd.to_datetime(row['dob'], errors='coerce')
                        if pd.isna(dob):
                            skip_reason = f"Row {row_num}: Invalid DOB format"
                        else:
                            row['dob'] = dob
                except Exception:
                    skip_reason = f"Row {row_num}: Invalid DOB"
        
        # Validate dojo
        if not skip_reason:
            if pd.isna(row['dojo']) or str(row['dojo']).strip() == '':
                skip_reason = f"Row {row_num}: Missing dojo"
        
        # Validate belt
        if not skip_reason:
            if pd.isna(row['belt']) or str(row['belt']).strip() == '':
                skip_reason = f"Row {row_num}: Missing belt"
            else:
                belt_val = str(row['belt']).strip().lower()
                if belt_val not in valid_belts:
                    skip_reason = f"Row {row_num}: Invalid belt '{row['belt']}'"
                else:
                    # Normalize belt value (capitalize first letter)
                    row['belt'] = belt_val.capitalize()
        
        # Validate and normalize day (REQUIRED)
        if not skip_reason:
            if pd.isna(row['day']) or str(row['day']).strip() == '':
                skip_reason = f"Row {row_num}: Missing day"
            else:
                day_val = str(row['day']).strip().lower()
                if day_val in saturday_tokens:
                    row['day'] = 'Saturday'
                elif day_val in sunday_tokens:
                    row['day'] = 'Sunday'
                else:
                    skip_reason = f"Row {row_num}: Invalid day '{row['day']}' (expected: Saturday/Sunday/Sat/Sun)"
        
        # Validate and normalize gender (REQUIRED)
        if not skip_reason:
            if pd.isna(row['gender']) or str(row['gender']).strip() == '':
                skip_reason = f"Row {row_num}: Missing gender"
            else:
                # Normalize: trim spaces and compare casefolded
                gender_val = str(row['gender']).strip().lower()
                if gender_val in male_tokens:
                    row['gender'] = 'Male'
                elif gender_val in female_tokens:
                    row['gender'] = 'Female'
                else:
                    skip_reason = f"Row {row_num}: Invalid gender '{row['gender']}' (expected: Male/Female/M/F/Boy/Girl/B/G)"
        
        if skip_reason:
            skipped_rows.append(skip_reason)
        else:
            valid_rows.append(row)
    
    # Report skipped rows with reasons
    if skipped_rows:
        errors.extend(skipped_rows)
    
    if valid_rows:
        cleaned_df = pd.DataFrame(valid_rows)
    else:
        cleaned_df = pd.DataFrame(columns=required_columns)
    
    return cleaned_df, errors


def process_excel_file(file_path: str) -> Tuple[pd.DataFrame, List[str]]:
    """
    Process uploaded Excel file
    Returns: (cleaned_dataframe, list_of_errors)
    """
    try:
        df = pd.read_excel(file_path)
        return validate_excel_data(df)
    except Exception as e:
        return pd.DataFrame(), [f"Error reading Excel file: {str(e)}"]


def create_template_excel() -> pd.DataFrame:
    """
    Create a template Excel DataFrame for download
    """
    template_data = {
        'Name': ['John Doe', 'Jane Smith'],
        'DOB': ['2010-05-15', '2011-08-22'],
        'Dojo': ['Main Dojo', 'East Branch'],
        'Belt': ['Yellow', 'Blue'],
        'Day': ['Saturday', 'Sunday'],
        'Gender': ['Male', 'Female']
    }
    return pd.DataFrame(template_data)
