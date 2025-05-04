# 자막 번역 도구 macOS 앱

자막 번역 도구를 macOS 애플리케이션으로 사용할 수 있습니다. 이 앱은 기존 명령줄 도구의 모든 기능을 그래픽 사용자 인터페이스(GUI)로 제공합니다.

## 주요 기능

- SRT 파일 형식의 자막 번역 (영어 → 한국어)
- YouTube 동영상 다운로드 및 자막 자동 추출
- 실시간 진행 상황 표시
- 번역 비용 및 토큰 사용량 통계

## 시작하기

### 1. 개발 모드에서 실행

개발 과정에서 앱을 테스트하려면 다음 명령을 실행하세요:

```bash
# 필요한 패키지 설치
pip install PyQt6 anthropic tqdm
pip install yt-dlp
pip install --upgrade assemblyai

# 앱 실행
cd app
python start_app.py
```

### 2. macOS 앱으로 빌드

독립 실행형 macOS 애플리케이션으로 빌드하려면:

```bash
cd app
chmod +x build_app.sh
./build_app.sh
```

빌드가 완료되면 `dist/SubtitleTranslator.app` 파일이 생성됩니다.

### 3. API 키 설정

앱 사용 전 다음 API 키가 필요합니다:

- **Anthropic Claude API 키**: 자막 번역에 사용
- **AssemblyAI API 키**: 자막 추출에 사용

API 키는 다음 방법으로 설정할 수 있습니다:

1. **환경 변수**로 설정:
   ```bash
   export ANTHROPIC_API_KEY=your_api_key_here
   export ASSEMBLYAI_API_KEY=your_api_key_here
   ```

2. **앱 내 설정 탭**에서 직접 입력

## 앱 사용 방법

### 자막 번역

1. "자막 번역" 탭 선택
2. "찾아보기" 버튼으로 SRT 파일 선택
3. 원하는 경우 출력 파일 경로 지정
4. "번역 시작" 버튼 클릭
5. 진행 상황이 실시간으로 표시됨

### YouTube 다운로드 및 자막 추출

1. "YouTube 다운로드 및 자막 추출" 탭 선택
2. YouTube URL 입력
3. 작업 옵션 선택 (자막 추출, 번역)
4. "다운로드" 버튼 클릭
5. 진행 상황 모니터링

### 설정 조정

"설정" 탭에서 다음 옵션을 조정할 수 있습니다:

- 번역 모델 선택
- 배치 크기 및 병렬 작업자 수 설정
- API 키 입력

## 문제 해결

- **앱이 실행되지 않는 경우**
  - 필요한 패키지가 설치되어 있는지 확인하세요
  - 권한 문제가 있다면: `chmod +x dist/SubtitleTranslator.app/Contents/MacOS/SubtitleTranslator`

- **"손상된 앱" 오류 메시지**
  - 터미널에서 실행: `xattr -cr dist/SubtitleTranslator.app`

- **API 키 오류**
  - 올바른 API 키를 설정했는지 확인하세요
  - 환경 변수가 제대로 설정되었는지 확인하세요

## 자세한 문서

더 자세한 내용은 다음 문서를 참조하세요:

- `INSTALL.md`: 설치 및 사용 방법 가이드
- `icon_guide.md`: 앱 아이콘 생성 가이드
- `SUMMARY.md`: 프로젝트 요약
- `README.md`: 패키징 가이드

## 라이선스

MIT License

## 기여

버그 신고나 기능 제안은 이슈 트래커를 이용해 주세요. 풀 리퀘스트도 환영합니다.