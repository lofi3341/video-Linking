import streamlit as st
import os
import numpy as np
import zipfile
import ffmpeg

# ディレクトリの作成
if not os.path.exists('uploads'):
    os.makedirs('uploads')
if not os.path.exists('output'):
    os.makedirs('output')
if not os.path.exists('downloads'):
    os.makedirs('downloads')

st.write("Directories created")

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
        # ffmpegを使用して動画の処理を行う例
        (
            ffmpeg
            .input(video_path)
            .output(os.path.join('output', 'merged_' + os.path.basename(video_path)), filter_complex='[0:v]split=3[v1][v2][v3];[v1][v2][v3]hstack=3[v]')
            .run()
        )
        output_paths.append(os.path.join('output', 'merged_' + os.path.basename(video_path)))
    return output_paths

# 動画から音声を抽出する関数
def extract_audio(video_path):
    audio_path = os.path.join('output', 'audio_' + os.path.basename(video_path).replace('.mp4', '.wav'))
    (
        ffmpeg
        .input(video_path)
        .output(audio_path, codec='pcm_s16le')
        .run()
    )
    return audio_path

# 音声を挿入する関数
def insert_audio(video_path, audio_path):
    output_path = os.path.join('output', 'final_' + os.path.basename(video_path))
    (
        ffmpeg
        .input(video_path)
        .input(audio_path)
        .output(output_path, vcodec='copy', acodec='aac')
        .run()
    )
    return output_path

# 動画と音声を削除する関数
def delete_files():
    for file in os.listdir('uploads'):
        os.remove(os.path.join('uploads', file))
    for file in os.listdir('output'):
        os.remove(os.path.join('output', file))
    for file in os.listdir('downloads'):
        os.remove(os.path.join('downloads', file))

# 動画を指定したサイズに変換する関数
def resize_video(video_path, width, height):
    output_path = os.path.join('output', f'resized_{os.path.basename(video_path)}')
    (
        ffmpeg
        .input(video_path)
        .output(output_path, vf=f'scale={width}:{height}', vcodec='libx264', acodec='aac')
        .run()
    )
    return output_path

# 全ての出力動画をzipアーカイブにまとめる関数
def create_zip(video_paths, zip_name):
    zip_path = os.path.join('downloads', zip_name)
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for video_path in video_paths:
            zipf.write(video_path, os.path.basename(video_path))
    return zip_path

# Streamlitインターフェース
st.title("動画分割・結合・音声挿入アプリ")
st.write("App started successfully")

uploaded_files = st.file_uploader("動画ファイルをアップロード", type=["mp4", "mov", "avi"], accept_multiple_files=True)
if uploaded_files:
    st.session_state.uploaded_videos = upload_videos(uploaded_files)
    st.write("Videos uploaded successfully")

if st.button("変換"):
    st.write("Processing videos")
    if 'uploaded_videos' in st.session_state:
        output_paths = process_and_merge_videos(st.session_state.uploaded_videos)

        extracted_audio_paths = []
        for video_path in st.session_state.uploaded_videos:
            audio_path = extract_audio(video_path)
            extracted_audio_paths.append(audio_path)

        output_with_audio_paths = []
        for video_path, audio_path in zip(output_paths, extracted_audio_paths):
            output_path = insert_audio(video_path, audio_path)
            output_with_audio_paths.append(output_path)

        st.session_state.converted_videos = output_with_audio_paths
        st.write("Videos processed successfully")

if 'converted_videos' in st.session_state:
    st.subheader("変換された動画")
    for video in st.session_state.converted_videos:
        video_name = os.path.basename(video)
        with open(video, "rb") as file:
            st.download_button(label=f"{video_name}をダウンロード", data=file, file_name=video_name, mime="video/mp4")

    if st.button("動画を2880x540に変換しまとめてzipでダウンロード"):
        st.write("Resizing videos to 2880x540")
        resized_videos = []
        for video_path in st.session_state.converted_videos:
            resized_video_path = resize_video(video_path, 2880, 540)
            resized_videos.append(resized_video_path)
        zip_path = create_zip(resized_videos, "resized_videos_2880x540.zip")
        with open(zip_path, "rb") as file:
            st.download_button(label="全動画を2880x540に変換しzipでダウンロード", data=file, file_name="resized_videos_2880x540.zip", mime="application/zip")

    if st.button("動画を1920x360に変換しまとめてzipでダウンロード"):
        st.write("Resizing videos to 1920x360")
        resized_videos = []
        for video_path in st.session_state.converted_videos:
            resized_video_path = resize_video(video_path, 1920, 360)
            resized_videos.append(resized_video_path)
        zip_path = create_zip(resized_videos, "resized_videos_1920x360.zip")
        with open(zip_path, "rb") as file:
            st.download_button(label="全動画を1920x360に変換しzipでダウンロード", data=file, file_name="resized_videos_1920x360.zip", mime="application/zip")

if st.button("リセット"):
    delete_files()
    if 'uploaded_videos' in st.session_state:
        st.session_state.uploaded_videos = []