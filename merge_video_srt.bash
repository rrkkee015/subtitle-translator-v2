ffmpeg -i video.webm -vf "subtitles=subtitle_ko.srt:charenc=UTF-8" \
  -c:v libvpx-vp9 -crf 20 -b:v 0 -row-mt 1 -cpu-used 0 \
  -auto-alt-ref 1 -lag-in-frames 25 -tile-columns 2 -frame-parallel 1 \
  -pix_fmt yuv420p -c:a libopus -b:a 192k video_ko_hq.webm