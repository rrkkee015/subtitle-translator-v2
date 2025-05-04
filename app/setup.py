#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
macOS 앱으로 패키징하기 위한 스크립트
py2app을 사용하여 GUI 애플리케이션을 Mac 애플리케이션으로 변환합니다.

사용법:
    1. 터미널에서 다음 명령 실행:
       python setup.py py2app
    2. dist 폴더에 생성된 .app 패키지 확인
"""

from setuptools import setup
import os
import sys

# 상위 디렉토리 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 앱 이름 및 버전
APP_NAME = "SubtitleTranslator"
VERSION = "1.0.0"
COPYRIGHT = "Copyright © 2024"

# 데이터 파일 경로 (아이콘, 설정 파일 등)
DATA_FILES = [
    # ('', ['icon.icns']),  # 아이콘 파일 (필요시 주석 해제)
    # 프로젝트 파일 패키징
    ('', ['../subtitle.py', '../youtube_subtitle.py', '../config.json']),
]

# py2app 옵션
PY2APP_OPTIONS = {
    'argv_emulation': True,
    'packages': ['PyQt6', 'anthropic', 'tqdm'],
    'includes': ['subprocess', 'threading', 're', 'sys', 'os', 'json', 'time', 'logging'],
    'iconfile': 'icon.icns',  # 아이콘 파일 (생성 후 주석 해제)
    'plist': {
        'CFBundleName': APP_NAME,
        'CFBundleDisplayName': APP_NAME,
        'CFBundleGetInfoString': f"{APP_NAME} {VERSION}",
        'CFBundleIdentifier': f"com.subtitletranslator.{APP_NAME.lower()}",
        'CFBundleVersion': VERSION,
        'CFBundleShortVersionString': VERSION,
        'NSHumanReadableCopyright': COPYRIGHT,
        'NSHighResolutionCapable': True,
    },
    'frameworks': [],  # 필요한 외부 프레임워크 (필요시 추가)
}

setup(
    name=APP_NAME,
    app=['app.py'],
    data_files=DATA_FILES,
    options={'py2app': PY2APP_OPTIONS},
    setup_requires=['py2app'],
    install_requires=[
        'PyQt6',
        'anthropic',
        'tqdm',
    ],
)
