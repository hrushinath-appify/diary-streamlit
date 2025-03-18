import firebase_admin
from firebase_admin import credentials, firestore

# Initialize Firebase if not already initialized
if not firebase_admin._apps:
    cred = credentials.Certificate("firebase_credentials.json")
    firebase_admin.initialize_app(cred)

# Get Firestore client
db = firestore.client()

def save_diary_entry(user_id, text, title="Untitled Entry"):
    """Save diary entry and return the saved data instantly."""
    diary_ref = db.collection("diary_entries").document(user_id).collection("entries").document()

    entry_data = {
        "title": title,
        "text": text,
        "createdAt": firestore.SERVER_TIMESTAMP  # Auto-generate timestamp
    }
    diary_ref.set(entry_data)

    # Return entry with a temporary timestamp (Firestore takes time to generate one)
    entry_data["createdAt"] = "Just Now"  # Temporary timestamp for instant UI update
    entry_data["id"] = diary_ref.id  # Store entry ID
    print("✅ Entry saved successfully!")  # 🔹 Debug print
    return entry_data  # ✅ Return saved entry for immediate UI update



def get_diary_entries(user_id):
    """Retrieve all diary entries for a user."""
    diary_ref = db.collection("diary_entries").document(user_id).collection("entries")
    docs = diary_ref.order_by("createdAt", direction=firestore.Query.DESCENDING).stream()

    entries = []
    for doc in docs:
        entry_data = doc.to_dict()
        entry_data["id"] = doc.id  # 🔹 Store entry ID if needed
        entries.append(entry_data)

    print(f"📖 Retrieved {len(entries)} entries")  # 🔹 Debug print
    return entries

