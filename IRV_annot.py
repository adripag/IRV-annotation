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
# Title
# --------------------------------------------------
st.title("IRV-specific Decision Tree")

st.write(
    "Use this interface to decide whether a reflexive-clitic verb "
    "should be annotated as IRV."
)


# --------------------------------------------------
# Student information
# --------------------------------------------------
st.subheader("Annotator information")

student_id = st.text_input("Student name or ID")


# --------------------------------------------------
# Sentence / construction
# --------------------------------------------------
st.subheader("Sentence / construction")

sentence = st.text_area("Sentence or example", height=100)
verb = st.text_input("Verb + RCLI construction")

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
    index=0
)

if irv1 == "Yes":
    decision = "Annotate as IRV"
    reason = "IRV.1 [INHERENT]: the verb only exists with the reflexive clitic."

elif irv1 == "No":

    # --------------------------------------------------
    # Test IRV.2
    # --------------------------------------------------
    irv2 = st.radio(
        "IRV.2 [DIFF-SENSE]: Does the verb without the RCLI have only clearly different meanings?",
        ["Select", "Yes", "No"],
        index=0
    )

    if irv2 == "Yes":
        decision = "Annotate as IRV"
        reason = "IRV.2 [DIFF-SENSE]: the non-reflexive verb has a clearly different meaning."

    elif irv2 == "No":

        # --------------------------------------------------
        # Test IRV.3
        # --------------------------------------------------
        irv3 = st.radio(
            "IRV.3 [DIFF-SUBCAT]: Does the simple verb have a different subcategorization frame?",
            ["Select", "Yes", "No"],
            index=0
        )

        if irv3 == "Yes":
            decision = "Annotate as IRV"
            reason = "IRV.3 [DIFF-SUBCAT]: the verb has a different subcategorization frame."

        elif irv3 == "No":

            subject_status = st.radio(
                "Does the verb have a subject?",
                ["Select", "No subject", "Has subject"],
                index=0
            )

            # --------------------------------------------------
            # Test IRV.4
            # --------------------------------------------------
            if subject_status == "No subject":

                irv4 = st.radio(
                    "IRV.4 [IMPERS]: Can the RCLI be replaced by an underspecified subject such as 'people', 'one', or 'as pessoas'?",
                    ["Select", "Yes", "No"],
                    index=0
                )

                if irv4 == "Yes":
                    decision = "Do NOT annotate as VMWE"
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
                    "IRV.5 [MIDDLE-INCHO]: Can a transitive version with a generic subject imply the reflexive version?",
                    ["Select", "Yes", "No"],
                    index=0
                )

                if irv5 == "Yes":
                    decision = "Do NOT annotate as VMWE"
                    reason = "IRV.5 [MIDDLE-INCHO]: the construction is middle or inchoative."

                elif irv5 == "No":

                    # --------------------------------------------------
                    # Test IRV.6
                    # --------------------------------------------------
                    irv6 = st.radio(
                        "IRV.6 [REFL]: Can the RCLI be replaced by 'oneself' or 'to oneself'?",
                        ["Select", "Yes", "No"],
                        index=0
                    )

                    if irv6 == "Yes":
                        decision = "Do NOT annotate as VMWE"
                        reason = "IRV.6 [REFL]: the construction is ordinary reflexive."

                    elif irv6 == "No":

                        subject_number = st.radio(
                            "What type of subject does the construction have?",
                            ["Select", "Singular subject", "Plural or coordinated subject"],
                            index=0
                        )

                        # --------------------------------------------------
                        # Test IRV.7
                        # --------------------------------------------------
                        if subject_number == "Singular subject":

                            irv7 = st.radio(
                                "IRV.7 [REFL-MUTUAL]: Is a reciprocal version possible with a plural subject without changing the meaning?",
                                ["Select", "Yes", "No"],
                                index=0
                            )

                            if irv7 == "Yes":
                                decision = "Do NOT annotate as VMWE"
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
                                index=0
                            )

                            if irv8 == "Yes":
                                decision = "Do NOT annotate as VMWE"
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
            st.error("Please enter your student name or ID before saving.")

        elif not sentence.strip() and not verb.strip():
            st.error("Please enter a sentence or a verb construction before saving.")

        else:
            row = {
                "student_id": student_id,
                "sentence": sentence,
                "verb_construction": verb,
                "final_decision": decision,
                "reason": reason,
            }

            st.session_state.annotations.append(row)

            st.success("Annotation saved for this session.")

else:
    st.info("Answer the questions above to obtain a decision.")


# --------------------------------------------------
# Show and download saved annotations
# --------------------------------------------------
st.divider()

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