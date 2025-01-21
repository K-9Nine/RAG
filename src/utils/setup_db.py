import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

import weaviate
import time
from src.utils.document_processor import DocumentProcessor, Category

def setup_database():
    print("Connecting to Weaviate...")
    client = weaviate.Client(
        url="http://weaviate:8080"
    )

    # Delete existing schema if it exists
    print("Cleaning up existing schema...")
    try:
        client.schema.delete_all()
        print("Deleted existing schema")
    except Exception as e:
        print(f"Note: {e}")

    time.sleep(2)  # Wait for deletion to complete

    # Create new schema
    print("Creating new schema...")
    schema = {
        "class": "SupportDocs",
        "vectorizer": "text2vec-openai",
        "moduleConfig": {
            "text2vec-openai": {
                "model": "ada",
                "modelVersion": "002",
                "type": "text"
            }
        },
        "properties": [
            {
                "name": "content",
                "dataType": ["text"],
                "moduleConfig": {
                    "text2vec-openai": {
                        "skip": False,
                        "vectorizePropertyName": False
                    }
                }
            },
            {
                "name": "category",
                "dataType": ["text"],
                "moduleConfig": {
                    "text2vec-openai": {
                        "skip": True,
                        "vectorizePropertyName": False
                    }
                }
            },
            {
                "name": "metadata",
                "dataType": ["text"],
                "moduleConfig": {
                    "text2vec-openai": {
                        "skip": True,
                        "vectorizePropertyName": False
                    }
                }
            }
        ]
    }

    try:
        client.schema.create_class(schema)
        print("Schema created successfully")
    except Exception as e:
        print(f"Error creating schema: {e}")
        return

    # Add test documents
    print("\nAdding test documents...")
    test_docs = [
        # Phone System
        {
            "content": "To change your CallSwitch password, log into the web portal, go to User Settings > Security, and select 'Change Password'. Enter your current password and your new password twice to confirm.",
            "category": "phone",
            "metadata": "password management"
        },
        {
            "content": "CallSwitch Voicemail Setup: To change your voicemail greeting, dial your extension, press * during the greeting, enter your PIN, then select option 4 to record a new greeting.",
            "category": "phone",
            "metadata": "voicemail configuration"
        },
        {
            "content": "Call Forwarding: Enable call forwarding by dialing *72 followed by the destination number. To disable, dial *73. You can also configure this in the CallSwitch web portal under User Settings > Forward.",
            "category": "phone",
            "metadata": "call management"
        },
        {
            "content": "Conference Calling: To start a conference call, dial the first participant and press *2 after they answer. This puts them on hold. Dial the second participant and press *2 after they answer. Press *2 again to connect all parties. You can add up to 5 participants.",
            "category": "phone",
            "metadata": "conference calls"
        },
        # Fibre Leased Line
        {
            "content": "Our Fibre Leased Line service provides dedicated, symmetric bandwidth from 100Mbps to 10Gbps. It includes a 99.9% uptime SLA, 24/7 support, and a 5-hour fix time guarantee. Installation typically takes 45-65 working days.",
            "category": "fibre",
            "metadata": "service overview"
        },
        {
            "content": "Fibre Leased Line fault reporting: Contact our 24/7 support team immediately at the dedicated number. Have your circuit reference ready. We'll begin diagnostics within 15 minutes and dispatch engineers if needed, with updates every hour.",
            "category": "fibre",
            "metadata": "fault reporting"
        },
        # Broadband
        {
            "content": "FTTC Broadband offers speeds up to 80Mbps download and 20Mbps upload. Installation requires an engineer visit to install a new master socket. Typical installation time is 10-15 working days.",
            "category": "broadband",
            "metadata": "FTTC service"
        },
        {
            "content": "For broadband faults, first check your router's power and connections. Try restarting the router. If issues persist, run a speed test and contact our support team with your results and account number.",
            "category": "broadband",
            "metadata": "troubleshooting"
        },
        # Microsoft Email
        {
            "content": "To set up Microsoft 365 email on your phone: Open the Outlook app, tap Add Account, enter your email and password. For manual setup, use outlook.office365.com as the server, port 993 for IMAP, and 587 for SMTP.",
            "category": "email",
            "metadata": "mobile setup"
        },
        {
            "content": "Reset your Microsoft 365 password through the web portal at portal.office.com. Click on your profile picture, select 'View account', then 'Security & privacy' and 'Password'. Follow the prompts to create a new password.",
            "category": "email",
            "metadata": "password reset"
        },
        {
            "content": "Microsoft Teams is included with your Microsoft 365 subscription. Download Teams from teams.microsoft.com, sign in with your email, and you can start collaborating with video calls, chat, and file sharing.",
            "category": "email",
            "metadata": "teams setup"
        },
        # Additional Phone System docs
        {
            "content": "To set up call recording, log into the CallSwitch portal and navigate to User Settings > Recording. You can enable automatic recording for all calls or set up on-demand recording by pressing *1 during a call.",
            "category": "phone",
            "metadata": "call recording"
        },
        {
            "content": "To access your voicemail remotely: 1. Dial your direct number 2. Press * during the greeting 3. Enter your PIN when prompted. You can then press 1 to listen to messages, 2 to change your greeting, or 3 to change your PIN.",
            "category": "phone",
            "metadata": "voicemail access"
        },
        {
            "content": "Setting up your desk phone: 1. Connect the phone to your network (PoE or power adapter) 2. The phone will automatically download its configuration 3. Log in with your extension and PIN 4. Your name and extension will appear on the display when ready.",
            "category": "phone",
            "metadata": "phone setup"
        },
        {
            "content": "Mobile app setup: 1. Download 'CallSwitch Mobile' from your app store 2. Open the app and enter your extension@company.com 3. Enter your CallSwitch password 4. Allow notifications for incoming calls 5. Configure mobile data and WiFi settings in the app.",
            "category": "phone",
            "metadata": "mobile setup"
        },
        {
            "content": "To transfer a call: 1. Blind Transfer: Press Transfer + Number + Transfer 2. Attended Transfer: Press Transfer + Number, wait for answer, then Transfer 3. To voicemail: Press Transfer + * + Extension + Transfer.",
            "category": "phone",
            "metadata": "call transfer"
        },
        {
            "content": "Hunt Group settings can be modified in the CallSwitch portal under Admin > Hunt Groups. You can set ring patterns (simultaneous or sequential), add/remove members, set overflow rules, and configure voicemail options.",
            "category": "phone",
            "metadata": "hunt groups"
        },
        {
            "content": "Auto Attendant configuration: Access Admin > Auto Attendant to set up menu options, record greetings, set business hours routing, and configure holiday schedules. Each menu option can route to extensions, hunt groups, or external numbers.",
            "category": "phone",
            "metadata": "auto attendant"
        },
        {
            "content": "Call Queue Management: 1. Log into CallSwitch portal 2. Go to Admin > Call Queues 3. Configure max queue size, timeout settings, and comfort messages 4. Add/remove agents 5. Set up overflow rules for busy periods.",
            "category": "phone",
            "metadata": "call queues"
        },
        {
            "content": "To set up call screening: 1. Log into CallSwitch portal 2. Go to User Settings > Screening 3. Choose to accept, reject, or send to voicemail for: anonymous calls, known contacts, or specific numbers.",
            "category": "phone",
            "metadata": "call screening"
        },
        {
            "content": "Busy Lamp Field (BLF) setup: 1. Log into portal 2. Go to User Settings > Phone 3. Select programmable keys 4. Assign extensions to BLF keys 5. Save and wait for phone to reboot. Keys will show colleague's status.",
            "category": "phone",
            "metadata": "BLF configuration"
        },
        # CallSwitch One Line Key Documents
        {
            "content": "CallSwitch One Line Key Overview: Users can manage desk phone line keys through CallSwitch One application. Supports BLF (Busy Lamp Field), Speed Dial, and Short Codes customization.",
            "category": "phone",
            "metadata": '{"type": "voip", "category": "features", "device": "callswitch", "subcategory": "line-keys"}'
        },
        {
            "content": "CallSwitch Line Key Access: 1) Open CallSwitch One Application 2) Navigate to Settings Cog 3) Select Line Key Configuration",
            "category": "phone",
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
        # Adding UCaaS Product Documents
        {
            "content": "UCaaS Overview: Advanced UCaaS License provides comprehensive communication solution integrating cloud telephony, video meetings, team messaging, and file sharing. Supports CRM integration and cloud storage.",
            "category": "phone",
            "metadata": '{"type": "ucaas", "category": "overview", "subcategory": "features"}'
        },
        {
            "content": "UCaaS Communication Features: Access via mobile, desktop, and web apps. Includes plug & play IP handsets, voice/video calls, and messaging. Users can seamlessly switch between communication methods.",
            "category": "phone",
            "metadata": '{"type": "ucaas", "category": "features", "subcategory": "communication"}'
        },
        {
            "content": "UCaaS Call Routing: Drag-and-drop call flow management with multi-level IVR menus, call queues, ring groups, time-of-day routing, on-hold music, and voicemail-to-email functionality.",
            "category": "phone",
            "metadata": '{"type": "ucaas", "category": "features", "subcategory": "call-routing"}'
        },
        {
            "content": "UCaaS Productivity Tools: Host audio/video conferences, use instant messaging, share files, and conduct video meetings with screen sharing and participant management features.",
            "category": "phone",
            "metadata": '{"type": "ucaas", "category": "features", "subcategory": "productivity"}'
        },
        {
            "content": "UCaaS Analytics: Live wallboards show real-time metrics (call wait times, abandonment rates). Includes scheduled reporting for KPI tracking and call supervision tools (listen, whisper, barge).",
            "category": "phone",
            "metadata": '{"type": "ucaas", "category": "features", "subcategory": "analytics"}'
        },
        
        # Adding CallSwitch One iOS App Documents
        {
            "content": "CallSwitch One iOS App Overview: Mobile app enables iPhone to function as work phone extension. Manage calls, messages, files, and settings remotely. Access through iPhone app store.",
            "category": "phone",
            "metadata": '{"type": "mobile", "category": "overview", "platform": "ios", "app": "callswitch"}'
        },
        {
            "content": "CallSwitch iOS Call Handling: Open app to keypad for direct dialing. Access History for call logs (missed/received/made). Use Contacts for internal users and device contacts with Filter option for categories.",
            "category": "phone",
            "metadata": '{"type": "mobile", "category": "calls", "platform": "ios", "app": "callswitch"}'
        },
        {
            "content": "CallSwitch iOS In-Call Features: During calls - Mute microphone, use Keypad for DTMF/short codes, toggle Speaker, add second call. Place calls on Hold or transfer to contacts.",
            "category": "phone",
            "metadata": '{"type": "mobile", "category": "features", "platform": "ios", "app": "callswitch"}'
        },
        {
            "content": "CallSwitch iOS Call Transfer: Press Transfer, select contact or enter external number. Default is unattended transfer. Enable attended (supervised) transfers in Settings > Calls.",
            "category": "phone",
            "metadata": '{"type": "mobile", "category": "transfers", "platform": "ios", "app": "callswitch"}'
        },
        {
            "content": "CallSwitch iOS Device Linking: Connect to desktop/browser version through My Devices. Use QR code icon to log in at callswitchone.app.",
            "category": "phone",
            "metadata": '{"type": "mobile", "category": "setup", "platform": "ios", "app": "callswitch", "feature": "linking"}'
        }
    ]

    processor = DocumentProcessor()
    processor.batch_process_documents(test_docs)

    time.sleep(2)  # Wait for indexing

    # Verify setup
    print("\nVerifying setup...")
    try:
        result = (
            client.query
            .aggregate("SupportDocs")
            .with_meta_count()
            .do()
        )
        
        count = result["data"]["Aggregate"]["SupportDocs"][0]["meta"]["count"]
        print(f"Successfully verified {count} documents in database")
        
        # Test search by category
        for category in ["phone", "fibre", "broadband", "email"]:
            print(f"\nTesting {category} category...")
            test = (
                client.query
                .get("SupportDocs")
                .with_where({
                    "path": ["category"],
                    "operator": "Equal",
                    "valueString": category
                })
                .with_limit(1)
                .do()
            )
            
            if test and 'data' in test and 'Get' in test['data'] and 'SupportDocs' in test['data']['Get']:
                print(f"✓ {category} category verified")
            else:
                print(f"✗ Warning: {category} category test failed")
            
    except Exception as e:
        print(f"Error verifying setup: {e}")

def setup_test_docs():
    test_docs = [
        # Previous documents remain...

        # Adding Android App Documents
        {
            "content": "CallSwitch One Android App Overview: Mobile app transforms Android device into work phone extension. Manage calls, messages, files, history, and settings remotely. Available on Google Play Store.",
            "category": "phone",
            "metadata": '{"type": "mobile", "category": "overview", "platform": "android", "app": "callswitch"}'
        },
        {
            "content": "CallSwitch Android Call Handling: Access keypad for direct dialing with green Call button. View Recent tab for call history (missed/received/made). Use Contacts for internal and device contact lists.",
            "category": "phone",
            "metadata": '{"type": "mobile", "category": "calls", "platform": "android", "app": "callswitch"}'
        },
        {
            "content": "CallSwitch Android Call Transfer: Press Transfer button, select contact or enter number. Default is unattended transfer. Configure attended transfers in Settings > Calls. Use Swap to toggle active lines.",
            "category": "phone",
            "metadata": '{"type": "mobile", "category": "transfers", "platform": "android", "app": "callswitch"}'
        },

        # Adding Profile and Dashboard Documents
        {
            "content": "CallSwitch One Profile Picture Overview: Update profile pictures through Dashboard, Desktop App, or Mobile App. Customize user profiles with personal images.",
            "category": "phone",
            "metadata": '{"type": "feature", "category": "profile", "product": "callswitch", "feature": "overview"}'
        },
        {
            "content": "CallSwitch Dashboard Profile Update: Access Voice > Users, click Edit icon. Upload image (max 800x800px) via Browse button or drag-drop. Adjust size/zoom with slider.",
            "category": "phone",
            "metadata": '{"type": "feature", "category": "profile", "product": "callswitch", "feature": "dashboard-update"}'
        },
        {
            "content": "CallSwitch Desktop Profile Change: Open desktop app or callswitchone.app. Navigate to Settings > Account & General. Click Change Image, upload and adjust using zoom slider.",
            "category": "phone",
            "metadata": '{"type": "feature", "category": "profile", "product": "callswitch", "feature": "desktop-update"}'
        },

        # Adding Audio and Music Documents
        {
            "content": "CallSwitch One Audio Overview: Supports wide range of audio formats for hold music, voicemail greetings, and call menu prompts. Multiple format options for different use cases.",
            "category": "phone",
            "metadata": '{"type": "feature", "category": "audio", "product": "callswitch", "feature": "overview"}'
        },
        {
            "content": "CallSwitch Common Audio Formats: Supports WAV, MP3, OGG, FLAC, AIFF, AU formats. Recommended for high-quality hold music and greetings. Best clarity and compatibility.",
            "category": "phone",
            "metadata": '{"type": "feature", "category": "audio", "product": "callswitch", "feature": "common-formats"}'
        },
        {
            "content": "CallSwitch MOH Upload: Click Add Audio, browse for file, set Audio Nickname and Label. Select Music On Hold from Type dropdown. Save Changes to complete upload.",
            "category": "phone",
            "metadata": '{"type": "feature", "category": "audio", "product": "callswitch", "feature": "moh-upload"}'
        },
        {
            "content": "CallSwitch Audio Recording: Select Record Audio tab, use shortcode *50. Press any key to stop, 1 to save, 2 to listen, 3 to re-record, 9 to exit. Files appear as Recorded by phone.",
            "category": "phone",
            "metadata": '{"type": "feature", "category": "audio", "product": "callswitch", "feature": "recording"}'
        },

        # Adding Call Park and Recording Documents
        {
            "content": "CallSwitch One Call Park Overview: Place callers on hold in parking spots for later retrieval by any team member. Enables flexible call transfers without direct transfer requirement.",
            "category": "phone",
            "metadata": '{"type": "feature", "category": "call-park", "product": "callswitch", "feature": "overview"}'
        },
        {
            "content": "CallSwitch Call Park Slots: Five default parking slots available in Parked Area (right side of CallSwitch One Application). Monitor parked calls through visual interface.",
            "category": "phone",
            "metadata": '{"type": "feature", "category": "call-park", "product": "callswitch", "feature": "slots"}'
        },
        {
            "content": "CallSwitch Park Short Codes: Use *11-*15 for Parking Spaces 1-5. Same code parks and retrieves calls (e.g., *11 for Space 1). Configure custom codes in Voice > Config > Short Code.",
            "category": "phone",
            "metadata": '{"type": "feature", "category": "call-park", "product": "callswitch", "feature": "short-codes"}'
        },
        {
            "content": "CallSwitch One Call Recording Overview: Configure recording settings globally or for specific users/routes. Access through Calls tab > Call History. Choose between Custom, Enabled, or Disabled options.",
            "category": "phone",
            "metadata": '{"type": "feature", "category": "recording", "product": "callswitch", "feature": "overview"}'
        },
        {
            "content": "CallSwitch Global Recording: Select Enabled option in Call History to record all calls system-wide. Choose Disabled to turn off all recording. Custom option for selective recording.",
            "category": "phone",
            "metadata": '{"type": "feature", "category": "recording", "product": "callswitch", "feature": "global"}'
        },

        # Adding Integration Documents
        {
            "content": "CallSwitch One Vincere Overview: Integrate Vincere CRM with CallSwitch One for seamless contact management. Connect contacts and candidates to phonebook system.",
            "category": "phone",
            "metadata": '{"type": "integration", "category": "crm", "product": "callswitch", "vendor": "vincere", "feature": "overview"}'
        },
        {
            "content": "CallSwitch Vincere Prerequisites: Request API Key and Client ID from Vincere Support (support@vincere.io). Provide redirect URL format: https://www.[dashboardID].callswitchone.com/oauth/vincere",
            "category": "phone",
            "metadata": '{"type": "integration", "category": "crm", "product": "callswitch", "vendor": "vincere", "feature": "setup"}'
        },
        {
            "content": "CallSwitch One BigQuery Overview: Integration complies with Google API Services User Data Policy and Limited Use requirements. Ensures privacy and security of accessed data.",
            "category": "phone",
            "metadata": '{"type": "integration", "category": "analytics", "product": "callswitch", "vendor": "bigquery", "feature": "overview"}'
        },
        {
            "content": "CallSwitch BigQuery Security: Adheres to strict privacy guidelines and security protocols. Limited data access ensures protection of sensitive information.",
            "category": "phone",
            "metadata": '{"type": "integration", "category": "analytics", "product": "callswitch", "vendor": "bigquery", "feature": "security"}'
        },

        # Adding Dashboard Login Documents
        {
            "content": "CallSwitch One Dashboard Login Overview: Create individual login credentials for team members. Improve security and enable role-based access control through customizable permissions.",
            "category": "phone",
            "metadata": '{"type": "feature", "category": "access", "product": "callswitch", "feature": "overview"}'
        },
        {
            "content": "CallSwitch Member Creation: Navigate to Account > Members. Click Invite Member, enter First/Last Name and Email. Assign role and customize access levels for specific Dashboard areas.",
            "category": "phone",
            "metadata": '{"type": "feature", "category": "access", "product": "callswitch", "feature": "member-creation"}'
        },
        {
            "content": "CallSwitch Role Management: Access Account > Members > Member Roles. Edit existing roles or create new ones. Customize Dashboard area access by ticking relevant boxes.",
            "category": "phone",
            "metadata": '{"type": "feature", "category": "access", "product": "callswitch", "feature": "roles"}'
        },

        # Adding Unified Communications Documents
        {
            "content": "Unified Communications Overview: Advanced platform with VoIP telephony, call handling, video meetings, chat, presence, and document sharing. Managed through secure dashboard, available on mobile, desktop, and web.",
            "category": "phone",
            "metadata": '{"type": "uc", "category": "overview", "subcategory": "platform"}'
        },
        {
            "content": "UC Applications: Available for desktop (Windows, Mac OS), mobile (iOS, Android), and web browsers. Features include VoIP telephony, advanced call routing, voicemail transcription, and call queues.",
            "category": "phone",
            "metadata": '{"type": "uc", "category": "features", "subcategory": "applications"}'
        },
        {
            "content": "UC Call Management: Drag-and-drop call flow builder with IVR menus, on-hold music, time diaries, voicemail. Includes hunt groups, call-forwarding, and call parking.",
            "category": "phone",
            "metadata": '{"type": "uc", "category": "features", "subcategory": "call-management"}'
        },
        {
            "content": "UC SMS Features: Business SMS supports individual and bulk messaging (up to 20,000 recipients). Includes campaign scheduling and cost tracking per recipient.",
            "category": "phone",
            "metadata": '{"type": "uc", "category": "features", "subcategory": "sms"}'
        },

        # Adding License Information
        {
            "content": "UC VoIP+ License: Includes 500 minutes to UK landlines/mobiles, basic VoIP features (call forwarding, on-hold music), SMS for up to 25 recipients.",
            "category": "phone",
            "metadata": '{"type": "uc", "category": "licensing", "subcategory": "voip-plus"}'
        },
        {
            "content": "UC Advanced License: 2,000 minutes to UK landlines/mobiles, bulk SMS (20,000 recipients), multi-level IVR, video meetings, live wallboards.",
            "category": "phone",
            "metadata": '{"type": "uc", "category": "licensing", "subcategory": "advanced"}'
        },
        {
            "content": "UCaaS License Benefits: 2000 minutes each to UK landlines/mobiles per user. Includes SSO support, CRM integration, bulk SMS (20,000 recipients), 90-day call recording, and voicemail transcription.",
            "category": "phone",
            "metadata": '{"type": "ucaas", "category": "licensing", "subcategory": "benefits"}'
        },

        # Adding Infrastructure and Security
        {
            "content": "UC Infrastructure: Hosted on Google Cloud for global availability and scalability. Features zero-trust security and regular updates through agile development.",
            "category": "phone",
            "metadata": '{"type": "uc", "category": "infrastructure", "subcategory": "cloud"}'
        },
        {
            "content": "UC Microsoft Teams Integration: Make and receive calls within Teams while retaining CallSwitch features. Compatible with leading desk phone manufacturers.",
            "category": "phone",
            "metadata": '{"type": "uc", "category": "integrations", "subcategory": "teams"}'
        },
        {
            "content": "UC CRM Integration: Supports Salesforce, HubSpot, Zoho with click-to-dial and screen pop-ups. Cloud storage backup with Azure, Amazon S3, Dropbox, Google Drive.",
            "category": "phone",
            "metadata": '{"type": "uc", "category": "integrations", "subcategory": "crm"}'
        },

        # Adding Reporting and Analytics
        {
            "content": "UC Reporting: Real-time wallboards and scheduled reports. Monitor KPIs including average wait times, answered calls, and abandonment rates.",
            "category": "phone",
            "metadata": '{"type": "uc", "category": "features", "subcategory": "reporting"}'
        },
        {
            "content": "CallSwitch Analytics: Live wallboards show real-time metrics (call wait times, abandonment rates). Includes scheduled reporting for KPI tracking and call supervision tools (listen, whisper, barge).",
            "category": "phone",
            "metadata": '{"type": "feature", "category": "analytics", "product": "callswitch", "feature": "overview"}'
        },

        # Adding Hot Desk Documents
        {
            "content": "Hot Desk Overview: Enable users to log into any configured desk phone. Access personal settings, contacts, and call history from any device. Ideal for flexible workspaces.",
            "category": "phone",
            "metadata": '{"type": "feature", "category": "hot-desk", "product": "callswitch", "feature": "overview"}'
        },
        {
            "content": "Hot Desk Setup: Configure in Voice > Users. Select Enable or Enable with PIN from Hot Desking dropdown. Set optional 4-digit PIN for added security.",
            "category": "phone",
            "metadata": '{"type": "feature", "category": "hot-desk", "product": "callswitch", "feature": "setup"}'
        },
        {
            "content": "Hot Desk Login Process: Use *59 code on phone. Enter extension number and PIN if enabled. Successful login shows username on display. Logout with *60.",
            "category": "phone",
            "metadata": '{"type": "feature", "category": "hot-desk", "product": "callswitch", "feature": "login"}'
        },

        # Adding Queue Management
        {
            "content": "Queue Overview: Manage incoming calls with advanced routing options. Configure wait times, announcements, and overflow handling. Monitor real-time queue status.",
            "category": "phone",
            "metadata": '{"type": "feature", "category": "queue", "product": "callswitch", "feature": "overview"}'
        },
        {
            "content": "Queue Routing Options: Choose from Ring All, Sequential, Least Recent, or Round Robin. Set wrap-up time between calls. Configure overflow destinations for busy periods.",
            "category": "phone",
            "metadata": '{"type": "feature", "category": "queue", "product": "callswitch", "feature": "routing"}'
        },
        {
            "content": "Queue Agent Status: Agents toggle availability with *61 (available) and *62 (unavailable). Status visible in dashboard and mobile app. Separate from Do Not Disturb.",
            "category": "phone",
            "metadata": '{"type": "feature", "category": "queue", "product": "callswitch", "feature": "agent-status"}'
        },

        # Adding Voicemail Features
        {
            "content": "Voicemail Setup: Access Voice > Users > Voicemail tab. Enable voicemail and configure PIN. Optional email notifications with message attachments.",
            "category": "phone",
            "metadata": '{"type": "feature", "category": "voicemail", "product": "callswitch", "feature": "setup"}'
        },
        {
            "content": "Voicemail Access: Dial *97 from desk phone or mobile app. Enter PIN when prompted. Press 1 for new messages, 2 for saved messages, 3 for greetings.",
            "category": "phone",
            "metadata": '{"type": "feature", "category": "voicemail", "product": "callswitch", "feature": "access"}'
        },
        {
            "content": "Voicemail Greetings: Record custom unavailable and busy greetings. Use *98 for direct greeting management. Upload pre-recorded greetings through dashboard.",
            "category": "phone",
            "metadata": '{"type": "feature", "category": "voicemail", "product": "callswitch", "feature": "greetings"}'
        },

        # Adding Call Flow Features
        {
            "content": "Call Flow Builder: Drag-and-drop interface for creating call routes. Add time conditions, IVR menus, queues, and voicemail. Test flows before publishing.",
            "category": "phone",
            "metadata": '{"type": "feature", "category": "call-flow", "product": "callswitch", "feature": "builder"}'
        },
        {
            "content": "Time Conditions: Set business hours, holidays, and special events. Route calls differently based on time/date. Create unlimited time profiles.",
            "category": "phone",
            "metadata": '{"type": "feature", "category": "call-flow", "product": "callswitch", "feature": "time"}'
        },
        {
            "content": "IVR Menus: Build multi-level menus with custom prompts. Configure digit actions and timeout handling. Set up emergency announcement overrides.",
            "category": "phone",
            "metadata": '{"type": "feature", "category": "call-flow", "product": "callswitch", "feature": "ivr"}'
        },

        # Adding Desktop App Features
        {
            "content": "Desktop App Overview: CallSwitch One desktop application for Windows and Mac. Access calls, messages, contacts, and settings. Available through download portal.",
            "category": "phone",
            "metadata": '{"type": "software", "category": "desktop", "product": "callswitch", "feature": "overview"}'
        },
        {
            "content": "Desktop Call Controls: Make/receive calls, transfer, hold, mute. Click-to-dial from contacts or history. Screen pop notifications for incoming calls.",
            "category": "phone",
            "metadata": '{"type": "software", "category": "desktop", "product": "callswitch", "feature": "calls"}'
        },
        {
            "content": "Desktop Chat Features: Internal messaging with file sharing. Create group chats for team collaboration. Persistent chat history across devices.",
            "category": "phone",
            "metadata": '{"type": "software", "category": "desktop", "product": "callswitch", "feature": "chat"}'
        },

        # Adding Web Browser Features
        {
            "content": "Web App Access: Use CallSwitch One through web browser at callswitchone.app. Compatible with Chrome, Firefox, Safari, Edge. No installation required.",
            "category": "phone",
            "metadata": '{"type": "software", "category": "web", "product": "callswitch", "feature": "access"}'
        },
        {
            "content": "Web App Features: Full functionality including calls, messages, contacts. Access call recordings and voicemail. Manage user settings and preferences.",
            "category": "phone",
            "metadata": '{"type": "software", "category": "web", "product": "callswitch", "feature": "features"}'
        },
        {
            "content": "Web App Requirements: Modern browser with WebRTC support. Microphone and camera permissions for calls/video. Stable internet connection required.",
            "category": "phone",
            "metadata": '{"type": "software", "category": "web", "product": "callswitch", "feature": "requirements"}'
        },

        # Adding Contact Management
        {
            "content": "Contact Overview: Centralized contact management across devices. Internal directory with presence. External contacts with custom fields.",
            "category": "phone",
            "metadata": '{"type": "feature", "category": "contacts", "product": "callswitch", "feature": "overview"}'
        },
        {
            "content": "Contact Import: Bulk import contacts via CSV file. Map custom fields during import. Merge duplicate entries automatically.",
            "category": "phone",
            "metadata": '{"type": "feature", "category": "contacts", "product": "callswitch", "feature": "import"}'
        },
        {
            "content": "Contact Groups: Create contact groups for easy management. Assign contacts to multiple groups. Use groups for bulk messaging.",
            "category": "phone",
            "metadata": '{"type": "feature", "category": "contacts", "product": "callswitch", "feature": "groups"}'
        },

        # Adding Short Code Features
        {
            "content": "Short Code Overview: Quick access to features through dial codes. Standard codes for voicemail, call park, queue login. Custom codes available.",
            "category": "phone",
            "metadata": '{"type": "feature", "category": "short-codes", "product": "callswitch", "feature": "overview"}'
        },
        {
            "content": "Common Short Codes: *97 (voicemail), *98 (greetings), *11-*15 (call park), *59/*60 (hot desk), *61/*62 (queue login/logout).",
            "category": "phone",
            "metadata": '{"type": "feature", "category": "short-codes", "product": "callswitch", "feature": "common"}'
        },
        {
            "content": "Custom Short Codes: Create custom codes in Voice > Config > Short Codes. Assign to specific features or external numbers. Maximum 6 digits.",
            "category": "phone",
            "metadata": '{"type": "feature", "category": "short-codes", "product": "callswitch", "feature": "custom"}'
        }
    ]

    processor = DocumentProcessor()
    processor.batch_process_documents(test_docs)

if __name__ == "__main__":
    setup_database()
    setup_test_docs() 