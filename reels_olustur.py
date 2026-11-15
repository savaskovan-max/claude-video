import os
from moviepy.editor import (
    ImageClip, ColorClip, TextClip, CompositeVideoClip, concatenate_videoclips
)

GENISLIK, YUKSEKLIK = 1080, 1920
FPS = 30
HEDEF_SURE = 30.0

# Depodaki tüm resim dosyalarını (uzantı ve büyük/küçük harf fark etmeksizin) bul
gecerli_uzantilar = (".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tif", ".tiff")
resimler = []

for kok, klasorler, dosyalar in os.walk("."):
    if ".git" in kok or ".github" in kok:
        continue
    for dosya in sorted(dosyalar):
        if dosya.lower().endswith(gecerli_uzantilar):
            resimler.append(os.path.join(kok, dosya))

print(f"Bulunan resim sayisi: {len(resimler)}", resimler)

yazilar = [
    "Ankara'nın kalbinde bir tarih:\nSaraçoğlu Mahallesi",
    "1944'ten günümüze uzanan\nözel mimari ve yeşil doku",
    "Kafeler, yürüyüş yolları ve\nhuzurlu atmosferiyle keşfetmeye değer!\n📍 Kızılay / Ankara"
]

def dikey_formatla(clip):
    oran_hedef = GENISLIK / YUKSEKLIK
    oran_mevcut = clip.w / clip.h
    if oran_mevcut > oran_hedef:
        yeni_genislik = int(clip.h * oran_hedef)
        clip = clip.crop(x_center=clip.w / 2, width=yeni_genislik)
    else:
        yeni_yukseklik = int(clip.w / oran_hedef)
        clip = clip.crop(y_center=clip.h / 2, height=yeni_yukseklik)
    return clip.resize((GENISLIK, YUKSEKLIK))

# Eğer hiç resim bulunamazsa bile videonun çökmemesi için 3 arka plan sahnesi oluştur
if len(resimler) == 0:
    resimler = ["yedek_1", "yedek_2", "yedek_3"]

gecis_suresi = 0.4
resim_sayisi = len(resimler)
tek_klip_suresi = (HEDEF_SURE + (resim_sayisi - 1) * gecis_suresi) / resim_sayisi

klipler = []

for i, resim_yolu in enumerate(resimler):
    if resim_yolu.startswith("yedek_"):
        klip = ColorClip(size=(GENISLIK, YUKSEKLIK), color=(30, 30, 35)).set_duration(tek_klip_suresi)
    else:
        klip = ImageClip(resim_yolu).set_duration(tek_klip_suresi)
        klip = dikey_formatla(klip)
        if i % 2 == 0:
            klip = klip.resize(lambda t: 1 + 0.015 * t).set_position(("center", "center"))
        else:
            klip = klip.resize(lambda t: 1.15 - 0.015 * t).set_position(("center", "center"))

    metin = yazilar[i % len(yazilar)]

    alt_yazi = TextClip(
        metin,
        fontsize=50,
        color="white",
        font="DejaVu-Sans-Bold",
        bg_color="rgba(0, 0, 0, 0.55)",
        method="caption",
        size=(900, None)
    ).set_position(("center", 1400)).set_duration(tek_klip_suresi)

    sahne = CompositeVideoClip([klip, alt_yazi], size=(GENISLIK, YUKSEKLIK))
    klipler.append(sahne)

ana_video = concatenate_videoclips(klipler, method="compose", padding=-gecis_suresi)

marka_yazisi = TextClip(
    "@ankaranevarneyok",
    fontsize=42,
    color="white",
    font="DejaVu-Sans-Bold",
    bg_color="rgba(220, 38, 38, 0.85)"
).set_position(("center", 160)).set_duration(ana_video.duration)

final_video = CompositeVideoClip([ana_video, marka_yazisi])

final_video.write_videofile(
    "saracoglu_reels.mp4",
    fps=FPS,
    codec="libx264",
    audio=False
)
