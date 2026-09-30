export const SERVICE_CATEGORIES = [
  "Loans - Payment and Sanctioning",
  "Insurance",
  "Deposit",
  "Withdrawal",
  "Account Opening",
  "Credit Card",
  "Debit Card",
  "Locker Issuing",
  "Cheque Withdrawal",
  "KYC Related",
  "Money Transfer",
  "Aadhaar Linking",
  "PAN Linking",
  "Other"
];

export const BRANCHES = [
  { branch_id: "BR001", branch_name: "Hyderabad Central", city: "Hyderabad", state: "Telangana", total_counters: 12, lat: 17.3850, lng: 78.4867 },
  { branch_id: "BR002", branch_name: "Kukatpally Branch", city: "Hyderabad", state: "Telangana", total_counters: 10, lat: 17.4933, lng: 78.3914 },
  { branch_id: "BR003", branch_name: "Secunderabad Branch", city: "Secunderabad", state: "Telangana", total_counters: 8, lat: 17.4399, lng: 78.4983 },
  { branch_id: "BR004", branch_name: "Warangal Urban", city: "Warangal", state: "Telangana", total_counters: 6, lat: 17.9689, lng: 79.5941 },
  { branch_id: "BR005", branch_name: "Vijayawada Main", city: "Vijayawada", state: "Andhra Pradesh", total_counters: 10, lat: 16.5062, lng: 80.6480 },
  { branch_id: "BR006", branch_name: "Karimnagar Branch", city: "Karimnagar", state: "Telangana", total_counters: 6, lat: 18.4386, lng: 79.1288 },
  { branch_id: "BR007", branch_name: "Visakhapatnam Port", city: "Visakhapatnam", state: "Andhra Pradesh", total_counters: 12, lat: 17.6868, lng: 83.2185 },
  { branch_id: "BR008", branch_name: "Tirupati City", city: "Tirupati", state: "Andhra Pradesh", total_counters: 8, lat: 13.6288, lng: 79.4192 }
];

export const RISK_LEVELS = {
  LOW: { label: "LOW", color: "emerald", badgeClass: "badge-low" },
  MEDIUM: { label: "MEDIUM", color: "amber", badgeClass: "badge-medium" },
  HIGH: { label: "HIGH", color: "orange", badgeClass: "badge-high" },
  CRITICAL: { label: "CRITICAL", color: "rose", badgeClass: "badge-critical" }
};

export const TIME_SLOTS = [
  "08:00 - 09:00",
  "09:00 - 10:00",
  "10:00 - 11:00",
  "11:00 - 12:00",
  "12:00 - 13:00",
  "13:00 - 14:00",
  "14:00 - 15:00",
  "15:00 - 16:00",
  "16:00 - 17:00"
];

export const DEMO_CREDENTIALS = [
  { role: "manager", label: "Manager (Hyderabad Central)", email: "manager_hyd@bank.com", password: "BankDemo#2026", branch: "BR001" },
  { role: "employee", label: "Employee (Hyderabad Cash Teller)", email: "teller1_hyd@bank.com", password: "BankDemo#2026", branch: "BR001" },
  { role: "regional_ops", label: "Regional Operations Director", email: "regional@bank.com", password: "BankDemo#2026", branch: "All Branches" }
];
