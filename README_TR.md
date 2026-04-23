# Argus

Argus, otonom görev yürütme, değerlendirme iş akışları ve genişletilebilir çalışma bileşenlerine odaklanan Python tabanlı bir agent framework'üdür.

## Bu Depoda Neler Var

- `argus/` altında çekirdek Argus paketi
- `evaluation/` altında BFCL ve SWEBench odaklı değerlendirme yardımcıları
- Agent çalışma ortamları için container tanımları
- `tests/` altında test kapsamı

## Hızlı Başlangıç

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

Test çalıştırma:

```bash
pytest
```

## Depo Yapısı

- `argus/`: çekirdek paket ve runtime modülleri
- `evaluation/`: benchmark ve adapter scriptleri
- `docs/`: proje dokümantasyonu
- `tests/`: otomatik testler

## Lisans

`LICENSE` dosyasına bakın.
