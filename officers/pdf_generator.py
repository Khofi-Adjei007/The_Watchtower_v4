from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch

def generate_pdf(docket):
    pdf_file_path = f"media/dockets/{docket.id}_report.pdf"

    # Create a canvas object
    c = canvas.Canvas(pdf_file_path, pagesize=letter)
    width, height = letter

    # Title
    c.setFont("Helvetica-Bold", 16)
    c.drawString(1 * inch, height - 1 * inch, "Docket Report")

    # Case Title
    c.setFont("Helvetica-Bold", 12)
    c.drawString(1 * inch, height - 1.5 * inch, f"Case Title: {docket.Case_Title}")

    # Date and Time of Incident
    c.setFont("Helvetica", 10)
    c.drawString(1 * inch, height - 2 * inch, f"Date and Time of Incident: {docket.date_time_of_incident}")

    # Date and Time of Report
    c.drawString(1 * inch, height - 2.5 * inch, f"Date and Time of Report: {docket.date_time_of_report}")

    # Complainant Information
    c.setFont("Helvetica-Bold", 12)
    c.drawString(1 * inch, height - 3 * inch, "Complainant Information")
    c.setFont("Helvetica", 10)
    c.drawString(1 * inch, height - 3.5 * inch, f"Name: {docket.complainant_name}")
    c.drawString(1 * inch, height - 4 * inch, f"Contact: {docket.complainant_contact}")
    c.drawString(1 * inch, height - 4.5 * inch, f"Address: {docket.complainant_physical_address}")

    # Suspect Information
    c.setFont("Helvetica-Bold", 12)
    c.drawString(1 * inch, height - 5 * inch, "Suspect Information")
    c.setFont("Helvetica", 10)
    c.drawString(1 * inch, height - 5.5 * inch, f"Name: {docket.suspect_name}")
    c.drawString(1 * inch, height - 6 * inch, f"Contact: {docket.suspect_contact}")
    c.drawString(1 * inch, height - 6.5 * inch, f"Address: {docket.suspect_physical_address}")

    # Victim Information
    c.setFont("Helvetica-Bold", 12)
    c.drawString(1 * inch, height - 7 * inch, "Victim Information")
    c.setFont("Helvetica", 10)
    c.drawString(1 * inch, height - 7.5 * inch, f"Name: {docket.victim_name}")
    c.drawString(1 * inch, height - 8 * inch, f"Contact: {docket.victim_contact}")
    c.drawString(1 * inch, height - 8.5 * inch, f"Address: {docket.victim_physical_address}")

    # Incident Details
    c.setFont("Helvetica-Bold", 12)
    c.drawString(1 * inch, height - 9 * inch, "Incident Details")
    c.setFont("Helvetica", 10)
    c.drawString(1 * inch, height - 9.5 * inch, f"Location: {docket.location_of_incident}")
    c.drawString(1 * inch, height - 10 * inch, f"Type: {docket.type_of_incident}")
    c.drawString(1 * inch, height - 10.5 * inch, f"Statement: {docket.statement_of_incident}")

    # Key Witness Information
    c.setFont("Helvetica-Bold", 12)
    c.drawString(1 * inch, height - 11 * inch, "Key Witness Information")
    c.setFont("Helvetica", 10)
    c.drawString(1 * inch, height - 11.5 * inch, f"Name: {docket.key_witness_name}")
    c.drawString(1 * inch, height - 12 * inch, f"Contact: {docket.key_witness_contact}")
    c.drawString(1 * inch, height - 12.5 * inch, f"Address: {docket.key_witness_physical_address}")

    # Final Report Details
    c.setFont("Helvetica-Bold", 12)
    c.drawString(1 * inch, height - 13 * inch, "Final Report Details")
    c.setFont("Helvetica", 10)
    c.drawString(1 * inch, height - 13.5 * inch, f"Reporting Officer Name: {docket.reporting_officer_name}")
    c.drawString(1 * inch, height - 14 * inch, f"Badge ID: {docket.reporting_officer_badge_id}")
    c.drawString(1 * inch, height - 14.5 * inch, f"Rank: {docket.reporting_officer_rank}")
    c.drawString(1 * inch, height - 15 * inch, f"Station: {docket.reporting_officer_station}")
    c.drawString(1 * inch, height - 15.5 * inch, f"Division: {docket.reporting_officer_division}")
    c.drawString(1 * inch, height - 16 * inch, f"Charges Filed: {docket.charges_filed}")
    c.drawString(1 * inch, height - 16.5 * inch, f"Legal Actions Taken: {docket.legal_actions_taken}")
    c.drawString(1 * inch, height - 17 * inch, f"Assigned Investigator: {docket.assigned_investigator}")
    c.drawString(1 * inch, height - 17.5 * inch, f"Case Status: {docket.case_status}")
    c.drawString(1 * inch, height - 18 * inch, f"Follow-up Required: {docket.follow_up_required}")
    c.drawString(1 * inch, height - 18.5 * inch, f"Additional Notes: {docket.additional_notes}")

    # Save the PDF
    c.save()

    return pdf_file_path
