#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
자막 번역 도구 실행 스크립트
이 스크립트는 개발 모드에서 앱을 직접 실행합니다.
"""

import sys
import os
import subprocess

def check_requirements():
    """필요한 패키지가 설치되어 있는지 확인"""
    required_packages = ['PyQt6', 'anthropic', 'tqdm']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"다음 패키지가 설치되지 않았습니다: {', '.join(missing_packages)}")
        install = input("필요한 패키지를 설치하시겠습니까? (y/n): ")
        if install.lower() == 'y':
            subprocess.run([sys.executable, "-m", "pip", "install"] + missing_packages)
            return True
        else:
            return False
    
    return True

def check_external_tools():
    """외부 도구 설치 확인"""
    missing_tools = []
    
    # yt-dlp 확인
    try:
        subprocess.run(["yt-dlp", "--version"], capture_output=True, text=True)
    except FileNotFoundError:
        missing_tools.append("yt-dlp")
    
    # assemblyai 확인
    try:
        subprocess.run(["assemblyai", "--version"], capture_output=True, text=True)
    except FileNotFoundError:
        missing_tools.append("assemblyai")
    
    if missing_tools:
        print(f"다음 외부 도구가 설치되지 않았습니다: {', '.join(missing_tools)}")
        install = input("필요한 도구를 설치하시겠습니까? (y/n): ")
        if install.lower() == 'y':
            if 'yt-dlp' in missing_tools:
                subprocess.run([sys.executable, "-m", "pip", "install", "yt-dlp"])
            if 'assemblyai' in missing_tools:
                subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "assemblyai"])
            return True
        else:
            print("주의: 일부 기능이 제한될 수 있습니다.")
            return True
    
    return True

def check_api_keys():
    """API 키 환경 변수 확인"""
    missing_keys = []
    
    if not os.environ.get('ANTHROPIC_API_KEY'):
        missing_keys.append("ANTHROPIC_API_KEY")
    
    if not os.environ.get('ASSEMBLYAI_API_KEY'):
        missing_keys.append("ASSEMBLYAI_API_KEY")
    
    if missing_keys:
        print("정보: API 키는 앱 내의 '설정' 탭에서 구성할 수 있습니다.")
    
    return True

def main():
    if not check_requirements():
        print("필요한 패키지가 설치되지 않아 앱을 실행할 수 없습니다.")
        return
    
    check_external_tools()
    check_api_keys()
    
    print("자막 번역 도구를 시작합니다...")
    
    # 앱 실행 (현재 디렉토리에서 app.py 실행)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    app_path = os.path.join(script_dir, "app.py")
    
    try:
        subprocess.run([sys.executable, app_path])
    except Exception as e:
        print(f"앱 실행 중 오류가 발생했습니다: {e}")

if __name__ == "__main__":
    main()