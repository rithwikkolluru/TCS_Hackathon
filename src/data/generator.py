import os
import random
import datetime
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from pathlib import Path

from src.utils.config import (
    RAW_DATA_DIR,
    SERVICE_CATEGORIES,
    SERVICE_DURATION_DEFAULTS,
    BRANCHES,
    CUSTOMER_TYPES,
    STAFF_ROLES
)


class SyntheticDataGenerator:
    def __init__(self, seed: int = 42, num_days: int = 90, start_date: str = "2026-06-01"):
        self.seed = seed
        self.num_days = num_days
        self.start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()
        random.seed(seed)
        np.random.seed(seed)

    def generate_all(self) -> Dict[str, pd.DataFrame]:
        """Generates all synthetic datasets: staff roster, appointments, visits, and customer feedback."""
        print("Generating Staff Roster...")
        staff_df = self.generate_staff_roster()

        print("Generating Appointments...")
        appointments_df = self.generate_appointments()

        print("Generating Branch Visits (Historical 90 days)...")
        visits_df = self.generate_visits(staff_df, appointments_df)

        print("Generating Customer Feedback (~500 comments)...")
        feedback_df = self.generate_customer_feedback(visits_df)

        # Save to raw data folder
        staff_df.to_csv(RAW_DATA_DIR / "staff_roster.csv", index=False)
        appointments_df.to_csv(RAW_DATA_DIR / "appointments.csv", index=False)
        visits_df.to_csv(RAW_DATA_DIR / "visits.csv", index=False)
        visits_df.to_parquet(RAW_DATA_DIR / "visits.parquet", index=False)
        feedback_df.to_csv(RAW_DATA_DIR / "customer_feedback.csv", index=False)

        print(f"Data generation complete! Saved to {RAW_DATA_DIR}")
        return {
            "staff_roster": staff_df,
            "appointments": appointments_df,
            "visits": visits_df,
            "customer_feedback": feedback_df
        }

    def generate_staff_roster(self) -> pd.DataFrame:
        """Generates realistic staff roster for all branches across the time horizon."""
        staff_records = []
        staff_counter = 100

        for branch in BRANCHES:
            b_id = branch["branch_id"]
            base_count = branch["base_staff_count"]

            # Role allocation per branch
            roles_distribution = [
                ("Manager", 1, ["Loans - Payment and Sanctioning", "Other"]),
                ("Loan Officer", max(2, int(base_count * 0.2)), ["Loans - Payment and Sanctioning"]),
                ("Teller", max(3, int(base_count * 0.3)), ["Withdrawal", "Deposit", "Cheque Withdrawal", "Money Transfer"]),
                ("Account Officer", max(2, int(base_count * 0.15)), ["Account Opening", "Credit Card", "Debit Card"]),
                ("KYC Officer", max(2, int(base_count * 0.15)), ["KYC Related", "Aadhaar Linking", "PAN Linking"]),
                ("Insurance Officer", max(1, int(base_count * 0.1)), ["Insurance"]),
                ("General Employee", max(1, int(base_count * 0.1)), ["Locker Issuing", "Other"])
            ]

            for role_name, count, default_services in roles_distribution:
                for _ in range(count):
                    staff_counter += 1
                    s_id = f"STF-{staff_counter}"
                    
                    # Generate some days of absence across the 90-day horizon
                    num_absences = random.randint(1, 5)
                    absence_dates = []
                    for _ in range(num_absences):
                        abs_day_offset = random.randint(0, self.num_days - 1)
                        abs_date = self.start_date + datetime.timedelta(days=abs_day_offset)
                        # Avoid Sunday absence since branch is closed
                        if abs_date.weekday() != 6:
                            absence_dates.append(abs_date.strftime("%Y-%m-%d"))

                    staff_records.append({
                        "staff_id": s_id,
                        "branch_id": b_id,
                        "role": role_name,
                        "service_categories_supported": ",".join(default_services),
                        "shift_start": "09:00",
                        "shift_end": "17:00",
                        "status": "Active",
                        "absence_dates": ";".join(sorted(set(absence_dates)))
                    })

        return pd.DataFrame(staff_records)

    def generate_appointments(self) -> pd.DataFrame:
        """Generates appointment records across branches."""
        appointment_records = []
        apt_counter = 1000

        appointment_services = [
            "Loans - Payment and Sanctioning", "Account Opening", "Insurance",
            "Locker Issuing", "KYC Related", "Credit Card"
        ]

        for day_offset in range(self.num_days):
            current_date = self.start_date + datetime.timedelta(days=day_offset)
            if current_date.weekday() == 6:  # Sunday
                continue

            for branch in BRANCHES:
                b_id = branch["branch_id"]
                # Daily appointment volume based on branch footfall multiplier
                num_apts = int(random.randint(8, 20) * branch["base_footfall_multiplier"])

                for _ in range(num_apts):
                    apt_counter += 1
                    apt_id = f"APT-{apt_counter}"
                    hour = random.randint(10, 15)
                    minute = random.choice([0, 15, 30, 45])
                    apt_time = datetime.datetime.combine(current_date, datetime.time(hour, minute))
                    
                    service = random.choice(appointment_services)
                    
                    # Outcomes: 75% completed, 10% cancelled, 10% no-show, 5% late
                    rand_val = random.random()
                    if rand_val < 0.75:
                        status = "Completed"
                        no_show = False
                        arrival_delay = random.randint(-10, 10)
                        arr_time = apt_time + datetime.timedelta(minutes=arrival_delay)
                        comp_time = arr_time + datetime.timedelta(minutes=random.randint(15, 40))
                    elif rand_val < 0.85:
                        status = "Cancelled"
                        no_show = False
                        arr_time = None
                        comp_time = None
                    elif rand_val < 0.95:
                        status = "No-Show"
                        no_show = True
                        arr_time = None
                        comp_time = None
                    else:
                        status = "Late"
                        no_show = False
                        arrival_delay = random.randint(15, 45)
                        arr_time = apt_time + datetime.timedelta(minutes=arrival_delay)
                        comp_time = arr_time + datetime.timedelta(minutes=random.randint(20, 50))

                    appointment_records.append({
                        "appointment_id": apt_id,
                        "branch_id": b_id,
                        "appointment_timestamp": apt_time.strftime("%Y-%m-%d %H:%M:%S"),
                        "service_category": service,
                        "status": status,
                        "arrival_timestamp": arr_time.strftime("%Y-%m-%d %H:%M:%S") if arr_time else None,
                        "completed_timestamp": comp_time.strftime("%Y-%m-%d %H:%M:%S") if comp_time else None,
                        "no_show": no_show
                    })

        return pd.DataFrame(appointment_records)

    def generate_visits(self, staff_df: pd.DataFrame, appointments_df: pd.DataFrame) -> pd.DataFrame:
        """Generates synthetic visit records with realistic footfall, waiting time, and queue patterns."""
        visits = []
        visit_counter = 100000

        # Pre-process staff absences by branch and date
        staff_absences = {}
        for _, row in staff_df.iterrows():
            b_id = row["branch_id"]
            abs_dates = row["absence_dates"].split(";") if row["absence_dates"] else []
            for ad in abs_dates:
                if ad:
                    staff_absences[(b_id, ad)] = staff_absences.get((b_id, ad), 0) + 1

        for day_offset in range(self.num_days):
            current_date = self.start_date + datetime.timedelta(days=day_offset)
            date_str = current_date.strftime("%Y-%m-%d")
            day_of_week = current_date.strftime("%A")
            is_weekend = current_date.weekday() in [5, 6]  # Sat/Sun
            if current_date.weekday() == 6:  # Branch closed on Sunday
                continue

            day_of_month = current_date.day
            is_salary_day = day_of_month in [1, 2, 3, 4, 5]
            is_month_end = day_of_month in [28, 29, 30, 31]

            # Day multiplier
            day_multiplier = 1.0
            if day_of_week == "Monday":
                day_multiplier = 1.35
            elif day_of_week == "Friday":
                day_multiplier = 1.25
            elif day_of_week == "Saturday":
                day_multiplier = 0.75

            if is_salary_day:
                day_multiplier *= 1.3
            if is_month_end:
                day_multiplier *= 1.4

            for branch in BRANCHES:
                b_id = branch["branch_id"]
                base_mult = branch["base_footfall_multiplier"]
                total_staff = branch["base_staff_count"]

                absent_count = staff_absences.get((b_id, date_str), 0)
                available_staff = max(2, total_staff - absent_count)

                # Operating hours: 9 AM to 5 PM
                for hour in range(9, 17):
                    # Hourly multiplier curve
                    if hour in [10, 11]:
                        hour_mult = 1.6  # Morning peak
                    elif hour in [12]:
                        hour_mult = 1.2
                    elif hour in [13]:
                        hour_mult = 0.8  # Lunch time slow
                    elif hour in [14, 15]:
                        hour_mult = 1.4  # Afternoon peak
                    else:
                        hour_mult = 0.9

                    # Base arrival count for this branch-hour slot
                    expected_arrivals = int(12 * base_mult * day_multiplier * hour_mult + random.normalvariate(0, 2))
                    expected_arrivals = max(3, expected_arrivals)

                    # Simulate visits within this hour
                    for _ in range(expected_arrivals):
                        visit_counter += 1
                        visit_id = f"VIS-{current_date.strftime('%Y%m%d')}-{visit_counter}"

                        minute = random.randint(0, 59)
                        second = random.randint(0, 59)
                        arrival_dt = datetime.datetime.combine(current_date, datetime.time(hour, minute, second))

                        # Pick service category with realistic weights
                        service_weights = [
                            0.06, # Loans
                            0.04, # Insurance
                            0.16, # Deposit
                            0.20, # Withdrawal
                            0.08, # Account Opening
                            0.06, # Credit Card
                            0.06, # Debit Card
                            0.03, # Locker Issuing
                            0.08, # Cheque Withdrawal
                            0.08, # KYC Related
                            0.07, # Money Transfer
                            0.04, # Aadhaar Linking
                            0.03, # PAN Linking
                            0.01  # Other
                        ]
                        service_cat = random.choices(SERVICE_CATEGORIES, weights=service_weights, k=1)[0]
                        cust_type = random.choices(CUSTOMER_TYPES, weights=[0.65, 0.10, 0.15, 0.10], k=1)[0]

                        is_apt = random.random() < 0.15
                        apt_status = "Booked" if is_apt else "Walk-in"

                        # Service time based on service category limits
                        min_dur, max_dur = SERVICE_DURATION_DEFAULTS.get(service_cat, (5.0, 15.0))
                        service_time = round(random.uniform(min_dur, max_dur), 2)

                        # Queue length at arrival: depends on arrivals vs staff capacity
                        base_queue = max(0, int((expected_arrivals / max(1, available_staff)) * random.uniform(1.2, 2.5)))
                        if apt_status == "Booked":
                            queue_at_arr = max(0, base_queue - random.randint(2, 5))  # Priority line for appointments
                        else:
                            queue_at_arr = base_queue + random.randint(0, 4)

                        # Waiting time formula based on queue length and available staff
                        wait_time = round(max(0.5, (queue_at_arr * service_time) / max(1, available_staff * 0.8) + random.uniform(-2, 3)), 2)
                        if apt_status == "Booked":
                            wait_time = round(wait_time * 0.4, 2)  # Faster for appointments

                        start_dt = arrival_dt + datetime.timedelta(minutes=wait_time)
                        end_dt = start_dt + datetime.timedelta(minutes=service_time)

                        # Counter and Token
                        token_prefix = service_cat[0].upper()
                        token_num = f"{token_prefix}{random.randint(100, 999)}"
                        counter_id = f"C{random.randint(1, branch['total_counters'])}"

                        # Completed status
                        if wait_time > 40 and random.random() < 0.25:
                            comp_status = "Abandoned"
                        else:
                            comp_status = "Completed"

                        visits.append({
                            "visit_id": visit_id,
                            "branch_id": b_id,
                            "arrival_timestamp": arrival_dt.strftime("%Y-%m-%d %H:%M:%S"),
                            "date": date_str,
                            "day_of_week": day_of_week,
                            "hour": hour,
                            "service_category": service_cat,
                            "customer_type": cust_type,
                            "appointment_status": apt_status,
                            "token_number": token_num,
                            "counter_id": counter_id,
                            "service_start_timestamp": start_dt.strftime("%Y-%m-%d %H:%M:%S"),
                            "service_end_timestamp": end_dt.strftime("%Y-%m-%d %H:%M:%S"),
                            "waiting_time_minutes": wait_time,
                            "service_time_minutes": service_time,
                            "employees_available": available_staff,
                            "employees_absent": absent_count,
                            "queue_length_at_arrival": queue_at_arr,
                            "completed_status": comp_status
                        })

        return pd.DataFrame(visits)

    def generate_customer_feedback(self, visits_df: pd.DataFrame) -> pd.DataFrame:
        """Generates ~500 realistic synthetic customer feedback comments without any PII."""
        feedback_records = []
        feedback_counter = 5000

        # Sample pool of realistic Indian banking feedback templates with ratings
        comment_templates = [
            # Negative - Wait times & queues
            (1, "Waited for over {wait} minutes at {branch} counter for {service}. Horrible queue management!"),
            (1, "Extremely slow processing for {service}. Only 2 staff available during peak morning hours."),
            (2, "Long waiting time for {service} at {branch}. Counter staff took too long."),
            (2, "The queue at {branch} for {service} was unmanaged. Took {wait} mins just to submit forms."),
            (1, "Loan processing delay is absurd. Staff keep referring to manager."),
            (2, "KYC updating took forever. Need online service options for this."),
            (2, "Aadhaar linking queue was messy. Senior citizens had to stand for 30 minutes."),

            # Positive - Quick service & helpful staff
            (5, "Very fast service for {service} at {branch}! Completed in under 10 minutes."),
            (5, "Helpful staff at counter. Quick cash withdrawal without any hassle."),
            (4, "Smooth process for {service}. Good assistance provided by staff."),
            (5, "Excellent customer support for account opening. Well explained by executive."),
            (4, "Appointed slot was honored immediately. No wait time for loan query."),
            (5, "Token system working very efficiently at {branch}."),

            # Neutral / Suggestions
            (3, "Service for {service} was average. Took about {wait} mins."),
            (3, "Branch was crowded but staff managed to process {service} steadily."),
            (3, "Please enable online portal for PAN linking so we don't have to visit branch."),
            (3, "Need more working counters during lunch hour between 1 PM and 2 PM.")
        ]

        # Sample 500 visits from visits_df to base feedback on real branch visits
        sample_visits = visits_df.sample(n=500, random_state=self.seed)

        for _, visit in sample_visits.iterrows():
            feedback_counter += 1
            f_id = f"FBK-{feedback_counter}"
            b_id = visit["branch_id"]
            b_name = next((b["branch_name"] for b in BRANCHES if b["branch_id"] == b_id), b_id)
            service = visit["service_category"]
            wait = int(visit["waiting_time_minutes"])
            ts = visit["arrival_timestamp"]

            # Select appropriate template based on actual wait time
            if wait > 25:
                template_pool = [t for t in comment_templates if t[0] in [1, 2, 3]]
            elif wait < 10:
                template_pool = [t for t in comment_templates if t[0] in [4, 5]]
            else:
                template_pool = comment_templates

            rating, tpl = random.choice(template_pool)
            comment_text = tpl.format(wait=wait, branch=b_name, service=service)

            feedback_records.append({
                "feedback_id": f_id,
                "branch_id": b_id,
                "timestamp": ts,
                "service_category": service,
                "rating": rating,
                "comment": comment_text
            })

        return pd.DataFrame(feedback_records)


if __name__ == "__main__":
    generator = SyntheticDataGenerator()
    generator.generate_all()
