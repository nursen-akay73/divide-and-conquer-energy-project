import sys
import random
import time
from dataclasses import dataclass

# İstersen dursun, ama artık RecursionError yaşamayacağız çünkü QuickSort iteratif.
sys.setrecursionlimit(100000)

# --------------------------------------------------
# Sayaç yapısı (enerji proxy'si)
# --------------------------------------------------
@dataclass
class Counters:
    """
    Algoritmaların yaptığı işlemleri saymak için kullanılan basit sayaç sınıfı.
    - comparisons: karşılaştırma sayısı (if, <= vb.)
    - assignments: atama / kopyalama / swap sayısı
    Bu sayıları daha sonra "enerji karmaşıklığı" için vekil (proxy) olarak kullanacağız.
    """
    comparisons: int = 0     # karşılaştırma sayısı
    assignments: int = 0     # atama / kopyalama / swap sayısı

    def reset(self):
        """Sayaçları sıfırlar."""
        self.comparisons = 0
        self.assignments = 0


# --------------------------------------------------
# Veri üretici
# --------------------------------------------------
def generate_array(n: int, mode: str = "random"):
    """
    Belirli senaryo için dizi üretir.

    Parametreler:
        n   : dizi boyutu
        mode: "random", "sorted" veya "reversed"

    Dönüş:
        Üretilen tamsayı listesi.
    """
    if mode == "random":
        arr = [random.randint(0, 10_000_000) for _ in range(n)]
    elif mode == "sorted":
        arr = list(range(n))                # 0, 1, 2, ..., n-1
    elif mode == "reversed":
        arr = list(range(n, 0, -1))         # n, n-1, ..., 1
    else:
        raise ValueError(f"Bilinmeyen mode: {mode}")
    return arr


# --------------------------------------------------
# MergeSort (sayaçlı versiyon)
# --------------------------------------------------
def mergesort(arr, counters: Counters):
    """
    MergeSort algoritması (sayaçlı versiyon).
    Yeni bir sıralı liste döner, arr üzerinde çalışmaz (pure function gibi).

    Parametre:
        arr      : sıralanacak liste
        counters : Counters nesnesi, işlemleri saymak için
    """
    # Base case: 0 veya 1 elemanlı listeler zaten sıralıdır
    if len(arr) <= 1:
        return arr

    mid = len(arr) // 2
    left = mergesort(arr[:mid], counters)
    right = mergesort(arr[mid:], counters)

    # Merge aşaması
    return merge(left, right, counters)


def merge(left, right, counters: Counters):
    """
    İki sıralı listeyi (left, right) birleştirir.
    Sayaçlara:
        - comparisons: eleman karşılaştırmaları
        - assignments: merged'e eleman ekleme işlemleri
    olarak yansıtılır.
    """
    i = j = 0
    merged = []

    while i < len(left) and j < len(right):
        counters.comparisons += 1  # left[i] ? right[j] karşılaştırması

        if left[i] <= right[j]:
            merged.append(left[i])
            counters.assignments += 1  # merged'e eleman yazdık
            i += 1
        else:
            merged.append(right[j])
            counters.assignments += 1
            j += 1

    # Kalanları ekle
    while i < len(left):
        merged.append(left[i])
        counters.assignments += 1
        i += 1

    while j < len(right):
        merged.append(right[j])
        counters.assignments += 1
        j += 1

    return merged


# --------------------------------------------------
# QuickSort (Rastgele Pivot + İTERATİF + sayaçlı)
# --------------------------------------------------
def quicksort(arr, counters: Counters, low: int = None, high: int = None):
    """
    In-place QuickSort (dizi üzerinde yerinde değişim yapar).

    BU SÜRÜM İTERATİF’TİR (yığın kullanır, recursion yok).
    - Kendi stack yapımızı kullanıyoruz.
    - Böylece Python'un recursion limitine takılmayız.
    - Pivot yine rastgele seçilir (Randomized QuickSort).
    """
    if len(arr) == 0:
        return

    if low is None or high is None:
        low, high = 0, len(arr) - 1

    # Python çağrı yığını yerine kendi stack'imizi kullanıyoruz.
    stack = [(low, high)]

    while stack:
        l, h = stack.pop()
        if l < h:
            p = partition(arr, counters, l, h)

            # Daha küçük olan alt aralığı sona itmeyi tercih etmek
            # teoride stack kullanımını azaltabilir, ama burada basit tutuyoruz.
            # Sol taraf
            if p - 1 > l:
                stack.append((l, p - 1))
            # Sağ taraf
            if p + 1 < h:
                stack.append((p + 1, h))


def partition(arr, counters: Counters, low: int, high: int):
    """
    QuickSort'un partition (bölme) fonksiyonu.

    - Pivot: [low, high] aralığından RASTGELE seçilir.
      (Randomized QuickSort)
    - Pivot'tan küçükler sol tarafa, büyükler sağ tarafa toplanır.

    Sayaçlar:
        - comparisons: arr[j] ? pivot karşılaştırmaları
        - assignments: swap işlemleri ve pivot ataması
    """
    # 1) Rastgele pivot indeksi seç
    pivot_index = random.randint(low, high)

    # 2) Pivot elemanını sona (high) taşı (klasik partition şekli için)
    arr[pivot_index], arr[high] = arr[high], arr[pivot_index]
    counters.assignments += 3  # swap için 3 atama saydık

    # 3) Pivot değerini belirle
    pivot = arr[high]
    counters.assignments += 1  # pivot değişkene atandı

    i = low - 1

    for j in range(low, high):
        counters.comparisons += 1  # arr[j] ? pivot

        if arr[j] <= pivot:
            i += 1
            # swap(arr[i], arr[j])
            arr[i], arr[j] = arr[j], arr[i]
            counters.assignments += 3  # 3 atama (swap)

    # Pivot'u doğru yerine al
    arr[i + 1], arr[high] = arr[high], arr[i + 1]
    counters.assignments += 3

    return i + 1


# --------------------------------------------------
# Küçük doğrulama testi (isteğe bağlı)
# --------------------------------------------------
if __name__ == "__main__":
    """
    Bu blok, dosya DOĞRUDAN çalıştırıldığında (python3 algorithms.py)
    aşağıdaki denemeyi yapar:
        - n=20 elemanlı rastgele dizi üretir
        - MergeSort ve QuickSort ile sıralar
        - Süre, karşılaştırma ve atama sayılarını ekrana yazdırır
    """
    n = 20
    mode = "random"

    base_arr = generate_array(n, mode)
    print("Orijinal dizi:", base_arr)

    # MergeSort testi
    c_merge = Counters()
    arr_merge = base_arr.copy()
    start = time.perf_counter()
    sorted_merge = mergesort(arr_merge, c_merge)
    end = time.perf_counter()
    print("\n[MergeSort]")
    print("Sonuç:", sorted_merge)
    print("Süre (s):", end - start)
    print("Karşılaştırma:", c_merge.comparisons)
    print("Atama:", c_merge.assignments)

    # QuickSort testi
    c_quick = Counters()
    arr_quick = base_arr.copy()
    start = time.perf_counter()
    quicksort(arr_quick, c_quick)
    end = time.perf_counter()
    print("\n[QuickSort]")
    print("Sonuç:", arr_quick)
    print("Süre (s):", end - start)
    print("Karşılaştırma:", c_quick.comparisons)
    print("Atama:", c_quick.assignments)
