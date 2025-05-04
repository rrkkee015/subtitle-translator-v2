#!/bin/bash

# macOS 자막 번역 도구 빌드 스크립트

# 필요한 패키지 설치
echo "필요한 패키지 설치 중..."
pip install PyQt6 anthropic tqdm yt-dlp
pip install --upgrade assemblyai
pip install py2app

# py2app 실행
echo "macOS 앱 빌드 중..."
python setup.py py2app

# 빌드 결과 확인
if [ -d "dist/SubtitleTranslator.app" ]; then
    echo "빌드 성공! 앱이 dist/SubtitleTranslator.app에 생성되었습니다."
    echo "실행하려면: open dist/SubtitleTranslator.app"

    # 앱 실행 권한 부여
    chmod +x "dist/SubtitleTranslator.app/Contents/MacOS/SubtitleTranslator"
    
    # 메타데이터 제거
    xattr -cr "dist/SubtitleTranslator.app"
    
    echo "앱을 실행하시겠습니까? (y/n)"
    read choice
    if [ "$choice" == "y" ] || [ "$choice" == "Y" ]; then
        open "dist/SubtitleTranslator.app"
    fi
else
    echo "빌드 실패! 오류를 확인하세요."
fi