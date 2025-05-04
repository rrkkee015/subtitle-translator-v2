# 앱 아이콘 생성 가이드

macOS 앱을 위한 `.icns` 아이콘 파일을 생성하는 방법입니다.

## 요구 사항

- 1024x1024 픽셀 PNG 또는 SVG 이미지
- macOS 시스템

## 방법 1: IconUtil 사용하기 (무료, 명령줄)

1. 다음 크기의 PNG 이미지를 준비합니다:
   - 16x16
   - 32x32
   - 64x64
   - 128x128
   - 256x256
   - 512x512
   - 1024x1024

2. 이미지 파일을 `.iconset` 폴더에 다음 이름으로 저장합니다:
   ```
   icon_16x16.png
   icon_32x32.png
   icon_64x64.png
   icon_128x128.png
   icon_256x256.png
   icon_512x512.png
   icon_1024x1024.png
   ```

3. 명령줄에서 다음 명령을 실행합니다:
   ```bash
   iconutil -c icns /path/to/your/icon.iconset -o icon.icns
   ```

## 방법 2: 온라인 변환 도구 사용 (무료, 간편함)

1. iConvert 같은 온라인 도구를 사용합니다:
   - [iConvert Icons](https://iconverticons.com/online/)
   - [CloudConvert](https://cloudconvert.com/png-to-icns)

2. 1024x1024 크기의 PNG 이미지를 업로드하고 .icns 형식으로 변환합니다.

## 방법 3: Sketch/Affinity Designer/Photoshop 사용 (유료)

1. 디자인 소프트웨어에서 1024x1024 크기의 아이콘을 디자인합니다.
2. 다양한 크기로 내보내기합니다.
3. 내보낸 파일을 사용하여 방법 1로 .icns 파일을 생성합니다.

## 방법 4: 아이콘 템플릿 사용하기

1. 이 가이드를 위해 준비한 간단한 텍스트 기반 아이콘 템플릿을 사용합니다:

```bash
# 텍스트 기반 아이콘 생성 (임시용)
cd /Users/robin/Documents/subtitle/app

# 임시 아이콘 폴더 생성
mkdir -p SubtitleIcon.iconset

# 다양한 크기의 텍스트 아이콘 생성하기 (요구되는 사이즈)
sips -s format png -z 16 16 -s formatOptions 100 [이미지 소스] --out SubtitleIcon.iconset/icon_16x16.png
sips -s format png -z 32 32 -s formatOptions 100 [이미지 소스] --out SubtitleIcon.iconset/icon_32x32.png
sips -s format png -z 128 128 -s formatOptions 100 [이미지 소스] --out SubtitleIcon.iconset/icon_128x128.png
sips -s format png -z 256 256 -s formatOptions 100 [이미지 소스] --out SubtitleIcon.iconset/icon_256x256.png
sips -s format png -z 512 512 -s formatOptions 100 [이미지 소스] --out SubtitleIcon.iconset/icon_512x512.png

# ICNS 파일 생성
iconutil -c icns SubtitleIcon.iconset -o icon.icns
```

## 앱에 아이콘 적용하기

1. 완성된 `.icns` 파일을 `/Users/robin/Documents/subtitle/app/` 폴더에 `icon.icns` 이름으로 저장합니다.

2. `setup.py` 파일에서 아이콘 관련 주석을 해제합니다:
   ```python
   DATA_FILES = [
       ('', ['icon.icns']),  # 주석 해제
       # ...
   ]
   
   PY2APP_OPTIONS = {
       # ...
       'iconfile': 'icon.icns',  # 주석 해제
       # ...
   }
   ```

3. 앱을 다시 빌드합니다:
   ```bash
   python setup.py py2app
   ```

## 참고

앱을 공식적으로 배포하려면 고품질 아이콘이 필요합니다. 위의 방법은 테스트 용도로 적합하며, 실제 배포 시에는 전문 디자이너에게 의뢰하는 것을 고려하세요.