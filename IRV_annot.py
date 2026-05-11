import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
from zoneinfo import ZoneInfo
import streamlit as st
import pandas as pd
from io import StringIO


# --------------------------------------------------
# Page configuration
# --------------------------------------------------
st.set_page_config(
    page_title="IRV Decision Tree",
    page_icon="🌳",
    layout="centered"
)


# --------------------------------------------------
# Initialize session state
# --------------------------------------------------
if "annotations" not in st.session_state:
    st.session_state.annotations = []


def clear_form():
    """Clear the current annotation form, but keep the student name and saved rows."""
    fields_to_reset = {
        # Text fields
        "sentence_input": "",
        "verb_input": "",

        # Current workflow tests
        "refl_test": "Select",
        "reciprocal_test": "Select",
        "passive_test": "Select",
        "impersonal_test": "Select",
        "middle_test": "Select",
        "requires_se_test": "Select",
        "diff_sense_test": "Select",
        "special_pattern_test": "Select",

        # Older workflow keys, kept for safety if a browser session still has them
        "irv1": "Select",
        "irv2": "Select",
        "irv3": "Select",
        "subject_status": "Select",
        "irv4": "Select",
        "irv5": "Select",
        "irv6": "Select",
        "subject_number": "Select",
        "irv7": "Select",
        "irv8": "Select",
    }

    for key, value in fields_to_reset.items():
        st.session_state[key] = value



# --------------------------------------------------
# Google Sheets connection
# --------------------------------------------------
@st.cache_resource
def get_google_worksheet():
    """Connect to the Google Sheet defined in Streamlit Secrets."""
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
    ]

    credentials = Credentials.from_service_account_info(
        st.secrets["google_service_account"],
        scopes=scopes,
    )

    client = gspread.authorize(credentials)

    spreadsheet_id = st.secrets["sheets"]["spreadsheet_id"]
    worksheet_name = st.secrets["sheets"].get("worksheet_name", "Sheet1")

    spreadsheet = client.open_by_key(spreadsheet_id)
    worksheet = spreadsheet.worksheet(worksheet_name)

    return worksheet


# --------------------------------------------------
# Title
# --------------------------------------------------
st.title("IRV-specific Decision Tree")

st.write(
    "Use this interface to decide whether a reflexive-clitic verb "
    "should be annotated as IRV."
)

st.info(
    "Answer the tests in order. Once the app gives a final decision, stop.\n\n"
    "Legend: RCLI = reflexive clitic; IRV = inherently reflexive verb."
)


# --------------------------------------------------
# Student information
# --------------------------------------------------
st.subheader("Annotator information")

student_id = st.text_input("Student name")


# --------------------------------------------------
# Sentence / construction
# --------------------------------------------------
st.subheader("Sentence / construction")

sentence = st.text_area(
    "Write or paste your sentence",
    height=100,
    key="sentence_input"
)

verb = st.text_input(
    "Write the verb + RCLI construction (e.g., 'queixar-se')",
    key="verb_input"
)

st.divider()

st.subheader("Decision procedure")

st.markdown(
    """
    First exclude uses of **se** that do not qualify as **IRV**.  
    Only after that, test whether the construction should be annotated as **IRV**.
    """
)

decision = None
reason = None


# ==================================================
# EXCLUSION TESTS
# ==================================================
st.markdown("### A. Exclusion tests: cases that are NOT annotated as IRV")


# --------------------------------------------------
# Test 1: Ordinary reflexive
# --------------------------------------------------
refl_test = st.radio(
    "1. Ordinary reflexive: Can 'se' be replaced by 'a si mesmo/a si mesma/a si mesmos/a si mesmas'?",
    ["Select", "Yes", "No"],
    index=0,
    key="refl_test",
    help=(
        "Answer YES if 'se' means that the subject acts on itself/himself/herself. "
        "If YES, this is ordinary reflexive and should NOT be annotated as IRV."
    )
)

with st.expander("Examples for 1. Ordinary reflexive"):
    st.caption(
        "YES example: Ela se olhou no espelho ⇔ Ela olhou a si mesma no espelho. "
        "Decision: do NOT annotate as IRV."
    )
    st.caption(
        "YES example: Paulo se lavou ⇔ Paulo lavou a si mesmo. "
        "Decision: do NOT annotate as IRV."
    )
    st.caption(
        "NO example: Ela se queixou do atraso ⇏ Ela queixou a si mesma do atraso. "
        "Decision: continue to the next test."
    )

if refl_test == "Yes":
    decision = "Do NOT annotate as IRV"
    reason = "Test 1 [REFL]: 'se' is an ordinary reflexive object."

elif refl_test == "No":

    # --------------------------------------------------
    # Test 2: Reciprocal
    # --------------------------------------------------
    reciprocal_test = st.radio(
        "2. Reciprocal: Does 'se' mean 'um ao outro/uma à outra/uns aos outros'?",
        ["Select", "Yes", "No"],
        index=0,
        key="reciprocal_test",
        help=(
            "Answer YES if the subject is plural or coordinated and the participants act on each other. "
            "If YES, this is reciprocal and should NOT be annotated as IRV."
        )
    )

    with st.expander("Examples for 2. Reciprocal"):
        st.caption(
            "YES example: João e Ana se beijaram ⇔ João beijou Ana e Ana beijou João. "
            "Decision: do NOT annotate as IRV."
        )
        st.caption(
            "YES example: Eles se cumprimentaram ⇔ eles cumprimentaram uns aos outros. "
            "Decision: do NOT annotate as IRV."
        )
        st.caption(
            "NO example: Eles se queixaram do atraso. "
            "Here, 'se' does not mean 'um ao outro'. Decision: continue to the next test."
        )

    if reciprocal_test == "Yes":
        decision = "Do NOT annotate as IRV"
        reason = "Test 2 [RECIPROCAL]: 'se' marks a reciprocal relation."

    elif reciprocal_test == "No":

        # --------------------------------------------------
        # Test 3: Passive-like se
        # --------------------------------------------------
        passive_test = st.radio(
            "3. Passive-like se: Can the sentence be turned into a passive sentence? Can the noun after the verb become the subject of a passive sentence with 'ser + participle'",
            ["Select", "Yes", "No"],
            index=0,
            key="passive_test",
            help=(
                "Try a passive paraphrase with 'ser + participle', such as 'casas são vendidas'. "
                "If the paraphrase works, do NOT annotate as IRV."
            )
        )

        with st.expander("Examples for 3. Passive-like se"):
            st.caption(
                "YES example: Vendem-se casas ⇔ Casas são vendidas. "
                "Decision: do NOT annotate as IRV."
            )
            st.caption(
                "YES example: Alugam-se apartamentos ⇔ Apartamentos são alugados. "
                "Decision: do NOT annotate as IRV."
            )
            st.caption(
                "YES example: Destaca-se o momento ⇔ O momento é destacado. "
                "The noun 'o momento' becomes the subject of the passive sentence. "
                "Decision: do NOT annotate as IRV."
            )

            st.caption(
                "NO example: Ela se destacou na competição ⇏ *Ela foi destacada na competição. "
                "Here, 'destacar-se' means 'stand out', not 'be highlighted/selected'. "
                "Decision: continue to the next tests."
            )
            st.caption(
                 "YES example with encontrar-se: Encontra-se essa habilidade em animais com polegares opositores "
                 "⇔ Essa habilidade é encontrada em animais com polegares opositores. "
                 "The noun 'essa habilidade' becomes the subject of the passive sentence. "
                 "Decision: do NOT annotate as IRV."
            )

            st.caption(
                 "NO example with encontrar-se: O paciente encontra-se em observação "
                "⇏ *O paciente é encontrado em observação. "
                "Here, 'encontra-se' means 'is/remains/is located in a state or situation', not 'is found'. "
                "Decision: continue to the next tests."
            )
            st.caption(
                "NO example: Ela se queixou do atraso. "
                "This cannot be turned into a passive sentence with the same meaning. "
                "Decision: continue to the next test."
            )

        if passive_test == "Yes":
            decision = "Do NOT annotate as IRV"
            reason = "Test 3 [PASSIVE-LIKE]: the construction can be paraphrased as a passive sentence."

        elif passive_test == "No":

            # --------------------------------------------------
            # Test 4: Impersonal se
            # --------------------------------------------------
            impersonal_test = st.radio(
                "4. Impersonal se: Is there no specific subject, and can the meaning be paraphrased with 'as pessoas', 'alguém', or 'a gente'?",
                ["Select", "Yes", "No"],
                index=0,
                key="impersonal_test",
                help=(
                    "Answer YES if the sentence has a generic human interpretation, "
                    "without a specific subject."
                )
            )

            with st.expander("Examples for 4. Impersonal se"):
                st.caption(
                    "YES example: Vive-se bem aqui ⇔ As pessoas vivem bem aqui. "
                    "Decision: do NOT annotate as IRV."
                )
                st.caption(
                    "YES example: Dorme-se muito no inverno ⇔ As pessoas dormem muito no inverno. "
                    "Decision: do NOT annotate as IRV."
                )
                st.caption(
                    "YES example: Precisa-se de assistentes ⇔ Alguém precisa de assistentes. "
                    "Decision: do NOT annotate as IRV."
                )
                st.caption(
                    "NO example: Ela se olhou no espelho. "
                    "There is a specific subject: 'ela'. Decision: continue to the next test."
                )

            if impersonal_test == "Yes":
                decision = "Do NOT annotate as IRV"
                reason = "Test 4 [IMPERSONAL]: the construction has a generic/underspecified subject."

            elif impersonal_test == "No":

                # --------------------------------------------------
                # Test 5: Middle/inchoative
                # --------------------------------------------------
                middle_test = st.radio(
                    "5. Middle/inchoative: Does verb + se imply a change of state or condition and no explicit agent is mentioned?",
                    ["Select", "Yes", "No"],
                    index=0,
                    key="middle_test",
                    help=(
                        "Answer YES if the subject becomes calm/open/broken/scared/worse/etc., "
                        "often without an explicit agent. If YES, do NOT annotate as IRV."
                    )
                )

                with st.expander("Examples for 5. Middle/inchoative"):
                    st.caption(
                        "YES example: O menino se acalmou ⇔ O menino ficou calmo. "
                        "Decision: do NOT annotate as IRV."
                    )
                    st.caption(
                        "YES example: A porta se abriu ⇔ A porta ficou aberta. "
                        "Decision: do NOT annotate as IRV."
                    )
                    st.caption(
                        "YES example: A situação se agravou ⇔ A situação ficou mais grave. "
                        "Decision: do NOT annotate as IRV."
                    )
                    st.caption(
                        "NO example: Ela se referiu à diretora. "
                        "This is not a change-of-state use. Decision: continue to the IRV tests."
                    )

                if middle_test == "Yes":
                    decision = "Do NOT annotate as IRV"
                    reason = "Test 5 [MIDDLE/INCHOATIVE]: the subject changes or enters a state."

                elif middle_test == "No":

                    # ==================================================
                    # IRV-POSITIVE TESTS
                    # ==================================================
                    st.markdown("### B. IRV tests: cases that ARE annotated as IRV")

                    # --------------------------------------------------
                    # Test 6: Verb requires se
                    # --------------------------------------------------
                    requires_se_test = st.radio(
                        "6. Required se: Does this verb normally require 'se' for this meaning?",
                        ["Select", "Yes", "No"],
                        index=0,
                        key="requires_se_test",
                        help=(
                            "Answer YES if the verb is conventionally used with 'se' for this meaning, "
                            "for example 'queixar-se' or 'abster-se'."
                        )
                    )

                    with st.expander("Examples for 6. Required se"):
                        st.caption(
                            "YES example: queixar-se → *queixar. "
                            "The verb normally requires 'se' for this meaning. "
                            "Decision: annotate as IRV."
                        )
                        st.caption(
                            "YES example: abster-se → *abster. "
                            "Decision: annotate as IRV."
                        )
                        st.caption(
                            "YES example: vangloriar-se → *vangloriar. "
                            "Decision: annotate as IRV."
                        )
                        st.caption(
                            "Note for Brazilian Portuguese: some speakers may omit 'se' with certain verbs in informal usage. "
                            "For this task, follow the standard/reference pattern used in the guidelines."
                        )

                    if requires_se_test == "Yes":
                        decision = "Annotate as IRV"
                        reason = "Test 6 [REQUIRED SE]: the verb normally requires 'se' for this meaning."

                    elif requires_se_test == "No":

                        # --------------------------------------------------
                        # Test 7: Different meaning
                        # --------------------------------------------------
                        diff_sense_test = st.radio(
                            "7. Different meaning: Does the verb without 'se' exist, but mean something clearly different?",
                            ["Select", "Yes", "No"],
                            index=0,
                            key="diff_sense_test",
                            help=(
                                "Answer YES if the form without 'se' exists, but has a different meaning "
                                "from the form with 'se'."
                            )
                        )

                        with st.expander("Examples for 7. Different meaning"):
                            st.caption(
                                "YES example: encontrar-se ≠ encontrar. "
                                "'O paciente encontra-se em observação' does not mean the same as 'encontrar o paciente'. "
                                "Decision: annotate as IRV."
                            )
                            st.caption(
                                "YES example: referir-se ≠ referir. "
                                "The form with 'se' means 'refer to someone/something'. "
                                "Decision: annotate as IRV."
                            )
                            st.caption(
                                "YES example: comportar-se ≠ comportar. "
                                "'Ele se comportou bem' differs from 'comportar algo'. "
                                "Decision: annotate as IRV."
                            )

                        if diff_sense_test == "Yes":
                            decision = "Annotate as IRV"
                            reason = "Test 7 [DIFFERENT MEANING]: the form without 'se' has a clearly different meaning."

                        elif diff_sense_test == "No":

                            # --------------------------------------------------
                            # Test 8: Special se pattern
                            # --------------------------------------------------
                            special_pattern_test = st.radio(
                                "8. Special se-pattern: Is 'se' needed for this verb expression or pattern?",
                                ["Select", "Yes", "No"],
                                index=0,
                                key="special_pattern_test",
                                help=(
                                    "Answer YES if the verb follows a conventional pattern with 'se', "
                                    "such as 'dignar-se a fazer algo' or 'prontificar-se a fazer algo'."
                                )
                            )

                            with st.expander("Examples for 8. Special se-pattern"):
                                st.caption(
                                    "YES example: Ela se dignou a responder. "
                                    "Pattern: 'dignar-se a fazer algo'. "
                                    "Decision: annotate as IRV."
                                )
                                st.caption(
                                    "YES example: Ele se prontificou a ajudar. "
                                    "Pattern: 'prontificar-se a fazer algo'. "
                                    "Decision: annotate as IRV."
                                )
                                st.caption(
                                    "YES example: O detetive se deparou com um problema. "
                                    "Pattern: 'deparar-se com algo'. "
                                    "Decision: annotate as IRV."
                                )

                            if special_pattern_test == "Yes":
                                decision = "Annotate as IRV"
                                reason = "Test 8 [SPECIAL SE-PATTERN]: 'se' is part of a conventional verb pattern."

                            elif special_pattern_test == "No":
                                decision = "REVIEW"
                                reason = (
                                    "No exclusion test or IRV-positive test clearly applied. "
                                    "Mark this case for review."
                                )


# --------------------------------------------------
# Final decision
# --------------------------------------------------
st.divider()

st.subheader("Final decision")

if decision:
    if decision == "Annotate as IRV":
        st.success(decision)
    elif decision == "Do NOT annotate as IRV":
        st.warning(decision)
    else:
        st.info(decision)

    st.write("**Reason:**", reason)

    if sentence or verb:
        st.write("**Example:**")
        if sentence:
            st.write(sentence)
        if verb:
            st.write(f"Verb construction: `{verb}`")

    # --------------------------------------------------
    # Save annotation to current session
    # --------------------------------------------------
    st.divider()
    st.subheader("Save annotation")

    if st.button("Save this annotation"):

        if not student_id.strip():
            st.error("Please enter your student name before saving.")

        elif not sentence.strip() and not verb.strip():
            st.error("Please enter a sentence or a verb construction before saving.")

        else:
            row = {
                "timestamp": datetime.now(ZoneInfo("America/Sao_Paulo")).isoformat(timespec="seconds"),
                "student_id": student_id,
                "sentence": sentence,
                "verb_construction": verb,
                "final_decision": decision,
                "reason": reason,
            }

            # Keep a local copy during the current session, so the student can still see/download it.
            st.session_state.annotations.append(row)

            # Save permanently to Google Sheets.
            try:
                worksheet = get_google_worksheet()
                worksheet.append_row(
                    [
                        row["timestamp"],
                        row["student_id"],
                        row["sentence"],
                        row["verb_construction"],
                        row["final_decision"],
                        row["reason"],
                    ],
                    value_input_option="USER_ENTERED",
                )

                st.success("Annotation saved to Google Sheets.")

                if st.button("Start new annotation"):
                    clear_form()
                    st.rerun()

            except Exception as e:
                st.error(
                    "The annotation was saved only in this session, "
                    "but it was not saved to Google Sheets."
                )
                st.exception(e)

else:
    st.info("Answer the questions above to obtain a decision.")


# --------------------------------------------------
# Show and download saved annotations
# --------------------------------------------------
st.divider()

st.info(
    "When you click 'Save this annotation', your answer is automatically saved to the "
    "project Google Sheet. At the end of your work session, please also download your "
    "CSV file as a personal backup."
)

st.subheader("Saved annotations for this session")

if st.session_state.annotations:
    saved_data = pd.DataFrame(st.session_state.annotations)

    st.dataframe(saved_data)

    csv_buffer = StringIO()
    saved_data.to_csv(csv_buffer, index=False)
    csv_data = csv_buffer.getvalue()

    filename_student = student_id.strip().replace(" ", "_") if student_id.strip() else "student"

    st.download_button(
        label="Download my CSV",
        data=csv_data,
        file_name=f"irv_annotations_{filename_student}.csv",
        mime="text/csv"
    )

    if st.button("Clear saved annotations from this session"):
        st.session_state.annotations = []
        st.success("Session annotations cleared. Please refresh the page if the table still appears.")


else:
    st.write("No annotations saved yet in this session.")
