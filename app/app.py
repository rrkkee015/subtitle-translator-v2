#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import threading
import subprocess
import re
import json
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QTabWidget, QLabel, QPushButton, QLineEdit, QFileDialog, 
                            QTextEdit, QProgressBar, QComboBox, QSpinBox, QMessageBox,
                            QGroupBox, QRadioButton, QCheckBox)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QUrl
from PyQt6.QtGui import QIcon, QDesktopServices, QFont

# 상위 디렉토리 추가하여 기존 모듈 import 가능하게 함
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 기존 모듈 import
from subtitle import SubtitleTranslator, SubtitleTranslationConfig

class RedirectOutput:
    """출력을 GUI로 리다이렉트"""
    def __init__(self, text_widget):
        self.text_widget = text_widget
        self.buffer = ""

    def write(self, text):
        self.buffer += text
        if '\n' in self.buffer:
            lines = self.buffer.split('\n')
            self.buffer = lines[-1]
            for line in lines[:-1]:
                self.text_widget.append(line)
        self.text_widget.ensureCursorVisible()

    def flush(self):
        if self.buffer:
            self.text_widget.append(self.buffer)
            self.buffer = ""


class TranslationThread(QThread):
    """자막 번역을 위한 스레드"""
    update_progress = pyqtSignal(int, int)
    update_status = pyqtSignal(str)
    finished_signal = pyqtSignal(bool, str)

    def __init__(self, input_file, output_file, config):
        super().__init__()
        self.input_file = input_file
        self.output_file = output_file
        self.config = config
        self.original_stdout = sys.stdout
        self.original_stderr = sys.stderr

    def run(self):
        try:
            self.update_status.emit(f"파일 '{self.input_file}'을(를) 번역합니다...")
            translator = SubtitleTranslator(self.config)
            
            # 원본 translate 메소드를 저장
            original_translate = translator.translate
            
            # batches 변수를 추적하기 위한 래퍼 함수
            def translate_wrapper(input_file, output_file):
                # 입력 파일 읽기 및 검증
                srt_content = translator.file_handler.read_srt_file(input_file)
                
                if not translator.file_handler.validate_srt_format(srt_content):
                    translator.logger.error("유효하지 않은 SRT 파일 형식입니다.")
                    raise ValueError("유효하지 않은 SRT 파일 형식입니다.")
                
                # 자막 분할 및 배치 생성
                subtitles = translator.processor.split_subtitles(srt_content)
                translator.logger.info(f"총 {len(subtitles)}개의 자막을 찾았습니다.")
                
                batches = translator.processor.create_batches(subtitles, translator.config.batch_size)
                translator.logger.info(f"자막을 {len(batches)}개의 배치로 나누었습니다.")
                
                # 진행 상황 업데이트를 위한 콜백 함수
                original_translate_batch_task = translator._translate_batch_task
                
                def progress_hook(args):
                    batch_index, translated_batch, input_tokens, output_tokens = original_translate_batch_task(args)
                    self.update_progress.emit(batch_index + 1, len(batches))
                    return batch_index, translated_batch, input_tokens, output_tokens
                
                # 원본 함수 대체
                translator._translate_batch_task = progress_hook
                
                # 원본 translate 함수 호출
                return original_translate(input_file, output_file)
            
            # translate 메소드를 래퍼로 대체
            translator.translate = translate_wrapper
            
            stats = translator.translate(self.input_file, self.output_file)
            self.update_status.emit(f"번역 완료! 결과가 {self.output_file}에 저장되었습니다.")
            
            # 결과 요약 생성
            summary = f"""
            번역 완료 요약:
            - 처리된 자막 수: {stats['subtitles_count']}
            - 배치 수: {stats['batches_count']}
            - 입력 토큰: {stats['input_tokens']}
            - 출력 토큰: {stats['output_tokens']}
            - 총 비용: ${stats['total_cost']:.4f}
            """
            
            self.finished_signal.emit(True, summary)
            
        except Exception as e:
            self.update_status.emit(f"오류 발생: {str(e)}")
            self.finished_signal.emit(False, str(e))


class YoutubeDownloadThread(QThread):
    """YouTube 동영상 다운로드 스레드"""
    update_status = pyqtSignal(str)
    finished_signal = pyqtSignal(bool, str, str)

    def __init__(self, youtube_url, download_directory=None):
        super().__init__()
        self.youtube_url = youtube_url
        self.download_directory = download_directory or os.path.expanduser("~/Downloads")

    def run(self):
        try:
            self.update_status.emit(f"YouTube 동영상 다운로드 중: {self.youtube_url}")
            
            # 작업 디렉토리를 다운로드 디렉토리로 변경
            current_dir = os.getcwd()
            os.chdir(self.download_directory)
            
            # yt-dlp 명령어 실행
            result = subprocess.run(
                ["yt-dlp", "-f", "bestvideo+bestaudio/best", self.youtube_url], 
                capture_output=True, 
                text=True
            )
            
            if result.returncode != 0:
                self.update_status.emit(f"다운로드 실패: {result.stderr}")
                self.finished_signal.emit(False, "", "다운로드 실패")
                return
            
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
                self.update_status.emit("다운로드된 파일명을 찾을 수 없습니다.")
                self.finished_signal.emit(False, "", "파일명을 찾을 수 없음")
                return
            
            # [videoID] 부분 제거
            clean_filename = re.sub(r'\s*\[[a-zA-Z0-9_-]+\](\.[^.]+)$', r'\1', filename)
            
            # 파일 이름 변경
            if clean_filename != filename:
                try:
                    os.rename(filename, clean_filename)
                    self.update_status.emit(f"파일명 변경: {filename} -> {clean_filename}")
                    filename = clean_filename
                except Exception as e:
                    self.update_status.emit(f"파일명 변경 실패: {e}")
            
            self.update_status.emit(f"동영상 다운로드 완료: {filename}")
            self.finished_signal.emit(True, filename, "다운로드 완료")
            
        except Exception as e:
            self.update_status.emit(f"다운로드 중 오류 발생: {str(e)}")
            self.finished_signal.emit(False, "", str(e))
        finally:
            # 작업 디렉토리 복원
            os.chdir(current_dir)


class ExtractSubtitleThread(QThread):
    """자막 추출 스레드"""
    update_status = pyqtSignal(str)
    finished_signal = pyqtSignal(bool, str, str)

    def __init__(self, video_filename):
        super().__init__()
        self.video_filename = video_filename

    def run(self):
        try:
            if not self.video_filename or not os.path.exists(self.video_filename):
                self.update_status.emit(f"파일을 찾을 수 없습니다: {self.video_filename}")
                self.finished_signal.emit(False, "", "파일을 찾을 수 없음")
                return
            
            self.update_status.emit(f"자막 추출 중: {self.video_filename}")
            
            # AssemblyAI 명령어 실행
            result = subprocess.run(
                ["assemblyai", "transcribe", self.video_filename, "--srt"],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                self.update_status.emit(f"자막 추출 실패: {result.stderr}")
                self.finished_signal.emit(False, "", "자막 추출 실패")
                return
            
            # 출력에서 생성된 SRT 파일명 추출
            output = result.stdout
            match = re.search(r'Successfully created file ([a-zA-Z0-9-]+\.srt)', output)
            
            if not match:
                self.update_status.emit("생성된 SRT 파일명을 찾을 수 없습니다.")
                self.finished_signal.emit(False, "", "SRT 파일명을 찾을 수 없음")
                return
            
            srt_filename = match.group(1)
            
            # 동영상 파일명과 동일하게 SRT 파일명 변경
            base_filename = os.path.splitext(self.video_filename)[0]
            new_srt_filename = f"{base_filename}.srt"
            
            try:
                os.rename(srt_filename, new_srt_filename)
                self.update_status.emit(f"SRT 파일명 변경: {srt_filename} -> {new_srt_filename}")
            except Exception as e:
                self.update_status.emit(f"SRT 파일명 변경 실패: {e}")
                self.finished_signal.emit(False, "", f"SRT 파일명 변경 실패: {e}")
                return
            
            self.update_status.emit(f"자막 추출 완료: {new_srt_filename}")
            self.finished_signal.emit(True, new_srt_filename, "자막 추출 완료")
            
        except Exception as e:
            self.update_status.emit(f"자막 추출 중 오류 발생: {str(e)}")
            self.finished_signal.emit(False, "", str(e))


class SubtitleTranslatorApp(QMainWindow):
    """자막 번역 앱 메인 윈도우"""
    
    def __init__(self):
        super().__init__()
        
        # 초기화 순서 변경: 속성부터 먼저 초기화
        self.translator_thread = None
        self.youtube_thread = None
        self.extract_thread = None
        self.extract_only_thread = None  # 단독 자막 추출용 스레드 추가
        self.downloaded_video = None
        self.extracted_subtitle = None
        
        # 기본 저장 위치 설정
        self.download_directory = os.path.expanduser("~/Downloads")
        
        # UI 초기화 및 설정 로드
        self.init_ui()
        self.config = self.load_config()
        
        # 설정 파일에서 저장 위치 로드
        self.load_directories_from_config()
        # UI에 저장 위치 반영
        if hasattr(self, 'download_dir_edit'):
            self.download_dir_edit.setText(self.download_directory)
        
    def init_ui(self):
        """UI 초기화"""
        self.setWindowTitle("자막 번역 도구")
        self.setGeometry(100, 100, 900, 700)
        self.setMinimumSize(800, 600)
        
        # 메인 위젯과 레이아웃
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # 탭 위젯 생성
        self.tabs = QTabWidget()
        self.tabs.setTabPosition(QTabWidget.TabPosition.North)
        main_layout.addWidget(self.tabs)

        # 탭 1: YouTube 다운로드
        self.tab_youtube = QWidget()
        self.tabs.addTab(self.tab_youtube, "YouTube 다운로드")
        self.setup_youtube_tab()

        # 탭 2: 자막 추출
        self.tab_extract = QWidget()
        self.tabs.addTab(self.tab_extract, "자막 추출")
        self.setup_extract_tab()

        # 탭 3: 자막 번역
        self.tab_translate = QWidget()
        self.tabs.addTab(self.tab_translate, "자막 번역")
        self.setup_translate_tab()
        
        # 탭 4: 설정
        self.tab_settings = QWidget()
        self.tabs.addTab(self.tab_settings, "설정")
        self.setup_settings_tab()
        
        # 하단 상태 바
        self.statusBar().showMessage("준비됨")
        
        # 앱 아이콘 설정
        # self.setWindowIcon(QIcon("app/icon.png"))
        
    def setup_translate_tab(self):
        """자막 번역 탭 설정"""
        layout = QVBoxLayout(self.tab_translate)
        
        # 파일 선택 그룹
        file_group = QGroupBox("입력 파일")
        file_layout = QHBoxLayout()
        
        self.input_file_edit = QLineEdit()
        self.input_file_edit.setPlaceholderText("번역할 SRT 파일 선택")
        self.input_file_edit.setReadOnly(True)
        
        browse_button = QPushButton("찾아보기")
        browse_button.clicked.connect(self.browse_input_file)
        
        file_layout.addWidget(self.input_file_edit, 4)
        file_layout.addWidget(browse_button, 1)
        file_group.setLayout(file_layout)
        layout.addWidget(file_group)
        
        # 출력 파일 그룹
        output_group = QGroupBox("출력 파일")
        output_layout = QHBoxLayout()
        
        self.output_file_edit = QLineEdit()
        self.output_file_edit.setPlaceholderText("출력 SRT 파일 경로 (자동 생성)")
        self.output_file_edit.setReadOnly(True)
        
        output_browse_button = QPushButton("찾아보기")
        output_browse_button.clicked.connect(self.browse_output_file)
        
        output_layout.addWidget(self.output_file_edit, 4)
        output_layout.addWidget(output_browse_button, 1)
        output_group.setLayout(output_layout)
        layout.addWidget(output_group)
        
        # 번역 버튼
        translate_button = QPushButton("번역 시작")
        translate_button.setMinimumHeight(40)
        translate_button.clicked.connect(self.start_translation)
        layout.addWidget(translate_button)
        
        # 진행 상황 표시
        progress_group = QGroupBox("진행 상황")
        progress_layout = QVBoxLayout()
        
        self.progress_bar = QProgressBar()
        progress_layout.addWidget(self.progress_bar)
        
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setMinimumHeight(250)
        progress_layout.addWidget(self.log_output)
        
        progress_group.setLayout(progress_layout)
        layout.addWidget(progress_group)
        
    def setup_youtube_tab(self):
        """YouTube 다운로드 탭 설정"""
        layout = QVBoxLayout(self.tab_youtube)
        
        # URL 입력 그룹
        url_group = QGroupBox("YouTube URL")
        url_layout = QHBoxLayout()
        
        self.youtube_url_edit = QLineEdit()
        self.youtube_url_edit.setPlaceholderText("YouTube 동영상 URL을 입력하세요")
        
        download_button = QPushButton("다운로드")
        download_button.clicked.connect(self.start_youtube_download)
        
        url_layout.addWidget(self.youtube_url_edit, 4)
        url_layout.addWidget(download_button, 1)
        url_group.setLayout(url_layout)
        layout.addWidget(url_group)
        
        # 작업 설정 그룹
        options_group = QGroupBox("다운로드 후 작업")
        options_layout = QVBoxLayout()
        
        self.option_extract = QCheckBox("자막 추출")
        self.option_extract.setChecked(True)
        options_layout.addWidget(self.option_extract)
        
        self.option_translate = QCheckBox("자막 번역")
        self.option_translate.setChecked(True)
        options_layout.addWidget(self.option_translate)
        
        options_group.setLayout(options_layout)
        layout.addWidget(options_group)
        
        # 진행 상황 그룹
        yt_progress_group = QGroupBox("진행 상황")
        yt_progress_layout = QVBoxLayout()
        
        self.yt_log_output = QTextEdit()
        self.yt_log_output.setReadOnly(True)
        self.yt_log_output.setMinimumHeight(300)
        yt_progress_layout.addWidget(self.yt_log_output)
        
        yt_progress_group.setLayout(yt_progress_layout)
        layout.addWidget(yt_progress_group)
        
    def setup_settings_tab(self):
        """설정 탭 설정"""
        layout = QVBoxLayout(self.tab_settings)
        
        # 모델 설정 그룹
        model_group = QGroupBox("번역 모델 설정")
        model_layout = QVBoxLayout()
        
        model_label = QLabel("Claude 모델:")
        self.model_combo = QComboBox()
        self.model_combo.addItems([
            "claude-3-7-sonnet-20250219",
            "claude-3-haiku-20240307",
            "claude-3-opus-20240229"
        ])
        model_layout.addWidget(model_label)
        model_layout.addWidget(self.model_combo)
        
        # 추가 설명 레이블
        model_help = QLabel("* claude-3-7-sonnet: 균형 잡힌, claude-3-haiku: 빠른 & 저렴한, claude-3-opus: 최고 품질")
        model_help.setWordWrap(True)
        model_layout.addWidget(model_help)
        
        # 배치 크기 설정
        batch_layout = QHBoxLayout()
        batch_label = QLabel("배치 크기:")
        self.batch_spin = QSpinBox()
        self.batch_spin.setMinimum(1)
        self.batch_spin.setMaximum(20)
        self.batch_spin.setValue(5)
        batch_layout.addWidget(batch_label)
        batch_layout.addWidget(self.batch_spin)
        model_layout.addLayout(batch_layout)
        
        # 병렬 작업자 수 설정
        workers_layout = QHBoxLayout()
        workers_label = QLabel("병렬 작업자 수:")
        self.workers_spin = QSpinBox()
        self.workers_spin.setMinimum(1)
        self.workers_spin.setMaximum(10)
        self.workers_spin.setValue(3)
        workers_layout.addWidget(workers_label)
        workers_layout.addWidget(self.workers_spin)
        model_layout.addLayout(workers_layout)
        
        model_group.setLayout(model_layout)
        layout.addWidget(model_group)
        
        # 디렉토리 설정 그룹
        dir_group = QGroupBox("파일 저장 위치 설정")
        dir_layout = QVBoxLayout()
        
        # 다운로드 디렉토리 설정
        download_dir_layout = QHBoxLayout()
        download_dir_label = QLabel("기본 저장 위치:")
        self.download_dir_edit = QLineEdit()
        self.download_dir_edit.setText(self.download_directory)
        self.download_dir_edit.setReadOnly(True)
        
        download_dir_button = QPushButton("변경")
        download_dir_button.clicked.connect(self.browse_download_directory)
        
        download_dir_layout.addWidget(download_dir_label)
        download_dir_layout.addWidget(self.download_dir_edit, 4)
        download_dir_layout.addWidget(download_dir_button, 1)
        dir_layout.addLayout(download_dir_layout)
        
        dir_note = QLabel("* 이 설정은 유튜브 동영상 다운로드와 자막 파일의 기본 저장 위치로 사용됩니다.")
        dir_layout.addWidget(dir_note)
        
        dir_group.setLayout(dir_layout)
        layout.addWidget(dir_group)
        
        # API 키 설정 그룹
        api_group = QGroupBox("API 키 설정")
        api_layout = QVBoxLayout()
        
        anthropic_layout = QHBoxLayout()
        anthropic_label = QLabel("Anthropic API 키:")
        self.anthropic_key_edit = QLineEdit()
        self.anthropic_key_edit.setPlaceholderText("ANTHROPIC_API_KEY 환경 변수 사용 중")
        self.anthropic_key_edit.setEchoMode(QLineEdit.EchoMode.Password)
        anthropic_layout.addWidget(anthropic_label)
        anthropic_layout.addWidget(self.anthropic_key_edit)
        api_layout.addLayout(anthropic_layout)
        
        assembly_layout = QHBoxLayout()
        assembly_label = QLabel("AssemblyAI API 키:")
        self.assembly_key_edit = QLineEdit()
        self.assembly_key_edit.setPlaceholderText("ASSEMBLYAI_API_KEY 환경 변수 사용 중")
        self.assembly_key_edit.setEchoMode(QLineEdit.EchoMode.Password)
        assembly_layout.addWidget(assembly_label)
        assembly_layout.addWidget(self.assembly_key_edit)
        api_layout.addLayout(assembly_layout)
        
        api_note = QLabel("* API 키는 애플리케이션이 실행되는 동안만 유효합니다. 앱 종료 시 저장되지 않습니다.")
        api_layout.addWidget(api_note)
        
        api_group.setLayout(api_layout)
        layout.addWidget(api_group)
        
        # 저장 버튼
        save_button = QPushButton("설정 저장")
        save_button.clicked.connect(self.save_settings)
        layout.addWidget(save_button)
        
        # 정보 그룹
        info_group = QGroupBox("앱 정보")
        info_layout = QVBoxLayout()
        
        info_text = QLabel(
            "자막 번역 도구 v1.1\n\n"
            "이 앱은 영어 SRT 자막을 한국어로 번역하고, 비디오 파일 또는 YouTube 동영상에서 자막을 추출하는 기능을 제공합니다.\n"
            "Claude API를 사용하여 고품질 번역을 제공합니다.\n\n"
            "revfactory © 2024 All Rights Reserved"
        )
        info_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_text.setWordWrap(True)
        info_layout.addWidget(info_text)
        
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        # 빈 공간 추가
        layout.addStretch()
    
    def load_config(self):
        """설정 로드"""
        config = SubtitleTranslationConfig()
        
        # UI에 설정 적용
        self.model_combo.setCurrentText(config.model)
        self.batch_spin.setValue(config.batch_size)
        self.workers_spin.setValue(config.max_workers)
        
        return config
        
    def load_directories_from_config(self):
        """설정 파일에서 디렉토리 정보 로드"""
        try:
            config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config.json")
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                    
                    # 다운로드 디렉토리 설정이 있으면 로드
                    if 'download_directory' in config_data:
                        self.download_directory = config_data['download_directory']
        except Exception as e:
            print(f"디렉토리 설정 로드 중 오류: {e}")
            # 오류 발생 시 기본값 사용
    
    def save_settings(self):
        """설정 저장"""
        try:
            # 설정 객체 업데이트
            self.config.model = self.model_combo.currentText()
            self.config.batch_size = self.batch_spin.value()
            self.config.max_workers = self.workers_spin.value()
            
            # API 키 환경 변수 설정
            if self.anthropic_key_edit.text():
                os.environ['ANTHROPIC_API_KEY'] = self.anthropic_key_edit.text()
            
            if self.assembly_key_edit.text():
                os.environ['ASSEMBLYAI_API_KEY'] = self.assembly_key_edit.text()
            
            # 설정 파일 생성
            config_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config.json")
            config_data = {
                "model": self.config.model,
                "batch_size": self.config.batch_size,
                "max_tokens": self.config.max_tokens,
                "max_workers": self.config.max_workers,
                "input_token_cost": self.config.input_token_cost,
                "output_token_cost": self.config.output_token_cost,
                "download_directory": self.download_directory
            }
            
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2)
            
            QMessageBox.information(self, "설정 저장", "설정이 성공적으로 저장되었습니다.")
            
        except Exception as e:
            QMessageBox.warning(self, "오류", f"설정 저장 중 오류가 발생했습니다: {str(e)}")
    
    def browse_input_file(self):
        """입력 파일 선택 다이얼로그"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "자막 파일 선택", self.download_directory, "SRT 파일 (*.srt);;모든 파일 (*)"
        )
        
        if file_path:
            self.input_file_edit.setText(file_path)
            
            # 출력 파일 경로 자동 생성
            base, ext = os.path.splitext(os.path.basename(file_path))
            output_file_name = f"{base}_ko{ext}"
            output_dir = os.path.dirname(os.path.abspath(file_path))
            output_file = os.path.join(output_dir, output_file_name)
            
            self.output_file_edit.setText(output_file)
    
    def browse_output_file(self):
        """출력 파일 선택 다이얼로그"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "출력 파일 선택", self.output_file_edit.text() or self.download_directory, "SRT 파일 (*.srt);;모든 파일 (*)"
        )
        
        if file_path:
            self.output_file_edit.setText(file_path)
            
    def browse_download_directory(self):
        """다운로드 디렉토리 선택 다이얼로그"""
        dir_path = QFileDialog.getExistingDirectory(
            self, "기본 저장 위치 선택", self.download_directory, 
            QFileDialog.Option.ShowDirsOnly | QFileDialog.Option.DontResolveSymlinks
        )
        
        if dir_path:
            self.download_directory = dir_path
            self.download_dir_edit.setText(dir_path)
    
    def start_translation(self):
        """번역 시작"""
        input_file = self.input_file_edit.text()
        output_file = self.output_file_edit.text()
        
        if not input_file:
            QMessageBox.warning(self, "경고", "번역할 자막 파일을 선택해주세요.")
            return
        
        if not os.path.exists(input_file):
            QMessageBox.warning(self, "경고", f"파일을 찾을 수 없습니다: {input_file}")
            return
        
        if not output_file:
            # 출력 파일 경로 자동 생성
            base, ext = os.path.splitext(os.path.basename(input_file))
            output_file_name = f"{base}_ko{ext}"
            output_dir = os.path.dirname(os.path.abspath(input_file))
            output_file = os.path.join(output_dir, output_file_name)
            self.output_file_edit.setText(output_file)
        
        # 로그 출력 초기화
        self.log_output.clear()
        
        # 로그 출력 리다이렉트
        self.stdout_redirect = RedirectOutput(self.log_output)
        sys.stdout = self.stdout_redirect
        sys.stderr = self.stdout_redirect
        
        # 진행 바 초기화
        self.progress_bar.setValue(0)
        
        # 번역 스레드 시작
        self.translator_thread = TranslationThread(input_file, output_file, self.config)
        self.translator_thread.update_progress.connect(self.update_progress)
        self.translator_thread.update_status.connect(self.update_status)
        self.translator_thread.finished_signal.connect(self.translation_finished)
        self.translator_thread.start()
        
        # UI 상태 업데이트
        self.statusBar().showMessage("번역 진행 중...")
    
    def update_progress(self, current, total):
        """진행 상황 업데이트"""
        progress = int((current / total) * 100)
        self.progress_bar.setValue(progress)
    
    def update_status(self, message):
        """상태 메시지 업데이트"""
        self.statusBar().showMessage(message)
        self.log_output.append(message)
        self.yt_log_output.append(message)
    
    def translation_finished(self, success, message):
        """번역 완료 처리"""
        # 표준 출력 복원
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__
        
        if success:
            QMessageBox.information(self, "번역 완료", f"번역이 완료되었습니다.\n\n{message}")
            self.statusBar().showMessage("번역 완료")
            self.progress_bar.setValue(100)
        else:
            QMessageBox.warning(self, "번역 실패", f"번역 중 오류가 발생했습니다:\n{message}")
            self.statusBar().showMessage("번역 실패")
            self.progress_bar.setValue(0)
    
    def start_youtube_download(self):
        """YouTube 다운로드 시작"""
        youtube_url = self.youtube_url_edit.text()
        
        if not youtube_url:
            QMessageBox.warning(self, "경고", "YouTube URL을 입력해주세요.")
            return
        
        # 로그 출력 초기화
        self.yt_log_output.clear()
        
        # 로그 출력 리다이렉트
        self.stdout_redirect = RedirectOutput(self.yt_log_output)
        sys.stdout = self.stdout_redirect
        sys.stderr = self.stdout_redirect
        
        # 다운로드 스레드 시작
        self.youtube_thread = YoutubeDownloadThread(youtube_url, self.download_directory)
        self.youtube_thread.update_status.connect(self.update_status)
        self.youtube_thread.finished_signal.connect(self.youtube_download_finished)
        self.youtube_thread.start()
        
        # UI 상태 업데이트
        self.statusBar().showMessage("YouTube 동영상 다운로드 중...")
    
    def youtube_download_finished(self, success, filename, message):
        """YouTube 다운로드 완료 처리"""
        if success:
            self.statusBar().showMessage("다운로드 완료")
            self.downloaded_video = filename
            
            if self.option_extract.isChecked():
                self.start_subtitle_extraction(filename)
            else:
                QMessageBox.information(self, "다운로드 완료", f"YouTube 동영상 다운로드가 완료되었습니다.\n파일: {filename}")
        else:
            QMessageBox.warning(self, "다운로드 실패", f"YouTube 동영상 다운로드 중 오류가 발생했습니다:\n{message}")
            self.statusBar().showMessage("다운로드 실패")
    
    def start_subtitle_extraction(self, video_filename):
        """자막 추출 시작"""
        self.extract_thread = ExtractSubtitleThread(video_filename)
        self.extract_thread.update_status.connect(self.update_status)
        self.extract_thread.finished_signal.connect(self.subtitle_extraction_finished)
        self.extract_thread.start()
        
        # UI 상태 업데이트
        self.statusBar().showMessage("자막 추출 중...")
    
    def subtitle_extraction_finished(self, success, filename, message):
        """자막 추출 완료 처리"""
        if success:
            self.statusBar().showMessage("자막 추출 완료")
            self.extracted_subtitle = filename
            
            if self.option_translate.isChecked():
                # 번역 탭으로 전환하고 파일 경로 설정
                self.tabs.setCurrentIndex(0)
                self.input_file_edit.setText(filename)
                
                # 출력 파일 경로 자동 생성
                base, ext = os.path.splitext(os.path.basename(filename))
                output_file_name = f"{base}_ko{ext}"
                output_dir = os.path.dirname(os.path.abspath(filename))
                output_file = os.path.join(output_dir, output_file_name)
                self.output_file_edit.setText(output_file)
                
                # 번역 시작
                self.start_translation()
            else:
                QMessageBox.information(self, "자막 추출 완료", f"자막 추출이 완료되었습니다.\n파일: {filename}")
        else:
            QMessageBox.warning(self, "자막 추출 실패", f"자막 추출 중 오류가 발생했습니다:\n{message}")
            self.statusBar().showMessage("자막 추출 실패")
            
    def setup_extract_tab(self):
        """자막 추출 탭 설정"""
        layout = QVBoxLayout(self.tab_extract)
        
        # 비디오 파일 선택 그룹
        file_group = QGroupBox("비디오 파일")
        file_layout = QHBoxLayout()
        
        self.video_file_edit = QLineEdit()
        self.video_file_edit.setPlaceholderText("자막을 추출할 비디오 파일 선택")
        self.video_file_edit.setReadOnly(True)
        
        browse_button = QPushButton("찾아보기")
        browse_button.clicked.connect(self.browse_video_file)
        
        file_layout.addWidget(self.video_file_edit, 4)
        file_layout.addWidget(browse_button, 1)
        file_group.setLayout(file_layout)
        layout.addWidget(file_group)
        
        # 추출 설정 그룹
        options_group = QGroupBox("자막 추출 후 작업")
        options_layout = QVBoxLayout()
        
        self.option_translate_after_extract = QCheckBox("자막 추출 후 번역하기")
        self.option_translate_after_extract.setChecked(True)
        options_layout.addWidget(self.option_translate_after_extract)
        
        options_group.setLayout(options_layout)
        layout.addWidget(options_group)
        
        # 추출 버튼
        extract_button = QPushButton("자막 추출 시작")
        extract_button.setMinimumHeight(40)
        extract_button.clicked.connect(self.start_extraction_only)
        layout.addWidget(extract_button)
        
        # 진행 상황 표시
        progress_group = QGroupBox("진행 상황")
        progress_layout = QVBoxLayout()
        
        self.extract_log_output = QTextEdit()
        self.extract_log_output.setReadOnly(True)
        self.extract_log_output.setMinimumHeight(300)
        progress_layout.addWidget(self.extract_log_output)
        
        progress_group.setLayout(progress_layout)
        layout.addWidget(progress_group)
        
    def browse_video_file(self):
        """비디오 파일 선택 다이얼로그"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "비디오 파일 선택", self.download_directory, 
            "비디오 파일 (*.mp4 *.mkv *.avi *.mov *.webm);;모든 파일 (*)"
        )
        
        if file_path:
            self.video_file_edit.setText(file_path)
            
    def start_extraction_only(self):
        """단독 자막 추출 시작"""
        video_file = self.video_file_edit.text()
        
        if not video_file:
            QMessageBox.warning(self, "경고", "자막을 추출할 비디오 파일을 선택해주세요.")
            return
            
        if not os.path.exists(video_file):
            QMessageBox.warning(self, "경고", f"파일을 찾을 수 없습니다: {video_file}")
            return
            
        # 로그 출력 초기화
        self.extract_log_output.clear()
        
        # 로그 출력 리다이렉트
        self.stdout_redirect = RedirectOutput(self.extract_log_output)
        sys.stdout = self.stdout_redirect
        sys.stderr = self.stdout_redirect
        
        # 자막 추출 스레드 시작
        self.extract_only_thread = ExtractSubtitleThread(video_file)
        self.extract_only_thread.update_status.connect(self.update_status)
        self.extract_only_thread.finished_signal.connect(self.extraction_only_finished)
        self.extract_only_thread.start()
        
        # UI 상태 업데이트
        self.statusBar().showMessage("자막 추출 중...")
        
    def extraction_only_finished(self, success, filename, message):
        """단독 자막 추출 완료 처리"""
        # 표준 출력 복원
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__
        
        if success:
            self.statusBar().showMessage("자막 추출 완료")
            
            if self.option_translate_after_extract.isChecked():
                # 번역 탭으로 전환하고 파일 경로 설정
                self.tabs.setCurrentIndex(0)
                self.input_file_edit.setText(filename)
                
                # 출력 파일 경로 자동 생성
                base, ext = os.path.splitext(os.path.basename(filename))
                output_file_name = f"{base}_ko{ext}"
                output_dir = os.path.dirname(os.path.abspath(filename))
                output_file = os.path.join(output_dir, output_file_name)
                self.output_file_edit.setText(output_file)
                
                QMessageBox.information(self, "자막 추출 완료", 
                    f"자막 추출이 완료되었습니다.\n파일: {filename}\n\n번역 탭으로 이동합니다.")
                
                # 번역 시작
                self.start_translation()
            else:
                QMessageBox.information(self, "자막 추출 완료", f"자막 추출이 완료되었습니다.\n파일: {filename}")
        else:
            QMessageBox.warning(self, "자막 추출 실패", f"자막 추출 중 오류가 발생했습니다:\n{message}")
            self.statusBar().showMessage("자막 추출 실패")


def main():
    app = QApplication(sys.argv)
    
    # 앱 스타일 설정
    app.setStyle("Fusion")
    
    window = SubtitleTranslatorApp()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()