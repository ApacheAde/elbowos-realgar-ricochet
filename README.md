# Realgar Ricochet

Full-colour Python 3 neon ember-canyon arcade for [ElbowOS](https://x.com/ElbowOS).

A realgar ember ricochets inside a charcoal canyon. Slide the ash scoop to keep it aloft and pop the glowing veins. Miss the scoop and the ember drops into the slag.

This is an original arcade. It is not a Nintendo ROM, not an emulator, and not a copy of the splice, sieve, volley, or pinball packs.

## Play

```
pip install -r requirements.txt
python3 realgar_ricochet.py --play
```

A / D or arrow keys slide the scoop. R resets. Esc quits.

## Record a 9:16 reel

```
python3 realgar_ricochet.py --record
```

Writes a 15-second 1080x1920 H.264 MP4 (dummy SDL video driver, ffmpeg libx264 yuv420p CRF 20, +faststart).

* Featured account: https://x.com/ElbowOS
* Drive reel: https://drive.google.com/file/d/1sFTwC0rxavi_18jmNpFJ5at2pFH5_Vfc/view?usp=drivesdk
* Repo: https://github.com/ApacheAde/elbowos-realgar-ricochet
