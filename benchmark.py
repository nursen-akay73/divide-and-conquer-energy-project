"""
benchmark.py
------------
Bu dosya, algorithms.py içindeki sayaçlı MergeSort ve QuickSort
algoritmalarını FARKLI GİRDİ BOYUTLARI ve FARKLI DİZİ SENARYOLARI
(random, sorted, reversed) için test eder.

Amaç:
- Zaman karmaşıklığına karşılık gelen gerçek çalışma süresini ölçmek
- Sayaçlardan (comparisons, assignments) yararlanarak
  enerji karmaşıklığı için bir "proxy" (yaklaşık metrik) üretmek
- Ek olarak CodeCarbon ile (tahmini) enerji/karbon çıktısı almak
- Elde edilen sonuçları tablo gibi terminalde göstermek
  (rapordaki tabloya birebir kopyalanabilir).
"""

import time
from codecarbon import EmissionsTracker

# Kendi yazdığımız algoritma ve sayaç yapısını içe aktarıyoruz
from algorithms import Counters, generate_array, mergesort, quicksort


def run_single_experiment(n: int, mode: str, repetitions: int = 5):
    """
    Verilen n ve mode için:
      - MergeSort'u 'repetitions' kez çalıştırır, süre + sayaç ortalamasını alır
      - QuickSort'u 'repetitions' kez çalıştırır, süre + sayaç ortalamasını alır
      - CodeCarbon ile tüm bu deneyi kapsayan (tahmini) enerji/karbon ölçümü alır

    Dönüş:
        merge_results, quick_results şeklinde iki sözlük (dict).
    """

    # MergeSort toplamları
    merge_time_total = 0.0
    merge_comp_total = 0
    merge_assign_total = 0

    # QuickSort toplamları
    quick_time_total = 0.0
    quick_comp_total = 0
    quick_assign_total = 0

    # CodeCarbon: Bu (n, mode) senaryosunun tüm repetitions çalışmasını kapsasın
    tracker = EmissionsTracker(
        project_name=f"DivideConquer_{mode}_{n}",
        measure_power_secs=1,
        log_level="error",
        save_to_file=False,
    )
    tracker.start()

    for _ in range(repetitions):
        # Her deney için aynı senaryoya uygun dizi üret
        base_arr = generate_array(n, mode)

        # ----------------- MERGESORT -----------------
        c_merge = Counters()
        arr_merge = base_arr.copy()
        start = time.perf_counter()
        _ = mergesort(arr_merge, c_merge)
        end = time.perf_counter()

        merge_time_total += (end - start)
        merge_comp_total += c_merge.comparisons
        merge_assign_total += c_merge.assignments

        # ----------------- QUICKSORT -----------------
        c_quick = Counters()
        arr_quick = base_arr.copy()
        start = time.perf_counter()
        quicksort(arr_quick, c_quick)
        end = time.perf_counter()

        quick_time_total += (end - start)
        quick_comp_total += c_quick.comparisons
        quick_assign_total += c_quick.assignments

    # Tracker stop: MUTLAKA for döngüsünün DIŞINDA olmalı
    emissions_kg = tracker.stop()

    # CodeCarbon bazı sürümlerde energy_consumed (kWh) bilgisini final_emissions_data içinde tutar
    data = getattr(tracker, "final_emissions_data", None)
    energy_kwh = getattr(data, "energy_consumed", None) if data is not None else None
    energy_joule = (energy_kwh * 3_600_000) if energy_kwh is not None else None  # 1 kWh = 3.6e6 J

    # Ortalamalar (ms cinsinden süre)
    merge_avg_time_ms = (merge_time_total / repetitions) * 1000.0
    quick_avg_time_ms = (quick_time_total / repetitions) * 1000.0

    merge_results = {
        "algo": "MergeSort",
        "n": n,
        "mode": mode,
        "repetitions": repetitions,
        "avg_time_ms": merge_avg_time_ms,
        "avg_comp": merge_comp_total / repetitions,
        "avg_assign": merge_assign_total / repetitions,
        "energy_proxy": (merge_comp_total + merge_assign_total) / repetitions,
        "energy_joule": energy_joule,     # CodeCarbon’dan (tahmini) Joule
        "emissions_kg": emissions_kg,     # kgCO2eq
    }

    quick_results = {
        "algo": "QuickSort",
        "n": n,
        "mode": mode,
        "repetitions": repetitions,
        "avg_time_ms": quick_avg_time_ms,
        "avg_comp": quick_comp_total / repetitions,
        "avg_assign": quick_assign_total / repetitions,
        "energy_proxy": (quick_comp_total + quick_assign_total) / repetitions,
        "energy_joule": energy_joule,     # aynı senaryo ölçümü (ikisi aynı tracker içinde)
        "emissions_kg": emissions_kg,
    }

    return merge_results, quick_results


def run_all_experiments():
    """
    Farklı n ve senaryolar için deneyleri çalıştırır ve
    sonuçları terminale tablo benzeri bir formatta yazar.
    """
    sizes = [1000, 5000, 10000]
    modes = ["random", "sorted", "reversed"]
    repetitions = 5

    print("=== Divide & Conquer Enerji Deneyi (Python) ===\n")
    print(f"Tekrar sayısı (repetitions): {repetitions}\n")

    header = (
        f"{'Algo':<10} {'n':>8} {'mode':>10} "
        f"{'avg_time_ms':>15} {'avg_comp':>12} {'avg_assign':>12} "
        f"{'energy_proxy':>13} {'energy_joule':>13} {'emissions_kg':>13}"
    )
    print(header)
    print("-" * len(header))

    for n in sizes:
        for mode in modes:
            merge_res, quick_res = run_single_experiment(n, mode, repetitions)

            # Format: enerji gelmezse "-" bas
            m_ej = f"{merge_res['energy_joule']:.2f}" if merge_res["energy_joule"] is not None else "-"
            m_em = f"{merge_res['emissions_kg']:.8f}" if merge_res["emissions_kg"] is not None else "-"

            q_ej = f"{quick_res['energy_joule']:.2f}" if quick_res["energy_joule"] is not None else "-"
            q_em = f"{quick_res['emissions_kg']:.8f}" if quick_res["emissions_kg"] is not None else "-"

            print(
                f"{merge_res['algo']:<10} "
                f"{merge_res['n']:>8} "
                f"{merge_res['mode']:>10} "
                f"{merge_res['avg_time_ms']:>15.3f} "
                f"{merge_res['avg_comp']:>12.1f} "
                f"{merge_res['avg_assign']:>12.1f} "
                f"{merge_res['energy_proxy']:>13.1f} "
                f"{m_ej:>13} "
                f"{m_em:>13}"
            )

            print(
                f"{quick_res['algo']:<10} "
                f"{quick_res['n']:>8} "
                f"{quick_res['mode']:>10} "
                f"{quick_res['avg_time_ms']:>15.3f} "
                f"{quick_res['avg_comp']:>12.1f} "
                f"{quick_res['avg_assign']:>12.1f} "
                f"{quick_res['energy_proxy']:>13.1f} "
                f"{q_ej:>13} "
                f"{q_em:>13}"
            )

        print("-" * len(header))


if __name__ == "__main__":
    run_all_experiments()
