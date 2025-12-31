import streamlit as st
import google.generativeai as genai
from elevenlabs.client import ElevenLabs

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="My Content Factory", layout="wide")
st.title("🎬 AI Content Generator Dashboard")
st.markdown("Automasi Riset & Voice Over untuk YouTube/TikTok")

# --- KONEKSI KE API (Mengambil kunci dari Brankas Rahasia) ---
# Kita menggunakan st.secrets agar API Key aman dan tidak terekspos di kode
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    elevenlabs_client = ElevenLabs(api_key=st.secrets["ELEVENLABS_API_KEY"])
except Exception as e:
    st.error("API Key belum disetting! Lanjut ke langkah deploy untuk setting secrets.")

# --- SIDEBAR (INPUT) ---
with st.sidebar:
    st.header("1. Konsep Video")
    platform = st.selectbox("Platform", ["YouTube Shorts (9:16)", "YouTube Long (16:9)", "TikTok (9:16)", "IG Reels (9:16)"])
    niche = st.text_input("Niche / Target Audience", value="Dark Psychology")
    topic = st.text_input("Topik Spesifik", placeholder="Contoh: Tanda orang manipulatif")
    style = st.selectbox("Visual Style", ["Cinematic Dark", "Bright Minimalist", "Cyberpunk", "Vintage History"])
    
    st.header("2. ElevenLabs Settings")
    # Ambil list suara dari akun ElevenLabs Anda (jika API connect)
    try:
        voices = elevenlabs_client.voices.get_all()
        voice_options = {v.name: v.voice_id for v in voices.voices}
        selected_voice_name = st.selectbox("Pilih Suara", list(voice_options.keys()))
        selected_voice_id = voice_options[selected_voice_name]
    except:
        st.warning("Connect API ElevenLabs dulu untuk memuat list suara.")
        selected_voice_id = "default"

    st.markdown("---")
    btn_riset = st.button("🚀 MULAI RISET & DRAFTING")

# --- AREA UTAMA ---
col1, col2 = st.columns([1, 1])

# --- LOGIKA GEMINI (RISET) ---
if btn_riset and topic:
    with st.spinner('Gemini sedang melakukan deep research...'):
        model = genai.GenerativeModel('gemini-pro')
        
        prompt = f"""
        Bertindaklah sebagai Content Creator Expert. Saya ingin membuat konten untuk {platform}.
        Niche: {niche}. Topik: {topic}. Visual Style: {style}.
        
        Tugasmu adalah membuat output lengkap berikut:
        1. 3 Opsi Judul (Clickbait tapi relevan).
        2. Hashtag & Keyword SEO.
        3. Script Narasi Lengkap (Terbagi menjadi scene: Hook, Isi, CTA). Total durasi sekitar 45-60 detik.
        4. Image Prompt untuk setiap scene (Deskripsikan visual agar cocok untuk AI Image Generator).
        5. Rekomendasi Musik & Ambience (Mood, Instrumen).
        
        Format output jangan pakai markdown tabel, pakai list yang rapi agar mudah dicopy.
        """
        
        response = model.generate_content(prompt)
        st.session_state['hasil_riset'] = response.text
        st.success("Riset Selesai!")

# --- TAMPILAN HASIL ---
if 'hasil_riset' in st.session_state:
    with col1:
        st.subheader("📝 Hasil Riset & Script")
        st.markdown(st.session_state['hasil_riset'])
    
    with col2:
        st.subheader("🎙️ Voice Over Generator")
        st.info("Copy bagian 'Narasi' dari hasil riset di kiri, lalu paste di bawah ini untuk dijadikan suara.")
        
        text_to_speak = st.text_area("Teks Narasi Final", height=300, placeholder="Paste naskah di sini...")
        
        if st.button("🔊 Generate Audio (ElevenLabs)"):
            if not text_to_speak:
                st.warning("Isi teks dulu!")
            else:
                with st.spinner("Sedang memproses suara..."):
                    try:
                        # Generate Audio
                        audio_generator = elevenlabs_client.generate(
                            text=text_to_speak,
                            voice=selected_voice_id,
                            model="eleven_multilingual_v2"
                        )
                        
                        # Streamlit butuh format bytes untuk memutar audio
                        # Kita konversi generator menjadi bytes
                        audio_bytes = b""
                        for chunk in audio_generator:
                            audio_bytes += chunk
                            
                        st.audio(audio_bytes, format="audio/mp3")
                        st.success("Audio siap! Klik titik tiga di player untuk download.")
                    except Exception as e:
                        st.error(f"Gagal generate audio: {e}")