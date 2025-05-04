# 자막 번역 도구 macOS 앱 패키징 가이드

이 가이드는 자막 번역 도구를 macOS에서 독립 실행형 애플리케이션으로 패키징하는 방법을 설명합니다.

## 필요 사항

- macOS 운영체제 (10.13 이상 권장)
- Python 3.6 이상
- pip 패키지 관리자

## 필수 패키지 설치

```bash
# GUI 및 번역 관련 패키지
pip install PyQt5 anthropic tqdm

# 패키징 관련 패키지
pip install py2app
```

## 앱 아이콘 생성 (선택사항)

1. 원하는 이미지로 `.icns` 파일을 생성합니다. 방법:

   - [IconMaker](https://apps.apple.com/us/app/iconmaker/id1530659617) 앱 사용 (맥 앱스토어)
   - [IconUtil](https://developer.apple.com/library/archive/documentation/GraphicsAnimation/Conceptual/HighResolutionOSX/Optimizing/Optimizing.html#//apple_ref/doc/uid/TP40012302-CH7-SW2) 커맨드라인 도구 사용
   - 온라인 변환 도구 사용

2. 생성된 아이콘 파일을 `app` 폴더에 `icon.icns` 이름으로 저장합니다.

## 앱 패키징 과정

1. 터미널을 열고 프로젝트의 `app` 디렉토리로 이동합니다:

```bash
cd /path/to/subtitle/app
```

2. `setup.py` 스크립트를 사용하여 앱을 빌드합니다:

```bash
python setup.py py2app
```

3. 빌드가 완료되면 `dist` 폴더에 독립 실행형 앱이 생성됩니다:

```bash
open dist/SubtitleTranslator.app
```

## 앱 사용 시 주의사항

1. **API 키 설정**: 앱 내 설정 탭에서 Anthropic API 키와 AssemblyAI API 키를 입력해야 합니다.

2. **필수 외부 도구**:
   - **yt-dlp**: YouTube 동영상 다운로드에 필요합니다.
   - **assemblyai**: 자막 추출에 필요합니다.

   이 도구들은 별도로 설치해야 합니다:

   ```bash
   pip install yt-dlp
   pip install --upgrade assemblyai
   ```

3. **권한**: 처음 실행 시 macOS의 보안 설정으로 인해 앱이 차단될 수 있습니다. "시스템 설정 > 개인 정보 보호 및 보안"에서 앱 실행을 허용해주세요.

## 문제 해결

- **앱이 실행되지 않는 경우**: 터미널에서 다음 명령으로 권한을 부여해보세요:

  ```bash
  chmod +x "dist/SubtitleTranslator.app/Contents/MacOS/SubtitleTranslator"
  ```

- **"손상된 앱" 오류 메시지**: 터미널에서 다음을 실행:

  ```bash
  xattr -cr "dist/SubtitleTranslator.app"
  ```

## 배포 방법

앱을 다른 사용자에게 배포하려면:

1. `dist/SubtitleTranslator.app`을 DMG 파일로 패키징:
   - Disk Utility 사용
   - [create-dmg](https://github.com/create-dmg/create-dmg) 도구 사용

2. 배포 전 코드 서명 고려 (Apple Developer 계정 필요):
   ```bash
   codesign --force --deep --sign "Developer ID Application: 개발자 이름" "dist/SubtitleTranslator.app"
   ```

## 추가 커스터마이징

- 더 많은 리소스를 앱에 포함하려면 `setup.py`의 `DATA_FILES` 목록을 수정하세요.
- 앱 아이콘이나 메타데이터를 변경하려면 `PY2APP_OPTIONS` 딕셔너리를 수정하세요.