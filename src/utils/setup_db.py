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
        },

        # Adding Call Transfer Features
        {
            "content": "Call Transfer Overview: Transfer calls between users, departments, or external numbers. Choose between attended (supervised) and blind transfers. Available on all devices.",
            "category": "phone",
            "metadata": '{"type": "feature", "category": "transfer", "product": "callswitch", "feature": "overview"}'
        },
        {
            "content": "Blind Transfer Process: Press Transfer button, dial destination number or select contact, press Transfer again. Call transfers immediately without consultation.",
            "category": "phone",
            "metadata": '{"type": "feature", "category": "transfer", "product": "callswitch", "feature": "blind"}'
        },
        {
            "content": "Attended Transfer: Press Transfer, dial number or select contact, wait for answer and announce call. Press Transfer to complete or Cancel to return.",
            "category": "phone",
            "metadata": '{"type": "feature", "category": "transfer", "product": "callswitch", "feature": "attended"}'
        },

        # Adding Conference Call Features
        {
            "content": "Conference Call Setup: Start with first caller, press Conference button, add second caller. Repeat for additional participants. Maximum 10 participants per conference.",
            "category": "phone",
            "metadata": '{"type": "feature", "category": "conference", "product": "callswitch", "feature": "setup"}'
        },
        {
            "content": "Conference Controls: Host can mute participants, remove callers, or end conference. Participants can mute themselves or exit conference at any time.",
            "category": "phone",
            "metadata": '{"type": "feature", "category": "conference", "product": "callswitch", "feature": "controls"}'
        },
        {
            "content": "Conference Scheduling: Schedule conferences through dashboard. Send invites with dial-in details. Optional PIN protection for secure meetings.",
            "category": "phone",
            "metadata": '{"type": "feature", "category": "conference", "product": "callswitch", "feature": "scheduling"}'
        },

        # Adding Video Meeting Features
        {
            "content": "Video Meeting Overview: Host video conferences with screen sharing and chat. Access through desktop app, mobile app, or web browser. No software required for guests.",
            "category": "phone",
            "metadata": '{"type": "feature", "category": "video", "product": "callswitch", "feature": "overview"}'
        },
        {
            "content": "Video Controls: Toggle camera/microphone, share screen, chat with participants. Host can mute all, remove participants, or lock meeting.",
            "category": "phone",
            "metadata": '{"type": "feature", "category": "video", "product": "callswitch", "feature": "controls"}'
        },
        {
            "content": "Video Recording: Host can record meetings with participant consent. Recordings available in dashboard for 30 days. Download or share via secure link.",
            "category": "phone",
            "metadata": '{"type": "feature", "category": "video", "product": "callswitch", "feature": "recording"}'
        },

        # Adding SMS Features
        {
            "content": "SMS Overview: Send individual or bulk SMS messages. Track delivery status and responses. Available through dashboard, desktop app, or mobile app.",
            "category": "phone",
            "metadata": '{"type": "feature", "category": "sms", "product": "callswitch", "feature": "overview"}'
        },
        {
            "content": "Bulk SMS: Upload recipient list (CSV) or select contact groups. Preview message and cost. Schedule sending time. Maximum 20,000 recipients per campaign.",
            "category": "phone",
            "metadata": '{"type": "feature", "category": "sms", "product": "callswitch", "feature": "bulk"}'
        },
        {
            "content": "SMS Templates: Create and save message templates. Use variables for personalization. Share templates across team for consistent messaging.",
            "category": "phone",
            "metadata": '{"type": "feature", "category": "sms", "product": "callswitch", "feature": "templates"}'
        },

        # Adding Call Forwarding Features
        {
            "content": "Call Forward Overview: Redirect calls to another number or voicemail. Set up different rules for busy/no answer scenarios. Configure through dashboard or phone.",
            "category": "phone",
            "metadata": '{"type": "feature", "category": "forwarding", "product": "callswitch", "feature": "overview"}'
        },
        {
            "content": "Forward Always Setup: Dial *72 followed by destination number to enable. Dial *73 to disable. All calls redirect immediately to specified number.",
            "category": "phone",
            "metadata": '{"type": "feature", "category": "forwarding", "product": "callswitch", "feature": "always"}'
        },
        {
            "content": "Forward on Busy/No Answer: Configure in dashboard under Voice > Users > Call Forward. Set different numbers for busy (*90/*91) and no answer (*92/*93).",
            "category": "phone",
            "metadata": '{"type": "feature", "category": "forwarding", "product": "callswitch", "feature": "conditional"}'
        },

        # Adding Hunt Group Features
        {
            "content": "Hunt Group Overview: Distribute calls across team members. Multiple routing strategies available. Configure overflow handling and voicemail options.",
            "category": "phone",
            "metadata": '{"type": "feature", "category": "hunt-group", "product": "callswitch", "feature": "overview"}'
        },
        {
            "content": "Hunt Group Routing: Choose Sequential (in order), Circular (round robin), or Simultaneous (ring all). Set ring time before moving to next member.",
            "category": "phone",
            "metadata": '{"type": "feature", "category": "hunt-group", "product": "callswitch", "feature": "routing"}'
        },
        {
            "content": "Hunt Group Management: Add/remove members through dashboard. Set business hours and holiday schedules. Configure overflow destination for busy periods.",
            "category": "phone",
            "metadata": '{"type": "feature", "category": "hunt-group", "product": "callswitch", "feature": "management"}'
        },

        # Adding Presence Features
        {
            "content": "Presence Overview: Monitor team member availability in real-time. Status updates automatically with calls or can be set manually. Visible across all devices.",
            "category": "phone",
            "metadata": '{"type": "feature", "category": "presence", "product": "callswitch", "feature": "overview"}'
        },
        {
            "content": "Presence States: Available, On Call, Do Not Disturb, Away, Offline. Custom status messages supported. Integration with calendar for automatic updates.",
            "category": "phone",
            "metadata": '{"type": "feature", "category": "presence", "product": "callswitch", "feature": "states"}'
        },
        {
            "content": "Presence Monitoring: View team status through BLF keys on phones or in apps. Click to call available users. Presence history in analytics reports.",
            "category": "phone",
            "metadata": '{"type": "feature", "category": "presence", "product": "callswitch", "feature": "monitoring"}'
        },

        # Adding Emergency Features
        {
            "content": "Emergency Call Setup: Configure emergency numbers and locations in dashboard. Set up notifications for emergency calls. Update locations for remote workers.",
            "category": "phone",
            "metadata": '{"type": "feature", "category": "emergency", "product": "callswitch", "feature": "setup"}'
        },
        {
            "content": "Emergency Notifications: Alert specified contacts when emergency numbers dialed. Include caller location and timestamp. Optional recording of emergency calls.",
            "category": "phone",
            "metadata": '{"type": "feature", "category": "emergency", "product": "callswitch", "feature": "notifications"}'
        },
        {
            "content": "Emergency Location Management: Register and update emergency locations through dashboard. Required for remote workers and hot desk users. Regular validation recommended.",
            "category": "phone",
            "metadata": '{"type": "feature", "category": "emergency", "product": "callswitch", "feature": "locations"}'
        },

        # Adding Phone Hardware Features
        {
            "content": "Supported Phone Models: Compatible with Yealink T4x, T5x series, Polycom VVX series, and Cisco SPA phones. Auto-provisioning available for supported models.",
            "category": "phone",
            "metadata": '{"type": "hardware", "category": "phones", "product": "callswitch", "feature": "models"}'
        },
        {
            "content": "Phone Provisioning: Add phones through MAC address in dashboard. Select model and user assignment. Configuration pushes automatically to device.",
            "category": "phone",
            "metadata": '{"type": "hardware", "category": "phones", "product": "callswitch", "feature": "provisioning"}'
        },
        {
            "content": "Phone Settings: Configure display language, timezone, ringtones, and screen brightness. Manage through dashboard or phone menu. Changes apply immediately.",
            "category": "phone",
            "metadata": '{"type": "hardware", "category": "phones", "product": "callswitch", "feature": "settings"}'
        },

        # Adding Network Requirements
        {
            "content": "Bandwidth Requirements: Minimum 100Kbps up/down per concurrent call. QoS recommended for voice traffic. Stable internet connection required.",
            "category": "phone",
            "metadata": '{"type": "network", "category": "requirements", "product": "callswitch", "feature": "bandwidth"}'
        },
        {
            "content": "Network Configuration: Open ports 5060-5061 (SIP), 10000-20000 (RTP). Configure firewall for SIP ALG. DHCP reservation recommended for phones.",
            "category": "phone",
            "metadata": '{"type": "network", "category": "requirements", "product": "callswitch", "feature": "ports"}'
        },
        {
            "content": "QoS Settings: Prioritize voice traffic (DSCP 46). Mark SIP signaling (DSCP 26). Configure VLAN for voice if available. Monitor jitter and latency.",
            "category": "phone",
            "metadata": '{"type": "network", "category": "requirements", "product": "callswitch", "feature": "qos"}'
        },

        # Adding Security Features
        {
            "content": "Password Policy: Minimum 8 characters, mix of upper/lower case, numbers, symbols. Regular password changes enforced. Failed login lockout protection.",
            "category": "phone",
            "metadata": '{"type": "security", "category": "authentication", "product": "callswitch", "feature": "passwords"}'
        },
        {
            "content": "Call Encryption: TLS for signaling, SRTP for media. Certificate-based authentication. End-to-end encryption for internal calls.",
            "category": "phone",
            "metadata": '{"type": "security", "category": "encryption", "product": "callswitch", "feature": "calls"}'
        },
        {
            "content": "Access Control: Role-based access control (RBAC). IP address restrictions available. Two-factor authentication support. Audit logging of all changes.",
            "category": "phone",
            "metadata": '{"type": "security", "category": "authentication", "product": "callswitch", "feature": "access"}'
        },

        # Adding Troubleshooting Guides
        {
            "content": "Audio Issues: Check microphone/speaker settings. Verify network connection. Test with different devices. Monitor call quality metrics in dashboard.",
            "category": "phone",
            "metadata": '{"type": "support", "category": "troubleshooting", "product": "callswitch", "feature": "audio"}'
        },
        {
            "content": "Connection Problems: Verify internet connectivity. Check phone power and network cable. Confirm phone registration status. Test alternate network if available.",
            "category": "phone",
            "metadata": '{"type": "support", "category": "troubleshooting", "product": "callswitch", "feature": "connection"}'
        },
        {
            "content": "Login Issues: Verify username/password. Clear browser cache for web app. Check account status in dashboard. Contact support for account lockouts.",
            "category": "phone",
            "metadata": '{"type": "support", "category": "troubleshooting", "product": "callswitch", "feature": "login"}'
        },

        # Adding Wallboard Features
        {
            "content": "Wallboard Overview: Real-time display of call center metrics. Customizable layouts and KPIs. Available on large screens or web browsers.",
            "category": "phone",
            "metadata": '{"type": "feature", "category": "wallboard", "product": "callswitch", "feature": "overview"}'
        },
        {
            "content": "Wallboard Metrics: Monitor calls waiting, average wait time, abandoned calls, agent status, SLA compliance. Historical comparisons available.",
            "category": "phone",
            "metadata": '{"type": "feature", "category": "wallboard", "product": "callswitch", "feature": "metrics"}'
        },
        {
            "content": "Wallboard Customization: Choose metrics to display, set thresholds for alerts, customize colors and layouts. Create multiple views for different teams.",
            "category": "phone",
            "metadata": '{"type": "feature", "category": "wallboard", "product": "callswitch", "feature": "customization"}'
        },

        # Adding Call Quality Monitoring
        {
            "content": "Quality Monitoring Overview: Track call quality metrics in real-time. Monitor jitter, packet loss, latency, and MOS scores. Identify network issues.",
            "category": "phone",
            "metadata": '{"type": "feature", "category": "quality", "product": "callswitch", "feature": "overview"}'
        },
        {
            "content": "Quality Metrics: MOS score (1-5 scale), jitter (<30ms ideal), packet loss (<1% target), latency (<150ms preferred). View in dashboard analytics.",
            "category": "phone",
            "metadata": '{"type": "feature", "category": "quality", "product": "callswitch", "feature": "metrics"}'
        },
        {
            "content": "Quality Alerts: Set thresholds for quality metrics. Receive notifications for poor quality calls. Generate reports for trend analysis.",
            "category": "phone",
            "metadata": '{"type": "feature", "category": "quality", "product": "callswitch", "feature": "alerts"}'
        },

        # Adding Supervisor Features
        {
            "content": "Supervisor Overview: Monitor agent activity, listen to calls, provide assistance. Access real-time metrics and historical reports.",
            "category": "phone",
            "metadata": '{"type": "feature", "category": "supervisor", "product": "callswitch", "feature": "overview"}'
        },
        {
            "content": "Call Monitoring: Listen to active calls silently. Whisper mode for agent coaching. Barge in for urgent situations. Record calls for training.",
            "category": "phone",
            "metadata": '{"type": "feature", "category": "supervisor", "product": "callswitch", "feature": "monitoring"}'
        },
        {
            "content": "Agent Management: View agent status and statistics. Adjust queue assignments. Monitor break times and schedule adherence.",
            "category": "phone",
            "metadata": '{"type": "feature", "category": "supervisor", "product": "callswitch", "feature": "management"}'
        },

        # Adding Call Center Reports
        {
            "content": "Report Types: Agent performance, queue statistics, call outcomes, quality metrics. Daily, weekly, monthly views available. Export to CSV/PDF.",
            "category": "phone",
            "metadata": '{"type": "feature", "category": "reports", "product": "callswitch", "feature": "types"}'
        },
        {
            "content": "Scheduled Reports: Set up automated report delivery. Choose recipients, frequency, and format. Store historical data for trend analysis.",
            "category": "phone",
            "metadata": '{"type": "feature", "category": "reports", "product": "callswitch", "feature": "scheduling"}'
        },
        {
            "content": "Custom Reports: Build custom reports with specific metrics. Filter by date, queue, agent, or outcome. Save templates for future use.",
            "category": "phone",
            "metadata": '{"type": "feature", "category": "reports", "product": "callswitch", "feature": "custom"}'
        },

        # Adding Calendar Integration Features
        {
            "content": "Calendar Overview: Integrate with Microsoft 365 or Google Calendar. Sync availability status, schedule calls and meetings. Automatic presence updates.",
            "category": "phone",
            "metadata": '{"type": "feature", "category": "calendar", "product": "callswitch", "feature": "overview"}'
        },
        {
            "content": "Calendar Setup: Connect account through OAuth. Grant calendar access permissions. Select sync frequency and event types to include.",
            "category": "phone",
            "metadata": '{"type": "feature", "category": "calendar", "product": "callswitch", "feature": "setup"}'
        },
        {
            "content": "Calendar Features: Schedule video meetings, set availability, block busy times. Click-to-join conference calls. Meeting reminders across devices.",
            "category": "phone",
            "metadata": '{"type": "feature", "category": "calendar", "product": "callswitch", "feature": "features"}'
        },

        # Adding Directory Integration
        {
            "content": "Directory Overview: Sync with Active Directory or LDAP. Automatic user provisioning and deprovisioning. Keep contact details updated.",
            "category": "phone",
            "metadata": '{"type": "feature", "category": "directory", "product": "callswitch", "feature": "overview"}'
        },
        {
            "content": "Directory Sync: Configure connection details and credentials. Select sync schedule and attributes. Handle conflicts and deletions.",
            "category": "phone",
            "metadata": '{"type": "feature", "category": "directory", "product": "callswitch", "feature": "sync"}'
        },
        {
            "content": "Directory Management: Map AD fields to user properties. Set up group-based permissions. Monitor sync status and errors.",
            "category": "phone",
            "metadata": '{"type": "feature", "category": "directory", "product": "callswitch", "feature": "management"}'
        },

        # Adding Single Sign-On (SSO)
        {
            "content": "SSO Overview: Support for SAML 2.0 and OAuth 2.0. Integrate with major identity providers. Simplify login across applications.",
            "category": "phone",
            "metadata": '{"type": "feature", "category": "sso", "product": "callswitch", "feature": "overview"}'
        },
        {
            "content": "SSO Configuration: Set up identity provider details. Configure assertion mapping. Test authentication flow. Enable MFA if required.",
            "category": "phone",
            "metadata": '{"type": "feature", "category": "sso", "product": "callswitch", "feature": "configuration"}'
        },
        {
            "content": "SSO Management: Monitor authentication attempts. Set password policies. Configure session timeouts. Handle failed login attempts.",
            "category": "phone",
            "metadata": '{"type": "feature", "category": "sso", "product": "callswitch", "feature": "management"}'
        },

        # Adding API Integration
        {
            "content": "API Overview: RESTful API for custom integrations. Manage calls, users, and settings programmatically. Webhook support for events.",
            "category": "phone",
            "metadata": '{"type": "feature", "category": "api", "product": "callswitch", "feature": "overview"}'
        },
        {
            "content": "API Authentication: Generate API keys in dashboard. Use Bearer token authentication. Rate limiting and usage monitoring.",
            "category": "phone",
            "metadata": '{"type": "feature", "category": "api", "product": "callswitch", "feature": "authentication"}'
        },
        {
            "content": "API Endpoints: Call control, user management, reporting, and configuration endpoints. Swagger documentation available. Example code provided.",
            "category": "phone",
            "metadata": '{"type": "feature", "category": "api", "product": "callswitch", "feature": "endpoints"}'
        },

        # Adding Compliance Features
        {
            "content": "Compliance Overview: Meet regulatory requirements for call recording, data protection, and security. Support for GDPR, HIPAA, and PCI compliance.",
            "category": "phone",
            "metadata": '{"type": "feature", "category": "compliance", "product": "callswitch", "feature": "overview"}'
        },
        {
            "content": "Data Protection: Encrypt sensitive data at rest and in transit. Set retention policies for recordings and logs. Regular security audits.",
            "category": "phone",
            "metadata": '{"type": "feature", "category": "compliance", "product": "callswitch", "feature": "data-protection"}'
        },
        {
            "content": "Audit Trails: Track all system changes and access attempts. Generate compliance reports. Monitor security events and policy violations.",
            "category": "phone",
            "metadata": '{"type": "feature", "category": "compliance", "product": "callswitch", "feature": "audit"}'
        },

        # Adding Disaster Recovery
        {
            "content": "Disaster Recovery Overview: Automatic failover between data centers. Regular backup of configuration and data. Business continuity planning.",
            "category": "phone",
            "metadata": '{"type": "feature", "category": "disaster-recovery", "product": "callswitch", "feature": "overview"}'
        },
        {
            "content": "Backup Procedures: Daily configuration backups. Call recording archives. Database replication across regions. Retention policy management.",
            "category": "phone",
            "metadata": '{"type": "feature", "category": "disaster-recovery", "product": "callswitch", "feature": "backup"}'
        },
        {
            "content": "Service Continuity: Alternative routing during outages. Mobile app fallback options. Emergency contact procedures and escalation paths.",
            "category": "phone",
            "metadata": '{"type": "feature", "category": "disaster-recovery", "product": "callswitch", "feature": "continuity"}'
        },

        # Adding Training Resources
        {
            "content": "User Training: Online tutorials and documentation. Live webinar sessions. Custom training programs for specific features. Self-paced learning modules.",
            "category": "phone",
            "metadata": '{"type": "feature", "category": "training", "product": "callswitch", "feature": "user"}'
        },
        {
            "content": "Admin Training: Advanced system configuration. User management best practices. Reporting and analytics workshops. Security training.",
            "category": "phone",
            "metadata": '{"type": "feature", "category": "training", "product": "callswitch", "feature": "admin"}'
        },
        {
            "content": "Training Materials: Video tutorials, user guides, quick reference cards. Regular updates for new features. Multi-language support.",
            "category": "phone",
            "metadata": '{"type": "feature", "category": "training", "product": "callswitch", "feature": "materials"}'
        },

        # Adding Support Services
        {
            "content": "Support Tiers: 24/7 emergency support. Standard business hours for general inquiries. Premium support options with dedicated account manager.",
            "category": "phone",
            "metadata": '{"type": "feature", "category": "support", "product": "callswitch", "feature": "tiers"}'
        },
        {
            "content": "Support Channels: Phone, email, chat, and ticket system. Remote assistance available. Knowledge base and community forums.",
            "category": "phone",
            "metadata": '{"type": "feature", "category": "support", "product": "callswitch", "feature": "channels"}'
        },
        {
            "content": "Issue Resolution: Defined SLAs for different priority levels. Escalation procedures for critical issues. Regular status updates.",
            "category": "phone",
            "metadata": '{"type": "feature", "category": "support", "product": "callswitch", "feature": "resolution"}'
        },

        # Adding Mobile Device Management
        {
            "content": "MDM Overview: Manage mobile app deployment and security. Configure device policies. Remote wipe capability for lost devices.",
            "category": "phone",
            "metadata": '{"type": "feature", "category": "mdm", "product": "callswitch", "feature": "overview"}'
        },
        {
            "content": "Device Enrollment: Self-service enrollment process. Bulk enrollment options. Automatic configuration push. Support for iOS and Android.",
            "category": "phone",
            "metadata": '{"type": "feature", "category": "mdm", "product": "callswitch", "feature": "enrollment"}'
        },
        {
            "content": "Security Policies: Enforce PIN codes, app restrictions, encryption. Control data sharing between apps. Monitor device compliance.",
            "category": "phone",
            "metadata": '{"type": "feature", "category": "mdm", "product": "callswitch", "feature": "security"}'
        },

        # Adding Analytics Features
        {
            "content": "Analytics Dashboard: Visual reports of call patterns, usage trends, and performance metrics. Customizable widgets and filters.",
            "category": "phone",
            "metadata": '{"type": "feature", "category": "analytics", "product": "callswitch", "feature": "dashboard"}'
        },
        {
            "content": "Usage Analytics: Track feature adoption, call volumes, peak times. Monitor user activity and system utilization. Capacity planning tools.",
            "category": "phone",
            "metadata": '{"type": "feature", "category": "analytics", "product": "callswitch", "feature": "usage"}'
        },
        {
            "content": "Performance Analytics: Monitor system health, network quality, user experience. Identify bottlenecks and optimization opportunities.",
            "category": "phone",
            "metadata": '{"type": "feature", "category": "analytics", "product": "callswitch", "feature": "performance"}'
        },

        # Adding Cost Management
        {
            "content": "Cost Overview: Track usage costs by department, user, or feature. Set budgets and alerts. Generate cost allocation reports.",
            "category": "phone",
            "metadata": '{"type": "feature", "category": "cost", "product": "callswitch", "feature": "overview"}'
        },
        {
            "content": "Billing Management: View detailed billing records. Export invoices and usage reports. Configure billing notifications and thresholds.",
            "category": "phone",
            "metadata": '{"type": "feature", "category": "cost", "product": "callswitch", "feature": "billing"}'
        },
        {
            "content": "Cost Optimization: Identify cost-saving opportunities. Analyze usage patterns. Recommend plan adjustments based on actual usage.",
            "category": "phone",
            "metadata": '{"type": "feature", "category": "cost", "product": "callswitch", "feature": "optimization"}'
        },

        # Adding System Updates
        {
            "content": "Update Process: Regular feature updates and security patches. Scheduled maintenance windows. Automatic updates for desktop and mobile apps.",
            "category": "phone",
            "metadata": '{"type": "feature", "category": "updates", "product": "callswitch", "feature": "process"}'
        },
        {
            "content": "Version Control: Track system versions across components. Rollback capability for critical issues. Beta testing program for new features.",
            "category": "phone",
            "metadata": '{"type": "feature", "category": "updates", "product": "callswitch", "feature": "versions"}'
        },
        {
            "content": "Release Notes: Detailed documentation of changes and improvements. Known issues and workarounds. Upgrade instructions when needed.",
            "category": "phone",
            "metadata": '{"type": "feature", "category": "updates", "product": "callswitch", "feature": "notes"}'
        },

        # Adding Fax Integration
        {
            "content": "Fax Overview: Send and receive faxes through email or web interface. Store faxes digitally. Automatic OCR for searchable content.",
            "category": "phone",
            "metadata": '{"type": "feature", "category": "fax", "product": "callswitch", "feature": "overview"}'
        },
        {
            "content": "Fax to Email: Receive faxes as PDF attachments. Configure multiple email recipients. Archive faxes automatically.",
            "category": "phone",
            "metadata": '{"type": "feature", "category": "fax", "product": "callswitch", "feature": "email"}'
        },
        {
            "content": "Fax Management: View fax history and status. Resend failed faxes. Set up cover page templates. Configure retention policies.",
            "category": "phone",
            "metadata": '{"type": "feature", "category": "fax", "product": "callswitch", "feature": "management"}'
        },

        # Adding Team Collaboration
        {
            "content": "Team Spaces: Create dedicated spaces for departments or projects. Share files and messages. Integrate with third-party tools.",
            "category": "phone",
            "metadata": '{"type": "feature", "category": "collaboration", "product": "callswitch", "feature": "spaces"}'
        },
        {
            "content": "File Sharing: Secure file transfer between team members. Version control for documents. Integration with cloud storage.",
            "category": "phone",
            "metadata": '{"type": "feature", "category": "collaboration", "product": "callswitch", "feature": "files"}'
        },
        {
            "content": "Team Chat: Group and direct messaging. Rich text formatting. Emoji and GIF support. Message threading and reactions.",
            "category": "phone",
            "metadata": '{"type": "feature", "category": "collaboration", "product": "callswitch", "feature": "chat"}'
        },

        # Adding Contact Center Features
        {
            "content": "Skills-based Routing: Route calls based on agent skills and proficiency. Define skill levels and priorities. Dynamic queue assignment.",
            "category": "phone",
            "metadata": '{"type": "feature", "category": "contact-center", "product": "callswitch", "feature": "skills"}'
        },
        {
            "content": "Queue Callback: Offer callback options during high volume. Maintain queue position. Schedule callbacks for specific times.",
            "category": "phone",
            "metadata": '{"type": "feature", "category": "contact-center", "product": "callswitch", "feature": "callback"}'
        },
        {
            "content": "Customer Surveys: Post-call satisfaction surveys. Custom survey questions. Automated survey delivery. Results analysis.",
            "category": "phone",
            "metadata": '{"type": "feature", "category": "contact-center", "product": "callswitch", "feature": "surveys"}'
        },

        # Adding Custom Integration
        {
            "content": "Webhook Integration: Configure webhooks for real-time events. Customize payload format. Monitor delivery status and retry failed webhooks.",
            "category": "phone",
            "metadata": '{"type": "feature", "category": "integration", "product": "callswitch", "feature": "webhooks"}'
        },
        {
            "content": "Custom Fields: Add custom fields to user profiles and calls. Map data from external systems. Use in reports and routing rules.",
            "category": "phone",
            "metadata": '{"type": "feature", "category": "integration", "product": "callswitch", "feature": "fields"}'
        },
        {
            "content": "Integration Builder: Visual tool for creating custom integrations. Pre-built templates for common systems. Test and debug tools.",
            "category": "phone",
            "metadata": '{"type": "feature", "category": "integration", "product": "callswitch", "feature": "builder"}'
        }
    ]

    processor = DocumentProcessor()
    processor.batch_process_documents(test_docs)

if __name__ == "__main__":
    setup_database()
    setup_test_docs() 