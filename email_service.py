import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
from typing import Dict, Any, Optional
from .config import settings

HTML_EMAIL_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Mediscope Health Checkup Reminder</title>
  <style>
    body {{
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
      background-color: #EDE8F5;
      margin: 0;
      padding: 30px 15px;
      color: #3D52A0;
    }}
    .email-container {{
      max-width: 620px;
      margin: 0 auto;
      background-color: #FFFFFF;
      border: 1px solid #ADBBDA;
      border-radius: 16px;
      overflow: hidden;
      box-shadow: 0 10px 25px -5px rgba(61, 82, 160, 0.08);
    }}
    .email-header {{
      background: linear-gradient(135deg, #3D52A0 0%, #7091E6 100%);
      color: #FFFFFF;
      padding: 32px 28px;
      text-align: center;
    }}
    .brand-title {{
      font-size: 26px;
      font-weight: 800;
      letter-spacing: -0.5px;
      margin: 0;
    }}
    .brand-subtitle {{
      font-size: 13px;
      font-weight: 500;
      color: #EDE8F5;
      margin-top: 6px;
      letter-spacing: 0.5px;
      text-transform: uppercase;
    }}
    .email-body {{
      padding: 32px 28px;
    }}
    .greeting {{
      font-size: 18px;
      font-weight: 700;
      color: #3D52A0;
      margin-top: 0;
      margin-bottom: 16px;
    }}
    .card-highlight {{
      background-color: #EDE8F5;
      border: 1px solid #ADBBDA;
      border-radius: 12px;
      padding: 20px;
      margin: 24px 0;
    }}
    .info-row {{
      display: flex;
      justify-content: space-between;
      padding: 8px 0;
      border-bottom: 1px dashed #ADBBDA;
      font-size: 14px;
    }}
    .info-row:last-child {{
      border-bottom: none;
    }}
    .label {{
      font-weight: 600;
      color: #3D52A0;
    }}
    .val {{
      font-weight: 700;
      color: #7091E6;
    }}
    .btn {{
      display: inline-block;
      background-color: #7091E6;
      color: #FFFFFF !important;
      text-decoration: none;
      font-weight: 700;
      font-size: 15px;
      padding: 14px 28px;
      border-radius: 8px;
      text-align: center;
      margin: 20px 0 10px 0;
    }}
    .email-footer {{
      background-color: #EDE8F5;
      border-top: 1px solid #ADBBDA;
      padding: 24px 28px;
      font-size: 12px;
      line-height: 1.6;
      color: #3D52A0;
    }}
    .disclaimer {{
      font-style: italic;
      color: #8697C4;
      margin-bottom: 14px;
    }}
    .copyright {{
      font-weight: 600;
      color: #3D52A0;
      border-top: 1px solid #ADBBDA;
      padding-top: 12px;
    }}
  </style>
</head>
<body>
  <div class="email-container">
    <div class="email-header">
      <div class="brand-title">MEDISCOPE</div>
      <div class="brand-subtitle">Health Report Companion</div>
    </div>
    <div class="email-body">
      <p class="greeting">Hello {recipient_name},</p>
      <p>This is your automated periodic health care reminder from <strong>Mediscope</strong>.</p>
      <p>Proactive monitoring and consistent routine health evaluations are vital for early biomarker tracking and holistic long-term wellbeing.</p>
      
      <div class="card-highlight">
        <div class="info-row">
          <span class="label">Patient Name:</span>
          <span class="val">{patient_name}</span>
        </div>
        <div class="info-row">
          <span class="label">Relationship:</span>
          <span class="val">{relationship}</span>
        </div>
        <div class="info-row">
          <span class="label">Reminder Type:</span>
          <span class="val">{reminder_type}</span>
        </div>
        <div class="info-row">
          <span class="label">Scheduled Checkup Date:</span>
          <span class="val">{scheduled_date}</span>
        </div>
        <div class="info-row">
          <span class="label">Notification Cadence:</span>
          <span class="val">{frequency}</span>
        </div>
      </div>

      <p>Before your scheduled appointment, please remember to generate your <strong>AI Doctor Consultation Briefing</strong> inside Mediscope to prepare targeted questions for your physician.</p>

      <div style="text-align: center;">
        <a href="http://localhost:5173" class="btn">Access Mediscope Portal &rarr;</a>
      </div>
    </div>
    <div class="email-footer">
      <div class="disclaimer">
        <strong>Safety Notice:</strong> {safety_disclaimer}
      </div>
      <div class="copyright">
        {copyright_statement}
      </div>
    </div>
  </div>
</body>
</html>
"""

def dispatch_checkup_email(
    recipient_email: str,
    recipient_name: str,
    patient_name: str,
    relationship: str,
    reminder_type: str,
    scheduled_date: str,
    frequency: str = "ANNUAL"
) -> Dict[str, Any]:
    """
    Dispatches a formatted HTML health checkup reminder email.
    Supports real SMTP when credentials exist, with fallback simulation engine that records full email body.
    """
    subject = f"Mediscope Reminder: Upcoming {reminder_type.replace('_', ' ').title()} for {patient_name}"
    
    html_content = HTML_EMAIL_TEMPLATE.format(
        recipient_name=recipient_name,
        patient_name=patient_name,
        relationship=relationship,
        reminder_type=reminder_type.replace('_', ' ').title(),
        scheduled_date=scheduled_date,
        frequency=frequency.title(),
        safety_disclaimer=settings.SAFETY_DISCLAIMER,
        copyright_statement=settings.COPYRIGHT_STATEMENT
    )

    actual_sent = False
    delivery_note = ""

    # Check if actual SMTP credentials are provided
    if settings.SMTP_USER and settings.SMTP_PASSWORD:
        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = settings.SMTP_FROM_EMAIL
            msg["To"] = recipient_email
            
            part = MIMEText(html_content, "html")
            msg.attach(part)

            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=10) as server:
                server.starttls()
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                server.sendmail(settings.SMTP_FROM_EMAIL, [recipient_email], msg.as_string())
            
            actual_sent = True
            delivery_note = f"Dispatched via live SMTP server ({settings.SMTP_HOST}) to {recipient_email}."
        except Exception as e:
            actual_sent = False
            delivery_note = f"Live SMTP attempt failed ({str(e)}). Fallen back to simulated instant delivery."
    else:
        actual_sent = True
        delivery_note = f"Simulated SMTP engine delivered successfully to {recipient_email} (Configure SMTP_USER/SMTP_PASSWORD in backend/.env for live remote server relay)."

    return {
        "status": "SENT" if actual_sent else "PENDING",
        "recipient_email": recipient_email,
        "recipient_name": recipient_name,
        "subject": subject,
        "sent_at": datetime.utcnow().isoformat(),
        "delivery_note": delivery_note,
        "html_preview": html_content
    }
