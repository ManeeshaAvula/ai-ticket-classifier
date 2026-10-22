"""Generate the sample support-ticket dataset (data/tickets.csv).

The dataset is a curated sample written for this project. Tickets are
composed from the hand-written templates below, combined with slot values
(products, devices, amounts, ...) and varied openers/closers so the texts
read like real support messages instead of exact duplicates.

Usage:
    python scripts/generate_dataset.py

Output:
    data/tickets.csv with columns: text,label
"""

import csv
import itertools
import random
from pathlib import Path

RANDOM_SEED = 42
TARGET_PER_LABEL = 90

OPENERS = [
    "Hi,",
    "Hello,",
    "Hi there,",
    "Hello support team,",
    "Good morning,",
    "",
    "",
    "",
]

CLOSERS = [
    "Thanks in advance.",
    "Please help.",
    "Thank you!",
    "Any help would be appreciated.",
    "Please advise.",
    "Thanks.",
    "",
    "",
    "",
]

# ---------------------------------------------------------------------------
# billing
# ---------------------------------------------------------------------------

BILLING_TEMPLATES = [
    "I was charged {amount} twice for my {plan} subscription this month. Please refund the duplicate charge.",
    "My credit card shows a charge of {amount} from you, but I cancelled my subscription on {date}. Why was I still billed?",
    "I need a copy of my invoice for {month} for our accounting department. The billing portal only shows the current month.",
    "Your system charged my card {amount} even though my payment method was declined. Can you explain this charge?",
    "I signed up for the {plan} plan at {amount} per month, but I am being billed {amount2}. Please correct my billing.",
    "How do I get a refund for the annual plan? I bought it on {date} and have not used the service since.",
    "The promo code {code} did not apply at checkout and I was charged the full price of {amount}. Please adjust my invoice.",
    "My payment failed three times but my bank says the money was taken. I see a pending charge of {amount} on my statement.",
    "Why did my subscription price increase from {amount} to {amount2} without any notice? I never agreed to a price change.",
    "I was billed for an add-on I never purchased. There is a line item for {amount} labelled 'premium add-on' on my latest invoice.",
    "Please update the billing address on my account and reissue last month's invoice with the new details.",
    "I downgraded from {plan} to the free tier last week but was still charged {amount} today. Please refund this.",
    "Can I switch my billing from monthly to yearly? I want to know the exact total before you charge my card.",
    "There is an unknown charge of {amount} from your company on my corporate card. I need an itemised receipt to expense it.",
    "My invoice for {month} includes seats for two employees who left the company in {month2}. Please credit our account.",
    "I keep getting payment reminder emails saying my card was declined, but the charge of {amount} went through on {date}.",
    "Do you offer refunds if I cancel in the middle of a billing cycle? I was charged {amount} on {date} and want to cancel.",
    "The tax on my invoice looks wrong. I am based in {state} and the VAT rate applied does not match. Can billing review this?",
    "I paid {amount} by bank transfer on {date} but my account still shows an overdue balance. Please apply my payment.",
    "Please stop charging my old card ending in {card}. I updated my payment method but the old card was billed {amount}.",
]

BILLING_UNIQUE = [
    "I was double charged for the same subscription in March and April. Two charges of 49 dollars each month. This is unacceptable, please refund all duplicates immediately.",
    "Your invoice says I owe for 15 user seats but we only have 9 people on the team. The extra seats appeared after the last renewal.",
    "I need to dispute a charge. I never authorised the renewal of the annual plan and the 1,188 dollar charge has put my account over its limit.",
    "Can someone from billing call me? I have been going back and forth over email for two weeks about a refund of 230 dollars that never arrived.",
    "The discount from our nonprofit status was removed from this month's bill. We sent the updated certificate in January and it was confirmed.",
    "I bought a gift subscription for my colleague but the receipt has my personal card details and wrong amount. The charge should have been 99 dollars, not 149.",
    "My card was charged in USD but my plan is priced in EUR, and the conversion left me paying about 8 percent more than the listed price.",
    "We need invoices from the last 6 months resent to our new finance email. The previous bookkeeper left and we cannot access the billing portal history.",
    "I was promised a credit of 75 dollars by your support agent last month for the outage, but this month's invoice does not show any credit.",
    "Automatic renewal charged my card a day before the reminder email arrived. I would have cancelled if the reminder had come on time.",
]

# ---------------------------------------------------------------------------
# technical_support
# ---------------------------------------------------------------------------

TECH_TEMPLATES = [
    "The {app} app crashes every time I try to {action} on my {device}. It started after the update on {date}.",
    "I keep getting error code {error} when I try to {action}. I have already tried reinstalling the app twice.",
    "Your website is extremely slow today. Pages take over 30 seconds to load on {browser}, while other sites work fine.",
    "The {feature} feature stopped working after the latest update. Clicking the button does nothing at all.",
    "When I export my data to {format}, the file is empty even though the dashboard shows over 200 records.",
    "The integration with {integration} keeps disconnecting. I have to reauthorise it every morning.",
    "My files are not syncing between my laptop and my phone. The desktop app shows 'sync pending' for two days now.",
    "I see a blank white screen after logging in on {browser}. Clearing the cache did not fix it.",
    "The API returns a 500 error when I POST to the /reports endpoint with more than 50 items. Smaller requests work.",
    "Uploads fail at around 90 percent with the message 'network error', even on a wired connection. Files are about 40 MB.",
    "Notifications stopped arriving on my {device} yesterday. App permissions are all enabled and battery optimisation is off.",
    "The search function does not find documents I uploaded last week, even when I search for the exact file name.",
    "Video calls freeze after about ten minutes and then the whole browser tab becomes unresponsive on {browser}.",
    "Every time I save my report, the app logs me out and I lose my changes. This has happened four times today.",
    "The mobile app drains my battery in the background. It used 38 percent overnight on my {device} without being opened.",
    "Two-factor codes by SMS arrive 15 minutes late, by which time they have expired. The authenticator app works fine.",
    "The calendar integration duplicates every event three times in {integration}. Deleting the duplicates makes them reappear.",
    "Drag and drop stopped working in the board view. I can only move cards using the menu since the {date} update.",
    "I cannot attach files larger than 5 MB even though my plan says the limit is 100 MB. The error message is misleading.",
    "The dashboard widgets show 'no data' since this morning, but the underlying reports contain data when I open them directly.",
]

TECH_UNIQUE = [
    "Since yesterday's update the desktop app shows a spinning loader forever on the projects page. I am on macOS 14 and have reinstalled twice.",
    "Our whole team's shared workspace disappeared from the sidebar this morning. Individual accounts are fine. This is urgent, we cannot work.",
    "The webhook deliveries to our server stopped on Friday. Your status page says all systems operational but the delivery log shows timeouts.",
    "Printing invoices from the app produces garbled characters instead of our company logo and address. PDFs downloaded from the web version are fine.",
    "The app works in Chrome but in Firefox the login button does not respond at all. Several of our staff only use Firefox.",
    "Undo (Ctrl+Z) deletes the entire paragraph instead of the last action in the new editor. I lost a full page of notes this way.",
    "When two people edit the same document, one person's changes overwrite the other's instead of merging. We lost a whole section yesterday.",
    "Accessibility issue: the new colour scheme makes the text unreadable with a screen reader's high contrast mode enabled.",
    "The CSV import maps the date column wrong, importing 03/04/2026 as March 4 instead of April 3. Our locale is day-first.",
    "Push notifications arrive in batches of twenty at 3am instead of when events happen. This started after I updated to version 8.2.",
]

# ---------------------------------------------------------------------------
# account_access
# ---------------------------------------------------------------------------

ACCESS_TEMPLATES = [
    "I forgot my password and the reset email never arrives. I have checked my spam folder several times since {date}.",
    "My account has been locked after too many login attempts, but I only entered my password once. Please unlock it.",
    "I cannot log in since I got a new phone. The authenticator app was on my old device and I no longer have access to it.",
    "The two-factor authentication codes are not being accepted even though the time on my phone is correct.",
    "Someone changed the email address on my account without my permission. I cannot access my account at all now.",
    "I am trying to log in with {sso} single sign-on and it loops back to the login page every time.",
    "My login works on the website but the mobile app says my credentials are invalid. It is the same password.",
    "I need to change the email address associated with my account from my old work email to a new one before I lose access.",
    "My account was suspended for 'suspicious activity' but I have only ever logged in from my home in {state}.",
    "The password reset link says it has expired even though I clicked it within two minutes of receiving the email.",
    "I created an account years ago with my personal email and now cannot merge it with my company account. Both use my name.",
    "After entering my password the page just refreshes and asks for it again. This happens on {browser} and the app.",
    "I lost my recovery codes when my laptop was stolen. How can I regain access to my account securely?",
    "Our admin left the company and nobody else can access the admin console. We need to transfer account ownership.",
    "I keep getting logged out every few minutes, even mid-task. Other colleagues on the same network do not have this issue.",
    "The 'sign in with {sso}' button returns an error saying my organisation has not configured it, but our IT says it is set up.",
    "I verified my identity with my ID last week and my account is still restricted. When will full access be restored?",
    "I cannot remember which email I used to sign up. I have subscriptions receipts in two different inboxes.",
    "My account says my email is already in use when I try to register, but the login page says no account exists for it.",
    "I need to deactivate the account of an employee who left, but I do not have the option in the admin panel.",
]

ACCESS_UNIQUE = [
    "I have been locked out of my account for three days. Password reset emails arrive six hours late and the links are already expired. Please help urgently.",
    "A colleague shared their login with me while they were on leave and now both our accounts are flagged. I need mine restored, I did nothing wrong.",
    "I signed up with Apple ID using the hide-my-email feature and now I cannot change my password because I do not know the relay address.",
    "The verification SMS never reaches my number. Calls come through fine, and other services' texts arrive instantly.",
    "My session was hijacked — I see logins from another country in my security log and password changes I did not make. I changed the password but the other sessions remain active.",
    "We migrated to a new identity provider and half the team gets 'user not found' when signing in, even though their accounts exist.",
    "I am the account owner but the recovery flow sends the code to a phone number I changed two years ago. There is no alternative option offered.",
    "Every Monday morning I have to reset my password because the system says it expired, even though I changed it the Friday before.",
    "My account was created by my employer, they deactivated my email, and now I cannot access the personal data I stored in the account.",
    "The login page rejects my password even though my password manager fills the same one that works on my phone's app.",
]

# ---------------------------------------------------------------------------
# shipping
# ---------------------------------------------------------------------------

SHIPPING_TEMPLATES = [
    "My order {order} was supposed to arrive on {date} and the tracking has not updated in five days. Where is my package?",
    "The tracking page says my parcel was delivered yesterday, but nothing arrived and my neighbours do not have it either.",
    "I received the wrong item in order {order}. I ordered the {item} in {colour} but received a completely different product.",
    "My package arrived damaged. The box was crushed and the {item} inside is cracked. I need a replacement or a refund.",
    "Can I change the delivery address for order {order}? I moved house last week and it is still going to my old address.",
    "The courier attempted delivery while I was home all day. Now they want me to collect it from a depot 20 miles away.",
    "Part of my order is missing. The {item} arrived but the {item2} that was in the same order never showed up.",
    "My shipment has been stuck at the {city} distribution centre since {date} according to tracking. Is it lost?",
    "I paid extra for express delivery on order {order} and it arrived four days late. I would like the shipping fee refunded.",
    "The delivery driver left my package in the rain by the gate instead of under the porch. The contents are water damaged.",
    "I need to return the {item} from order {order} but the returns portal says my order number is not recognised.",
    "Tracking shows two separate packages for my order but I only received one. The second has no updates since it left your warehouse.",
    "My order {order} was marked as 'out for delivery' three days in a row and each evening it goes back to the depot.",
    "The estimated delivery date keeps moving. It was {date}, then {date2}, and now no date is shown at all.",
    "I ordered two of the {item} and only one was in the box, though the packing slip says two were shipped.",
    "Customs has held my international shipment for two weeks. Do I need to provide any documents to release it?",
    "The address on my shipping label is missing the apartment number, so the courier cannot complete the delivery.",
    "Can I schedule my delivery for a specific day? Order {order} keeps being attempted while I am at work.",
    "My return was received by your warehouse on {date} according to tracking, but I have heard nothing about my refund or exchange.",
    "The gift I ordered for a birthday on {date} still has not arrived, although I ordered it ten days ago with standard delivery.",
]

SHIPPING_UNIQUE = [
    "The courier delivered my parcel to the wrong street entirely — the photo proof of delivery shows a house I do not recognise. Order 88123.",
    "My package smells strongly of smoke and the outer box is scorched. I have not opened it. What should I do?",
    "I was charged for overnight shipping but the order did not even leave your facility for two days. The delay was on your side, not the courier's.",
    "Three delivery attempts were supposedly made, but my doorbell camera shows nobody came to the door at those times.",
    "The fragile item I ordered was shipped in a plain envelope with no padding and arrived shattered. Photos attached to my earlier email.",
    "My subscription box for this month never arrived, although the payment was taken and the order shows as fulfilled in my account.",
    "I need the delivery held at the depot instead because I will be travelling. The tracking link does not give me that option.",
    "The replacement you sent for my damaged item was delivered to my billing address instead of my shipping address and I cannot collect it.",
    "Tracking updated to 'delivered to front desk' but my building has no front desk. Nobody signed for it. This is the second lost parcel this year.",
    "My order was split into three shipments without telling me, and I am being charged three separate delivery fees.",
]

# ---------------------------------------------------------------------------
# general
# ---------------------------------------------------------------------------

GENERAL_TEMPLATES = [
    "Do you have a user guide or documentation for the {feature} feature? I want to learn how to use it properly.",
    "What are your customer support opening hours over the holiday period? I could not find them on your website.",
    "I just wanted to say your {feature} feature is excellent. It has saved our team hours every week. Keep it up!",
    "Can you tell me more about the differences between the {plan} and {plan2} plans? I am deciding which one fits our team.",
    "Is there a discount for students or educational institutions? I teach at a university and would like to use your tool in class.",
    "How do I export all of my data if I decide to leave the platform in the future? I like to know before committing.",
    "Do you offer onboarding or training sessions for new teams? We are rolling this out to about 30 people.",
    "I read about your company in an article and wanted to ask whether you have a partnership or reseller programme.",
    "Is your service available in {country}? Our team is distributed and I want to check before signing up.",
    "What new features are on your roadmap for this year? We are evaluating tools for a long-term commitment.",
    "Can I suggest a feature? It would be great if the {feature} could also handle recurring schedules.",
    "Do you have a community forum or user group where I can ask other users how they set up their workflows?",
    "I am writing a review of tools in your category for our company blog. Could you share your latest product information sheet?",
    "How large can my team be on the free plan before we need to upgrade? We are a small nonprofit with volunteers.",
    "Does your company attend or sponsor any industry conferences this year? I would like to meet the team in person.",
    "I am interested in a career at your company. Where can I find your current job openings and application process?",
    "Can you recommend which plan would suit a freelance designer working alone? I do not need team features.",
    "Is there a way to try the premium features before buying? A short trial would help me convince my manager.",
    "I would like to update the contact person for our account's correspondence. Nothing is wrong, we just reorganised.",
    "Your webinar last week on workflow automation was really useful. Will the recording be shared with attendees?",
]

GENERAL_UNIQUE = [
    "Just browsing at this stage — do you publish a comparison of your pricing tiers anywhere? The website only shows two of the three plans in the table.",
    "I am doing research for my thesis on SaaS onboarding and wondered if someone from your team would answer a few questions.",
    "Love the product. One small suggestion: a dark mode for the dashboard would make long sessions much easier on the eyes.",
    "My company is being acquired and our tooling will be reviewed. Can you send an overview document I can share with the new IT team?",
    "Do you provide a sandbox or demo environment for evaluation? Procurement requires us to test before any purchase discussion.",
    "I noticed your help centre articles are only in English. Are there plans to translate them into Spanish or German?",
    "We are a charity with limited budget. Do you have any case studies from similar organisations using your platform?",
    "Could you confirm whether your service is suitable for a single user? Most of your marketing seems aimed at large teams.",
    "I found your company through a podcast sponsorship. Is there an offer code for listeners, or a page describing the deal?",
    "Please send me your media kit and brand assets. I write for a small business magazine and we are featuring tools like yours.",
]

# ---------------------------------------------------------------------------
# Slot values
# ---------------------------------------------------------------------------

SLOTS = {
    "amount": ["$19", "$29.99", "$49", "$79", "$120", "$250", "€45", "£59"],
    "amount2": ["$39", "$59.99", "$89", "$149", "$300", "€65", "£79"],
    "plan": ["Basic", "Pro", "Team", "Business", "Starter", "Growth"],
    "plan2": ["Pro", "Team", "Business", "Enterprise", "Growth"],
    "date": [
        "March 3", "March 14", "April 2", "April 19", "May 6",
        "last Tuesday", "last Friday", "the 12th", "the 28th of last month",
    ],
    "date2": ["next Monday", "the 20th", "the following week", "two days later"],
    "month": ["January", "February", "March", "April", "May"],
    "month2": ["February", "March", "April"],
    "code": ["WELCOME10", "SPRING25", "LOYAL20", "NEWSLETTER15"],
    "state": ["Texas", "Ohio", "Colorado", "Oregon", "Florida"],
    "card": ["4421", "8709", "3356", "9012"],
    "app": ["desktop", "mobile", "web"],
    "action": [
        "open a project", "upload a file", "open the reports page",
        "start a video call", "edit my document", "load the dashboard",
    ],
    "device": ["Pixel 8", "iPhone 13", "iPhone 15", "Samsung Galaxy S23", "Windows laptop", "MacBook Air"],
    "error": ["ERR_1042", "0x8004", "E_CONN_RESET", "AUTH_207", "500 Internal", "SYNC_31"],
    "feature": [
        "reporting", "automation rules", "shared inbox", "template gallery",
        "time tracking", "approval workflow", "bulk edit", "custom fields",
    ],
    "format": ["CSV", "PDF", "Excel"],
    "integration": ["Slack", "Google Calendar", "Salesforce", "Zapier", "Outlook"],
    "browser": ["Chrome", "Firefox", "Safari", "Edge"],
    "sso": ["Google", "Microsoft", "Okta", "Apple"],
    "order": ["#10482", "#20917", "#33120", "#45771", "#58204", "#61039", "#77410", "#90255"],
    "item": ["wireless keyboard", "desk lamp", "office chair", "monitor stand", "notebook set", "phone case"],
    "item2": ["wireless mouse", "USB-C cable", "desk organiser", "mug", "screen protector"],
    "colour": ["black", "white", "navy blue", "grey", "red"],
    "city": ["Denver", "Memphis", "Chicago", "Phoenix", "Atlanta"],
    "country": ["Canada", "Germany", "Australia", "Brazil", "India"],
}

CATEGORIES = {
    "billing": (BILLING_TEMPLATES, BILLING_UNIQUE),
    "technical_support": (TECH_TEMPLATES, TECH_UNIQUE),
    "account_access": (ACCESS_TEMPLATES, ACCESS_UNIQUE),
    "shipping": (SHIPPING_TEMPLATES, SHIPPING_UNIQUE),
    "general": (GENERAL_TEMPLATES, GENERAL_UNIQUE),
}


def render(template: str, rng: random.Random) -> str:
    """Fill a template's {slots} with random values."""
    text = template
    for key, values in SLOTS.items():
        placeholder = "{" + key + "}"
        while placeholder in text:
            text = text.replace(placeholder, rng.choice(values), 1)
    opener = rng.choice(OPENERS)
    closer = rng.choice(CLOSERS)
    parts = [p for p in (opener, text, closer) if p]
    return " ".join(parts)


def build_rows() -> list[tuple[str, str]]:
    rng = random.Random(RANDOM_SEED)
    rows: set[tuple[str, str]] = set()

    for label, (templates, uniques) in CATEGORIES.items():
        for ticket in uniques:
            rows.add((ticket, label))
        combos = list(itertools.product(templates, OPENERS, CLOSERS))
        rng.shuffle(combos)
        per_label = sum(1 for _, lbl in rows if lbl == label)
        for template, _opener, _closer in combos:
            if per_label >= TARGET_PER_LABEL:
                break
            text = render(template, rng)
            if (text, label) not in rows:
                rows.add((text, label))
                per_label += 1

    result = list(rows)
    rng.shuffle(result)
    return result


def main() -> None:
    rows = build_rows()
    out_path = Path(__file__).resolve().parent.parent / "data" / "tickets.csv"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(["text", "label"])
        writer.writerows(rows)
    counts: dict[str, int] = {}
    for _, label in rows:
        counts[label] = counts.get(label, 0) + 1
    print(f"Wrote {len(rows)} tickets to {out_path}")
    for label in sorted(counts):
        print(f"  {label}: {counts[label]}")


if __name__ == "__main__":
    main()
