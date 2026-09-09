#!/bin/bash
# usage: reel.sh <boss>  -> renders/reels/<boss>_reel.gif + per-clip gifs + key stills
b=$1; cd ${NCS_ART_ROOT:-$HOME}/renders; mkdir -p reels reels/tmp_$b; rm -f reels/tmp_$b/*
i=0; for k in idle walk attack death; do
  ffmpeg -y -loglevel error -framerate 24 -i ${b}_$k/f_%04d.png -vf "split[a][c];[a]palettegen[p];[c][p]paletteuse" reels/${b}_$k.gif
  for f in ${b}_$k/f_*.png; do cp "$f" reels/tmp_$b/$(printf 'r_%04d.png' $i); i=$((i+1)); done
done
ffmpeg -y -loglevel error -framerate 24 -i reels/tmp_$b/r_%04d.png -vf "split[a][c];[a]palettegen[p];[c][p]paletteuse" reels/${b}_reel.gif
cp ${b}_attack/f_0017.png reels/${b}_attack_key.png; cp ${b}_death/f_0048.png reels/${b}_death_key.png; rm -rf reels/tmp_$b
ls -la reels/${b}_reel.gif
