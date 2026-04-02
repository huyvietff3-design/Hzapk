import streamlit as st
import asyncio
import edge_tts
import os

# Cấu hình trang
st.set_page_config(page_title="AI Tiếng Việt - Text to Speech", page_icon="🎙️")

st.title("🎙️ AI Voice Generator (Vietnamese)")
st.markdown("Công cụ chuyển đổi văn bản thành giọng nói AI chất lượng cao để làm video.")

# Danh sách giọng đọc Việt Nam của Microsoft Edge
VOICES = {
    "Nữ - Hoài My (Tự nhiên)": "vi-VN-HoaiMyNeural",
    "Nam - Nam Minh (Mạnh mẽ)": "vi-VN-NamMinhNeural"
}

# Giao diện Sidebar & Main
with st.sidebar:
    st.header("Cài đặt giọng nói")
    selected_voice = st.selectbox("Chọn giọng đọc:", list(VOICES.keys()))
    rate = st.slider("Tốc độ đọc (%)", min_value=-50, max_value=50, value=0)
    pitch = st.slider("Tông giọng (Hz)", min_value=-20, max_value=20, value=0)

# Chỉnh định dạng rate và pitch cho đúng format của edge-tts
rate_str = f"{rate:+d}%"
pitch_str = f"{pitch:+d}Hz"

# Ô nhập văn bản
text_input = st.text_area("Nhập nội dung cần chuyển đổi:", height=250, 
                          placeholder="Ví dụ: Chào mừng bạn đến với kênh của mình. Chúc bạn một ngày tốt lành!")

# Hàm xử lý TTS
async def generate_voice(text, voice, rate, pitch):
    output_file = "output.mp3"
    communicate = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch)
    await communicate.save(output_file)
    return output_file

# Nút thực hiện
if st.button("Tạo giọng nói ngay"):
    if not text_input.strip():
        st.warning("Vui lòng nhập văn bản!")
    else:
        with st.spinner("Đang xử lý giọng nói AI..."):
            try:
                # Chạy async trong streamlit
                output_path = asyncio.run(generate_voice(
                    text_input, 
                    VOICES[selected_voice], 
                    rate_str, 
                    pitch_str
                ))
                
                # Hiển thị trình phát nhạc
                st.success("Tạo thành công!")
                audio_file = open(output_path, 'rb')
                audio_bytes = audio_file.read()
                st.audio(audio_bytes, format='audio/mp3')
                
                # Nút tải về
                st.download_button(
                    label="Tải file MP3 về máy",
                    data=audio_bytes,
                    file_name="ai_voice_vietnamese.mp3",
                    mime="audio/mp3"
                )
                
                audio_file.close()
                # Tùy chọn: Xóa file tạm sau khi dùng
                # os.remove(output_path)
                
            except Exception as e:
                st.error(f"Đã xảy ra lỗi: {e}")

st.divider()
st.caption("Gợi ý: Dùng giọng Hoài My cho các video review hoặc kể chuyện để có độ truyền cảm tốt nhất.")