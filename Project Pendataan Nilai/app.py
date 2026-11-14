from flask import Flask, render_template, request, redirect, url_for, Response
import csv
import io

app = Flask(__name__)

# Penyimpanan data sementara di memori
daftar_nilai = []

# Skala Penilaian Resmi SIAKAD UNJ
def hitung_konversi_unj(nilai_akhir):
    if 86 <= nilai_akhir <= 100:
        return "A", 4.0, "Sangat Baik"
    elif 81 <= nilai_akhir < 86:
        return "A-", 3.7, "Hampir Sangat Baik"
    elif 76 <= nilai_akhir < 81:
        return "B+", 3.3, "Lebih dari Baik"
    elif 71 <= nilai_akhir < 76:
        return "B", 3.0, "Baik"
    elif 66 <= nilai_akhir < 71:
        return "B-", 2.7, "Hampir Baik"
    elif 61 <= nilai_akhir < 66:
        return "C+", 2.3, "Lebih dari Cukup"
    elif 56 <= nilai_akhir < 61:
        return "C", 2.0, "Cukup"
    elif 51 <= nilai_akhir < 56:
        return "C-", 1.7, "Hampir Cukup"
    elif 46 <= nilai_akhir < 51:
        return "D", 1.0, "Kurang"
    else:
        return "E", 0.0, "Gagal"

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        nim = request.form.get("nim").strip()
        nama = request.form.get("nama").strip()
        mata_kuliah = request.form.get("mata_kuliah").strip()
        
        # Komponen nilai standar perkuliahan
        tugas = float(request.form.get("tugas", 0))
        uts = float(request.form.get("uts", 0))
        uas = float(request.form.get("uas", 0))
        praktikum = float(request.form.get("praktikum", 0))

        # Bobot nilai (Tugas 20%, Praktikum 20%, UTS 30%, UAS 30%)
        nilai_akhir = round((tugas * 0.20) + (praktikum * 0.20) + (uts * 0.30) + (uas * 0.30), 2)
        huruf, bobot, predikat = hitung_konversi_unj(nilai_akhir)

        daftar_nilai.append({
            "nim": nim,
            "nama": nama,
            "mata_kuliah": mata_kuliah,
            "tugas": tugas,
            "praktikum": praktikum,
            "uts": uts,
            "uas": uas,
            "nilai_akhir": nilai_akhir,
            "huruf": huruf,
            "bobot": bobot,
            "predikat": predikat
        })
        return redirect(url_for("index"))

    # Statistik kelas untuk dashboard
    total_mhs = len(daftar_nilai)
    rata_kelas = round(sum(d["nilai_akhir"] for d in daftar_nilai) / total_mhs, 2) if total_mhs > 0 else 0
    lulus = sum(1 for d in daftar_nilai if d["bobot"] >= 2.0)

    return render_template(
        "index.html",
        daftar_nilai=daftar_nilai,
        total_mhs=total_mhs,
        rata_kelas=rata_kelas,
        lulus=lulus
    )

@app.route("/hapus/<int:index>")
def hapus(index):
    if 0 <= index < len(daftar_nilai):
        daftar_nilai.pop(index)
    return redirect(url_for("index"))

@app.route("/ekspor-csv")
def ekspor_csv():
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["NIM", "Nama Mahasiswa", "Mata Kuliah", "Tugas (20%)", "Praktikum (20%)", "UTS (30%)", "UAS (30%)", "Nilai Akhir", "Grade", "Bobot", "Predikat"])
    
    for d in daftar_nilai:
        writer.writerow([
            d["nim"], d["nama"], d["mata_kuliah"],
            d["tugas"], d["praktikum"], d["uts"], d["uas"],
            d["nilai_akhir"], d["huruf"], d["bobot"], d["predikat"]
        ])
    
    output.seek(0)
    return Response(
        output,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=Rekap_Nilai_Teknik_Mesin_UNJ.csv"}
    )

if __name__ == "__main__":
    app.run(debug=True)