#!/usr/bin/env python3
import argparse
import subprocess
import os
import re
import time
import logging
import sys

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

def download_video(youtube_url):
    """YouTube 동영상을 다운로드합니다."""
    logger.info(f"YouTube 동영상 다운로드 중: {youtube_url}")
    
    # yt-dlp 명령어 실행
    result = subprocess.run(
        ["yt-dlp", "-f", "bestvideo+bestaudio/best", youtube_url], 
        capture_output=True, 
        text=True
    )
    
    if result.returncode != 0:
        logger.error(f"다운로드 실패: {result.stderr}")
        return None
    
    # 출력에서 파일명 추출
    output_lines = result.stderr.split('\n') if result.stderr else result.stdout.split('\n')
    filename = None
    
    for line in output_lines:
        if "Merging formats into" in line:
            match = re.search(r'Merging formats into "(.*?)"', line)
            if match:
                filename = match.group(1)
                break
    
    if not filename:
        logger.error("다운로드된 파일명을 찾을 수 없습니다.")
        return None
    
    # [videoID] 부분 제거
    clean_filename = re.sub(r'\s*\[[a-zA-Z0-9_-]+\](\.[^.]+)$', r'\1', filename)
    
    # 파일 이름 변경
    if clean_filename != filename:
        try:
            os.rename(filename, clean_filename)
            logger.info(f"파일명 변경: {filename} -> {clean_filename}")
            filename = clean_filename
        except Exception as e:
            logger.error(f"파일명 변경 실패: {e}")
    
    return filename

def extract_subtitle(video_filename):
    """AssemblyAI를 사용하여 동영상에서 자막을 추출합니다."""
    if not video_filename or not os.path.exists(video_filename):
        logger.error(f"파일을 찾을 수 없습니다: {video_filename}")
        return None
    
    logger.info(f"자막 추출 중: {video_filename}")
    
    # AssemblyAI 명령어 실행
    result = subprocess.run(
        ["assemblyai", "transcribe", video_filename, "--srt"],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        logger.error(f"자막 추출 실패: {result.stderr}")
        return None
    
    # 출력에서 생성된 SRT 파일명 추출
    output = result.stdout
    match = re.search(r'Successfully created file ([a-zA-Z0-9-]+\.srt)', output)
    
    if not match:
        logger.error("생성된 SRT 파일명을 찾을 수 없습니다.")
        return None
    
    srt_filename = match.group(1)
    
    # 동영상 파일명과 동일하게 SRT 파일명 변경
    base_filename = os.path.splitext(video_filename)[0]
    new_srt_filename = f"{base_filename}.srt"
    
    try:
        os.rename(srt_filename, new_srt_filename)
        logger.info(f"SRT 파일명 변경: {srt_filename} -> {new_srt_filename}")
    except Exception as e:
        logger.error(f"SRT 파일명 변경 실패: {e}")
        return None
    
    return new_srt_filename

def translate_subtitle(srt_filename):
    """자막 파일을 한글로 번역합니다."""
    if not srt_filename or not os.path.exists(srt_filename):
        logger.error(f"자막 파일을 찾을 수 없습니다: {srt_filename}")
        return False
    
    logger.info(f"자막 번역 중: {srt_filename}")
    
    # subtitle.py 스크립트 실행
    result = subprocess.run(
        ["python", "subtitle.py", srt_filename],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        logger.error(f"자막 번역 실패: {result.stderr}")
        return False
    
    logger.info("자막 번역 완료")
    return True

def main():
    parser = argparse.ArgumentParser(description="YouTube 동영상 다운로드 및 한글 자막 추출")
    parser.add_argument("url", help="YouTube 동영상 URL")
    args = parser.parse_args()
    
    # 1단계: 동영상 다운로드
    video_filename = download_video(args.url)
    if not video_filename:
        logger.error("동영상 다운로드 실패, 프로세스 종료.")
        return
    
    # 2단계: 자막 추출
    srt_filename = extract_subtitle(video_filename)
    if not srt_filename:
        logger.error("자막 추출 실패, 프로세스 종료.")
        return
    
    # 3단계: 자막 번역
    if not translate_subtitle(srt_filename):
        logger.error("자막 번역 실패, 프로세스 종료.")
        return
    
    logger.info("모든 과정이 완료되었습니다!")
    logger.info(f"  - 동영상 파일: {video_filename}")
    logger.info(f"  - 원본 자막 파일: {srt_filename}")
    logger.info(f"  - 번역된 자막 파일: {os.path.splitext(srt_filename)[0]}_ko.srt")

if __name__ == "__main__":
    main()