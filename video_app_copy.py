import streamlit as st
import cv2
import os
import numpy as np

# ディレクトリの作成
if not os.path.exists('uploads'):
    os.makedirs('uploads')
if not os.path.exists('output'):
    os.makedirs('output')

# 動画ファイルをアップロードする関数
def upload_videos(uploaded_files):
    saved_files = []
    for uploaded_file in uploaded_files:
        video_path = os.path.join('uploads', uploaded_file.name)
        with open(video_path, 'wb') as f:
            f.write(uploaded_file.getbuffer())
        saved_files.append(video_path)
    return saved_files

# 動画を分割し、結合する関数
def process_and_merge_videos(video_paths):
    output_paths = []
    for video_path in video_paths:
        cap = cv2.VideoCapture(video_path)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')

        output_path = os.path.join('output', 'merged_' + os.path.basename(video_path))
        out = cv2.VideoWriter(output_path, fourcc, fps, (5760, 1080))

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            left_top = frame[:height//2, :width//2]
            right_top = frame[:height//2, width//2:]
            left_bottom = frame[height//2:, :width//2]

            combined_frame = np.hstack((left_top, right_top, left_bottom))
            out.write(combined_frame)

        cap.release()
        out.release()
        output_paths.append(output_path)
    return output_paths

# Streamlitインターフェース
st.title("動画分割と結合アプリ")

uploaded_files = st.file_uploader("動画ファイルをアップロード", type=["mp4", "mov", "avi"], accept_multiple_files=True)
if uploaded_files:
    st.session_state.uploaded_videos = upload_videos(uploaded_files)

if 'uploaded_videos' in st.session_state:
    st.subheader("アップロードされた動画")
    for video in st.session_state.uploaded_videos:
        st.write(os.path.basename(video))
        if st.button(f"{os.path.basename(video)}を削除"):
            os.remove(video)
            st.session_state.uploaded_videos.remove(video)
            st.experimental_rerun()

if st.button("変換"):
    if 'uploaded_videos' in st.session_state:
        output_paths = process_and_merge_videos(st.session_state.uploaded_videos)
        st.session_state.converted_videos = output_paths

if 'converted_videos' in st.session_state:
    st.subheader("変換された動画")
    for video in st.session_state.converted_videos:
        video_name = os.path.basename(video)
        with open(video, "rb") as file:
            st.download_button(label=f"{video_name}をダウンロード", data=file, file_name=video_name, mime="video/mp4")