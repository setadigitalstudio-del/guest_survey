import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime, timezone

st.set_page_config(page_title="Guest Preferences", page_icon="🏨", layout="centered")

# ---------------------------------------------------------------
# Questions: edit text/options here only. Key = column name in sheet.
# ---------------------------------------------------------------
QUESTIONS = [
    ("q1", "When choosing a hotel room, which feature is most important to you?", [
        "Quietness and tranquility", "Natural light and a view",
        "Easy access to hotel facilities", "Spaciousness and comfort",
        "Affordable price"]),
    ("q2", "When deciding to purchase additional hotel services, which factor influences your decision the most?", [
        "How well the services fit my travel plans",
        "The price and value of the services",
        "The explanations and recommendations provided by hotel staff",
        "The ability to make a decision and purchase the services on the spot"]),
    ("q3", "If you are dissatisfied with a hotel service, how would you prefer to express your concern?", [
        "Speak directly to the staff", "Send a private message to the hotel",
        "Fill out a digital feedback form", "Speak to the hotel manager"]),
    ("q4", "Which additional service could enhance your hotel experience?", [
        "Room upgrade", "Breakfast or restaurant services",
        "Spa and relaxation services", "Airport transfer", "None of the above"]),
    ("q5", "How certain are your current travel plans?", [
        "They are completely confirmed", "Minor changes may occur",
        "The travel dates may change", "They have not been decided yet"]),
    ("q6", "What would most encourage you to choose a hotel's special offer?", [
        "A lower price", "More services at the same price",
        "Flexibility in when the services can be used",
        "A unique and special experience"]),
    ("q7", "During holidays and leisure time, which activity do you prefer most?", [
        "Spending time alone and doing personal activities",
        "Spending time with friends or family",
        "Participating in group activities",
        "Trying new experiences and activities",
        "A combination of the above"]),
    ("q8", "When planning a trip, which of the following is most important to you?", [
        "Having a clear, pre-planned itinerary",
        "Flexibility and the ability to change plans",
        "Discovering new places and activities",
        "Relaxation and avoiding a busy schedule",
        "A combination of planning and flexibility"]),
    ("q9", "If things do not go as expected during your trip, what do you usually do?", [
        "I try to stick to my original plan", "I quickly choose an alternative plan",
        "I consult with my travel companions",
        "I adjust my plans according to the circumstances",
        "I prefer to ask hotel staff for guidance"]),
    ("q10", "When would you prefer to receive offers for additional hotel services?", [
        "A few days before arrival", "During hotel check-in",
        "During my stay, at a convenient time",
        "Only when I request them myself",
        "I prefer not to receive any offers"]),
]

LETTERS = "ABCDE"
COLUMNS = ["timestamp", "hotel", "guest_id"] + [q[0] for q in QUESTIONS]


def get_sheet():
    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=["https://www.googleapis.com/auth/spreadsheets"],
    )
    client = gspread.authorize(creds)
    return client.open_by_key(st.secrets["sheet_id"]).sheet1


# Hotel and guest come from the link: ?hotel=antalya&guest=123
params = st.query_params
hotel = params.get("hotel", "unknown")
guest_id = params.get("guest", "anonymous")

st.title("Hotel Guest Preferences Questionnaire")
st.caption("It takes about 2 minutes. Your answers help the hotel personalize your stay.")

if st.session_state.get("done"):
    st.success("Thank you! Your answers have been recorded.")
    st.stop()

with st.form("survey"):
    answers = {}
    for key, text, options in QUESTIONS:
        labels = [f"{LETTERS[i]}) {opt}" for i, opt in enumerate(options)]
        n = key[1:]
        choice = st.radio(f"{n}. {text}", labels, index=None, key=key)
        answers[key] = choice[0] if choice else None
        st.divider()

    consent = st.checkbox(
        "I agree that my answers may be stored and used by the hotel to improve my experience."
    )
    submitted = st.form_submit_button("Submit", type="primary")

if submitted:
    missing = [k for k, v in answers.items() if v is None]
    if missing:
        nums = ", ".join(k[1:] for k in missing)
        st.error(f"Please answer all questions. Missing: {nums}")
    elif not consent:
        st.error("Please accept the consent checkbox to submit.")
    else:
        row = [datetime.now(timezone.utc).isoformat(), hotel, guest_id] + [
            answers[q[0]] for q in QUESTIONS
        ]
        try:
            get_sheet().append_row(row, value_input_option="USER_ENTERED")
            st.session_state["done"] = True
            st.rerun()
        except Exception as e:
            st.error("Could not save your answers. Please try again.")
            st.caption(str(e))
