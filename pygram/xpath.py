"""XPATH definitions for common web elements."""


FOLLOW_BUTTON_XPATH = """
    //button[text()='Following' or
        text()='Requested' or
        text()='Follow' or
        text()='Follow Back' or
        text()='Unblock' or
        text()='Message']
"""
