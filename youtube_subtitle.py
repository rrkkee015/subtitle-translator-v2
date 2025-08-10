#!/usr/bin/env python3
import argparse
import subprocess
import os
import re
import time
import logging
import sys
from dotenv import load_dotenv

load_dotenv()

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
    """AssemblyAI Python API를 사용하여 동영상에서 자막을 추출합니다."""
    if not video_filename or not os.path.exists(video_filename):
        logger.error(f"파일을 찾을 수 없습니다: {video_filename}")
        return None
    
    logger.info(f"자막 추출 중: {video_filename}")
    
    try:
        import assemblyai as aai
        
        # API 키 확인 (환경변수에서)
        api_key = os.getenv('ASSEMBLYAI_API_KEY')
        if not api_key:
            logger.error("ASSEMBLYAI_API_KEY 환경변수가 설정되지 않았습니다.")
            return None
        
        aai.settings.api_key = api_key
        
        # 동영상 파일을 업로드하고 전사 요청
        logger.info("동영상 파일을 업로드하고 전사를 요청합니다...")
        transcriber = aai.Transcriber()
        transcript = transcriber.transcribe(video_filename)
        
        if transcript.status == aai.TranscriptStatus.error:
            logger.error(f"전사 실패: {transcript.error}")
            return None
        
        # SRT 형식으로 자막 생성
        base_filename = os.path.splitext(video_filename)[0]
        srt_filename = f"{base_filename}.srt"
        
        # SRT 형식으로 자막 저장
        srt_content = transcript.export_subtitles_srt()
        with open(srt_filename, 'w', encoding='utf-8') as f:
            f.write(srt_content)
        
        logger.info(f"자막 파일 생성 완료: {srt_filename}")
        return srt_filename
        
    except ImportError:
        logger.error("assemblyai 패키지가 설치되지 않았습니다.")
        return None
    except Exception as e:
        logger.error(f"자막 추출 중 오류 발생: {e}")
        return None

def translate_subtitle(srt_filename):
    """자막 파일을 한글로 번역합니다."""
    if not srt_filename or not os.path.exists(srt_filename):
        logger.error(f"자막 파일을 찾을 수 없습니다: {srt_filename}")
        return False
    
    logger.info(f"자막 번역 중: {srt_filename}")
    
    # subtitle.py 스크립트 실행 (stdout과 stderr를 파이프하지 않고 그대로 출력)
    result = subprocess.run(
        ["python", "subtitle.py", srt_filename],
        text=True
    )
    
    if result.returncode != 0:
        logger.error("자막 번역 실패")
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