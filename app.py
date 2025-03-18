import asyncio

# Ensure a running event loop
try:
    asyncio.get_running_loop()
except RuntimeError:
    asyncio.set_event_loop(asyncio.new_event_loop())

import streamlit as st
import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
import os
import time
from datetime import datetime
from whisper_api import transcribe_audio
from firebase_utils import save_diary_entry, get_diary_entries

# Set page config
st.set_page_config(page_title="Diary App", page_icon="📝", layout="centered")

# --------------------------- AUDIO RECORDING ---------------------------
st.session_state.setdefault("recording", False)
st.session_state.setdefault("audio_data", None)
st.session_state.setdefault("entry_title", "")  # Store entry title before recording
st.session_state.setdefault("entries", None)  # Cache entries to improve UI speed

def start_recording(sample_rate=44100):
    """Start recording audio."""
    st.session_state.recording = True
    st.session_state.audio_data = sd.rec(int(60 * sample_rate), samplerate=sample_rate, channels=1, dtype='int16')
    st.success("🎙️ Recording started... Speak now!")

def stop_recording(sample_rate=44100):
    """Stop recording and save file."""
    if not st.session_state.recording:
        st.warning("⚠️ No recording in progress!")
        return None

    st.session_state.recording = False
    sd.stop()
    filename = f"recording_{int(time.time())}.wav"
    wav.write(filename, sample_rate, st.session_state.audio_data)
    st.session_state.audio_data = None  # Reset audio data
    return filename

# --------------------------- MAIN APP UI ---------------------------
st.markdown("<h1 style='text-align: center;'>📝 Voice-Powered Diary</h1>", unsafe_allow_html=True)

# Authentication Section
st.subheader("🔑 Authentication")
user_id = st.text_input("👤 Enter Your User ID:", "")

# Title Input Before Recording
st.subheader("📌 Entry Title")
entry_title = st.text_input("✍️ Enter Title for Your Entry:", key="entry_title")

# Recording Section
st.subheader("🎙️ Record Audio")

col1, col2 = st.columns(2)

with col1:
    if st.button("▶️ Start Recording", key="start"):
        if not user_id:
            st.error("⚠️ Please enter a valid User ID before recording.")
        elif not entry_title.strip():
            st.error("⚠️ Please enter a title before recording.")
        else:
            start_recording()

with col2:
    if st.button("⏹️ Stop Recording", key="stop"):
        filename = stop_recording()
        if filename:
            st.success(f"🎧 Recording saved temporarily as `{filename}`")

            # Transcription Process
            with st.spinner("📝 Transcribing..."):
                transcription = transcribe_audio(filename)
                if transcription:
                    st.text_area("🗒️ Transcribed Text:", transcription, height=150)

                    # Saving entry with spinner
                    with st.spinner("💾 Saving entry..."):
                        new_entry = save_diary_entry(user_id, transcription, entry_title)

                    # ✅ Update UI instantly
                    if "entries" not in st.session_state or st.session_state.entries is None:
                        st.session_state.entries = []
                    st.session_state.entries.insert(0, new_entry)  # Add latest entry at the top

                    st.success("✅ Entry saved successfully!")

                    # Delete the recorded file after transcription
                    os.remove(filename)
                else:
                    st.error("❌ Transcription failed. Please try again.")

# --------------------------- DISPLAY DIARY ENTRIES ---------------------------
st.subheader("📜 My Diary Entries")

if user_id:
    if st.session_state.entries is None:  # Load only once per session
        with st.spinner("📖 Loading your diary entries..."):
            st.session_state.entries = get_diary_entries(user_id)

    entries = st.session_state.entries  # Use cached entries

    if entries:
        st.write("🔍 **Search Your Diary Entries:**")
        search_query = st.text_input("🔎 Search by keyword:")

        filtered_entries = [
            entry for entry in entries
            if search_query.lower() in entry.get('text', '').lower()
            or search_query.lower() in entry.get('title', '').lower()
        ]

        for idx, entry in enumerate(filtered_entries):
            timestamp = entry.get('createdAt', 'No timestamp available')
            text = entry.get('text', 'No text available')
            title = entry.get('title', f"Entry {idx+1}")  # ✅ Display saved title

            # Show "Just Now" for newly added entries
            if timestamp == "Just Now":
                timestamp = "🕒 Just Now"
            elif isinstance(timestamp, datetime):
                timestamp = timestamp.strftime('%Y-%m-%d %H:%M')

            entry_name = f"{title} - {timestamp}"  # ✅ Show title instead of "Entry X"

            # ✅ Ensure text visibility inside expander
            with st.expander(entry_name):
                st.write(text)

    else:
        st.info("📭 No diary entries found. Start recording now!")
else:
    st.warning("⚠️ Enter a User ID to view diary entries.")
