satuan = ('Nol', 'Satu', 'Dua', 'Tiga', 'Empat', 'Lima', 'Enam', 'Tujuh', 'Delapan', 'Sembilan')
suffix = ((1000000000000, "trilyun"),
          (1000000000, "milyar"),
          (1000000, "juta"),
          (1000, "ribu"),
          (100, "ratus"),
          (10, "puluh"))


def find_first(predicate, items):
    hasil = list(filter(predicate, items))
    return hasil[0] if len(hasil) > 0 else None


def terbilang(angka):
    if angka < 0:
        return "negatif " + terbilang(abs(angka)).strip()
    elif 0 <= angka <= 9:
        return satuan[int(angka)]
    elif 11 <= angka <= 19:
        return "{} belas".format(satuan[angka % 10]).replace("Satu belas", "Sebelas").strip()
    else:
        pos, batas = find_first(lambda x: angka >= x[1][0], enumerate(suffix))
        if batas is not None:
            return "{} {} {}".format(terbilang(int(angka / batas[0])), suffix[pos][1],
                                     terbilang(angka % batas[0]) if angka % batas[0] > 0 else "")\
                .replace("Satu puluh", "Sepuluh")\
                .replace("Satu ratus", "Seratus")\
                .replace("Satu ribu", "Seribu").strip()
        else:
            return ""