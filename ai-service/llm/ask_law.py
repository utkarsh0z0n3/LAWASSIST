import ollama
from input_handler import create_user_data

# OPTIONAL (better language detection)
try:
    from langdetect import detect
except:
    detect = None


# -------------------------
# LANGUAGE DETECTION
# -------------------------

def detect_language(text):
    if detect:
        try:
            if detect(text) == "hi":
                return "hi"
        except:
            pass
    return "en"


# -------------------------
# CLEAN OUTPUT
# -------------------------

def clean_output(text):

    garbage_phrases = [
        "Here is the rewritten bail application:",
        "Here is the draft:",
        "Revised draft:",
        "Here is",
        "Here’s"
    ]

    for g in garbage_phrases:
        if text.startswith(g):
            text = text.replace(g, "").strip()

    return text.strip()


# -------------------------
# POST CLEAN (VERY IMPORTANT)
# -------------------------

def post_clean(text):

    # remove duplicate lines
    lines = text.split("\n")
    seen = set()
    cleaned = []

    for l in lines:
        l_clean = l.strip()

        if not l_clean:
            cleaned.append(l)
            continue

        if l_clean not in seen:
            cleaned.append(l)
            seen.add(l_clean)

    text = "\n".join(cleaned)

    # remove placeholders (anything inside brackets)
    import re
    text = re.sub(r"\(.*?\)", "", text)
    text = re.sub(r"\[.*?\]", "", text)

    # fix repeated phrases
    text = text.replace("अभियुक्त पर यह आरोप है कि अभियुक्त पर", "अभियुक्त पर यह आरोप है कि")

    # fix spacing
    text = re.sub(r"\n\s*\n", "\n\n", text)

    return text.strip()         
# -------------------------
# VALIDATION
# -------------------------

def validate_output(text, lang):

    issues = []

    # ❌ First person
    if any(x in text for x in ["मैं", "मेरे", "मेरा", "हम"]):
        issues.append("First person detected")

    # ❌ Confession (HARD FAIL)
    if any(x in text for x in ["स्वीकार", "गलती", "पश्चाताप"]):
        return ["Confession detected"]  # force reject

    # ❌ Meta text
    if "Here is" in text:
        issues.append("Meta text")

    # ❌ Repetition
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    if len(set(lines)) < len(lines) * 0.7:
        issues.append("Repetition")

    # ❌ Structure
    if lang == "hi" and not text.startswith("जमानत आवेदन पत्र"):
        issues.append("Wrong Hindi start")

    if lang == "en" and not text.startswith("BAIL APPLICATION"):
        issues.append("Wrong English start")

    # ❌ Missing custody
    if lang == "hi" and "न्यायिक हिरासत" not in text:
        issues.append("Missing custody detail")

    return issues


# -------------------------
# SCORING
# -------------------------

def evaluate_output(text, lang):

    issues = validate_output(text, lang)

    # HARD reject if confession
    if issues == ["Confession detected"]:
        return 0, issues

    score = 100
    score -= len(issues) * 15

    if len(text.split()) < 80:
        score -= 10
        issues.append("Too short")

    return score, issues


# -------------------------
# MODEL ROUTING
# -------------------------

def get_model(lang, attempt):

    if lang == "hi":
        primary = "aya"
        fallback = "mixtral"
    else:
        primary = "mixtral"
        fallback = "aya"

    return primary if attempt == 0 else fallback


# -------------------------
# PROMPTS
# -------------------------

def get_prompts(user_data, lang):

    if lang == "hi":

        system_prompt = f"""
आप एक वरिष्ठ भारतीय आपराधिक अधिवक्ता हैं।

यह ड्राफ्ट सीधे न्यायालय में प्रस्तुत किया जाएगा।

अनिवार्य नियम:

- "मैं", "हम", "मेरा", "मेरे" बिल्कुल न लिखें
- केवल तीसरे पुरुष (अभियुक्त) का प्रयोग करें
- "अभियुक्त ने अपराध किया", "स्वीकार किया", "गलती", "पश्चाताप" बिल्कुल न लिखें
- कोई अनुमान या अतिरिक्त तथ्य न जोड़ें
- कोई नोट या स्पष्टीकरण न लिखें
- कोई placeholder न लिखें
- केवल अंतिम ड्राफ्ट दें
- अधिकतम 5 आधार

केवल ये वैध आधार लिखें:

1. कोई पूर्व आपराधिक इतिहास नहीं
2. फरार होने की संभावना नहीं
3. साक्ष्य से छेड़छाड़ की संभावना नहीं
4. आगे की हिरासत आवश्यक नहीं
5. अपराध गंभीर प्रकृति का नहीं

प्रारूप:

जमानत आवेदन पत्र

माननीय न्यायिक मजिस्ट्रेट न्यायालय, {user_data['court']}

महोदय,

अभियुक्त {user_data['client_name']} के विरुद्ध आरोप है कि {user_data['facts']}। अभियुक्त को पुलिस द्वारा गिरफ्तार किया गया है तथा वह वर्तमान में न्यायिक हिरासत में है।

आधार:

1. ...
2. ...
3. ...
4. ...
5. ...

अतः प्रार्थना है कि माननीय न्यायालय अभियुक्त को जमानत प्रदान करने की कृपा करें।

दिनांक:
स्थान:

अधिवक्ता
"""

        user_prompt = "जमानत आवेदन पत्र तैयार करें।"

    else:

        system_prompt = f"""
You are a senior Indian criminal lawyer.

STRICT RULES:
- Output ONLY final draft
- No explanation
- No repetition
- Max 5 grounds
- No hallucination

STRUCTURE:

BAIL APPLICATION

IN THE COURT OF {user_data['court']}

MOST RESPECTFULLY SHOWETH:

The applicant {user_data['client_name']} is accused of {user_data['offence']}. {user_data['facts']}. The applicant is currently in judicial custody.

GROUNDS:

1. No prior criminal record.
2. Not likely to abscond.
3. Will not tamper with evidence.
4. Further custody not required.
5. Offence not of serious nature.

PRAYER:

It is therefore most respectfully prayed that this Hon’ble Court may be pleased to grant bail.

Date:
Place:

Counsel for the Applicant
"""

        user_prompt = "Generate the bail application."

    return system_prompt, user_prompt


# -------------------------
# GENERATION WITH RETRY
# -------------------------

def generate_with_retry(user_data, lang):

    best_answer = ""
    best_score = -1

    for attempt in range(3):

        model = get_model(lang, attempt)

        print(f"\nAttempt {attempt+1} using model: {model}")

        system_prompt, user_prompt = get_prompts(user_data, lang)

        response = ollama.chat(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            options={"temperature": 0.0}
        )

        answer = response["message"]["content"]
        answer = clean_output(answer)
        answer = post_clean(answer)

        score, issues = evaluate_output(answer, lang)

        print(f"Score: {score}")
        if issues:
            print("⚠️ Issues:", issues)

        if score > best_score:
            best_score = score
            best_answer = answer

        if score >= 85 and not issues:
            return answer

    return best_answer


# -------------------------
# MAIN
# -------------------------

def ask():

    user_data = create_user_data()

    combined = user_data["offence"] + " " + user_data["facts"]
    lang = detect_language(combined)

    print(f"\nDetected language: {lang.upper()}")
    print("\nGenerating draft...\n")

    final_answer = generate_with_retry(user_data, lang)

    print("\n======= FINAL DRAFT =======\n")
    print(final_answer)
    print("\n===========================\n")


# -------------------------
# CLI
# -------------------------

if __name__ == "__main__":
    print("\nIndian Law Assistant\n")
    ask()