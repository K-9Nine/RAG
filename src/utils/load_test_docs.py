import requests
import json
import sys

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
    },
    # CallSwitch One iOS App Documents
    {
        "content": "CallSwitch One iOS App Overview: Mobile app enables iPhone to function as work phone extension. Manage calls, messages, files, and settings remotely. Access through iPhone app store.",
        "metadata": '{"type": "mobile", "category": "overview", "platform": "ios", "app": "callswitch"}'
    },
    {
        "content": "CallSwitch iOS Call Handling: Open app to keypad for direct dialing. Access History for call logs (missed/received/made). Use Contacts for internal users and device contacts with Filter option for categories.",
        "metadata": '{"type": "mobile", "category": "calls", "platform": "ios", "app": "callswitch"}'
    },
    {
        "content": "CallSwitch iOS Parked Calls: Retrieve parked calls from Parked Tab in History area. Select orange phone icon to connect to parked call.",
        "metadata": '{"type": "mobile", "category": "call-management", "platform": "ios", "app": "callswitch"}'
    },
    {
        "content": "CallSwitch iOS In-Call Features: During calls - Mute microphone, use Keypad for DTMF/short codes, toggle Speaker, add second call. Place calls on Hold or transfer to contacts.",
        "metadata": '{"type": "mobile", "category": "features", "platform": "ios", "app": "callswitch"}'
    },
    {
        "content": "CallSwitch iOS Call Transfer: Press Transfer, select contact or enter external number. Default is unattended transfer. Enable attended (supervised) transfers in Settings > Calls.",
        "metadata": '{"type": "mobile", "category": "transfers", "platform": "ios", "app": "callswitch"}'
    },
    {
        "content": "CallSwitch iOS Messaging: Access Chat area for conversations. Create new chats with New Chat Icon. Send text messages, attachments, files, emojis, and voice notes.",
        "metadata": '{"type": "mobile", "category": "messaging", "platform": "ios", "app": "callswitch"}'
    },
    {
        "content": "CallSwitch iOS Group Chats: Create new groups via New Group menu option. View and join existing group chats. Manage group messaging features.",
        "metadata": '{"type": "mobile", "category": "group-chat", "platform": "ios", "app": "callswitch"}'
    },
    {
        "content": "CallSwitch iOS DND Settings: Access More menu for Do Not Disturb options. Choose between Local DND (app-only) or Global DND (all linked devices).",
        "metadata": '{"type": "mobile", "category": "settings", "platform": "ios", "app": "callswitch", "feature": "dnd"}'
    },
    {
        "content": "CallSwitch iOS Account Settings: Update Status, customize Theme, monitor inclusive minutes. Adjust call/chat preferences and notification settings.",
        "metadata": '{"type": "mobile", "category": "settings", "platform": "ios", "app": "callswitch", "feature": "account"}'
    },
    {
        "content": "CallSwitch iOS Device Linking: Connect to desktop/browser version through My Devices. Use QR code icon to log in at callswitchone.app.",
        "metadata": '{"type": "mobile", "category": "setup", "platform": "ios", "app": "callswitch", "feature": "linking"}'
    },
    # CallSwitch One Android App Documents
    {
        "content": "CallSwitch One Android App Overview: Mobile app transforms Android device into work phone extension. Manage calls, messages, files, history, and settings remotely. Available on Google Play Store.",
        "metadata": '{"type": "mobile", "category": "overview", "platform": "android", "app": "callswitch"}'
    },
    {
        "content": "CallSwitch Android Call Handling: Access keypad for direct dialing with green Call button. View Recent tab for call history (missed/received/made). Use Contacts for internal and device contact lists.",
        "metadata": '{"type": "mobile", "category": "calls", "platform": "android", "app": "callswitch"}'
    },
    {
        "content": "CallSwitch Android Parked Calls: Access parked calls through Parked Tab in Recent section. Select phone icon to connect to parked call.",
        "metadata": '{"type": "mobile", "category": "call-management", "platform": "android", "app": "callswitch"}'
    },
    {
        "content": "CallSwitch Android Call Transfer: Press Transfer button, select contact or enter number. Default is unattended transfer. Configure attended transfers in Settings > Calls. Use Swap to toggle active lines.",
        "metadata": '{"type": "mobile", "category": "transfers", "platform": "android", "app": "callswitch"}'
    },
    {
        "content": "CallSwitch Android Messaging: Access Chats via icon. View conversations or press blue Chat Bubble for new chat. Send text, attachments, files, emojis, and voice notes.",
        "metadata": '{"type": "mobile", "category": "messaging", "platform": "android", "app": "callswitch"}'
    },
    {
        "content": "CallSwitch Android Group Chats: Create groups via Chat Bubble > Group Chat. Add participants and manage group conversations through Groups Tab.",
        "metadata": '{"type": "mobile", "category": "group-chat", "platform": "android", "app": "callswitch"}'
    },
    {
        "content": "CallSwitch Android DND Settings: Access More menu for Do Not Disturb options. Toggle between Local DND (app-only) or Global DND (all linked devices).",
        "metadata": '{"type": "mobile", "category": "settings", "platform": "android", "app": "callswitch", "feature": "dnd"}'
    },
    {
        "content": "CallSwitch Android Account Settings: Update Status, customize Theme, track inclusive minutes. Manage call/chat preferences and notification settings.",
        "metadata": '{"type": "mobile", "category": "settings", "platform": "android", "app": "callswitch", "feature": "account"}'
    },
    {
        "content": "CallSwitch Android Device Linking: Connect to desktop/browser version via My Devices. Use QR code icon to log in to Desktop App or Web App.",
        "metadata": '{"type": "mobile", "category": "setup", "platform": "android", "app": "callswitch", "feature": "linking"}'
    },
    # CallSwitch One Desktop App Documents
    {
        "content": "CallSwitch One Desktop Overview: Desktop app provides comprehensive communication tool with call handling, messaging, file sharing, and contact management. Enables flexible work from any location.",
        "metadata": '{"type": "desktop", "category": "overview", "platform": "desktop", "app": "callswitch"}'
    },
    {
        "content": "CallSwitch Desktop Navigation: Menu bar for calls/chats/settings. Contacts section with filters (internal/phonebook/department/hunt group). Call history shows inbound/outbound/internal calls. Dialpad for manual calls.",
        "metadata": '{"type": "desktop", "category": "navigation", "platform": "desktop", "app": "callswitch"}'
    },
    {
        "content": "CallSwitch Desktop Call Handling: Make calls via green phone icon or dialpad. Adjust Caller ID settings. Choose Blind or Attended Transfer from dropdown. Drag and drop contacts for transfers.",
        "metadata": '{"type": "desktop", "category": "calls", "platform": "desktop", "app": "callswitch"}'
    },
    {
        "content": "CallSwitch Desktop Call Parking: Park calls using short codes (*11-*15) or select from parking spaces list. Retrieve calls via green phone icon in parking area or use designated short code.",
        "metadata": '{"type": "desktop", "category": "call-parking", "platform": "desktop", "app": "callswitch"}'
    },
    {
        "content": "CallSwitch Desktop Chat Features: Access Chats area for conversations. Attach files, add emojis, record voice notes, format messages. Create new chats with + New Chat. Add multiple participants for group chats.",
        "metadata": '{"type": "desktop", "category": "messaging", "platform": "desktop", "app": "callswitch"}'
    },
    {
        "content": "CallSwitch Desktop SMS: Send SMS via ellipsis menu next to contacts. Use chat interface for SMS messages. Configure outbound Caller ID in chat settings.",
        "metadata": '{"type": "desktop", "category": "sms", "platform": "desktop", "app": "callswitch"}'
    },
    {
        "content": "CallSwitch Desktop Account Settings: Change profile picture, enable DND, adjust themes. Configure Caller ID, recording options, call forwarding, and park preferences.",
        "metadata": '{"type": "desktop", "category": "settings", "platform": "desktop", "app": "callswitch", "feature": "account"}'
    },
    {
        "content": "CallSwitch Desktop Notifications: Manage chat and call notifications. Sort contacts and integrate phonebooks/CRM contacts. Adjust input/output devices and ringtone preferences.",
        "metadata": '{"type": "desktop", "category": "settings", "platform": "desktop", "app": "callswitch", "feature": "notifications"}'
    },
    {
        "content": "CallSwitch Desktop Short Codes: Quick access to features using preset codes. Available for call parking, retrieval, and other common functions.",
        "metadata": '{"type": "desktop", "category": "features", "platform": "desktop", "app": "callswitch", "feature": "short-codes"}'
    },
    # CallSwitch One Pro Product Documents
    {
        "content": "CallSwitch One Pro Overview: Comprehensive unified communications solution for team connectivity and productivity. Features voice, video, messaging, and integrations for seamless communication across devices and locations.",
        "metadata": '{"type": "product", "category": "overview", "product": "callswitch-pro"}'
    },
    {
        "content": "CallSwitch Pro Communication Tools: Mobile/Desktop/Web apps for calls anywhere. Integrated video meetings, Microsoft Teams integration, instant messaging, file sharing, and conference calling.",
        "metadata": '{"type": "product", "category": "features", "product": "callswitch-pro", "feature": "communication"}'
    },
    {
        "content": "CallSwitch Pro Call Management: Drag-and-drop call flow builder with IVR menus, queues, on-hold music, ring groups, time routing. Includes voicemail-to-email and bulk SMS.",
        "metadata": '{"type": "product", "category": "features", "product": "callswitch-pro", "feature": "call-management"}'
    },
    {
        "content": "CallSwitch Pro Recording Features: 90-day secure cloud storage for call recordings. Automatic voicemail transcription to email for easy access.",
        "metadata": '{"type": "product", "category": "features", "product": "callswitch-pro", "feature": "recording"}'
    },
    {
        "content": "CallSwitch Pro Analytics: Live wallboards for real-time call statistics (wait times, answered calls, abandonment rates). Scheduled reporting for KPI tracking.",
        "metadata": '{"type": "product", "category": "features", "product": "callswitch-pro", "feature": "analytics"}'
    },
    {
        "content": "CallSwitch Pro Management Tools: Monitor live calls with Call Listen feature. Coach agents using Whisper mode. Join active calls with Barge capability.",
        "metadata": '{"type": "product", "category": "features", "product": "callswitch-pro", "feature": "supervision"}'
    },
    {
        "content": "CallSwitch Pro Integrations: CRM and cloud storage platform integration. SSO support for Google and Microsoft with multi-factor authentication.",
        "metadata": '{"type": "product", "category": "features", "product": "callswitch-pro", "feature": "integrations"}'
    },
    {
        "content": "CallSwitch Pro Benefits: 2000 UK minutes (landline/mobile) per user. One inclusive number per user. Bulk SMS to 20,000 recipients. Supports plug-and-play IP handsets.",
        "metadata": '{"type": "product", "category": "benefits", "product": "callswitch-pro"}'
    },
    # CallSwitch One Integration Documents
    {
        "content": "CallSwitch One Integrations Overview: Comprehensive integration options via customer dashboard. Build seamless SaaS ecosystem with CRM, productivity tools, storage, and communication platforms.",
        "metadata": '{"type": "integrations", "category": "overview", "product": "callswitch"}'
    },
    {
        "content": "CallSwitch CRM Integration Features: Supports Salesforce, HubSpot, Pipedrive, Zoho, Vtiger, Capsule, Vincere. Features: Click-to-dial, contact sync, automatic call logging, screen popups for incoming calls.",
        "metadata": '{"type": "integrations", "category": "crm", "product": "callswitch", "feature": "functionality"}'
    },
    {
        "content": "CallSwitch Microsoft Teams Integration: Connect CallSwitch features with Teams for voice calls, call routing, hunt groups. Slack integration provides call activity notifications in channels.",
        "metadata": '{"type": "integrations", "category": "productivity", "product": "callswitch", "feature": "teams"}'
    },
    {
        "content": "CallSwitch Phonebook Integration: Sync with Google Contacts and Microsoft 365. Keep contacts synchronized across devices, improve caller identification and customer service.",
        "metadata": '{"type": "integrations", "category": "phonebook", "product": "callswitch", "feature": "sync"}'
    },
    {
        "content": "CallSwitch SSO Integration: Support for Microsoft Active Directory (user sync, MFA) and Google Workspace (secure login, dashboard protection).",
        "metadata": '{"type": "integrations", "category": "security", "product": "callswitch", "feature": "sso"}'
    },
    {
        "content": "CallSwitch Recording Integration: 90-day rolling storage with extended options via Amazon S3, Google Drive, Azure, Dropbox. CallCabinet integration for compliance, encryption, analytics.",
        "metadata": '{"type": "integrations", "category": "recording", "product": "callswitch", "feature": "storage"}'
    },
    {
        "content": "CallSwitch Cloud Storage: Secure backup for call recordings and CDR data. Supports Amazon S3, Google Drive, Microsoft Azure, Dropbox integration.",
        "metadata": '{"type": "integrations", "category": "storage", "product": "callswitch", "feature": "cloud"}'
    },
    {
        "content": "CallSwitch Browser Extensions: Chrome and Firefox extensions for click-to-dial and caller ID customization. Make calls directly from browser windows.",
        "metadata": '{"type": "integrations", "category": "browser", "product": "callswitch", "feature": "extensions"}'
    },
    {
        "content": "CallSwitch Data Integration: Microsoft Power BI and Google BigQuery integration for live wallboards and historical reporting. Create real-time dashboards and performance insights.",
        "metadata": '{"type": "integrations", "category": "analytics", "product": "callswitch", "feature": "data"}'
    },
    {
        "content": "CallSwitch API & Webhooks: Open API and webhook library for custom integrations. Manage audio files, call routing, recordings, costs, CDR data. Build custom wallboards and applications.",
        "metadata": '{"type": "integrations", "category": "development", "product": "callswitch", "feature": "api"}'
    },
    # CallSwitch Feature Comparison Documents
    {
        "content": "CallSwitch Core System Comparison: CallSwitch One vs Business/Lite - Mobile App (One/Business: Full, Lite: Dialler Only), Desktop/Web Apps (All), MFA (One/Business only), Text-to-Speech (One/Business only).",
        "metadata": '{"type": "comparison", "category": "core", "product": "callswitch", "feature": "system"}'
    },
    {
        "content": "CallSwitch Integration Comparison: CallSwitch One offers unlimited CRM integrations, Teams integration, API library, webhooks, cloud storage. Business limited to 1 CRM. Lite has no integrations.",
        "metadata": '{"type": "comparison", "category": "integrations", "product": "callswitch", "feature": "capabilities"}'
    },
    {
        "content": "CallSwitch Call Management Comparison: CallSwitch One provides unlimited routes/groups/queues. Business: 8 routes, 25 groups, 8 queues. Lite: 1 each. One/Business include caller ID routing, IVR menus.",
        "metadata": '{"type": "comparison", "category": "features", "product": "callswitch", "feature": "call-management"}'
    },
    {
        "content": "CallSwitch Messaging Comparison: One/Business include internal chat, group messaging, file sharing. One adds bulk SMS (20k recipients). Lite has limited SMS, no messaging features.",
        "metadata": '{"type": "comparison", "category": "features", "product": "callswitch", "feature": "messaging"}'
    },
    {
        "content": "CallSwitch Video Comparison: One/Business support 50-participant video meetings (instant/scheduled). One adds password protection. Lite has no video capabilities.",
        "metadata": '{"type": "comparison", "category": "features", "product": "callswitch", "feature": "video"}'
    },
    {
        "content": "CallSwitch Contact Center Comparison: One/Business include call monitoring, whisper/barge. One adds live wallboards, scheduled reporting. Lite has limited analytics only.",
        "metadata": '{"type": "comparison", "category": "features", "product": "callswitch", "feature": "contact-center"}'
    },
    {
        "content": "CallSwitch One Advantages: Unlimited integrations, routes, groups, queues. Enhanced features include bulk SMS, password-protected meetings, live wallboards, scheduled reporting, API access.",
        "metadata": '{"type": "comparison", "category": "summary", "product": "callswitch", "feature": "advantages"}'
    },
    # CallSwitch One License Improvement Documents
    {
        "content": "CallSwitch One Platform Upgrade: Built on new public cloud infrastructure with open APIs and expanded features. Available as CallSwitch One S (VoIP) and CallSwitch One Pro (UCaaS).",
        "metadata": '{"type": "improvements", "category": "overview", "product": "callswitch-one", "feature": "platform"}'
    },
    {
        "content": "CallSwitch One Core Improvements: Full mobile app access, cross-platform desktop/web apps, software-only options, dashboard MFA, presence indicators, text-to-speech, free call recording.",
        "metadata": '{"type": "improvements", "category": "features", "product": "callswitch-one", "feature": "core"}'
    },
    {
        "content": "CallSwitch One Routing Improvements: Unlimited call routes, hunt groups, and call queues. Call Follow-Me feature coming in roadmap. No restrictions on routing options or group setups.",
        "metadata": '{"type": "improvements", "category": "features", "product": "callswitch-one", "feature": "routing"}'
    },
    {
        "content": "CallSwitch One Integration Improvements: New API and webhook libraries for third-party integration. Unlimited CRM integration capability. Enhanced connectivity options.",
        "metadata": '{"type": "improvements", "category": "features", "product": "callswitch-one", "feature": "integrations"}'
    },
    {
        "content": "CallSwitch One Communication Improvements: Custom on-hold music, customizable greetings, group mailboxes, bulk SMS (20k recipients), SMS for 25 users, enhanced call assurance.",
        "metadata": '{"type": "improvements", "category": "features", "product": "callswitch-one", "feature": "communication"}'
    },
    {
        "content": "CallSwitch One Management Improvements: Time-based routing configuration, real-time wallboards for call center stats, automated scheduled reporting for performance insights.",
        "metadata": '{"type": "improvements", "category": "features", "product": "callswitch-one", "feature": "management"}'
    },
    {
        "content": "CallSwitch One UC Improvements: Feature-rich video meetings (roadmap), Single Sign-On (SSO) for secure authentication, enhanced unified communication capabilities.",
        "metadata": '{"type": "improvements", "category": "features", "product": "callswitch-one", "feature": "uc"}'
    },
    {
        "content": "CallSwitch One vs CallSwitch Summary: Comprehensive evolution offering superior flexibility, scalability, functionality. Enhanced user experience with modern communication features.",
        "metadata": '{"type": "improvements", "category": "summary", "product": "callswitch-one", "feature": "benefits"}'
    },
    # CallSwitch One Installation Documents
    {
        "content": "CallSwitch One App Overview: Turn smartphones and desktops into work phone extensions. Handle calls, messages, file sharing, and settings from anywhere. Available for invited users.",
        "metadata": '{"type": "installation", "category": "overview", "product": "callswitch", "feature": "apps"}'
    },
    {
        "content": "CallSwitch One Mobile Installation: Download via SMS invitation link or from app stores (Google Play/Apple). Sign in with mobile number and verify with 6-digit SMS code.",
        "metadata": '{"type": "installation", "category": "mobile", "product": "callswitch", "feature": "setup"}'
    },
    {
        "content": "CallSwitch One Desktop Installation: Download from welcome email link or callswitchone.com/downloads. Sign in with mobile number or scan QR code from mobile app (More > My Devices > Link a Device).",
        "metadata": '{"type": "installation", "category": "desktop", "product": "callswitch", "feature": "setup"}'
    },
    {
        "content": "CallSwitch One Web Access: Access via browser at callswitchone.app. Same functionality as desktop app with no downloads required. Sign in with mobile number.",
        "metadata": '{"type": "installation", "category": "web", "product": "callswitch", "feature": "access"}'
    },
    {
        "content": "CallSwitch One Mobile Download: Get app from callswitchone.com/downloads or search 'CallSwitch One' in Google Play Store or Apple App Store. Follow SMS invitation link if provided.",
        "metadata": '{"type": "installation", "category": "mobile", "product": "callswitch", "feature": "download"}'
    },
    {
        "content": "CallSwitch One Desktop Download: Visit callswitchone.com/downloads, select operating system, follow installation instructions. Alternative: Use welcome email download link.",
        "metadata": '{"type": "installation", "category": "desktop", "product": "callswitch", "feature": "download"}'
    },
    {
        "content": "CallSwitch One Mobile Sign-In: Enter mobile number in app, receive 6-digit verification code via SMS, enter code to complete setup and start using features.",
        "metadata": '{"type": "installation", "category": "mobile", "product": "callswitch", "feature": "authentication"}'
    },
    {
        "content": "CallSwitch One Desktop Sign-In: Enter mobile number or use mobile app to scan QR code (More > My Devices > Link a Device > Scan Desktop QR Code).",
        "metadata": '{"type": "installation", "category": "desktop", "product": "callswitch", "feature": "authentication"}'
    },
    # CallSwitch One Auto-Deployment Documents
    {
        "content": "CallSwitch One Auto-Deployment Overview: App enables smartphones and desktops as work phone extensions. Supports remote/mobile/office work with calls, messaging, file sharing, and settings management.",
        "metadata": '{"type": "deployment", "category": "overview", "product": "callswitch", "feature": "setup"}'
    },
    {
        "content": "CallSwitch One Mobile Setup: Download from callswitchone.com/downloads or app stores. Enter mobile number and Company Code from admin. Verify with SMS code. Complete profile with name/email.",
        "metadata": '{"type": "deployment", "category": "mobile", "product": "callswitch", "feature": "setup"}'
    },
    {
        "content": "CallSwitch One Mobile Activation: System assigns Extension Number visible on home screen/dial pad. Ready for calls after profile completion and extension assignment.",
        "metadata": '{"type": "deployment", "category": "mobile", "product": "callswitch", "feature": "activation"}'
    },
    {
        "content": "CallSwitch One Desktop QR Setup: If mobile app ready - open desktop app, use mobile app to scan (More > My Devices > Link a Device > Scan Desktop QR Code).",
        "metadata": '{"type": "deployment", "category": "desktop", "product": "callswitch", "feature": "qr-setup"}'
    },
    {
        "content": "CallSwitch One Desktop Manual Setup: Download from callswitchone.com/downloads. Select Login as Member, use Company Code. Enter name, email, create password (8+ chars, mixed case, number, special).",
        "metadata": '{"type": "deployment", "category": "desktop", "product": "callswitch", "feature": "manual-setup"}'
    },
    {
        "content": "CallSwitch One Desktop Activation: After registration, log in with email/password. Desktop app ready for calls and features after successful login.",
        "metadata": '{"type": "deployment", "category": "desktop", "product": "callswitch", "feature": "activation"}'
    },
    {
        "content": "CallSwitch One Web Access: Visit callswitchone.app for browser-based access. Identical functionality to desktop app without downloads. Use same login credentials.",
        "metadata": '{"type": "deployment", "category": "web", "product": "callswitch", "feature": "access"}'
    },
    {
        "content": "CallSwitch One Password Requirements: Minimum 8 characters, must include uppercase and lowercase letters, at least one number, and one special character.",
        "metadata": '{"type": "deployment", "category": "security", "product": "callswitch", "feature": "password"}'
    },
    # CallSwitch One Hot Desking Documents
    {
        "content": "CallSwitch One Hot Desking Overview: Enable users to log into shared devices with personal credentials for flexible workspaces. Supports Yealink and Grandstream devices from TelcoSwitch/NetXL.",
        "metadata": '{"type": "feature", "category": "hot-desking", "product": "callswitch", "feature": "overview"}'
    },
    {
        "content": "CallSwitch Hot Desk Device Setup: Access Config > Hardware > My Devices. Click +Add Hardware, enter MAC Address and Serial Number. Name device, select handset type, enable Hot Desking toggle.",
        "metadata": '{"type": "feature", "category": "hot-desking", "product": "callswitch", "feature": "device-setup"}'
    },
    {
        "content": "CallSwitch Hot Desk MAC Address: Find MAC on device barcode, box, or device menu. For Yealink phones: Menu > Status to locate MAC address. Required for device provisioning.",
        "metadata": '{"type": "feature", "category": "hot-desking", "product": "callswitch", "feature": "mac-address"}'
    },
    {
        "content": "CallSwitch Hot Desk Login: Use default short code *59 or configure custom code. Enter Extension Number and PIN (if enabled). Device displays Hot Desk as registered name when ready.",
        "metadata": '{"type": "feature", "category": "hot-desking", "product": "callswitch", "feature": "login"}'
    },
    {
        "content": "CallSwitch Hot Desk User Setup: In dashboard Users section, edit user settings. Select Enable or Enable with PIN from Hot Desking dropdown. Set 4-digit PIN if required.",
        "metadata": '{"type": "feature", "category": "hot-desking", "product": "callswitch", "feature": "user-setup"}'
    },
    {
        "content": "CallSwitch Hot Desk Short Codes: Default login/logout code is *59. Create custom codes via Config > Short Codes in dashboard. Configure for flexible login options.",
        "metadata": '{"type": "feature", "category": "hot-desking", "product": "callswitch", "feature": "short-codes"}'
    },
    {
        "content": "CallSwitch Hot Desk Monitoring: View active hot desk sessions in Hardware section > Hot Desking tab. Track logged-in users and their assigned devices.",
        "metadata": '{"type": "feature", "category": "hot-desking", "product": "callswitch", "feature": "monitoring"}'
    },
    {
        "content": "CallSwitch Hot Desk Security: Optional PIN security with 4-digit code. Enable with PIN option adds authentication layer for shared device access.",
        "metadata": '{"type": "feature", "category": "hot-desking", "product": "callswitch", "feature": "security"}'
    },
    # CallSwitch One Provisioning Documents
    {
        "content": "CallSwitch One Provisioning Overview: Auto-provision Yealink and Grandstream devices from TelcoSwitch/NetXL. Third-party handsets require support contact with MAC address for provisioning system access.",
        "metadata": '{"type": "provisioning", "category": "overview", "product": "callswitch", "feature": "setup"}'
    },
    {
        "content": "CallSwitch Phone Provisioning Steps: Access Config > Hardware > My Devices. Click +Add Hardware. Enter MAC address, serial number (optional), name device, select handset type from dropdown.",
        "metadata": '{"type": "provisioning", "category": "setup", "product": "callswitch", "feature": "configuration"}'
    },
    {
        "content": "CallSwitch MAC Address Location: Find MAC address on device barcode, original box, or device menu. For Yealink phones: Menu > Status. Required for device provisioning setup.",
        "metadata": '{"type": "provisioning", "category": "setup", "product": "callswitch", "feature": "mac-address"}'
    },
    {
        "content": "CallSwitch User Assignment: Use Grid/List View to display devices. Select user from Assigned User(s) dropdown. Map MAC addresses to users. Device auto-registers on boot.",
        "metadata": '{"type": "provisioning", "category": "setup", "product": "callswitch", "feature": "assignment"}'
    },
    {
        "content": "CallSwitch Multi-Account Setup: For multi-account devices, select Show More option. Use extended dropdown to assign additional users to the device.",
        "metadata": '{"type": "provisioning", "category": "setup", "product": "callswitch", "feature": "multi-account"}'
    },
    {
        "content": "CallSwitch Device Management: Changes in dashboard automatically update device. Reassign users through dropdown menu. Real-time provisioning updates.",
        "metadata": '{"type": "provisioning", "category": "management", "product": "callswitch", "feature": "updates"}'
    },
    {
        "content": "CallSwitch Supported Devices: Yealink and Grandstream devices from TelcoSwitch/NetXL support auto-provisioning. Contact support for third-party handset provisioning.",
        "metadata": '{"type": "provisioning", "category": "hardware", "product": "callswitch", "feature": "compatibility"}'
    },
    # CallSwitch One Call Monitoring Documents
    {
        "content": "CallSwitch One Call Monitor Overview: Enables supervisors and trainers to improve communication and customer service through live call monitoring. Features include listen, whisper, and join capabilities.",
        "metadata": '{"type": "feature", "category": "monitoring", "product": "callswitch", "feature": "overview"}'
    },
    {
        "content": "CallSwitch Monitor Setup: Access Voice Tab > Users, click Edit for target user. Enable Listen toggle in Call Monitor tab. Optional: Enable Whisper for coaching, Join for participation.",
        "metadata": '{"type": "feature", "category": "monitoring", "product": "callswitch", "feature": "setup"}'
    },
    {
        "content": "CallSwitch Monitor Permissions: Enable Listen for silent monitoring, Whisper for agent coaching (caller can't hear), Join for full conversation participation. Allow Other SIP Users option for team monitoring.",
        "metadata": '{"type": "feature", "category": "monitoring", "product": "callswitch", "feature": "permissions"}'
    },
    {
        "content": "CallSwitch Monitor Short Codes: Configure via Voice Tab > Config > Short Codes. Add codes for Listen/Whisper/Join to Extension commands. Use *10 to *99 range for custom codes.",
        "metadata": '{"type": "feature", "category": "monitoring", "product": "callswitch", "feature": "short-codes"}'
    },
    {
        "content": "CallSwitch Listen Mode: Use assigned Listen Short Code to silently monitor active calls. Ideal for quality assessment and training purposes.",
        "metadata": '{"type": "feature", "category": "monitoring", "product": "callswitch", "feature": "listen"}'
    },
    {
        "content": "CallSwitch Whisper Mode: Use Whisper Short Code to privately coach agents during calls. Callers cannot hear supervisor guidance. Perfect for real-time training.",
        "metadata": '{"type": "feature", "category": "monitoring", "product": "callswitch", "feature": "whisper"}'
    },
    {
        "content": "CallSwitch Join Mode: Dial Join Short Code to enter conversation. Both agent and caller can hear supervisor. Used for escalation or additional support.",
        "metadata": '{"type": "feature", "category": "monitoring", "product": "callswitch", "feature": "join"}'
    },
    {
        "content": "CallSwitch Monitor Benefits: Enables real-time coaching, instant customer service improvement, flexible monitoring options. Multiple users can monitor and assist as needed.",
        "metadata": '{"type": "feature", "category": "monitoring", "product": "callswitch", "feature": "benefits"}'
    },
    # CallSwitch One Statistics Documents
    {
        "content": "CallSwitch One Statistics Overview: Track detailed insights for inbound/outbound calls across users, hunt groups, and queues. Monitor total calls, unanswered/answered calls, average/total duration.",
        "metadata": '{"type": "feature", "category": "statistics", "product": "callswitch", "feature": "overview"}'
    },
    {
        "content": "CallSwitch User Statistics Access: Navigate to Voice Tab > Calls > Inbound/Outbound Statistics > Search Statistics. Select users/groups via Calls To dropdown, set date range and timeframe.",
        "metadata": '{"type": "feature", "category": "statistics", "product": "callswitch", "feature": "user-stats"}'
    },
    {
        "content": "CallSwitch Queue Statistics: Access via Voice Tab > Calls > Inbound > Queue Statistics. Track total calls, durations (total/talk/ring/wait), agent missed calls, last call answered.",
        "metadata": '{"type": "feature", "category": "statistics", "product": "callswitch", "feature": "queue-stats"}'
    },
    {
        "content": "CallSwitch Queue Metrics: Filter by date range, timeframe, and call answer time. View comprehensive metrics including total calls, various duration types, missed calls tracking.",
        "metadata": '{"type": "feature", "category": "statistics", "product": "callswitch", "feature": "queue-metrics"}'
    },
    {
        "content": "CallSwitch Report Scheduling: Access Voice > Calls > Statistics > Schedule Reports. Set report nickname, frequency (daily/weekly), select statistics, add email recipients and delivery times.",
        "metadata": '{"type": "feature", "category": "statistics", "product": "callswitch", "feature": "scheduling"}'
    },
    {
        "content": "CallSwitch Statistics Export: Download statistics to local device for detailed analysis. Export options available for all statistical views including user and queue data.",
        "metadata": '{"type": "feature", "category": "statistics", "product": "callswitch", "feature": "export"}'
    },
    {
        "content": "CallSwitch Statistics Benefits: Monitor performance metrics, analyze call patterns, optimize call management. Automated reporting keeps teams updated without manual effort.",
        "metadata": '{"type": "feature", "category": "statistics", "product": "callswitch", "feature": "benefits"}'
    },
    {
        "content": "CallSwitch Statistics Metrics: Track total calls, answered/unanswered calls, average duration, total duration. Comprehensive insights for performance monitoring.",
        "metadata": '{"type": "feature", "category": "statistics", "product": "callswitch", "feature": "metrics"}'
    },
    # CallSwitch One Group Chat Documents
    {
        "content": "CallSwitch One Group Chat Creation: Access Chat icon in main navigation, click New Chat. Search and select group members, enter Group Name, click Create Group.",
        "metadata": '{"type": "feature", "category": "chat", "product": "callswitch", "feature": "group-creation"}'
    },
    {
        "content": "CallSwitch Group Chat Features: Send messages to all members simultaneously, share files (documents/images), record and send voice notes. Enables team-wide communication.",
        "metadata": '{"type": "feature", "category": "chat", "product": "callswitch", "feature": "capabilities"}'
    },
    {
        "content": "CallSwitch Group Chat Management: Access options via ellipsis menu - Add Users, Pin Chat, Mute Chat, Leave Group. Manage group membership and notifications.",
        "metadata": '{"type": "feature", "category": "chat", "product": "callswitch", "feature": "management"}'
    },
    {
        "content": "CallSwitch Group Chat Editing: Select Edit to upload group image, rename group, or delete chat. Customize group appearance and settings for better organization.",
        "metadata": '{"type": "feature", "category": "chat", "product": "callswitch", "feature": "editing"}'
    },
    {
        "content": "CallSwitch Group Chat Navigation: Find group chats in Chat section. Pin important groups for quick access. Use search to find specific group conversations.",
        "metadata": '{"type": "feature", "category": "chat", "product": "callswitch", "feature": "navigation"}'
    },
    {
        "content": "CallSwitch Group Chat Sharing: Share files, documents, images within group. Send voice notes for quick audio communication. Facilitates team collaboration.",
        "metadata": '{"type": "feature", "category": "chat", "product": "callswitch", "feature": "sharing"}'
    },
    # CallSwitch One Short Code Documents
    {
        "content": "CallSwitch One Short Codes Overview: Configure custom short codes (*10 to *99) for quick access to system functions. Manage through CallSwitch One Administrative Dashboard.",
        "metadata": '{"type": "feature", "category": "short-codes", "product": "callswitch", "feature": "overview"}'
    },
    {
        "content": "CallSwitch Short Code Access: Log into Administrative Dashboard, navigate to Config section, select Short Codes. System provides interface for code management.",
        "metadata": '{"type": "feature", "category": "short-codes", "product": "callswitch", "feature": "access"}'
    },
    {
        "content": "CallSwitch Short Code Creation: Click Add Short Code button. System suggests lowest available code (*10-*99). Select desired function from Command dropdown menu.",
        "metadata": '{"type": "feature", "category": "short-codes", "product": "callswitch", "feature": "creation"}'
    },
    {
        "content": "CallSwitch Short Code Configuration: Configure additional details for specific commands (e.g., parking slot numbers). Save Changes to apply new short code settings.",
        "metadata": '{"type": "feature", "category": "short-codes", "product": "callswitch", "feature": "configuration"}'
    },
    {
        "content": "CallSwitch Short Code Management: Create and manage custom codes for quick access to system functions from VoIP devices. Enable efficient call handling and feature access.",
        "metadata": '{"type": "feature", "category": "short-codes", "product": "callswitch", "feature": "management"}'
    },
    # CallSwitch One Voicemail Documents
    {
        "content": "CallSwitch One Voicemail Overview: Change mailbox greetings via four methods - direct recording, VoIP device recording, pre-recorded file upload, or text-to-speech generation.",
        "metadata": '{"type": "feature", "category": "voicemail", "product": "callswitch", "feature": "overview"}'
    },
    {
        "content": "CallSwitch Direct Recording: Dial mailbox extension, select Option 4 to record new greeting. Follow prompts to save recording directly in voicemail system.",
        "metadata": '{"type": "feature", "category": "voicemail", "product": "callswitch", "feature": "direct-recording"}'
    },
    {
        "content": "CallSwitch VoIP Recording: Dial *50 from device, press any key to save. Access Voice Tab > Audio to find recording. Edit mailbox (Config > Mailboxes), select from Greeting dropdown.",
        "metadata": '{"type": "feature", "category": "voicemail", "product": "callswitch", "feature": "voip-recording"}'
    },
    {
        "content": "CallSwitch Audio Upload: Go to Voice Tab > Audio > Add Audio. Upload file, set Nickname and Type (Mailbox Greeting). Assign via Config > Mailboxes > Edit > Greeting dropdown.",
        "metadata": '{"type": "feature", "category": "voicemail", "product": "callswitch", "feature": "audio-upload"}'
    },
    {
        "content": "CallSwitch Text-to-Speech: Access Voice Tab > Audio > Add Audio > Text to Speech. Enter script, select Voice Type/Language/Actor. Set as Mailbox Greeting type and assign.",
        "metadata": '{"type": "feature", "category": "voicemail", "product": "callswitch", "feature": "text-to-speech"}'
    },
    {
        "content": "CallSwitch Greeting Assignment: Navigate to Config > Mailboxes, click Edit icon. Select greeting from dropdown menu, click Save Changes to apply new greeting.",
        "metadata": '{"type": "feature", "category": "voicemail", "product": "callswitch", "feature": "assignment"}'
    },
    # CallSwitch One Hunt Group Documents
    {
        "content": "CallSwitch One Hunt Groups Overview: Hunt groups distribute incoming calls across multiple team members. Enable simultaneous or sequential routing to group extensions.",
        "metadata": '{"type": "feature", "category": "hunt-groups", "product": "callswitch", "feature": "overview"}'
    },
    {
        "content": "CallSwitch Hunt Group Setup: Access Voice tab > Users dropdown > Hunt Groups tab. Select users for group, assign Nickname and Group Extension number.",
        "metadata": '{"type": "feature", "category": "hunt-groups", "product": "callswitch", "feature": "setup"}'
    },
    {
        "content": "CallSwitch Hunt Group Configuration: Choose team members to include, set group identification nickname, configure extension for routing. Save changes to activate.",
        "metadata": '{"type": "feature", "category": "hunt-groups", "product": "callswitch", "feature": "configuration"}'
    },
    {
        "content": "CallSwitch Hunt Group Management: Distribute calls to multiple extensions simultaneously or sequentially. Manage team availability through hunt group settings.",
        "metadata": '{"type": "feature", "category": "hunt-groups", "product": "callswitch", "feature": "management"}'
    },
    # CallSwitch One Department Documents
    {
        "content": "CallSwitch One Department Access: Navigate to Voice tab > Users > Departments in account dashboard. Manage department structure and user assignments.",
        "metadata": '{"type": "feature", "category": "departments", "product": "callswitch", "feature": "access"}'
    },
    {
        "content": "CallSwitch Department Creation: Click Create Department button. Enter Department Name and optional Description. Select users to add to department. Save Changes to apply.",
        "metadata": '{"type": "feature", "category": "departments", "product": "callswitch", "feature": "creation"}'
    },
    {
        "content": "CallSwitch Department Management: Department information visible in SIP User Details tab and CallSwitch One Application. Organize users by department for better management.",
        "metadata": '{"type": "feature", "category": "departments", "product": "callswitch", "feature": "management"}'
    },
    {
        "content": "CallSwitch Department Organization: Structure users into logical groups for easier administration. Department assignments reflect in user details and application interface.",
        "metadata": '{"type": "feature", "category": "departments", "product": "callswitch", "feature": "organization"}'
    },
    # CallSwitch One Call Routing Documents
    {
        "content": "CallSwitch One Call Routing Overview: Direct and manage incoming calls with predetermined instructions. Essential for optimizing call handling, customer service, and communication workflows.",
        "metadata": '{"type": "feature", "category": "routing", "product": "callswitch", "feature": "overview"}'
    },
    {
        "content": "CallSwitch Routing Features: Customizable instructions and advanced options including IVR menus, call queuing, conference bridges, voicemail. Direct calls to appropriate staff members.",
        "metadata": '{"type": "feature", "category": "routing", "product": "callswitch", "feature": "capabilities"}'
    },
    {
        "content": "CallSwitch Route Creation: Access Voice Tab > Inbound Settings > Routing > Add Call Route. Assign Nickname for identification. Drag-and-drop modules to build route.",
        "metadata": '{"type": "feature", "category": "routing", "product": "callswitch", "feature": "setup"}'
    },
    {
        "content": "CallSwitch Route Configuration: Specify destination (user/group/external), set ring duration (minimum 15s for VoIP). Customize caller tones with default or custom audio.",
        "metadata": '{"type": "feature", "category": "routing", "product": "callswitch", "feature": "configuration"}'
    },
    {
        "content": "CallSwitch Route Assignment: Link configured route to system number. Save changes to activate new call routing setup. Ensure proper destination and timing settings.",
        "metadata": '{"type": "feature", "category": "routing", "product": "callswitch", "feature": "assignment"}'
    },
    {
        "content": "CallSwitch Routing Modules: IVR for call menus, Queue for caller management, Conference Bridge for multiple participants, Voicemail for missed calls. Enhance inbound experience.",
        "metadata": '{"type": "feature", "category": "routing", "product": "callswitch", "feature": "modules"}'
    },
    # CallSwitch One Ring Order Documents
    {
        "content": "CallSwitch One Ring Order Overview: Multiple ring order options for call queue distribution. Customize ring order per Call Queue group for efficient and fair call handling.",
        "metadata": '{"type": "feature", "category": "queues", "product": "callswitch", "feature": "ring-order"}'
    },
    {
        "content": "CallSwitch Fewest Calls Order: Routes calls to user with least answered calls. Uses timeout setting to move to next user if call unanswered. Ensures balanced call distribution.",
        "metadata": '{"type": "feature", "category": "queues", "product": "callswitch", "feature": "fewest-calls"}'
    },
    {
        "content": "CallSwitch Least Talking Time: Directs calls to user with lowest total call duration. Reset based on configurable Ring Order Period. Balances workload by talk time.",
        "metadata": '{"type": "feature", "category": "queues", "product": "callswitch", "feature": "talking-time"}'
    },
    {
        "content": "CallSwitch Longest Idle: Assigns calls to user with longest time since last answered call. Ensures fair distribution based on agent availability.",
        "metadata": '{"type": "feature", "category": "queues", "product": "callswitch", "feature": "longest-idle"}'
    },
    {
        "content": "CallSwitch Ring All: Simultaneously rings all users in queue. First responder takes call. No timeout or ring order period required. Fastest response time option.",
        "metadata": '{"type": "feature", "category": "queues", "product": "callswitch", "feature": "ring-all"}'
    },
    {
        "content": "CallSwitch Sequential Across: Routes calls sequentially, continuing from last answering user. Maintains call distribution sequence across multiple calls.",
        "metadata": '{"type": "feature", "category": "queues", "product": "callswitch", "feature": "sequential-across"}'
    },
    {
        "content": "CallSwitch Sequential Restart: Sequential routing restarting from first user for each new call. Consistent starting point for call distribution.",
        "metadata": '{"type": "feature", "category": "queues", "product": "callswitch", "feature": "sequential-restart"}'
    },
    # CallSwitch One Chat Permission Documents
    {
        "content": "CallSwitch One Chat Permissions Overview: Control internal chat access and functionality through dashboard settings. Customize user permissions for chat, SMS, and group management.",
        "metadata": '{"type": "feature", "category": "chat", "product": "callswitch", "feature": "permissions-overview"}'
    },
    {
        "content": "CallSwitch Chat Access Setup: Navigate to Users page in dashboard, click Edit for target user. Access Chat tab to configure chat-related permissions and features.",
        "metadata": '{"type": "feature", "category": "chat", "product": "callswitch", "feature": "access-setup"}'
    },
    {
        "content": "CallSwitch Chat Enable Options: Toggle Chat Enabled for internal chat/SMS access (requires UK mobile). Disable for voice-only users. Control mobile push notifications.",
        "metadata": '{"type": "feature", "category": "chat", "product": "callswitch", "feature": "enable-options"}'
    },
    {
        "content": "CallSwitch Group Chat Permissions: Set Can Create Groups permission for group chat creation. Assign Group Chat Admin rights for existing chat modification.",
        "metadata": '{"type": "feature", "category": "chat", "product": "callswitch", "feature": "group-permissions"}'
    },
    {
        "content": "CallSwitch External Contact Rights: Enable Can Add External Contacts for phonebook additions. Allow users to add and SMS external contacts as needed.",
        "metadata": '{"type": "feature", "category": "chat", "product": "callswitch", "feature": "external-contacts"}'
    },
    {
        "content": "CallSwitch Chat Settings Management: Save Changes after permission configuration. Settings update immediately for affected users. Customize access based on role requirements.",
        "metadata": '{"type": "feature", "category": "chat", "product": "callswitch", "feature": "settings-management"}'
    },
    # CallSwitch One Queue Availability Documents
    {
        "content": "CallSwitch One Queue Availability Overview: Manage user readiness for queue calls. Ensures efficient call routing and improved experience for customers and colleagues.",
        "metadata": '{"type": "feature", "category": "queues", "product": "callswitch", "feature": "availability-overview"}'
    },
    {
        "content": "CallSwitch Queue Availability Function: Users control readiness to take queue calls while remaining available for direct calls and hunt groups. Different from Do Not Disturb which blocks all calls.",
        "metadata": '{"type": "feature", "category": "queues", "product": "callswitch", "feature": "functionality"}'
    },
    {
        "content": "CallSwitch Queue vs DND: Queue availability affects only queue calls, allowing direct and hunt group calls. DND blocks all incoming calls on app and deskphone.",
        "metadata": '{"type": "feature", "category": "queues", "product": "callswitch", "feature": "comparison"}'
    },
    {
        "content": "CallSwitch Desktop Queue Toggle: Click avatar, toggle Available in Call Queue option. Quick access for status changes during breaks or absences.",
        "metadata": '{"type": "feature", "category": "queues", "product": "callswitch", "feature": "desktop-toggle"}'
    },
    {
        "content": "CallSwitch Mobile Queue Toggle: Access More > Settings > Calls, toggle Available in Call Queues setting. Manage availability on the go.",
        "metadata": '{"type": "feature", "category": "queues", "product": "callswitch", "feature": "mobile-toggle"}'
    },
    {
        "content": "CallSwitch Dashboard Queue Settings: Navigate to Users page, Edit user, Advanced tab. Toggle Available in Call Queues, Save Changes. Administrative control over queue availability.",
        "metadata": '{"type": "feature", "category": "queues", "product": "callswitch", "feature": "dashboard-settings"}'
    },
    {
        "content": "CallSwitch Queue Usage Scenarios: Toggle availability for lunch breaks, brief absences, end of workday. Maintain efficient queue operation during user unavailability.",
        "metadata": '{"type": "feature", "category": "queues", "product": "callswitch", "feature": "usage"}'
    },
    # CallSwitch One Mailbox Configuration Documents
    {
        "content": "CallSwitch One Mailbox Overview: Configure voicemail mailboxes through CallSwitch One Administrative dashboard. Manage greetings, notifications, and security settings.",
        "metadata": '{"type": "feature", "category": "mailbox", "product": "callswitch", "feature": "overview"}'
    },
    {
        "content": "CallSwitch Mailbox Access: Navigate to Config section > Mailboxes in dashboard. Click Add Mailbox to create new mailbox configuration.",
        "metadata": '{"type": "feature", "category": "mailbox", "product": "callswitch", "feature": "access"}'
    },
    {
        "content": "CallSwitch Mailbox Setup: Set Nickname for identification, system generates Mailbox Extension. Choose greeting type from dropdown (system or custom). Optional 4-digit PIN for security.",
        "metadata": '{"type": "feature", "category": "mailbox", "product": "callswitch", "feature": "setup"}'
    },
    {
        "content": "CallSwitch Mailbox Notifications: Configure email address for voicemail notifications. System sends alerts when new messages arrive.",
        "metadata": '{"type": "feature", "category": "mailbox", "product": "callswitch", "feature": "notifications"}'
    },
    {
        "content": "CallSwitch Mailbox Management: Enable/disable features via toggle switches. Save Changes to apply new configuration. Internal dialing available for message retrieval.",
        "metadata": '{"type": "feature", "category": "mailbox", "product": "callswitch", "feature": "management"}'
    },
    # CallSwitch One SMS Documents
    {
        "content": "CallSwitch One SMS Overview: Send SMS messages to individual contacts or entire phonebooks. Options for instant delivery, drafts, or scheduled sending.",
        "metadata": '{"type": "feature", "category": "sms", "product": "callswitch", "feature": "overview"}'
    },
    {
        "content": "CallSwitch SMS Access: Navigate to Voice Tab > SMS > Campaigns in CallSwitch One dashboard. Click New SMS to create message. Select Sender ID from dropdown menu.",
        "metadata": '{"type": "feature", "category": "sms", "product": "callswitch", "feature": "access"}'
    },
    {
        "content": "CallSwitch SMS Setup: Add Subject for campaign, choose Sender ID (number appearing as sender). Purchase mobile number from CallSwitch One to enable SMS replies.",
        "metadata": '{"type": "feature", "category": "sms", "product": "callswitch", "feature": "setup"}'
    },
    {
        "content": "CallSwitch SMS Recipients: Send to individual contacts or entire phonebooks. Select recipients from available options. Preview message on right-hand side.",
        "metadata": '{"type": "feature", "category": "sms", "product": "callswitch", "feature": "recipients"}'
    },
    {
        "content": "CallSwitch SMS Delivery Options: Send instantly with Send button, save as draft for later, or schedule delivery with date/time selection.",
        "metadata": '{"type": "feature", "category": "sms", "product": "callswitch", "feature": "delivery"}'
    },
    {
        "content": "CallSwitch SMS Scheduling: Toggle Schedule Message option, select delivery date and time, click Schedule to confirm. Manage scheduled messages in dashboard.",
        "metadata": '{"type": "feature", "category": "sms", "product": "callswitch", "feature": "scheduling"}'
    },
    # CallSwitch One Route Change Documents
    {
        "content": "CallSwitch One Route Change Overview: Use short codes to switch between call routes directly from desk phones or CallSwitch One application. Enable flexible call routing management.",
        "metadata": '{"type": "feature", "category": "routing", "product": "callswitch", "feature": "route-change"}'
    },
    {
        "content": "CallSwitch Route Change Access: Navigate to Voice tab > Config > Short Codes in dashboard. Click Add Short Code to begin configuration process.",
        "metadata": '{"type": "feature", "category": "routing", "product": "callswitch", "feature": "access"}'
    },
    {
        "content": "CallSwitch Route Change Setup: Select available short code (*10-*99). Choose Change the active call route on a number from Command dropdown. Select target number and new route.",
        "metadata": '{"type": "feature", "category": "routing", "product": "callswitch", "feature": "setup"}'
    },
    {
        "content": "CallSwitch Route Reversion: Create additional short code to revert route to original state. Enables easy switching between different routing configurations.",
        "metadata": '{"type": "feature", "category": "routing", "product": "callswitch", "feature": "reversion"}'
    },
    {
        "content": "CallSwitch Route Change Usage: Dial assigned short code from desk phone or CallSwitch One app to change route. Use reversion code to switch back if configured.",
        "metadata": '{"type": "feature", "category": "routing", "product": "callswitch", "feature": "usage"}'
    },
    # CallSwitch One Message Route Documents
    {
        "content": "CallSwitch One Message Routes Overview: Manage incoming SMS routing to chat, email, URL, or text-to-speech delivery. Configure through Voice tab > Inbound Settings > Routing.",
        "metadata": '{"type": "feature", "category": "messaging", "product": "callswitch", "feature": "routes-overview"}'
    },
    {
        "content": "CallSwitch Message Route Setup: Click Add Message Route, set Nickname, select Phonebook, assign Mobile Number (purchased through CallSwitch One). Configure routing modules.",
        "metadata": '{"type": "feature", "category": "messaging", "product": "callswitch", "feature": "route-setup"}'
    },
    {
        "content": "CallSwitch Chat Message Routing: Drag Send Message to Chat module to route area. Select recipient users from dropdown. Messages appear in CallSwitch One Application chat.",
        "metadata": '{"type": "feature", "category": "messaging", "product": "callswitch", "feature": "chat-routing"}'
    },
    {
        "content": "CallSwitch Email Message Routing: Use Send Message to Email module. Add recipient email addresses with plus sign. Forward SMS messages directly to email inboxes.",
        "metadata": '{"type": "feature", "category": "messaging", "product": "callswitch", "feature": "email-routing"}'
    },
    {
        "content": "CallSwitch URL Message Routing: Forward Message to URL module enables system integration. Direct messages to specific URLs for custom handling.",
        "metadata": '{"type": "feature", "category": "messaging", "product": "callswitch", "feature": "url-routing"}'
    },
    {
        "content": "CallSwitch Text-to-Speech Routing: Assign number to route, messages read aloud when received. Press 1 to repeat message during playback. Voice delivery of SMS messages.",
        "metadata": '{"type": "feature", "category": "messaging", "product": "callswitch", "feature": "tts-routing"}'
    },
    # CallSwitch One Time Diary Documents
    {
        "content": "CallSwitch One Time Diary Overview: Apply different call routes based on time of day, week, or specific dates. Ensure efficient call routing according to organization schedule.",
        "metadata": '{"type": "feature", "category": "time-diary", "product": "callswitch", "feature": "overview"}'
    },
    {
        "content": "CallSwitch Time Diary Access: Navigate to Inbound Settings > Time Diaries. Click Create a Time Diary, set Diary Nickname, assign to numbers. Configure working hours and routes.",
        "metadata": '{"type": "feature", "category": "time-diary", "product": "callswitch", "feature": "access"}'
    },
    {
        "content": "CallSwitch Working Hours Setup: Define hours (e.g., 09:00-17:00), select Call Route for active periods. Use Copy to All for consistent routing. Add multiple time periods with + icon.",
        "metadata": '{"type": "feature", "category": "time-diary", "product": "callswitch", "feature": "working-hours"}'
    },
    {
        "content": "CallSwitch Out-of-Hours Configuration: Set Call Route for closed periods. Configure advanced options for different out-of-hours destinations. Manage after-hours call handling.",
        "metadata": '{"type": "feature", "category": "time-diary", "product": "callswitch", "feature": "out-of-hours"}'
    },
    {
        "content": "CallSwitch Custom Days: Access Custom Days tab, click Add Custom Days. Select dates from calendar, define times and routes. Add multiple special dates or holidays.",
        "metadata": '{"type": "feature", "category": "time-diary", "product": "callswitch", "feature": "custom-days"}'
    },
    {
        "content": "CallSwitch Time Diary Management: Review routes using interface symbol. Save Changes to apply settings. Manage multiple time periods including lunch breaks and shifts.",
        "metadata": '{"type": "feature", "category": "time-diary", "product": "callswitch", "feature": "management"}'
    },
    # CallSwitch One Number Assignment Documents
    {
        "content": "CallSwitch One Number Assignment Overview: Assign DDI (Direct Dial In) numbers to users for direct access without reception routing. Enable seamless communication through direct numbers.",
        "metadata": '{"type": "feature", "category": "numbers", "product": "callswitch", "feature": "overview"}'
    },
    {
        "content": "CallSwitch Number Access: Navigate to Voice tab > My Numbers in CallSwitch One dashboard. View list of available numbers and current routing assignments.",
        "metadata": '{"type": "feature", "category": "numbers", "product": "callswitch", "feature": "access"}'
    },
    {
        "content": "CallSwitch Number Assignment: Use Routing dropdown next to desired number, select user from list. Calls automatically route to selected user after assignment.",
        "metadata": '{"type": "feature", "category": "numbers", "product": "callswitch", "feature": "assignment"}'
    },
    {
        "content": "CallSwitch Number Routing: Assigned numbers ring all user devices including desk phones, mobile devices, and desktop applications. Ensures availability across all platforms.",
        "metadata": '{"type": "feature", "category": "numbers", "product": "callswitch", "feature": "routing"}'
    },
    {
        "content": "CallSwitch DDI Management: Monitor number assignments through Routing column. View and modify current call routes, time diaries, or user assignments for each number.",
        "metadata": '{"type": "feature", "category": "numbers", "product": "callswitch", "feature": "management"}'
    },
    # CallSwitch One Call Restriction Documents
    {
        "content": "CallSwitch One Call Restrictions Overview: Control fraud, expenses, and nuisance calls through customizable restrictions. Configure outbound/inbound call limitations via dashboard.",
        "metadata": '{"type": "feature", "category": "restrictions", "product": "callswitch", "feature": "overview"}'
    },
    {
        "content": "CallSwitch Outbound Restrictions: Access Calls > Restrictions to deny specific destinations (local/premium/international). Set Maximum Cost Per Minute limit for outbound calls.",
        "metadata": '{"type": "feature", "category": "restrictions", "product": "callswitch", "feature": "outbound"}'
    },
    {
        "content": "CallSwitch International Blocking: Toggle switch to block all international calls. Add country exceptions via Select Country dropdown. Remove exceptions with Delete button.",
        "metadata": '{"type": "feature", "category": "restrictions", "product": "callswitch", "feature": "international"}'
    },
    {
        "content": "CallSwitch Inbound Restrictions: Enable Block All Anonymous Inbound Calls to prevent withheld numbers. Customize inbound call handling for enhanced security.",
        "metadata": '{"type": "feature", "category": "restrictions", "product": "callswitch", "feature": "inbound"}'
    },
    {
        "content": "CallSwitch Number Blocking: Add specific number sequences to restricted list. Choose Outbound, Inbound, or Both restriction types. Remove restrictions via Delete button.",
        "metadata": '{"type": "feature", "category": "restrictions", "product": "callswitch", "feature": "number-blocking"}'
    },
    {
        "content": "CallSwitch Restriction Management: Configure restrictions through Voice tab > Calls > Restrictions. Save Changes to apply new settings. Monitor and update as needed.",
        "metadata": '{"type": "feature", "category": "restrictions", "product": "callswitch", "feature": "management"}'
    },
    # CallSwitch One Caller ID Documents
    {
        "content": "CallSwitch One Caller ID Overview: Configure available outbound Caller ID numbers for users. Manage through dashboard or short codes. Enable flexible number presentation for outgoing calls.",
        "metadata": '{"type": "feature", "category": "caller-id", "product": "callswitch", "feature": "overview"}'
    },
    {
        "content": "CallSwitch Caller ID Access: Navigate to Voice tab > Users > Edit user > App Registration tab. View and manage list of available numbers for Caller ID use.",
        "metadata": '{"type": "feature", "category": "caller-id", "product": "callswitch", "feature": "access"}'
    },
    {
        "content": "CallSwitch Caller ID Assignment: Click plus sign next to desired numbers or Select All for full access. Save changes to apply number assignments to user profile.",
        "metadata": '{"type": "feature", "category": "caller-id", "product": "callswitch", "feature": "assignment"}'
    },
    {
        "content": "CallSwitch App Caller ID: Users change Caller ID through dropdown menu on keypad in CallSwitch One Application. Dynamic selection from assigned numbers.",
        "metadata": '{"type": "feature", "category": "caller-id", "product": "callswitch", "feature": "app-usage"}'
    },
    {
        "content": "CallSwitch Deskphone Caller ID: Configure short codes for Caller ID changes on deskphones. Enable quick number switching for outbound calls.",
        "metadata": '{"type": "feature", "category": "caller-id", "product": "callswitch", "feature": "deskphone"}'
    },
    # CallSwitch One Phonebook Documents
    {
        "content": "CallSwitch One Phonebook Overview: Manage and share contact information efficiently through centralized phonebooks. Access via dashboard, browser URL, or desk phones.",
        "metadata": '{"type": "feature", "category": "phonebook", "product": "callswitch", "feature": "overview"}'
    },
    {
        "content": "CallSwitch Phonebook Creation: Navigate to Config > Phonebooks. Click Create Phonebook, set Nickname, Username, and Password for access control. Save Changes to generate access URL.",
        "metadata": '{"type": "feature", "category": "phonebook", "product": "callswitch", "feature": "creation"}'
    },
    {
        "content": "CallSwitch Phonebook Sharing: Access phonebook via generated URL using credentials. Add URL to desk phone interfaces for multiple phonebook access. Share credentials with team.",
        "metadata": '{"type": "feature", "category": "phonebook", "product": "callswitch", "feature": "sharing"}'
    },
    {
        "content": "CallSwitch Contact Management: Click Edit on phonebook, use Add Contact for individual entries or Import Contacts from CSV for bulk upload. Add phone numbers and email addresses.",
        "metadata": '{"type": "feature", "category": "phonebook", "product": "callswitch", "feature": "contacts"}'
    },
    {
        "content": "CallSwitch Internal Extensions: Enable Include SIP Users option to incorporate internal extensions into phonebook. Integrate internal and external contacts in one location.",
        "metadata": '{"type": "feature", "category": "phonebook", "product": "callswitch", "feature": "extensions"}'
    },
    {
        "content": "CallSwitch CSV Import: Upload multiple contacts simultaneously using CSV import feature. Efficiently manage large contact lists through bulk operations.",
        "metadata": '{"type": "feature", "category": "phonebook", "product": "callswitch", "feature": "import"}'
    },
    # CallSwitch One Profile Picture Documents
    {
        "content": "CallSwitch One Profile Picture Overview: Update profile pictures through Dashboard, Desktop App, or Mobile App. Customize user profiles with personal images.",
        "metadata": '{"type": "feature", "category": "profile", "product": "callswitch", "feature": "overview"}'
    },
    {
        "content": "CallSwitch Dashboard Profile Update: Access Voice > Users, click Edit icon. Upload image (max 800x800px) via Browse button or drag-drop. Adjust size/zoom with slider.",
        "metadata": '{"type": "feature", "category": "profile", "product": "callswitch", "feature": "dashboard-update"}'
    },
    {
        "content": "CallSwitch Desktop Profile Change: Open desktop app or callswitchone.app. Navigate to Settings > Account & General. Click Change Image, upload and adjust using zoom slider.",
        "metadata": '{"type": "feature", "category": "profile", "product": "callswitch", "feature": "desktop-update"}'
    },
    {
        "content": "CallSwitch Mobile Profile Update: Access More > Settings > Account in mobile app. Tap profile square, choose Take New Photo or Use Existing Photo. Adjust and save image.",
        "metadata": '{"type": "feature", "category": "profile", "product": "callswitch", "feature": "mobile-update"}'
    },
    {
        "content": "CallSwitch Profile Management: Change profile picture anytime by repeating upload process. Available across all platforms for consistent user identification.",
        "metadata": '{"type": "feature", "category": "profile", "product": "callswitch", "feature": "management"}'
    },
    # CallSwitch One Dashboard Login Documents
    {
        "content": "CallSwitch One Dashboard Login Overview: Create individual login credentials for team members. Improve security and enable role-based access control through customizable permissions.",
        "metadata": '{"type": "feature", "category": "access", "product": "callswitch", "feature": "overview"}'
    },
    {
        "content": "CallSwitch Member Creation: Navigate to Account > Members. Click Invite Member, enter First/Last Name and Email. Assign role and customize access levels for specific Dashboard areas.",
        "metadata": '{"type": "feature", "category": "access", "product": "callswitch", "feature": "member-creation"}'
    },
    {
        "content": "CallSwitch Access Customization: Use tabs below member details to set access for Users, Hunt Groups, Numbers. Enable/disable access to individual items. Save Changes to apply.",
        "metadata": '{"type": "feature", "category": "access", "product": "callswitch", "feature": "permissions"}'
    },
    {
        "content": "CallSwitch Member Activation: System sends Welcome Email with Activate Account button. Member creates password and activates account. Resend email via green refresh icon if needed.",
        "metadata": '{"type": "feature", "category": "access", "product": "callswitch", "feature": "activation"}'
    },
    {
        "content": "CallSwitch Role Management: Access Account > Members > Member Roles. Edit existing roles or create new ones. Customize Dashboard area access by ticking relevant boxes.",
        "metadata": '{"type": "feature", "category": "access", "product": "callswitch", "feature": "roles"}'
    },
    {
        "content": "CallSwitch Role Creation: Click Add Role button, set Name, select accessible Dashboard areas. Save Changes to create new role. Assign to new or existing members.",
        "metadata": '{"type": "feature", "category": "access", "product": "callswitch", "feature": "role-creation"}'
    },
    # CallSwitch One Vincere Integration Documents
    {
        "content": "CallSwitch One Vincere Overview: Integrate Vincere CRM with CallSwitch One for seamless contact management. Connect contacts and candidates to phonebook system.",
        "metadata": '{"type": "integration", "category": "crm", "product": "callswitch", "vendor": "vincere", "feature": "overview"}'
    },
    {
        "content": "CallSwitch Vincere Prerequisites: Request API Key and Client ID from Vincere Support (support@vincere.io). Provide redirect URL format: https://www.[dashboardID].callswitchone.com/oauth/vincere",
        "metadata": '{"type": "integration", "category": "crm", "product": "callswitch", "vendor": "vincere", "feature": "setup"}'
    },
    {
        "content": "CallSwitch Vincere Installation: Access Account > Integrations, click Install Integration. Select Vincere, enter Client ID, API Key, and Vincere URL (e.g., https://myaccount.vincere.io).",
        "metadata": '{"type": "integration", "category": "crm", "product": "callswitch", "vendor": "vincere", "feature": "installation"}'
    },
    {
        "content": "CallSwitch Vincere Source Selection: Choose integration source - Contacts (Vincere contacts to phonebook) or Candidates (Vincere candidates to phonebook). Complete process twice for both.",
        "metadata": '{"type": "integration", "category": "crm", "product": "callswitch", "vendor": "vincere", "feature": "configuration"}'
    },
    {
        "content": "CallSwitch Vincere Authorization: Click Continue at Vincere for login form. Enter Vincere credentials, Sign In. System redirects to CallSwitch One for phonebook configuration.",
        "metadata": '{"type": "integration", "category": "crm", "product": "callswitch", "vendor": "vincere", "feature": "authorization"}'
    },
    {
        "content": "CallSwitch Vincere Details: Find API details in Vincere account under Settings cog > Marketplace > API tab. Required for integration setup and configuration.",
        "metadata": '{"type": "integration", "category": "crm", "product": "callswitch", "vendor": "vincere", "feature": "credentials"}'
    },
    # CallSwitch One BigQuery Integration Documents
    {
        "content": "CallSwitch One BigQuery Overview: Integration complies with Google API Services User Data Policy and Limited Use requirements. Ensures privacy and security of accessed data.",
        "metadata": '{"type": "integration", "category": "analytics", "product": "callswitch", "vendor": "bigquery", "feature": "overview"}'
    },
    {
        "content": "CallSwitch BigQuery Data Access: Integration only requests list of projects and associated datasets. Data used exclusively for BigQuery integration purposes.",
        "metadata": '{"type": "integration", "category": "analytics", "product": "callswitch", "vendor": "bigquery", "feature": "data-access"}'
    },
    {
        "content": "CallSwitch BigQuery Consent: Projects and datasets must be explicitly shared and accessible to integrating user. Ensures controlled data access and privacy compliance.",
        "metadata": '{"type": "integration", "category": "analytics", "product": "callswitch", "vendor": "bigquery", "feature": "consent"}'
    },
    {
        "content": "CallSwitch BigQuery Security: Adheres to strict privacy guidelines and security protocols. Limited data access ensures protection of sensitive information.",
        "metadata": '{"type": "integration", "category": "analytics", "product": "callswitch", "vendor": "bigquery", "feature": "security"}'
    },
    # CallSwitch One Call Park Documents
    {
        "content": "CallSwitch One Call Park Overview: Place callers on hold in parking spots for later retrieval by any team member. Enables flexible call transfers without direct transfer requirement.",
        "metadata": '{"type": "feature", "category": "call-park", "product": "callswitch", "feature": "overview"}'
    },
    {
        "content": "CallSwitch Call Park Slots: Five default parking slots available in Parked Area (right side of CallSwitch One Application). Monitor parked calls through visual interface.",
        "metadata": '{"type": "feature", "category": "call-park", "product": "callswitch", "feature": "slots"}'
    },
    {
        "content": "CallSwitch Call Park Process: Press/hold Hold key for 3 seconds to park call. Click green receiver icon or use shortcodes to retrieve parked calls from any device.",
        "metadata": '{"type": "feature", "category": "call-park", "product": "callswitch", "feature": "usage"}'
    },
    {
        "content": "CallSwitch Park Short Codes: Use *11-*15 for Parking Spaces 1-5. Same code parks and retrieves calls (e.g., *11 for Space 1). Configure custom codes in Voice > Config > Short Code.",
        "metadata": '{"type": "feature", "category": "call-park", "product": "callswitch", "feature": "short-codes"}'
    },
    {
        "content": "CallSwitch Park BLF Keys: Add Call Park Short Codes as BLF (Busy Lamp Field) Keys on deskphones for quick access. Monitor parking spot status through BLF indicators.",
        "metadata": '{"type": "feature", "category": "call-park", "product": "callswitch", "feature": "blf"}'
    },
    # CallSwitch One Call Recording Documents
    {
        "content": "CallSwitch One Call Recording Overview: Configure recording settings globally or for specific users/routes. Access through Calls tab > Call History. Choose between Custom, Enabled, or Disabled options.",
        "metadata": '{"type": "feature", "category": "recording", "product": "callswitch", "feature": "overview"}'
    },
    {
        "content": "CallSwitch Global Recording: Select Enabled option in Call History to record all calls system-wide. Choose Disabled to turn off all recording. Custom option for selective recording.",
        "metadata": '{"type": "feature", "category": "recording", "product": "callswitch", "feature": "global"}'
    },
    {
        "content": "CallSwitch User Recording: Navigate to Users section, click blue pencil icon next to user. Toggle Call Recording switch to On for recording all user's inbound/outbound calls.",
        "metadata": '{"type": "feature", "category": "recording", "product": "callswitch", "feature": "user-setup"}'
    },
    {
        "content": "CallSwitch Route Recording: Access Inbound Settings > Routing. Click Show Advanced Settings dropdown for specific route. Enable Call Recording and Save Changes.",
        "metadata": '{"type": "feature", "category": "recording", "product": "callswitch", "feature": "route-setup"}'
    },
    {
        "content": "CallSwitch Recording Management: Padlocked settings indicate Global Recording is active. Switch to Custom mode in Call History to adjust individual settings.",
        "metadata": '{"type": "feature", "category": "recording", "product": "callswitch", "feature": "management"}'
    },
    # CallSwitch One Audio Format Documents
    {
        "content": "CallSwitch One Audio Overview: Supports wide range of audio formats for hold music, voicemail greetings, and call menu prompts. Multiple format options for different use cases.",
        "metadata": '{"type": "feature", "category": "audio", "product": "callswitch", "feature": "overview"}'
    },
    {
        "content": "CallSwitch Common Audio Formats: Supports WAV, MP3, OGG, FLAC, AIFF, AU formats. Recommended for high-quality hold music and greetings. Best clarity and compatibility.",
        "metadata": '{"type": "feature", "category": "audio", "product": "callswitch", "feature": "common-formats"}'
    },
    {
        "content": "CallSwitch Specialized Audio: GSM, SLN, VOC, VOX, VORBIS, CAF, SD2 formats supported. Specialized formats for specific audio requirements and use cases.",
        "metadata": '{"type": "feature", "category": "audio", "product": "callswitch", "feature": "specialized"}'
    },
    {
        "content": "CallSwitch Additional Formats: Supports 8SVX, AIF, AIFC, AIFFC, AL, AMB, AVR, CDDA, CDR, CVS, CVSD, CVU, DAT, DVMS, and many other audio file types.",
        "metadata": '{"type": "feature", "category": "audio", "product": "callswitch", "feature": "additional"}'
    },
    {
        "content": "CallSwitch Audio Best Practices: Use high-quality formats (WAV/MP3) for better clarity. Check file size and compatibility before upload. Ensure format is supported for smooth playback.",
        "metadata": '{"type": "feature", "category": "audio", "product": "callswitch", "feature": "best-practices"}'
    },
    # CallSwitch One Playlist Documents
    {
        "content": "CallSwitch One Playlist Overview: Create and manage audio playlists for hold music and caller wait times. Access through Voice tab > Audio > Playlists for customized caller experience.",
        "metadata": '{"type": "feature", "category": "audio", "product": "callswitch", "feature": "playlist-overview"}'
    },
    {
        "content": "CallSwitch Playlist Creation: Click Add Playlist button. Assign Nickname, set Playback Order from dropdown. Optional: Enable as Default Hold Music for system-wide use.",
        "metadata": '{"type": "feature", "category": "audio", "product": "callswitch", "feature": "playlist-creation"}'
    },
    {
        "content": "CallSwitch Playlist Configuration: Select audio files from dropdown menu, click plus icon to add to playlist box. Combine Music On Hold with other audio files for custom experience.",
        "metadata": '{"type": "feature", "category": "audio", "product": "callswitch", "feature": "playlist-config"}'
    },
    {
        "content": "CallSwitch Playlist Management: Save Changes to finalize playlist settings. Use for hold music, wait times, and other caller scenarios requiring audio playback.",
        "metadata": '{"type": "feature", "category": "audio", "product": "callswitch", "feature": "playlist-management"}'
    },
    # CallSwitch One Music On Hold Documents
    {
        "content": "CallSwitch One Music On Hold Overview: Upload and manage custom music files for call queues, routes, and users. Access through Voice tab > Audio > Audio Files section.",
        "metadata": '{"type": "feature", "category": "audio", "product": "callswitch", "feature": "moh-overview"}'
    },
    {
        "content": "CallSwitch MOH Upload: Click Add Audio, browse for file, set Audio Nickname and Label. Select Music On Hold from Type dropdown. Save Changes to complete upload.",
        "metadata": '{"type": "feature", "category": "audio", "product": "callswitch", "feature": "moh-upload"}'
    },
    {
        "content": "CallSwitch MOH Management: Access files in Custom tab. Download (blue arrow), Play (red button), Edit (blue icon), or Delete (red bin). Search feature available for file location.",
        "metadata": '{"type": "feature", "category": "audio", "product": "callswitch", "feature": "moh-management"}'
    },
    {
        "content": "CallSwitch MOH Assignment: Apply music to Queue Notice Playlists, Call Routes, or Users. Configure default music settings for consistent customer experience.",
        "metadata": '{"type": "feature", "category": "audio", "product": "callswitch", "feature": "moh-assignment"}'
    },
    {
        "content": "CallSwitch Default MOH: Access pre-loaded music options in Default tab of Audio section. Use as alternatives to custom uploads. Ready-to-use professional audio selections.",
        "metadata": '{"type": "feature", "category": "audio", "product": "callswitch", "feature": "moh-default"}'
    },
    # CallSwitch One Audio File Documents
    {
        "content": "CallSwitch One Audio File Overview: Upload, record, or generate audio files through Voice tab > Audio > Audio Files. Multiple creation methods available for different needs.",
        "metadata": '{"type": "feature", "category": "audio", "product": "callswitch", "feature": "file-overview"}'
    },
    {
        "content": "CallSwitch Audio Upload: Click Add Audio, use Browse button to locate file. Set Audio Nickname, Label, and Type. Save Changes to complete upload process.",
        "metadata": '{"type": "feature", "category": "audio", "product": "callswitch", "feature": "file-upload"}'
    },
    {
        "content": "CallSwitch Audio Recording: Select Record Audio tab, use shortcode *50. Press any key to stop, 1 to save, 2 to listen, 3 to re-record, 9 to exit. Files appear as Recorded by phone.",
        "metadata": '{"type": "feature", "category": "audio", "product": "callswitch", "feature": "recording"}'
    },
    {
        "content": "CallSwitch Text-to-Speech: Access Text to Speech tab, enter script. Select Voice Type, Accent, Actor. Preview TTS before saving. Set nickname and type for organization.",
        "metadata": '{"type": "feature", "category": "audio", "product": "callswitch", "feature": "tts"}'
    },
    {
        "content": "CallSwitch Audio Management: Download (blue arrow), Play (red button), Edit (blue icon), Delete (red bin). Search Audio Files feature for quick location. Files stored in Custom tab.",
        "metadata": '{"type": "feature", "category": "audio", "product": "callswitch", "feature": "file-management"}'
    }
]

def load_test_documents():
    try:
        response = requests.post(
            "http://localhost:8088/api/load-documents",  # Updated to correct port
            json=documents
        )
        print(f"Status code: {response.status_code}")
        print("Response:", response.json())
        return response.status_code == 200
    except requests.exceptions.RequestException as e:
        print(f"Error making request: {e}")
        return False
    except json.JSONDecodeError as e:
        print(f"Error decoding response: {e}")
        return False

if __name__ == "__main__":
    success = load_test_documents()
    if not success:
        sys.exit(1) 