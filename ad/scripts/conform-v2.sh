#!/usr/bin/env bash
# WHERE'D YOU GET THAT — conform 18 clips + 2 cards into the 30s master.
# Each clip is generated at 3s; only the leading N frames are used, where the
# model is still stable. Frame counts sum to exactly 720 (30.000s @ 24fps).
set -e
N="scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=24"

#          shot: 1  2  3  4  5   6  7  8  9 10 11   12 13 14 15 16 17 18
FRAMES=(    40 32 32 34 40   26 34 24 24 48 32   30 22 32 22 46 44 60 )
# end: 2f white flash + 96f MAYBE IT'S TRUE card = 98
# live 622 + 98 = 720

ins=(); filt=""; concat=""
for i in $(seq 0 17); do
  n=$(printf "%02d" $((i+1)))
  ins+=( -i "c$n.mp4" )
  d=$(python3 -c "print(${FRAMES[$i]}/24)")
  filt+="[$i:v]$N,trim=duration=$d,setpts=PTS-STARTPTS[v$i];"
  concat+="[v$i]"
done
# 18=flash 19=card1 20=card2 21=silence
ffmpeg -y -loglevel error "${ins[@]}" \
 -f lavfi -t 0.0834 -i color=c=white:s=1920x1080:r=24 \
 -loop 1 -t 2.5 -i card1.png \
 -loop 1 -t 3.0 -i card2.png \
 -f lavfi -i anullsrc=r=48000:cl=stereo \
 -filter_complex "$filt\
[18:v]setsar=1,fps=24,trim=duration=0.083334,setpts=PTS-STARTPTS[vf];\
[19:v]$N,trim=duration=2.5,setpts=PTS-STARTPTS[vc1];\
[20:v]$N,trim=duration=3.0,setpts=PTS-STARTPTS[vc2];\
${concat}[vf][vc1][vc2]concat=n=21:v=1:a=0[outv]" \
 -map "[outv]" -map 21:a -shortest \
 -c:v libx264 -preset fast -crf 16 -pix_fmt yuv420p -r 24 \
 -c:a aac -b:a 192k -ar 48000 -movflags +faststart wheredyougetthat-30s.mp4
ffprobe -v error -select_streams v:0 -count_frames \
  -show_entries stream=nb_read_frames,duration -of csv=p=0 wheredyougetthat-30s.mp4
