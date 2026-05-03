import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
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
    "Legend: RCLI = reflexive clitic; REFLV = reflexive-clitic verb form."
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

sentence = st.text_area("Write or paste your sentence", height=100)
verb = st.text_input("Write the verb + RCLI construction (e.g., 'queixar-se')")

st.divider()

st.subheader("Decision procedure")

decision = None
reason = None


# --------------------------------------------------
# Test IRV.1
# --------------------------------------------------
irv1 = st.radio(
    "IRV.1 [INHERENT]: Does the verb only exist with the RCLI and never occur without it?",
    ["Select", "Yes", "No"],
    index=0,
    help=(
        "Answer YES if the verb normally requires the reflexive clitic. "
        "For example, in Portuguese, 'abster-se' does not normally occur as '*abster'."
    )
)

with st.expander("Examples for IRV.1 [INHERENT]"):
    st.caption(
        "YES for example: abster-se ⇒ abster. "
        "The verb normally requires the reflexive clitic. "
        "Decision: annotate as IRV."
    )
    st.caption(
        "NO for example: olhar-se ⇒ olhar. "
        "The verb 'olhar' exists without the clitic and keeps a related meaning. "
        "Decision: go to the next test."
    )

if irv1 == "Yes":
    decision = "Annotate as IRV"
    reason = "IRV.1 [INHERENT]: the verb only exists with the reflexive clitic."

elif irv1 == "No":

    # --------------------------------------------------
    # Test IRV.2
    # --------------------------------------------------
    irv2 = st.radio(
        "IRV.2 [DIFF-SENSE]: Given the same verb without the RCLI, are all of its meanings clearly different from the REFLV form?",
        ["Select", "Yes", "No"],
        index=0,
        help=(
            "Answer YES if the reflexive and non-reflexive forms have clearly different meanings, "
            "not just a reflexive object meaning."
        )
    )

    with st.expander("Examples for IRV.2 [DIFF-SENSE]"):
        st.caption(
            "YES example: referir-se ≠ referir. "
            "The reflexive and non-reflexive forms have clearly different meanings. "
            "Decision: annotate as IRV."
        )
        st.caption(
            "NO for example: lavar-se ≈ lavar a si mesmo/a si mesma. "
            "The non-reflexive form keeps a related meaning; the clitic marks the object as the same person. "
            "Decision: go to the next test."
        )

    if irv2 == "Yes":
        decision = "Annotate as IRV"
        reason = "IRV.2 [DIFF-SENSE]: the non-reflexive form of the verb has a clearly different meaning."

    elif irv2 == "No":

        # --------------------------------------------------
        # Test IRV.3
        # --------------------------------------------------
        irv3 = st.radio(
            "IRV.3 [DIFF-SUBCAT]: If you remove the reflexive clitic, does the verb require a different complement pattern, beyond simply replacing the clitic with 'si mesmo'?",
            ["Select", "Yes", "No"],
            index=0,
            help=(
                "Answer YES only if the reflexive and non-reflexive versions require different structures, "
                "for example a prepositional complement becomes a direct object: "
                "'X se esqueceu de Y' vs. 'X esqueceu Y'. "
                "Answer NO if the clitic can simply be replaced by 'a si mesmo/a si mesma', as in "
                "'A menina se olhou' vs. 'A menina olhou a si mesma'."
            )
        )

        with st.expander("Examples for IRV.3 [DIFF-SUBCAT]"):
            st.caption(
                "YES for example: X se esqueceu de Y ⇔ X esqueceu Y. "
                "The reflexive form uses 'de Y', while the non-reflexive form takes 'Y' directly. "
                "Decision: annotate as IRV."
            )
            st.caption(
                "NO example: A menina se olhou no espelho ⇔ A menina olhou a si mesma no espelho. "
                "Here, 'se' is just the reflexive object, so this is not a different complement pattern. "
                "Decision: go to the next test."
            )

        if irv3 == "Yes":
            decision = "Annotate as IRV"
            reason = (
                "IRV.3 [DIFF-SUBCAT]: removing the reflexive clitic changes "
                "the structure or complement required by the verb."
            )

        elif irv3 == "No":

            subject_status = st.radio(
                "Does the verb have a subject?",
                ["Select", "No subject", "Has subject"],
                index=0,
                help=(
                    "Choose 'No subject' for impersonal-like cases such as 'dorme-se muito'. "
                    "Choose 'Has subject' when there is an explicit subject, as in 'a menina se olhou'."
                )
            )

            with st.expander("Examples for subject status"):
                st.caption(
                    "NO SUBJECT for example: dorme-se muito no inverno. "
                    "There is no explicit participant before the verb."
                )
                st.caption(
                    "HAS SUBJECT example: a menina se olhou no espelho. "
                    "The subject is 'a menina'."
                )

            # --------------------------------------------------
            # Test IRV.4
            # --------------------------------------------------
            if subject_status == "No subject":
                irv4 = st.radio(
                    "IRV.4 [IMPERS]: Can the RCLI be replaced by an underspecified subject such as 'a gente', 'você', or 'as pessoas' without changing the basic meaning?",
                    ["Select", "Yes", "No"],
                    index=0,
                    help=(
                        "Try a paraphrase with a generic human subject. "
                        "If the meaning is preserved, the construction is impersonal."
                    )
                )

                with st.expander("Examples for IRV.4 [IMPERS]"):
                    st.caption(
                        "YES for example: dorme-se muito no inverno ⇔ as pessoas dormem muito no inverno. "
                        "The reflexive-clitic form has a generic human interpretation. "
                        "Decision: do NOT annotate as IRV."
                    )
                    st.caption(
                        "Important: apply this test only when there is no explicit subject. "
                        "If the sentence has a subject, such as 'a menina se olhou no espelho', "
                        "skip IRV.4 and continue with IRV.5 [MIDDLE-INCHO]."
                    )

                if irv4 == "Yes":
                    decision = "Do NOT annotate as IRV"
                    reason = "IRV.4 [IMPERS]: the construction is impersonal."

                elif irv4 == "No":
                    decision = "Annotate as IRV"
                    reason = "The construction has no subject and is not impersonal."

            # --------------------------------------------------
            # Tests for constructions with subject
            # --------------------------------------------------
            elif subject_status == "Has subject":

                # --------------------------------------------------
                # Test IRV.5
                # --------------------------------------------------
                irv5 = st.radio(
                    "IRV.5 [MIDDLE-INCHO]: Can the reflexive-clitic sentence be explained as the result of someone/something causing the event?",
                    ["Select", "Yes", "No"],
                    index=0,
                    help=(
                        "Try to build a non-reflexive version with 'alguém', 'as pessoas', "
                        "or 'algo' as the cause. If the non-reflexive version naturally implies "
                        "the reflexive-clitic version, answer YES."
                    )
                )

                with st.expander("Examples for IRV.5 [MIDDLE-INCHO]"):
                    st.caption(
                        "YES example: o menino se acalmou ⇐ alguém acalmou o menino. "
                        "The reflexive-clitic sentence 'o menino se acalmou' can be understood "
                        "as the result of an external cause: someone calmed the boy. "
                        "So this is a middle/inchoative alternation. "
                        "Decision: do NOT annotate as IRV."
                    )
                    st.caption(
                        "NO example: o menino se queixou ⇏ alguém queixou o menino. "
                        "The verb 'queixar-se' does not have a regular non-reflexive causal version "
                        "like 'queixar alguém'. So 'o menino se queixou' cannot be explained as "
                        "'someone caused the boy to complain' using the same verb. "
                        "Decision: go to the next test."
                    )

                if irv5 == "Yes":
                    decision = "Do NOT annotate as IRV"
                    reason = "IRV.5 [MIDDLE-INCHO]: the construction is middle or inchoative."

                elif irv5 == "No":
                    # --------------------------------------------------
                    # Test IRV.6
                    # --------------------------------------------------
                    irv6 = st.radio(
                        "IRV.6 [REFL]: Can the RCLI be replaced by 'si mesmo/si mesma' or 'a si mesmo/a si mesma'?",
                        ["Select", "Yes", "No"],
                        index=0,
                        help=(
                            "Answer YES if the clitic behaves like an ordinary reflexive object, "
                            "equivalent to 'himself', 'herself', or 'oneself'."
                        )
                    )

                    with st.expander("Examples for IRV.6 [REFL]"):
                        st.caption(
                            "YES example: Paulo se lava ⇔ Paulo lava a si mesmo. "
                            "The clitic can be replaced by 'a si mesmo'. "
                            "Decision: do NOT annotate as IRV."
                        )
                        st.caption(
                            "YES example: A menina se olhou no espelho ⇔ A menina olhou a si mesma no espelho. "
                            "The clitic functions as the object of 'olhar'. "
                            "Decision: do NOT annotate as IRV."
                        )
                        st.caption(
                            "NO example: Paulo se queixou ⇏ Paulo queixou a si mesmo. "
                            "The clitic cannot be replaced by 'a si mesmo'. "
                            "Decision: go to the next test."
                        )

                    if irv6 == "Yes":
                        decision = "Do NOT annotate as IRV"
                        reason = "IRV.6 [REFL]: the construction is ordinary reflexive."

                    elif irv6 == "No":

                        subject_number = st.radio(
                            "What type of subject does the construction have?",
                            ["Select", "Singular subject", "Plural or coordinated subject"],
                            index=0,
                            help=(
                                "Choose 'Singular subject' for examples like 'Pedro se ...'. "
                                "Choose 'Plural or coordinated subject' for examples like 'Pedro e Clara se ...' or 'eles se ...'."
                            )
                        )

                        with st.expander("Examples for subject number"):
                            st.caption("Singular subject example: Pedro se olhou no espelho.")
                            st.caption("Plural/coordinated subject example: Pedro e Clara se abraçaram.")

                        # --------------------------------------------------
                        # Test IRV.7
                        # --------------------------------------------------
                        if subject_number == "Singular subject":

                            irv7 = st.radio(
                                "IRV.7 [REFL-MUTUAL]: Is a reciprocal version possible with a plural subject without changing the meaning?",
                                ["Select", "Yes", "No"],
                                index=0,
                                help=(
                                    "Try changing the singular subject to a plural subject and adding "
                                    "'um ao outro', 'uma à outra', 'uns aos outros', or 'umas às outras'. "
                                    "If the meaning remains compatible, answer YES."
                                )
                            )

                            with st.expander("Examples for IRV.7 [REFL-MUTUAL]"):
                                st.caption(
                                    "YES example: Pedro se lavou ⇔ Pedro e Ana se lavaram um ao outro. "
                                    "A reciprocal version is possible. "
                                    "Decision: do NOT annotate as IRV."
                                )
                                st.caption(
                                    "NO example: Pedro se queixou ⇏ Pedro e Ana se queixaram um ao outro. "
                                    "The reciprocal version does not preserve the relevant meaning. "
                                    "Decision: annotate as IRV."
                                )

                            if irv7 == "Yes":
                                decision = "Do NOT annotate as IRV"
                                reason = "IRV.7 [REFL-MUTUAL]: the construction allows a reflexive-mutual reading."

                            elif irv7 == "No":
                                decision = "Annotate as IRV"
                                reason = (
                                    "The construction is not inherent, different-sense, "
                                    "different-subcat, impersonal, middle/inchoative, "
                                    "reflexive, or reflexive-mutual."
                                )

                        # --------------------------------------------------
                        # Test IRV.8
                        # --------------------------------------------------
                        elif subject_number == "Plural or coordinated subject":

                            irv8 = st.radio(
                                "IRV.8 [RECIPRO]: Can the construction be paraphrased as A acts on B and B acts on A?",
                                ["Select", "Yes", "No"],
                                index=0,
                                help=(
                                    "For a coordinated subject, try: A and B PronV ⇔ A V B and B V A. "
                                    "For a plural subject, try: A.PL PronV ⇔ A.PL V A.PL."
                                )
                            )

                            with st.expander("Examples for IRV.8 [RECIPRO]"):
                                st.caption(
                                    "YES example: João e Ana se beijam ⇔ João beija Ana e Ana beija João. "
                                    "The clitic marks a reciprocal relation. "
                                    "Decision: do NOT annotate as IRV."
                                )
                                st.caption(
                                    "YES example: os presos se agridem ⇔ os presos agridem os presos. "
                                    "The event is interpreted reciprocally among members of the group. "
                                    "Decision: do NOT annotate as IRV."
                                )
                                st.caption(
                                    "NO example: João e Ana se queixaram ⇏ João queixou Ana e Ana queixou João. "
                                    "The reciprocal paraphrase does not work with the same verb meaning. "
                                    "Decision: annotate as IRV."
                                )

                            if irv8 == "Yes":
                                decision = "Do NOT annotate as IRV"
                                reason = "IRV.8 [RECIPRO]: the construction is reciprocal."

                            elif irv8 == "No":
                                decision = "Annotate as IRV"
                                reason = (
                                    "The construction is not reciprocal and no previous "
                                    "exclusion test applied."
                                )


# --------------------------------------------------
# Final decision
# --------------------------------------------------
st.divider()

st.subheader("Final decision")

if decision:
    if decision == "Annotate as IRV":
        st.success(decision)
    else:
        st.warning(decision)

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
                "timestamp": datetime.now().isoformat(timespec="seconds"),
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
