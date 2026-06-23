import re

def redact_sensitive_info(text):
    """
    Detects and redacts common sensitive information from text:
    phone numbers, emails, addresses, ID numbers (SSN/Aadhaar-style),
    credit card numbers, and IP addresses.
    """

    patterns = {
        'EMAIL': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        'PHONE': r'(\+?\d{1,3}[-.\s]?)?\(?\d{3,5}\)?[-.\s]?\d{3,4}[-.\s]?\d{3,4}\b',
        'SSN': r'\b\d{3}-\d{2}-\d{4}\b',
        'AADHAAR': r'\b\d{4}\s?\d{4}\s?\d{4}\b',  # Indian 12-digit ID
        'CREDIT_CARD': r'\b(?:\d{4}[-\s]?){3}\d{4}\b',
        'IP_ADDRESS': r'\b(?:\d{1,3}\.){3}\d{1,3}\b',
        'PAN_CARD': r'\b[A-Z]{5}\d{4}[A-Z]\b',  # Indian PAN format
        'PIN_CODE': r'\b\d{6}\b',  # Indian postal PIN code
    }

    redacted_text = text

    for label, pattern in patterns.items():
        redacted_text = re.sub(pattern, f'[REDACTED_{label}]', redacted_text)

    # Basic address detection (looks for common address keywords + numbers)
    address_pattern = r'\b\d+\s+[A-Za-z\s]+(Street|St|Road|Rd|Avenue|Ave|Lane|Ln|Block|Sector|Nagar|Colony)\b'
    redacted_text = re.sub(address_pattern, '[REDACTED_ADDRESS]', redacted_text, flags=re.IGNORECASE)

    return redacted_text


# Example usage
if __name__ == "__main__":
    sample_text = """
    Hi, my name is Mahipal. You can reach me at mahipal@example.com or call 9876543210.
    My Aadhaar number is 1234 5678 9012, and I live at 45 Vaishali Nagar, Jaipur, 302021.
    My card number is 4111-1111-1111-1111.
    """

    my_text = """
Hi, this is Mahipal.
My number is 9876543210 and email is mahipal@example.com.
"""
result = redact_sensitive_info(my_text)
print(result)