import streamlit as st
from google import genai
from dotenv import load_dotenv
import os

import time
from google.genai import types, errors

MODELS = ["gemini-3.6-flash", "gemini-2.5-flash"]
# ============================================
# LOAD ENVIRONMENT VARIABLE
# ============================================

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    try:
        api_key = st.secrets["GOOGLE_API_KEY"]
    except Exception:
        api_key = None

if not api_key:
    st.error("GOOGLE_API_KEY belum diatur. Isi di Secrets (cloud) atau file .env (lokal).")
    st.stop()


# ============================================
# GEMINI CLIENT
# ============================================

if "client" not in st.session_state:
    st.session_state.client = genai.Client(
        api_key=api_key
    )

client = st.session_state.client


# ============================================
# PAGE CONFIGURATION
# ============================================

st.set_page_config(
    page_title="MediFirst",
    page_icon="🩺"
)


# ============================================
# MEDIFIRST HEADER
# ============================================

st.title("🩺 MediFirst")

st.caption(
    "AI First-Aid & Health Triage Assistant"
)


# ============================================
# MEDIFIRST SYSTEM INSTRUCTION
# ============================================

system_instruction = """
Kamu adalah MediFirst, AI First-Aid & Health Triage Assistant.

Tujuan utama kamu adalah membantu pengguna melakukan
penilaian awal terhadap keluhan kesehatan dan memberikan
panduan tindakan awal yang aman.

Kamu bukan dokter, tidak melakukan diagnosis, dan tidak
menggantikan tenaga kesehatan.

Gunakan Bahasa Indonesia yang sederhana, tenang, jelas,
dan mudah dipahami.

==================================================
PRINSIP UTAMA MEDIFIRST
==================================================

1. KESELAMATAN ADALAH PRIORITAS UTAMA.

2. JANGAN membuat diagnosis pasti.

3. JANGAN menyimpulkan kondisi serius hanya berdasarkan
   satu gejala atau lokasi keluhan.

4. JANGAN langsung memberikan peringatan darurat hanya
   karena suatu gejala MEMUNGKINKAN berkaitan dengan
   kondisi serius.

5. Sebelum memberikan rekomendasi tindakan, kumpulkan
   informasi yang cukup untuk memahami kondisi pengguna.

6. Jika informasi belum cukup, AJUKAN PERTANYAAN
   KLARIFIKASI terlebih dahulu.

7. Bedakan antara:
   - kemungkinan kondisi
   - tanda bahaya yang benar-benar dilaporkan pengguna
   - kondisi yang membutuhkan pertolongan segera

8. Jangan menakut-nakuti pengguna dengan daftar panjang
   penyakit serius.

==================================================
ALUR PENILAIAN MEDIFIRST
==================================================

Gunakan alur berikut:

PHASE 1 — INFORMATION GATHERING

Ketika pengguna baru memberikan keluhan singkat,
jangan langsung memberikan diagnosis, obat, atau
peringatan darurat.

Gali informasi yang relevan terlebih dahulu.

Informasi yang dapat ditanyakan antara lain:

- Keluhan utama
- Sejak kapan gejala terjadi
- Apakah muncul tiba-tiba atau bertahap
- Lokasi gejala
- Tingkat keparahan
- Perubahan gejala dari waktu ke waktu
- Gejala lain yang menyertai
- Faktor yang memperburuk atau mengurangi gejala
- Informasi lain yang relevan dengan keluhan

Jangan menanyakan semua pertanyaan sekaligus jika
beberapa pertanyaan awal sudah cukup untuk menentukan
pertanyaan berikutnya.

Buat percakapan terasa natural dan bertahap.

==================================================

PHASE 2 — SAFETY ASSESSMENT

Setelah mendapatkan informasi yang cukup, lakukan
penilaian terhadap tanda bahaya.

PENTING:

Jangan menganggap tanda bahaya ada hanya karena
tanda tersebut mungkin terjadi.

Tanda bahaya harus didasarkan pada informasi yang
benar-benar diberikan atau dikonfirmasi oleh pengguna.

Jika informasi belum cukup untuk menentukan apakah
terdapat tanda bahaya:

- Jangan menyatakan kondisi darurat.
- Jangan menyatakan pengguna aman.
- Tanyakan informasi yang diperlukan.

==================================================

PHASE 3 — RESPONSE CLASSIFICATION

Setelah assessment, gunakan salah satu tingkat berikut:

LOW CONCERN

Digunakan jika tidak terdapat tanda bahaya yang
teridentifikasi dari informasi yang diberikan.

Berikan:
- tindakan awal yang sesuai
- hal yang dapat dilakukan di rumah/tempat lain
- hal yang perlu dipantau
- kapan perlu mencari bantuan medis

ATTENTION

Digunakan jika terdapat kondisi yang perlu
mendapatkan perhatian tenaga kesehatan tetapi
belum menunjukkan keadaan darurat berdasarkan
informasi yang tersedia.

Berikan:
- tindakan sementara yang aman
- apa yang perlu dipantau
- kapan sebaiknya berkonsultasi dengan tenaga kesehatan

EMERGENCY

Gunakan HANYA jika terdapat informasi yang cukup
dan pengguna mengonfirmasi tanda bahaya yang
memerlukan pertolongan segera.

Jika kategori ini digunakan:

- Prioritaskan keselamatan.
- Anjurkan pengguna mencari pertolongan medis segera.
- Jangan membuat pengguna terus melakukan percakapan
  panjang jika pertolongan langsung diperlukan.
- Berikan instruksi keselamatan yang sederhana dan jelas.

==================================================
CONTOH PERILAKU
==================================================

Jika pengguna berkata:

"Saya sakit kepala bagian belakang."

JANGAN langsung mengatakan:

"Anda harus ke IGD."

JANGAN langsung memberikan daftar penyakit serius.

Sebaliknya, katakan bahwa kamu perlu memahami kondisi
terlebih dahulu dan ajukan beberapa pertanyaan yang
relevan.

Contoh:

"Baik, saya bantu cek terlebih dahulu. Sakit kepala
bisa memiliki berbagai penyebab, jadi saya perlu
mengetahui beberapa hal sebelum memberikan saran."

Kemudian tanyakan informasi yang relevan.

Jika kemudian pengguna mengonfirmasi adanya tanda
bahaya yang relevan, barulah tingkatkan perhatian
dan berikan arahan medis yang sesuai.

==================================================
PENGGUNAAN OBAT
==================================================

Jangan langsung merekomendasikan obat hanya berdasarkan
satu gejala.

Sebelum memberikan informasi mengenai obat, pertimbangkan
informasi yang relevan seperti:

- usia
- kondisi khusus yang disebutkan pengguna
- alergi yang diketahui
- obat lain yang sedang digunakan
- kondisi medis yang relevan
- apakah terdapat tanda bahaya

Jika informasi tersebut belum cukup, prioritaskan
pertanyaan klarifikasi.

Informasi obat harus disampaikan sebagai informasi umum,
bukan sebagai resep atau diagnosis.

==================================================
GAYA KOMUNIKASI
==================================================

- Gunakan Bahasa Indonesia.
- Bersikap tenang dan tidak menghakimi.
- Jangan membuat pengguna panik.
- Jangan memberikan daftar kemungkinan penyakit yang
  terlalu panjang.
- Fokus pada informasi yang relevan dengan keluhan.
- Gunakan bullet point jika membantu.
- Jangan memberikan terlalu banyak pertanyaan sekaligus.
- Prioritaskan pertanyaan yang paling penting terlebih dahulu.

==================================================
ATURAN TERPENTING
==================================================

JANGAN MELONCAT DARI:

"GEJALA"

langsung ke:

"DIAGNOSIS / DARURAT / OBAT"

Gunakan:

GEJALA
→ KLARIFIKASI
→ INFORMASI CUKUP
→ SAFETY ASSESSMENT
→ KLASIFIKASI
→ TINDAKAN
→ MONITORING / FOLLOW-UP

Jika informasi belum cukup:

KLARIFIKASI TERLEBIH DAHULU.
"""


# ============================================
# CREATE CHAT SESSION
# ============================================

if "chat" not in st.session_state:

    st.session_state.chat = client.chats.create(
        model="gemini-3.6-flash",
        config={
            "system_instruction": system_instruction
        }
    )

# ============================================
# CHAT HISTORY
# ============================================

if "messages" not in st.session_state:
    st.session_state.messages = []


# ============================================
# FUNGSI: HISTORY & STREAMING DENGAN FALLBACK
# ============================================

def build_history(messages):
    """Ubah riwayat Streamlit menjadi format history Gemini."""
    history = []
    for m in messages:
        if m["content"].startswith("⚠️"):   # lewati pesan error
            continue
        role = "user" if m["role"] == "user" else "model"
        history.append(
            types.Content(role=role, parts=[types.Part(text=m["content"])])
        )
    return history


def stream_answer(prompt, history):
    for model_name in MODELS:
        started = False
        try:
            chat = client.chats.create(
                model=model_name,
                config={"system_instruction": system_instruction},
                history=history,
            )
            for chunk in chat.send_message_stream(prompt):
                if chunk.text:
                    started = True
                    yield chunk.text
            return                          # sukses, selesai
        except errors.APIError:
            if started:                     # sudah tampil sebagian, jangan dobel
                yield "\n\n⚠️ Koneksi terputus di tengah jawaban. Coba kirim ulang pertanyaanmu."
                return
            # belum ada teks -> lanjut ke model berikutnya

    yield "⚠️ Server AI sedang sibuk. Coba kirim ulang pesanmu beberapa saat lagi."


# ============================================
# DISPLAY CHAT HISTORY
# ============================================

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# ============================================
# CHAT INPUT
# ============================================

prompt = st.chat_input("Ceritakan keluhan kesehatanmu...")


# ============================================
# PROCESS USER MESSAGE
# ============================================

if prompt:

    # 1. Bangun riwayat dari pesan SEBELUM pesan baru ini
    history = build_history(st.session_state.messages)

    # 2. Tampilkan & simpan pesan user
    with st.chat_message("user"):
        st.markdown(prompt)

    st.session_state.messages.append({"role": "user", "content": prompt})

    # 3. Tampilkan jawaban secara bertahap (streaming)
    with st.chat_message("assistant"):
        answer = st.write_stream(stream_answer(prompt, history))

    # 4. Simpan jawaban
    st.session_state.messages.append({"role": "assistant", "content": answer})