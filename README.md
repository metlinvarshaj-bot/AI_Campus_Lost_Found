# AI Campus Lost & Found

An AI-powered campus Lost & Found management system built using Python and Streamlit.

The application helps students report lost and found items, automatically identify possible matches using AI-based similarity techniques, verify ownership, and complete secure item handover using OTP and QR-based verification.

---

## Features

### Student Features

- Student registration and login
- Secure password hashing
- Report Lost Item
- Report Found Item
- Upload item images
- View submitted reports
- AI-powered Possible Matches
- View text, location, time, and image similarity scores
- Submit ownership verification details
- Secure handover using OTP and QR code
- Track returned items
- Reward points and reward history

### Admin Features

- Admin login
- Verification Review
- Approve or reject ownership verification
- Secure handover management
- Campus Lost & Found analytics
- View total lost and found items
- View AI matches
- View returned items
- View verification statistics
- View reward statistics

---

## AI Matching

The system combines multiple similarity signals to identify possible Lost and Found item matches.

### 1. Text Similarity

Sentence Transformers are used to compare item descriptions.

Model:

`all-MiniLM-L6-v2`

The descriptions are converted into embeddings and compared using cosine similarity.

### 2. Location Similarity

The reported lost and found locations are compared.

- Exact location: 100
- Shared location words: 70
- No meaningful match: 0

### 3. Time Similarity

Lost and found timestamps are compared.

- Within 30 minutes: 100
- Within 60 minutes: 80
- Within 3 hours: 50
- Within 6 hours: 25
- More than 6 hours: 0

### 4. Image Similarity

When both Lost and Found items have images, CLIP is used for image similarity.

Model:

`openai/clip-vit-base-patch32`

### Final Matching Score

When both images are available:

- Text: 50%
- Location: 20%
- Time: 15%
- Image: 15%

When images are unavailable:

- Text: 60%
- Location: 25%
- Time: 15%

Matches above the configured similarity threshold are displayed as possible matches.

---

## Secure Handover Workflow

The application follows this workflow:

1. Student reports a Lost item.
2. Another student reports a Found item.
3. AI automatically searches for possible matches.
4. Matching scores are displayed.
5. Student submits ownership verification details.
6. Admin reviews the verification request.
7. Admin approves or rejects the request.
8. For approved matches, a secure handover is created.
9. OTP and QR token are generated.
10. OTP is verified.
11. Match status changes to `RETURNED`.
12. Lost and Found item status is updated.
13. Reward points are recorded for the finder.

---

## Technology Stack

### Frontend

- Streamlit

### Backend

- Python
- SQLAlchemy
- SQLite

### AI / Machine Learning

- Sentence Transformers
- Transformers
- PyTorch
- TorchVision
- Scikit-learn
- CLIP

### Data and Visualization

- Pandas
- Plotly

### Security / Utilities

- SHA-256 password hashing
- Python Secrets
- QR Code generation

---

## Project Structure

```text
AI_Campus_Lost_Found/
│
├── ai/
│   ├── image_matcher.py
│   ├── match_engine.py
│   ├── smart_matcher.py
│   └── text_matcher.py
│
├── assets/
│
├── database/
│   ├── __init__.py
│   ├── db.py
│   └── schema.py
│
├── pages/
│   ├── admin_analytics.py
│   ├── admin_verification.py
│   ├── dashboard.py
│   ├── found_item.py
│   ├── handover.py
│   ├── login.py
│   ├── lost_item.py
│   ├── my_reports.py
│   ├── possible_matches.py
│   ├── rewards.py
│   └── verification.py
│
├── uploads/
│   ├── lost/
│   └── found/
│
├── utils/
│
├── app.py
├── init_db.py
├── seed_users.py
├── repair_match_status.py
├── requirements.txt
└── README.md