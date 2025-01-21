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

if __name__ == "__main__":
    setup_database() 