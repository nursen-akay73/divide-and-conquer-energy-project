# Divide & Conquer Energy Project
MergeSort vs QuickSort karşılaştırması: **zaman**, **işlem sayacı (comparisons/assignments)**, **proxy enerji metriği** ve **CodeCarbon tahmini enerji/karbon** çıktıları. Ayrıca deneyleri çalıştırmak için **Streamlit GUI** içerir.

## Amaç
Bu projede Divide & Conquer tabanlı iki sıralama algoritması (MergeSort ve QuickSort) farklı giriş koşullarında karşılaştırılmıştır:
- Çalışma süresi (avg_time_ms)
- Karşılaştırma sayısı (avg_comp)
- Atama / swap sayısı (avg_assign)
- Proxy enerji metriği: `energy_proxy = avg_comp + avg_assign`
- (Opsiyonel) CodeCarbon ile tahmini `energy_joule` ve `emissions_kg`

> Not: `energy_proxy` gerçek Joule ölçümü değildir; algoritmaların yaptığı işlem sayıları üzerinden hesaplanan **yaklaşık (proxy) bir enerji metriğidir**. CodeCarbon ise donanımdan doğrudan ölçüm yapmaz; tahmini enerji/karbon değerleri üretir.

## Deney Senaryoları (mode)
- **random**: Rastgele veri (ortalama duruma yakın)
- **sorted**: Önceden sıralı veri (özel durum davranışını görürsün)
- **reversed**: Ters sıralı veri (stres testi / kötü duruma yakın)

## Proje Yapısı
- `algorithms.py`  
  Sayaçlı MergeSort ve iteratif (recursion’sız) sayaçlı QuickSort + veri üretici.
- `benchmark.py`  
  Farklı `n` ve `mode` kombinasyonlarında deneyleri çalıştırır, tablo çıktısı üretir.
- `gui_app.py`  
  Streamlit arayüzü: seçilen `n`, `mode`, `repetitions` ile deneyi çalıştırır ve grafikleri gösterir.

## Kurulum
Önerilen: sanal ortam (venv)

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
