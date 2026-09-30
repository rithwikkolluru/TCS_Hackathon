from typing import Dict, Any, List
from src.utils.config import SERVICE_DURATION_DEFAULTS


class DigitalRedirectionEngine:
    """Evaluates service categories for digital redirection feasibility and time savings."""

    DIGITAL_MAPPINGS = {
        "Money Transfer": {
            "digital_available": True,
            "digital_channel": "Mobile Banking / UPI / Internet Banking",
            "confidence": 0.95,
            "redirect_suitability": "High",
            "instructions": "Transfer funds instantly via Mobile Banking App or UPI without visiting branch counters."
        },
        "Aadhaar Linking": {
            "digital_available": True,
            "digital_channel": "Internet Banking Portal / ATM Service",
            "confidence": 0.90,
            "redirect_suitability": "High",
            "instructions": "Link Aadhaar number securely under 'Services > Statutory Updates' in Internet Banking."
        },
        "PAN Linking": {
            "digital_available": True,
            "digital_channel": "Internet Banking Portal / Income Tax e-Filing",
            "confidence": 0.92,
            "redirect_suitability": "High",
            "instructions": "Submit PAN details online via Bank Mobile App or Income Tax Portal."
        },
        "Debit Card": {
            "digital_available": True,
            "digital_channel": "Mobile Banking App",
            "confidence": 0.88,
            "redirect_suitability": "High",
            "instructions": "Request new debit card, block card, or change PIN directly in Mobile Banking."
        },
        "Credit Card": {
            "digital_available": True,
            "digital_channel": "Internet Banking Portal",
            "confidence": 0.85,
            "redirect_suitability": "Medium-High",
            "instructions": "Apply for credit card upgrade or view statements online."
        },
        "KYC Related": {
            "digital_available": True,
            "digital_channel": "Re-KYC Portal / Video KYC",
            "confidence": 0.80,
            "redirect_suitability": "Medium",
            "instructions": "Complete Periodic Re-KYC using Video KYC or document upload."
        },
        "Account Opening": {
            "digital_available": True,
            "digital_channel": "Instant Video KYC Savings Account Portal",
            "confidence": 0.75,
            "redirect_suitability": "Medium",
            "instructions": "Open zero-balance or regular savings account instantly with Video KYC."
        },
        "Deposit": {
            "digital_available": True,
            "digital_channel": "Cash Deposit Machine (CDM) / ATM",
            "confidence": 0.70,
            "redirect_suitability": "Medium",
            "instructions": "Deposit cash up to Rs 50,000 using 24/7 Cash Deposit Machines."
        },
        "Withdrawal": {
            "digital_available": True,
            "digital_channel": "24/7 ATM Kiosk",
            "confidence": 0.85,
            "redirect_suitability": "High",
            "instructions": "Withdraw cash from any nationwide ATM kiosk."
        },
        "Cheque Withdrawal": {
            "digital_available": False,
            "digital_channel": "Branch Drop Box",
            "confidence": 0.40,
            "redirect_suitability": "Low",
            "instructions": "Drop cheque in 24/7 Drop Box to avoid standing in teller queue."
        },
        "Insurance": {
            "digital_available": False,
            "digital_channel": "Insurance Self-Service Web Portal",
            "confidence": 0.50,
            "redirect_suitability": "Low",
            "instructions": "Explore policy options online, physical branch consultation recommended for claim processing."
        },
        "Locker Issuing": {
            "digital_available": False,
            "digital_channel": "None (Requires Physical Vault Access)",
            "confidence": 0.0,
            "redirect_suitability": "None",
            "instructions": "Physical branch visit mandatory for vault verification and key handover."
        },
        "Loans - Payment and Sanctioning": {
            "digital_available": False,
            "digital_channel": "Pre-approved Digital Loan Portal",
            "confidence": 0.45,
            "redirect_suitability": "Low",
            "instructions": "Check pre-approved loan eligibility online; final sanctioning requires branch verification."
        },
        "Other": {
            "digital_available": False,
            "digital_channel": "Customer Support Helpline 1800-BANK",
            "confidence": 0.30,
            "redirect_suitability": "Low",
            "instructions": "Contact Customer Support Helpline."
        }
    }

    def evaluate_redirection(self, service_category: str, customer_type: str = "Regular") -> Dict[str, Any]:
        """Evaluates whether a service request can be redirected digitally."""

        mapping = self.DIGITAL_MAPPINGS.get(service_category, self.DIGITAL_MAPPINGS["Other"])
        min_dur, max_dur = SERVICE_DURATION_DEFAULTS.get(service_category, (5.0, 15.0))
        time_saved = round((min_dur + max_dur) / 2.0, 1)

        is_digital = mapping["digital_available"]

        # Senior citizens may prefer branch visit, lower digital confidence
        confidence = mapping["confidence"]
        if customer_type == "Senior Citizen":
            confidence = round(confidence * 0.7, 2)

        if is_digital and confidence > 0.5:
            recommendation_text = (
                f"This {service_category} request may be completed through {mapping['digital_channel']}, "
                f"which could save approximately {time_saved} minutes of branch queue pressure."
            )
        else:
            recommendation_text = (
                f"Branch visit is recommended for {service_category}. Digital options are limited or require physical verification."
            )

        return {
            "service_category": service_category,
            "customer_type": customer_type,
            "digital_available": is_digital,
            "digital_channel": mapping["digital_channel"],
            "estimated_branch_time_saved_minutes": time_saved,
            "confidence": confidence,
            "redirect_suitability": mapping["redirect_suitability"],
            "instructions": mapping["instructions"],
            "recommendation": recommendation_text
        }


def get_digital_recommendation(service_category: str, customer_type: str = "Regular") -> Dict[str, Any]:
    engine = DigitalRedirectionEngine()
    return engine.evaluate_redirection(service_category, customer_type)


if __name__ == "__main__":
    engine = DigitalRedirectionEngine()
    res1 = engine.evaluate_redirection("Money Transfer", "Regular")
    print(res1)
    res2 = engine.evaluate_redirection("Locker Issuing", "Regular")
    print(res2)
