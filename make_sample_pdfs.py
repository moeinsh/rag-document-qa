#!/usr/bin/env python3
"""Generate 2-3 fictional sample PDFs used to demo the RAG app.

All companies, products and people in these documents are FICTIONAL and
were invented for this demonstration. Any resemblance to real entities
is coincidental.
"""
import os

from fpdf import FPDF

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data")


class Doc(FPDF):
    def header(self):
        pass

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(130, 130, 130)
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", align="C")

    def h1(self, text):
        self.set_font("Helvetica", "B", 18)
        self.set_text_color(20, 60, 120)
        self.multi_cell(0, 10, text)
        self.ln(2)

    def h2(self, text):
        self.set_font("Helvetica", "B", 13)
        self.set_text_color(30, 30, 30)
        self.multi_cell(0, 8, text)
        self.ln(1)

    def p(self, text):
        self.set_font("Helvetica", "", 11)
        self.set_text_color(30, 30, 30)
        self.multi_cell(0, 6, text)
        self.ln(2)

    def bullets(self, items):
        self.set_font("Helvetica", "", 11)
        self.set_text_color(30, 30, 30)
        for it in items:
            # fpdf2 leaves the cursor past the right margin after a line that
            # starts with spaces; reset x before every row.
            self.set_x(self.l_margin)
            self.multi_cell(0, 6, f"  - {it}")
        self.ln(2)


def manual_nimbus():
    d = Doc()
    d.alias_nb_pages()
    d.set_auto_page_break(True, 20)
    d.add_page()
    d.h1("Nimbus Home Hub - User Manual")
    d.p("Nimbus Labs (fictional company) - Model NH-200 - Revision 3.1")
    d.h2("1. Overview")
    d.p("The Nimbus Home Hub is a fictional smart-home controller that connects "
        "your lights, locks, thermostats and sensors through one app. It supports "
        "Wi-Fi 6 (2.4 and 5 GHz), Zigbee 3.0 and Bluetooth 5.2, and handles up to "
        "120 connected devices.")
    d.h2("2. What is in the box")
    d.bullets(["Nimbus Home Hub NH-200", "USB-C power adapter (15 W)",
               "Ethernet cable (1 m)", "Quick start card"])
    d.h2("3. First-time setup")
    d.bullets([
        "Plug in the hub and wait for the LED to pulse blue (about 60 seconds).",
        "Install the Nimbus app and create an account.",
        "In the app, tap Add Device and scan the QR code under the hub.",
        "Choose your Wi-Fi network and enter the password.",
        "When the LED turns solid green, setup is complete.",
    ])
    d.h2("4. Factory reset")
    d.p("If you sell or give away the hub, erase your data first. To factory reset: "
        "press and hold the reset button on the back of the unit for 10 seconds "
        "until the LED blinks amber, then release. The hub reboots and restores "
        "factory defaults in about 2 minutes. All paired devices and your account "
        "link are removed.")
    d.h2("5. Troubleshooting")
    d.bullets([
        "LED solid red: no internet - check the Ethernet cable or Wi-Fi password.",
        "Devices drop offline: move the hub away from microwaves and thick walls.",
        "App cannot find the hub: make sure your phone is on the same 2.4 GHz network during setup.",
    ])
    d.h2("6. Warranty")
    d.p("The Nimbus Home Hub carries a 24-month limited warranty covering "
        "manufacturing defects in materials and workmanship. The warranty does "
        "not cover physical damage, water damage, or unauthorized modifications. "
        "To claim, contact support with your proof of purchase.")
    return d


def handbook_northwind():
    d = Doc()
    d.alias_nb_pages()
    d.set_auto_page_break(True, 20)
    d.add_page()
    d.h1("Northwind Traders - Employee Handbook")
    d.p("Northwind Traders is a fictional company used for demonstration. "
        "Effective date: January 2026.")
    d.h2("1. Remote work policy")
    d.bullets([
        "Employees become eligible for remote work after 3 months of employment.",
        "Core collaboration hours are 10:00 to 15:00 in your local time zone.",
        "A one-time home-office equipment stipend of $800 is provided.",
        "Remote employees must attend the quarterly on-site week.",
    ])
    d.h2("2. Paid vacation")
    d.p("Full-time employees receive 20 paid vacation days per year, accrued "
        "monthly at 1.67 days per month. New hires start accruing on day one. "
        "Up to 5 unused days may be carried over to the next calendar year; "
        "any remaining balance expires on March 31.")
    d.h2("3. Sick leave and parental leave")
    d.bullets([
        "Sick leave: 10 paid days per year, no accrual cap within the year.",
        "Parental leave: 12 weeks fully paid after 12 months of employment.",
        "Notify your manager before 9:30 AM on any sick day.",
    ])
    d.h2("4. Expense reimbursement")
    d.p("Submit expenses within 30 days of the purchase date through the "
        "expenses portal. Receipts are required for any expense over $25. "
        "Travel bookings should use the company's travel partner when possible.")
    return d


def faq_pixelforge():
    d = Doc()
    d.alias_nb_pages()
    d.set_auto_page_break(True, 20)
    d.add_page()
    d.h1("PixelForge Studio - Support FAQ")
    d.p("PixelForge Studio is a fictional independent game studio. "
        "Last updated: June 2026.")
    d.h2("Accounts and login")
    d.p("Q: I forgot my password. How do I reset it?")
    d.p("A: Click Forgot Password on the login screen. We email you a reset link "
        "that is valid for 24 hours. If it expires, request a new one. "
        "We strongly recommend enabling two-factor authentication in "
        "Account Settings for extra security.")
    d.h2("Refunds")
    d.p("Q: Can I get a refund for a game I bought?")
    d.p("A: Yes. Refunds are granted within 14 days of purchase as long as the "
        "game has been played for less than 2 hours in total. Request a refund "
        "from your order history page; approved refunds return to the original "
        "payment method within 5 business days.")
    d.h2("System requirements")
    d.bullets([
        "OS: Windows 10 64-bit or macOS 13+",
        "Memory: 8 GB RAM minimum, 16 GB recommended",
        "Graphics: DirectX 12 compatible GPU with 4 GB VRAM",
        "Storage: 25 GB available space (SSD recommended)",
    ])
    d.h2("Contacting support")
    d.p("Open a ticket from the Help Center. Average first response time is "
        "under 12 hours on business days. For billing issues, include your "
        "order number to speed things up.")
    return d


def main():
    os.makedirs(DATA, exist_ok=True)
    jobs = [
        ("nimbus_home_hub_manual.pdf", manual_nimbus),
        ("northwind_employee_handbook.pdf", handbook_northwind),
        ("pixelforge_support_faq.pdf", faq_pixelforge),
    ]
    for filename, builder in jobs:
        path = os.path.join(DATA, filename)
        builder().output(path)
        print(f"wrote {path}")


if __name__ == "__main__":
    main()
