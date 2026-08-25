#!/usr/bin/env bash
# THE LINE — conform the six segments into the 30s master.
# Run where the five clips (s1..s5.mp4) and card.png are present.
# Output: 1920x1080, 24fps, exactly 720 frames, silent 48kHz stereo track.
set -e
N="scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=24"
ffmpeg -y \
 -i s1.mp4 -i s2.mp4 -i s3.mp4 -i s4.mp4 -i s5.mp4 \
 -loop 1 -t 5 -i card.png \
 -f lavfi -t 0.0834 -i color=c=white:s=1920x1080:r=24 \
 -f lavfi -i anullsrc=r=48000:cl=stereo \
 -filter_complex "\
[0:v]$N,trim=duration=5,setpts=PTS-STARTPTS[v0];\
[1:v]$N,trim=duration=5,setpts=PTS-STARTPTS[v1];\
[2:v]$N,trim=duration=5,setpts=PTS-STARTPTS[v2];\
[3:v]$N,trim=duration=5,setpts=PTS-STARTPTS[v3];\
[4:v]$N,trim=duration=4.916667,setpts=PTS-STARTPTS[v4];\
[6:v]setsar=1,fps=24,trim=duration=0.083334,setpts=PTS-STARTPTS[vf];\
[5:v]$N,trim=duration=5,setpts=PTS-STARTPTS[v5];\
[v0][v1][v2][v3][v4][vf][v5]concat=n=7:v=1:a=0[outv]" \
 -map "[outv]" -map 7:a -shortest \
 -c:v libx264 -preset fast -crf 16 -pix_fmt yuv420p -r 24 \
 -c:a aac -b:a 192k -ar 48000 \
 -movflags +faststart the-line-30s-master.mp4
ffprobe -v error -select_streams v:0 -count_frames \
  -show_entries stream=nb_read_frames,duration -of csv=p=0 the-line-30s-master.mp4
