# YouTube 자막 번역기 v2

이 도구는 영어 SRT 자막 파일을 한국어로 번역하며, YouTube 동영상에서 자동으로 자막을 추출하는 기능을 제공합니다. Claude API를 사용하여 자연스러운 번역을 제공합니다.

## 주요 기능

- SRT 파일 형식의 자막 번역 (영어 → 한국어)
- YouTube 동영상 다운로드 및 자막 자동 추출
- 자막을 배치 단위로 처리하여 효율적인 번역
- 병렬 처리를 통한 번역 속도 향상
- 실시간 진행 상황 표시
- 자막 시간 중복 자동 감지 및 조정
- 번역 비용 계산 및 통계 제공
- 설정 파일을 통한 쉬운 커스터마이징


## 스크린샷
<img width="895" alt="스크린샷 2025-05-05 13 51 26" src="https://github.com/user-attachments/assets/bf44a2b1-ba97-4a06-8d04-86cb5bf1e877" />

<img width="896" alt="스크린샷 2025-05-05 13 51 38" src="https://github.com/user-attachments/assets/c90d79d5-a008-41f9-b14e-6801cd216be2" />

<img width="897" alt="스크린샷 2025-05-05 13 51 48" src="https://github.com/user-attachments/assets/1e797d92-e8bb-48ff-8c03-4cdc1c3d590b" />

<img width="896" alt="스크린샷 2025-05-05 13 51 57" src="https://github.com/user-attachments/assets/b8dc2522-dde8-4508-9603-a4b0cc42b6b1" />

## 요구 사항

- Python 3.6 이상
- Anthropic API 키 ([Claude API](https://anthropic.com/) 계정 필요)
- AssemblyAI CLI (자막 추출용)
- yt-dlp (YouTube 동영상 다운로드용)
- 필요한 패키지: `anthropic`, `tqdm`

```bash
pip install anthropic tqdm
pip install --upgrade assemblyai
pip install yt-dlp
```

## 설정

1. **API 키 설정**

   환경 변수로 API 키를 설정하세요:

   ```bash
   # Anthropic API 키 (자막 번역용)
   # Linux/macOS
   export ANTHROPIC_API_KEY=your_api_key_here

   # Windows (CMD)
   set ANTHROPIC_API_KEY=your_api_key_here

   # Windows (PowerShell)
   $env:ANTHROPIC_API_KEY="your_api_key_here"
   
   # AssemblyAI API 키 (자막 추출용)
   # Linux/macOS
   export ASSEMBLYAI_API_KEY=your_api_key_here
   
   # Windows (CMD)
   set ASSEMBLYAI_API_KEY=your_api_key_here
   
   # Windows (PowerShell)
   $env:ASSEMBLYAI_API_KEY="your_api_key_here"
   ```

2. **설정 파일 (선택사항)**

   프로그램의 동작을 커스터마이징하려면 설정 파일을 사용할 수 있습니다. 기본 설정 파일은 `config.json`이며, 다음 명령어로 생성할 수 있습니다:

   ```bash
   python subtitle.py --gen-config
   ```

   설정 파일 예시:

   ```json
   {
     "model": "claude-3-7-sonnet-20250219",
     "batch_size": 5,
     "max_tokens": 8000,
     "max_workers": 3,
     "input_token_cost": 0.000003,
     "output_token_cost": 0.00000375
   }
   ```

## 사용법

### 자막 번역

```bash
python subtitle.py path/to/your/subtitle.srt
```

결과 파일은 입력 파일과 같은 위치에 `[원본파일명]_ko.srt` 형식으로 저장됩니다.

### YouTube 동영상 다운로드 및 자막 추출

```bash
python youtube_subtitle.py "https://www.youtube.com/watch?v=VIDEO_ID"
```

이 명령어는 다음 작업을 순차적으로 수행합니다:
1. YouTube 동영상 다운로드
2. AssemblyAI를 사용한 자막 추출
3. 추출된 자막 번역 (한국어)

### 자막 번역 명령줄 옵션

```bash
python subtitle.py path/to/your/subtitle.srt [options]
```

옵션:
- `-o, --output PATH`: 출력 파일 경로 지정
- `-m, --model MODEL`: 사용할 Claude 모델 지정
- `-b, --batch-size SIZE`: 자막 배치 크기 지정
- `-w, --workers COUNT`: 병렬 처리 작업자 수 지정
- `-c, --config PATH`: 사용자 설정 파일 경로 지정
- `--gen-config`: 현재 설정으로 기본 설정 파일 생성 후 종료

### 예시

```bash
# 자막 번역 기본 사용법
python subtitle.py video.srt

# 출력 파일 지정
python subtitle.py video.srt -o translated_video.srt

# 배치 크기 및 병렬 작업자 수 변경
python subtitle.py video.srt -b 10 -w 5

# 다른 모델 사용
python subtitle.py video.srt -m claude-3-haiku-20240307

# 사용자 설정 파일 사용
python subtitle.py video.srt -c my_config.json

# YouTube 동영상 다운로드 및 자막 추출/번역
python youtube_subtitle.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
```

## 출력 예시

프로그램 실행 시 다음과 같은 정보가 표시됩니다:

```
2023-05-01 15:30:45 - __main__ - INFO - 파일 'video.srt'을(를) 번역합니다...
2023-05-01 15:30:45 - __main__ - INFO - 총 150개의 자막을 찾았습니다.
2023-05-01 15:30:45 - __main__ - INFO - 자막을 30개의 배치로 나누었습니다.
번역 진행 중: 100%|██████████| 30/30 [01:25<00:00,  2.85it/s]
2023-05-01 15:32:10 - __main__ - INFO - 자막 시간 중복 확인 및 조정 중...
2023-05-01 15:32:10 - __main__ - INFO - 시간 중복이 감지되어 자동으로 조정되었습니다.
2023-05-01 15:32:10 - __main__ - INFO - 번역 완료! 결과가 video_ko.srt에 저장되었습니다.
2023-05-01 15:32:10 - __main__ - INFO - 총 사용된 입력 토큰: 12500
2023-05-01 15:32:10 - __main__ - INFO - 총 사용된 출력 토큰: 15800
2023-05-01 15:32:10 - __main__ - INFO - 총 요금: $0.0968
2023-05-01 15:32:10 - __main__ - INFO - 번역 완료 요약:
2023-05-01 15:32:10 - __main__ - INFO - - 처리된 자막 수: 150
2023-05-01 15:32:10 - __main__ - INFO - - 배치 수: 30
2023-05-01 15:32:10 - __main__ - INFO - - 입력 토큰: 12500
2023-05-01 15:32:10 - __main__ - INFO - - 출력 토큰: 15800
2023-05-01 15:32:10 - __main__ - INFO - - 총 비용: $0.0968
```

## 주의사항

- API 키는 절대 코드나 설정 파일에 직접 입력하지 마세요. 항상 환경 변수를 사용하세요.
- 번역 비용은 Anthropic의 현재 요금 정책에 따라 계산됩니다. 요금 정책이 변경될 수 있으니 Anthropic 공식 문서를 확인하세요.
- AssemblyAI를 사용한 자막 추출은 영어 음성이 주로 포함된 동영상에 최적화되어 있습니다.
- YouTube 동영상 다운로드는 해당 국가의.저작권법과 YouTube 이용약관을 준수하는 범위 내에서 사용하세요.

## 라이선스

MIT License

## 기여

버그 신고나 기능 제안은 이슈 트래커를 이용해 주세요. 풀 리퀘스트도 환영합니다.
