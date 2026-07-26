"""
Centralized message content for the DYP Admissions WhatsApp Bot.

All text messages, list menus, button configurations, and media URLs
are defined here. flow_logic.py references these constants to send
the correct response for each user interaction.

MEDIA URLS: Replace the placeholder URLs below with your actual
publicly-hosted media URLs (e.g., Render static files, S3 bucket,
Google Drive direct links, etc.) before going live.
"""

# ─────────────────────────────────────────────────────────────────────
# WELCOME / GREETING
# ─────────────────────────────────────────────────────────────────────

WELCOME_TEXT = (
    "🙏 *Welcome to D.Y. Patil College of Engineering & Technology, Kolhapur!*\n\n"
    "🏛️ An Autonomous Institute | NAAC 'A' Grade | NBA Accredited\n"
    "🎓 42+ Years of Excellence in Technical Education\n\n"
    "We're glad you're interested in DYPCET! Explore everything about our "
    "college — academics, placements, facilities, fee structure, and "
    "admission process — right here on WhatsApp.\n\n"
    "👇 Tap the button below to explore our *Options Menu*."
)

# ─────────────────────────────────────────────────────────────────────
# ACKNOWLEDGMENT MESSAGES (post-broadcast button responses)
# ─────────────────────────────────────────────────────────────────────

ACK_FREEZE = (
    "✅ *Great choice!* We're glad you've decided to freeze your admission "
    "at DYPCET.\n\n"
    "📞 Our admission counsellors will reach out to you shortly.\n"
    "☎️ Helpline: *9158915999 / 9158615999*\n\n"
    "Meanwhile, explore more about your future campus 👇"
)

ACK_EXPLORE = (
    "👀 *No worries!* Take your time to explore all that DYPCET has to offer.\n\n"
    "Browse through our departments, placements, campus life, and more. "
    "We're confident you'll love what you see! 🎓\n\n"
    "Here's the full menu 👇"
)

# ─────────────────────────────────────────────────────────────────────
# MAIN OPTIONS MENU (Interactive List)
# ─────────────────────────────────────────────────────────────────────

MAIN_MENU_HEADER = "📋 DYPCET Info Menu"
MAIN_MENU_BODY = (
    "Select any option below to learn more about D.Y. Patil College of "
    "Engineering & Technology, Kolhapur."
)
MAIN_MENU_FOOTER = "DYPCET Admissions 2026-27"
MAIN_MENU_BUTTON = "🔽 View Options"
MAIN_MENU_SECTIONS = [
    {
        "title": "📚 Info & Admission",
        "rows": [
            {
                "id": "about",
                "title": "🏛️ About DYPCET",
                "description": "History, accreditations & rankings",
            },
            {
                "id": "fee",
                "title": "💰 Fee Structure",
                "description": "Category-wise fee details 2025-26",
            },
            {
                "id": "placements",
                "title": "📈 Placements",
                "description": "Placement stats & top recruiters",
            },
            {
                "id": "admission",
                "title": "📝 Admission Process",
                "description": "Documents, steps & helpline",
            },
        ],
    },
    {
        "title": "🏟️ Campus & Facilities",
        "rows": [
            {
                "id": "facilities",
                "title": "🏫 Facilities",
                "description": "Hostel, bus, canteen, sports & more",
            },
        ],
    },
]

# ─────────────────────────────────────────────────────────────────────
# FACILITIES SUB-MENU (Interactive List)
# ─────────────────────────────────────────────────────────────────────

FACILITIES_MENU_HEADER = "🏟️ Campus Facilities"
FACILITIES_MENU_BODY = "Explore DYPCET's world-class campus facilities:"
FACILITIES_MENU_FOOTER = "DYPCET Admissions 2026-27"
FACILITIES_MENU_BUTTON = "🔽 View Facilities"
FACILITIES_MENU_SECTIONS = [
    {
        "title": "Facilities",
        "rows": [
            {
                "id": "bus",
                "title": "🚌 Bus Transport",
                "description": "Routes, timings & fees",
            },
            {
                "id": "hostels",
                "title": "🏠 Hostels",
                "description": "Boys & girls hostel details",
            },
            {
                "id": "canteen",
                "title": "🍽️ Canteen",
                "description": "Mess & food facilities",
            },
            {
                "id": "ncc",
                "title": "🎖️ NCC",
                "description": "National Cadet Corps activities",
            },
            {
                "id": "nss",
                "title": "🤝 NSS",
                "description": "National Service Scheme & rural internship",
            },
        ],
    },
]

# ─────────────────────────────────────────────────────────────────────
# BROADCAST BUTTONS (sent after congrats template)
# ─────────────────────────────────────────────────────────────────────

BROADCAST_FOLLOWUP_TEXT = (
    "🎓 What would you like to do next?"
)

BROADCAST_BUTTONS = [
    {"id": "freeze_admission", "title": "✅ Freeze Admission"},
    {"id": "explore_options", "title": "👀 Explore Options"},
]

# ─────────────────────────────────────────────────────────────────────
# MEDIA ASSET URLS
# Replace these with your actual publicly-hosted URLs before deploying.
# ─────────────────────────────────────────────────────────────────────

MEDIA_URLS = {
    "fee_structure": "https://your-host.com/media/fee_structure_2025_26.jpg",
    "placement_brochure": "https://your-host.com/media/placement_brochure_2025.pdf",
    "sports_achievements": "https://your-host.com/media/sports_achievements.jpg",
    "nss_activities": "https://your-host.com/media/nss_rural_internship.jpg",
    "admission_documents": "https://your-host.com/media/admission_documents_2026_27.jpg",
    "contact_info": "https://your-host.com/media/contacts.jpg",
    "hostel_info": "https://your-host.com/media/hostel.jpg",
    "campus_tour": "https://your-host.com/media/campus_tour.mp4",
}

# ─────────────────────────────────────────────────────────────────────
# INDIVIDUAL RESPONSE CONTENT
# Each key maps to a handler ID from the list/button menus.
# ─────────────────────────────────────────────────────────────────────

ABOUT_TEXT = (
    "🏛️ *About D.Y. Patil College of Engineering & Technology*\n\n"
    "📍 Kasaba Bawada, Kolhapur, Maharashtra 416006\n\n"
    "• *Established:* 1984 (42+ Years of Excellence)\n"
    "• *Affiliation:* Shivaji University, Kolhapur\n"
    "• *Status:* Autonomous Institute\n"
    "• *NAAC:* 'A' Grade Accredited\n"
    "• *NBA:* Accredited Programs\n"
    "• *DTE Code:* EN 06250 (Engineering) | AR 06532 (Architecture)\n\n"
    "🎓 *Programs Offered:*\n"
    "B.E. — Computer, IT, AI&DS, Electronics & Telecomm, "
    "Mechanical, Civil, Electrical\n"
    "B.Arch — Architecture\n"
    "M.E. / M.Tech / MBA / MCA\n\n"
    "🌐 Website: www.coek.dypgroup.edu.in\n"
    "📞 Admissions: 9158915999 / 9158615999\n"
    "📧 info.dypcet@dypgroup.edu.in"
)

FEE_CAPTION = (
    "💰 *Fee Structure — First Year Engineering 2025-26*\n\n"
    "Category-wise tuition & development fees as per FRA norms.\n"
    "📞 For queries: 9158915999"
)

PLACEMENTS_TEXT = (
    "📈 *Placements at DYPCET*\n\n"
    "🏆 Top recruiters include TCS, Infosys, Wipro, Cognizant, "
    "Persistent Systems, L&T, and many more.\n\n"
    "💼 *Highest Package:* ₹44 LPA (2024-25)\n"
    "💼 *Average Package:* ₹4.5 LPA\n"
    "📊 *Placement Rate:* 85%+\n\n"
    "📄 Download our placement brochure for full details 👇"
)

ADMISSION_CAPTION = (
    "📝 *Admission Process 2026-27*\n\n"
    "📋 *Documents Required:*\n"
    "1. MHT-CET 2026 / JEE Main 2026 Score Card\n"
    "2. HSC (12th) Mark Sheet\n"
    "3. School Leaving / Transfer Certificate\n"
    "4. Nationality / Domicile / Birth Certificate\n"
    "5. Aadhaar Card\n"
    "6. Passport Size Photos & Scanned Signature\n\n"
    "📂 *Category-specific:* Caste Certificate, EWS, NCL, "
    "Caste Validity (as applicable)\n\n"
    "🏢 *Admission Guidance & Counselling Centre — Open Daily*\n"
    "📞 9158915999 / 9158615999"
)

BUS_TEXT = (
    "🚌 *Bus Transport Facility*\n\n"
    "DYPCET provides daily bus service covering major routes across "
    "Kolhapur city and nearby towns.\n\n"
    "🛣️ *Key Routes:* Kolhapur City, Ichalkaranji, Jaysingpur, "
    "Hatkanangale, Kagal, Gadhinglaj, and more\n\n"
    "💰 *Annual Bus Fee:* As per distance (₹8,000 – ₹20,000 approx.)\n"
    "⏰ *Timings:* Morning & Evening as per college schedule\n\n"
    "📞 Contact Transport Dept: 0231-2601431/33"
)

HOSTELS_TEXT = (
    "🏠 *Hostel Facility*\n\n"
    "Separate Boys' & Girls' hostels with 24/7 security:\n\n"
    "🛏️ *Rooms:* Double & Triple sharing available\n"
    "🍽️ *Mess:* Veg & Non-veg options\n"
    "📶 *Amenities:* Wi-Fi, hot water, laundry, recreation room, "
    "reading hall\n"
    "🔒 *Security:* CCTV, biometric entry, warden on campus\n\n"
    "💰 *Annual Fee:* ₹60,000 – ₹80,000 (approx.)\n"
    "📞 Contact: 0231-2601431/33"
)

CANTEEN_TEXT = (
    "🍽️ *Canteen & Mess Facility*\n\n"
    "DYPCET's campus canteen serves hygienic, affordable food:\n\n"
    "☕ *Breakfast, Lunch, Snacks & Dinner* available\n"
    "🥗 *Veg & Non-veg* options\n"
    "💰 *Budget-friendly* pricing for students\n"
    "⏰ *Timings:* 7:30 AM – 9:00 PM\n\n"
    "The central mess is available for hostel students with "
    "monthly plans."
)

NCC_TEXT = (
    "🎖️ *National Cadet Corps (NCC)*\n\n"
    "DYPCET has an active NCC unit that builds discipline, "
    "leadership, and patriotism:\n\n"
    "🎯 *Activities:* Camps, parades, adventure training, "
    "social service\n"
    "🏅 *Certificates:* 'B' & 'C' certificates available\n"
    "✨ *Benefits:* NCC 'C' certificate holders get preference in "
    "govt. jobs, defense services & higher education\n\n"
    "📞 Contact NCC Officer for enrollment details"
)

NSS_TEXT = (
    "🤝 *National Service Scheme (NSS)*\n\n"
    "DYPCET's NSS unit organizes impactful social initiatives:\n\n"
    "🏘️ *Rural & Social Internship* — Students live in villages "
    "and work on community development\n"
    "🩺 *Health Camps, Tree Plantation, Blood Donation Drives*\n"
    "📚 *Literacy Programs & Skill Development Workshops*\n"
    "🏛️ *Visits:* Gram Panchayats, health centres, dairy units, "
    "primary schools\n\n"
    "🎓 NSS develops leadership, social awareness, and earns "
    "activity points for your resume."
)

# ─────────────────────────────────────────────────────────────────────
# RETURN PROMPT (shown after every leaf response)
# ─────────────────────────────────────────────────────────────────────

RETURN_PROMPT = (
    "──────────────────\n"
    "💡 Type *menu* or send any message to go back to the main Options Menu."
)

# ─────────────────────────────────────────────────────────────────────
# BROADCAST TEMPLATE CONFIG
# ─────────────────────────────────────────────────────────────────────

BROADCAST_TEMPLATE_NAME = "admission_congrats"
BROADCAST_TEMPLATE_LANG = "en_US"
