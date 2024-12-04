import requests
import json

# Example documents with pre-serialized metadata
documents = [
    # VoIP Documents
    {
        "content": "VoIP System: Our company uses Cisco IP phones. Common issues include network connectivity problems and power cycling. First steps: 1) Check if phone has power 2) Verify network cable is connected 3) Test network connectivity",
        "metadata": '{"type": "voip", "category": "hardware"}'
    },
    {
        "content": "Cisco Phone Features: To transfer calls: 1) Press Transfer button 2) Dial extension 3) Press Transfer again. For conference calls: 1) Press Conference 2) Dial participant 3) Press Conference again",
        "metadata": '{"type": "voip", "category": "how-to"}'
    },
    # Email Documents
    {
        "content": "Email System: We use Microsoft Exchange/Office 365. Common issues include Outlook configuration and password resets. For connection issues, first check Outlook's connection status and verify internet connectivity.",
        "metadata": '{"type": "email", "category": "software"}'
    },
    {
        "content": "Email Password Reset: To reset your email password: 1) Visit portal.office.com 2) Click 'Forgot Password' 3) Follow verification steps. If locked out, contact IT Support at x1234",
        "metadata": '{"type": "email", "category": "password"}'
    },
    # Network Documents
    {
        "content": "WiFi Access: Company WiFi SSID is 'CompanyNet'. For guest access, use 'Guest-WiFi'. Guest passwords change monthly, current password available at reception.",
        "metadata": '{"type": "network", "category": "connectivity"}'
    },
    {
        "content": "VPN Access: Use Cisco AnyConnect for remote access. Installation steps: 1) Download from internal portal 2) Install with admin rights 3) Use your network credentials to connect",
        "metadata": '{"type": "network", "category": "remote-access"}'
    },
    # Printer Documents
    {
        "content": "Printer Setup: Network printers are auto-configured via PrintServer01. For manual setup: 1) Click Add Printer 2) Browse network 3) Select printer by location code",
        "metadata": '{"type": "printer", "category": "setup"}'
    },
    {
        "content": "Printer Issues: Common problems include paper jams and offline status. For paper jams, follow on-screen instructions. For offline printers, check network cable and power cycle",
        "metadata": '{"type": "printer", "category": "troubleshooting"}'
    },
    # Software Documents
    {
        "content": "Software Installation: Standard software can be installed from Software Center. For additional software, submit request via IT Portal with business justification",
        "metadata": '{"type": "software", "category": "installation"}'
    },
    {
        "content": "Software Updates: Windows updates are automatic outside business hours. Do not postpone more than 3 times. For urgent updates, save work and click 'Update and Restart'",
        "metadata": '{"type": "software", "category": "updates"}'
    },
    # Yealink Phone Documents
    {
        "content": "Yealink Remote Phonebook Overview: Remote phonebooks allow users to access contacts stored on a remote server, such as CallSwitch One Dashboard. This provides centralized contact management and automatic synchronization.",
        "metadata": '{"type": "voip", "category": "features", "device": "yealink"}'
    },
    {
        "content": "Yealink Phone GUI Access: To access the phone's GUI: 1) Find phone's IP address 2) Enter IP in browser 3) Login with username: admin, password: admin",
        "metadata": '{"type": "voip", "category": "access", "device": "yealink"}'
    },
    {
        "content": "Yealink Remote Phonebook Setup: 1) Go to Directory section in GUI 2) Select Settings 3) Disable Local Directory 4) Enable Remote Phonebook 5) Click Confirm",
        "metadata": '{"type": "voip", "category": "configuration", "device": "yealink"}'
    },
    {
        "content": "Yealink Remote Phonebook Configuration: Under Directory > Remote Phone Book, enter: 1) Remote URL from CallSwitch One Dashboard 2) Display Name for phonebook. Can add up to 5 remote phonebooks.",
        "metadata": '{"type": "voip", "category": "configuration", "device": "yealink"}'
    },
    {
        "content": "Yealink Remote Phonebook Benefits: 1) Centralized contact management 2) Up to 5 phonebooks supported 3) Automatic synchronization with server 4) Always up-to-date contact lists",
        "metadata": '{"type": "voip", "category": "features", "device": "yealink"}'
    },
    # Password Management
    {
        "content": "Password Policy: Passwords must be 12+ characters with uppercase, lowercase, numbers, and symbols. Change required every 90 days. Cannot reuse last 5 passwords.",
        "metadata": '{"type": "security", "category": "policy"}'
    },
    {
        "content": "Password Reset Portal: Access self-service password reset at reset.company.com. Must have registered phone/email. For lockouts, contact IT Support with employee ID.",
        "metadata": '{"type": "security", "category": "self-service"}'
    },

    # Remote Work Setup
    {
        "content": "Remote Desktop Access: Use Microsoft Remote Desktop. Server address: rds.company.com. Configure MFA through Microsoft Authenticator app.",
        "metadata": '{"type": "remote-work", "category": "access"}'
    },
    {
        "content": "Home Office Setup: Minimum requirements: Stable internet (10+ Mbps), company laptop, headset for calls. VPN must be connected for network resources.",
        "metadata": '{"type": "remote-work", "category": "requirements"}'
    },

    # Mobile Device
    {
        "content": "Mobile Email Setup: Use Outlook mobile app. Setup: 1) Download app 2) Enter company email 3) Use SSO for authentication 4) Enable device encryption if prompted",
        "metadata": '{"type": "mobile", "category": "email"}'
    },
    {
        "content": "BYOD Policy: Personal devices must have: 1) PIN/biometric lock 2) Current OS version 3) Company MDM installed 4) Encryption enabled",
        "metadata": '{"type": "mobile", "category": "policy"}'
    },

    # Collaboration Tools
    {
        "content": "Microsoft Teams: Primary tool for chat, calls, meetings. Use channels for team communication. Direct messages for private chats. Schedule meetings via Outlook or Teams.",
        "metadata": '{"type": "collaboration", "category": "communication"}'
    },
    {
        "content": "SharePoint Sites: Department files on SharePoint. Access via Teams or browser. Use Sync for offline access. Share files using Groups or specific permissions.",
        "metadata": '{"type": "collaboration", "category": "file-sharing"}'
    },

    # Hardware Support
    {
        "content": "Laptop Docking: Connect power before docking. Ensure monitor cables secure. If no display: 1) Check cable connections 2) Try different port 3) Restart laptop while docked",
        "metadata": '{"type": "hardware", "category": "docking-station"}'
    },
    {
        "content": "Monitor Setup: Supports up to 2 external monitors. Use DisplayPort for 4K. Arrange displays in Windows Settings > System > Display. Recommended height: eye level",
        "metadata": '{"type": "hardware", "category": "monitors"}'
    },

    # Security
    {
        "content": "Phishing Guidelines: Check sender email carefully. Never click unexpected links. Report suspicious emails using Outlook's Report Phishing button. When in doubt, contact IT.",
        "metadata": '{"type": "security", "category": "awareness"}'
    },
    {
        "content": "Data Classification: Confidential data needs encryption. Use company OneDrive/SharePoint only. No personal cloud storage. External sharing requires manager approval.",
        "metadata": '{"type": "security", "category": "data-protection"}'
    },

    # Software Licensing
    {
        "content": "Software Requests: Submit via IT Portal. Include: 1) Software name 2) Business justification 3) Manager approval. Allow 5 business days for review and installation.",
        "metadata": '{"type": "software", "category": "procurement"}'
    },
    {
        "content": "License Compliance: Software audits quarterly. Unauthorized software will be removed. Report unused licenses to IT for reallocation. Keep installation media secure.",
        "metadata": '{"type": "software", "category": "compliance"}'
    },

    # CallSwitch One Line Key Documents
    {
        "content": "CallSwitch One Line Key Overview: Users can manage desk phone line keys through CallSwitch One application. Supports BLF (Busy Lamp Field), Speed Dial, and Short Codes customization.",
        "metadata": '{"type": "voip", "category": "features", "device": "callswitch", "subcategory": "line-keys"}'
    },
    {
        "content": "CallSwitch Line Key Access: 1) Open CallSwitch One Application 2) Navigate to Settings Cog 3) Select Line Key Configuration",
        "metadata": '{"type": "voip", "category": "access", "device": "callswitch", "subcategory": "line-keys"}'
    },
    {
        "content": "CallSwitch BLF Setup: Under Line Key Configuration, select BLF as Key Type. Enter extension number as Value. For Contact Tab selection, choose from list of CallSwitch One users within organization.",
        "metadata": '{"type": "voip", "category": "configuration", "device": "callswitch", "subcategory": "blf"}'
    },
    {
        "content": "CallSwitch Speed Dial Configuration: Select Speed Dial as Key Type. Enter Label (name) and Value (phone number). Use Custom Tab for manual entry of external numbers.",
        "metadata": '{"type": "voip", "category": "configuration", "device": "callswitch", "subcategory": "speed-dial"}'
    },
    {
        "content": "CallSwitch Short Codes: Configure Short Code keys using administrator-provided commands. Access via Short Code Tab in Line Key Configuration. Select command to assign to key.",
        "metadata": '{"type": "voip", "category": "configuration", "device": "callswitch", "subcategory": "short-codes"}'
    },
    {
        "content": "CallSwitch Line Key Management: Edit existing keys through Edit button. Delete unwanted keys with Delete button. Click Submit after changes, then Save Configuration to apply. Changes update automatically on desk phone.",
        "metadata": '{"type": "voip", "category": "management", "device": "callswitch", "subcategory": "line-keys"}'
    },
    {
        "content": "CallSwitch Configuration Reset: To restore original desk phone key layout, select Revert Changes in Line Key Configuration section. This resets all customizations to default.",
        "metadata": '{"type": "voip", "category": "troubleshooting", "device": "callswitch", "subcategory": "line-keys"}'
    },
    # CallSwitch One BLF Configuration Documents
    {
        "content": "CallSwitch One BLF Overview: BLF (Busy Lamp Field) keys enable users to monitor extension status and perform actions like speed dialing or call parking directly from deskphones.",
        "metadata": '{"type": "voip", "category": "features", "device": "callswitch", "subcategory": "blf"}'
    },
    {
        "content": "CallSwitch Line Key Basics: Key 1 must be set as a Line Key for making and receiving calls. Additional keys (starting from Key 2) can be configured as BLF or Speed Dial.",
        "metadata": '{"type": "voip", "category": "configuration", "device": "callswitch", "subcategory": "line-keys"}'
    },
    {
        "content": "CallSwitch BLF Key Setup: 1) Navigate to Provisioning tab for user 2) Select BLF from dropdown 3) Enter user name or command as Label 4) Input extension number or short code (e.g., *11 for Call Park) as Value",
        "metadata": '{"type": "voip", "category": "configuration", "device": "callswitch", "subcategory": "blf"}'
    },
    {
        "content": "CallSwitch Speed Dial Setup: 1) Select Speed Dial from dropdown 2) Add contact name as Label 3) Enter external number with area code as Value 4) Save configuration",
        "metadata": '{"type": "voip", "category": "configuration", "device": "callswitch", "subcategory": "speed-dial"}'
    },
    {
        "content": "CallSwitch Key Management: Changes automatically update on deskphone after saving. To modify or remove keys: 1) Return to Provisioning section 2) Click Delete button next to specific key 3) Save changes",
        "metadata": '{"type": "voip", "category": "management", "device": "callswitch", "subcategory": "line-keys"}'
    },
    {
        "content": "CallSwitch BLF Use Cases: Monitor extension status (busy/available), access shared features like call parking. Speed Dial keys provide quick access to frequently used external numbers.",
        "metadata": '{"type": "voip", "category": "features", "device": "callswitch", "subcategory": "blf-usage"}'
    },
    # UCaaS Product Documents
    {
        "content": "UCaaS Overview: Advanced UCaaS License provides comprehensive communication solution integrating cloud telephony, video meetings, team messaging, and file sharing. Supports CRM integration and cloud storage.",
        "metadata": '{"type": "ucaas", "category": "overview", "subcategory": "features"}'
    },
    {
        "content": "UCaaS Communication Features: Access via mobile, desktop, and web apps. Includes plug & play IP handsets, voice/video calls, and messaging. Users can seamlessly switch between communication methods.",
        "metadata": '{"type": "ucaas", "category": "features", "subcategory": "communication"}'
    },
    {
        "content": "UCaaS Call Routing: Drag-and-drop call flow management with multi-level IVR menus, call queues, ring groups, time-of-day routing, on-hold music, and voicemail-to-email functionality.",
        "metadata": '{"type": "ucaas", "category": "features", "subcategory": "call-routing"}'
    },
    {
        "content": "UCaaS Productivity Tools: Host audio/video conferences, use instant messaging, share files, and conduct video meetings with screen sharing and participant management features.",
        "metadata": '{"type": "ucaas", "category": "features", "subcategory": "productivity"}'
    },
    {
        "content": "UCaaS Analytics: Live wallboards show real-time metrics (call wait times, abandonment rates). Includes scheduled reporting for KPI tracking and call supervision tools (listen, whisper, barge).",
        "metadata": '{"type": "ucaas", "category": "features", "subcategory": "analytics"}'
    },
    {
        "content": "UCaaS License Benefits: 2000 minutes each to UK landlines/mobiles per user. Includes SSO support, CRM integration, bulk SMS (20,000 recipients), 90-day call recording, and voicemail transcription.",
        "metadata": '{"type": "ucaas", "category": "licensing", "subcategory": "benefits"}'
    },
    {
        "content": "UCaaS Contact: Amvia Sales - Address: 1 North Bank, Sheffield, S3 8JY, Phone: 0333 733 8050, Email: sales@amvia.co.uk, Website: www.amvia.co.uk",
        "metadata": '{"type": "ucaas", "category": "contact", "subcategory": "sales"}'
    },
    # Unified Communications Solution Documents
    {
        "content": "Unified Communications Overview: Advanced platform with VoIP telephony, call handling, video meetings, chat, presence, and document sharing. Managed through secure dashboard, available on mobile, desktop, and web.",
        "metadata": '{"type": "uc", "category": "overview", "subcategory": "platform"}'
    },
    {
        "content": "UC Applications: Available for desktop (Windows, Mac OS), mobile (iOS, Android), and web browsers. Features include VoIP telephony, advanced call routing, voicemail transcription, and call queues.",
        "metadata": '{"type": "uc", "category": "features", "subcategory": "applications"}'
    },
    {
        "content": "UC Call Management: Drag-and-drop call flow builder with IVR menus, on-hold music, time diaries, voicemail. Includes hunt groups, call-forwarding, and call parking.",
        "metadata": '{"type": "uc", "category": "features", "subcategory": "call-management"}'
    },
    {
        "content": "UC SMS Features: Business SMS supports individual and bulk messaging (up to 20,000 recipients). Includes campaign scheduling and cost tracking per recipient.",
        "metadata": '{"type": "uc", "category": "features", "subcategory": "sms"}'
    },
    {
        "content": "UC Video Meetings: Custom URLs, password-protection, waiting rooms. Features include screen sharing, in-meeting chat, and participant management.",
        "metadata": '{"type": "uc", "category": "features", "subcategory": "video"}'
    },
    {
        "content": "UC Microsoft Teams Integration: Make and receive calls within Teams while retaining CallSwitch features. Compatible with leading desk phone manufacturers.",
        "metadata": '{"type": "uc", "category": "integrations", "subcategory": "teams"}'
    },
    {
        "content": "UC CRM Integration: Supports Salesforce, HubSpot, Zoho with click-to-dial and screen pop-ups. Cloud storage backup with Azure, Amazon S3, Dropbox, Google Drive.",
        "metadata": '{"type": "uc", "category": "integrations", "subcategory": "crm"}'
    },
    {
        "content": "UC Reporting: Real-time wallboards and scheduled reports. Monitor KPIs including average wait times, answered calls, and abandonment rates.",
        "metadata": '{"type": "uc", "category": "features", "subcategory": "reporting"}'
    },
    {
        "content": "UC Infrastructure: Hosted on Google Cloud for global availability and scalability. Features zero-trust security and regular updates through agile development.",
        "metadata": '{"type": "uc", "category": "infrastructure", "subcategory": "cloud"}'
    },
    {
        "content": "UC VoIP+ License: Includes 500 minutes to UK landlines/mobiles, basic VoIP features (call forwarding, on-hold music), SMS for up to 25 recipients.",
        "metadata": '{"type": "uc", "category": "licensing", "subcategory": "voip-plus"}'
    },
    {
        "content": "UC Advanced License: 2,000 minutes to UK landlines/mobiles, bulk SMS (20,000 recipients), multi-level IVR, video meetings, live wallboards.",
        "metadata": '{"type": "uc", "category": "licensing", "subcategory": "advanced"}'
    },
    # CallSwitch One Sales Documents
    {
        "content": "CallSwitch One Platform Overview: Industry-leading unified communications platform for all business sizes. Features VoIP telephony, video meetings, chat, file sharing, and call management. Accessible via secure mobile, desktop, and web apps.",
        "metadata": '{"type": "callswitch", "category": "overview", "subcategory": "platform"}'
    },
    {
        "content": "CallSwitch One Apps: Available on Windows, Mac, iOS, and Android. Includes directory services for internal/external contacts, instant messaging, and presence indicators.",
        "metadata": '{"type": "callswitch", "category": "features", "subcategory": "applications"}'
    },
    {
        "content": "CallSwitch One Call Features: Advanced routing with IVR menus, queues, hunt groups, time-based routing. Management includes whisper, listen, barge, and voicemail transcription.",
        "metadata": '{"type": "callswitch", "category": "features", "subcategory": "call-management"}'
    },
    {
        "content": "CallSwitch One Call Flow: Drag-and-drop call routing builder, custom on-hold music, call queues and parking for efficient handling.",
        "metadata": '{"type": "callswitch", "category": "features", "subcategory": "call-flow"}'
    },
    {
        "content": "CallSwitch One SMS: Send messages to individuals or phonebooks (20,000 recipients max). Includes campaign scheduling and real-time pricing updates.",
        "metadata": '{"type": "callswitch", "category": "features", "subcategory": "sms"}'
    },
    {
        "content": "CallSwitch One Video: Password-protected meetings with waiting rooms and mute controls. Features include screen sharing, in-meeting chat, and hand-raising.",
        "metadata": '{"type": "callswitch", "category": "features", "subcategory": "video"}'
    },
    {
        "content": "CallSwitch One Integrations: CRM support for Salesforce, HubSpot, Zoho (contact sync, call logging, screen popups). Cloud storage with Azure, Amazon S3, Dropbox, Google Drive.",
        "metadata": '{"type": "callswitch", "category": "features", "subcategory": "integrations"}'
    },
    {
        "content": "CallSwitch One Analytics: Live wallboards for real-time stats (wait times, abandonment rates). Automated scheduled reporting for performance insights.",
        "metadata": '{"type": "callswitch", "category": "features", "subcategory": "reporting"}'
    },
    {
        "content": "CallSwitch One S License: 500 UK minutes (landline/mobile), basic VoIP features, SMS (25 recipients), call routing, mobile/desktop/web apps.",
        "metadata": '{"type": "callswitch", "category": "licensing", "subcategory": "standard"}'
    },
    {
        "content": "CallSwitch One Pro License: 2,000 UK minutes, bulk SMS (20,000 recipients), multi-level IVR, live wallboards, video meetings. Includes all S features.",
        "metadata": '{"type": "callswitch", "category": "licensing", "subcategory": "pro"}'
    }
]

def load_test_documents():
    response = requests.post(
        "http://localhost:8000/api/load-documents",
        json=documents
    )
    print(response.json())

if __name__ == "__main__":
    load_test_documents() 