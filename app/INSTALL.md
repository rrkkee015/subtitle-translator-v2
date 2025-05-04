# 자막 번역 도구 macOS 앱 설치 및 실행 가이드

이 문서는 자막 번역 도구를 macOS 앱으로 설치하고 실행하는 방법을 설명합니다.

## 1. 요구 사항

### 시스템 요구 사항
- macOS 10.14 (Mojave) 이상
- 인터넷 연결 (API 호출용)
- 최소 4GB RAM
- 최소 500MB 디스크 공간

### 필수 API 키
- [Anthropic Claude API 키](https://anthropic.com/) - 번역 기능 사용
- [AssemblyAI API 키](https://www.assemblyai.com/) - YouTube 동영상 자막 추출용

## 2. 개발 환경 설정 (개발자용)

아직 앱이 빌드되지 않은 경우, 다음 단계를 따릅니다:

### 2.1 필수 패키지 설치

```bash
# Python 패키지 설치
pip install PyQt5 anthropic tqdm yt-dlp

# 자막 추출 도구 설치
pip install --upgrade assemblyai

# 앱 패키징 도구 설치
pip install py2app
```

### 2.2 앱 빌드하기

```bash
# 앱 디렉토리로 이동
cd /Users/robin/Documents/subtitle/app

# 앱 빌드
python setup.py py2app
```

빌드가 성공하면 `dist` 폴더에 `SubtitleTranslator.app` 이 생성됩니다.

## 3. 앱 설치 (일반 사용자용)

### 3.1 DMG 파일에서 설치하기 (배포용)

1. 제공된 `SubtitleTranslator.dmg` 파일을 더블클릭합니다.
2. 열린 창에서 `SubtitleTranslator.app`을 응용 프로그램 폴더로 드래그합니다.
3. 설치가 완료되면 DMG 창을 닫고 디스크 이미지를 꺼냅니다.

### 3.2 앱 폴더에서 직접 실행하기 (개발 테스트용)

1. Finder에서 `dist/SubtitleTranslator.app`으로 이동합니다.
2. 앱 아이콘을 더블클릭하여 실행합니다.

### 3.3 보안 관련 주의사항

macOS의 보안 설정으로 인해 처음 실행 시 다음과 같은 경고가 표시될 수 있습니다:
> "SubtitleTranslator.app"은 확인되지 않은 개발자가 배포했기 때문에 열 수 없습니다.

해결 방법:
1. 시스템 환경설정 > 보안 및 개인 정보 보호로 이동합니다.
2. "일반" 탭에서 "그래도 열기" 버튼을 클릭합니다.
3. 경고 대화상자에서 "열기"를 선택합니다.

## 4. 앱 사용 방법

### 4.1 API 키 설정

앱 첫 실행 시:
1. "설정" 탭으로 이동합니다.
2. Anthropic API 키와 AssemblyAI API 키를 입력합니다.
3. "설정 저장" 버튼을 클릭합니다.

API 키는 환경 변수로도 설정할 수 있습니다:

```bash
# MacOS/Linux
export ANTHROPIC_API_KEY=your_api_key_here
export ASSEMBLYAI_API_KEY=your_api_key_here
```

### 4.2 자막 번역 사용하기

1. "자막 번역" 탭으로 이동합니다.
2. "찾아보기" 버튼을 클릭하여 번역할 SRT 파일을 선택합니다.
3. 필요시 출력 파일 경로를 지정합니다. (기본값: 원본파일명_ko.srt)
4. "번역 시작" 버튼을 클릭합니다.
5. 진행 상황이 실시간으로 표시됩니다.

### 4.3 YouTube 다운로드 및 자막 추출 사용하기

1. "YouTube 다운로드 및 자막 추출" 탭으로 이동합니다.
2. YouTube URL을 입력합니다.
3. 원하는 작업(자막 추출, 자막 번역)을 선택합니다.
4. "다운로드" 버튼을 클릭합니다.
5. 처리 과정이 로그 창에 표시됩니다.

### 4.4 설정 조정하기

"설정" 탭에서 다음 옵션을 조정할 수 있습니다:
- 번역 모델 선택 (기본값: claude-3-7-sonnet-20250219)
- 배치 크기 조정 (자막을 몇 개씩 처리할지 설정)
- 병렬 작업자 수 조정 (동시에 몇 개의 번역 작업을 진행할지 설정)

## 5. 문제 해결

### 5.1 앱이 실행되지 않는 경우

터미널에서 다음 명령으로 권한을 부여합니다:
```bash
chmod +x "/Applications/SubtitleTranslator.app/Contents/MacOS/SubtitleTranslator"
```

### 5.2 "손상된 앱" 오류 메시지

터미널에서 다음을 실행합니다:
```bash
xattr -cr "/Applications/SubtitleTranslator.app"
```

### 5.3 API 키 오류

API 키가 올바르게 설정되었는지 확인합니다:
1. 설정 탭에서 API 키를 다시 입력합니다.
2. 입력한 API 키에 공백이나 추가 문자가 없는지 확인합니다.
3. 환경 변수가 올바르게 설정되었는지 확인합니다.

### 5.4 YouTube 다운로드 실패

1. URL이 유효한지 확인합니다.
2. yt-dlp가 제대로 설치되었는지 확인합니다:
   ```bash
   pip install --upgrade yt-dlp
   ```

### 5.5 자막 추출 실패

1. AssemblyAI CLI가 제대로 설치되었는지 확인합니다:
   ```bash
   pip install --upgrade assemblyai
   ```
2. 동영상 파일 형식이 지원되는지 확인합니다. MP4, MKV, AVI 형식이 권장됩니다.

## 6. 제거 방법

앱을 제거하려면:
1. 응용 프로그램 폴더에서 `SubtitleTranslator.app`을 찾습니다.
2. 휴지통으로 드래그하거나 우클릭 후 "휴지통으로 이동"을 선택합니다.
3. 관련 설정 파일도 제거하려면:
   ```bash
   rm -rf ~/Library/Preferences/com.subtitletranslator.subtitletranslator.plist
   ```

## 7. 문의 및 지원

문제가 지속되거나 추가 지원이 필요한 경우 GitHub 이슈를 통해 문의해 주세요.

---

© 2024 자막 번역 도구 - All Rights Reserved