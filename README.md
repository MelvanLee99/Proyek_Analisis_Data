# Air Quality Analysis Dashboard

Proyek ini melakukan **Exploratory Data Analysis (EDA)** terhadap data
kualitas udara dan kondisi meteorologi di Beijing, dengan fokus pada
stasiun pemantauan **Changping**. Hasil analisis disajikan melalui
dashboard interaktif yang dibangun menggunakan **Streamlit**.

## 1. Gambaran Umum Proyek

Dataset berisi pengamatan kualitas udara per jam pada periode **1 Maret
2013 hingga 28 Februari 2017**. Dataset Changping memiliki 35.064 baris
observasi sebelum proses pembersihan.

Analisis berfokus pada: - Perubahan rata-rata konsentrasi PM2.5 setiap
bulan. - Hubungan PM2.5 dengan polutan lain, seperti PM10, CO, dan
NO2. - Hubungan konsentrasi polutan dengan variabel cuaca.

## 2. Struktur Direktori

Pastikan struktur proyek kurang lebih seperti berikut:

``` text
Proyek_Analisis_Data/
├── PRSA_Data_Changping_20130301-20170228.csv/
├── Proyek_Analisis_Data.ipynb
├── air_quality_changping_clean.csv
├── dashboard.py
├── requirements.txt
└── README.md
```

Dashboard menggunakan file `air_quality_changping_clean.csv`. Pastikan
file tersebut berada di lokasi yang sesuai dengan path yang digunakan
pada `dashboard.py`.

## 3. Persyaratan

Sebelum menjalankan dashboard, pastikan perangkat Anda telah memiliki: -
Python (disarankan Python 3.10 atau lebih baru). - pip untuk menginstal
library Python. - Koneksi internet untuk menginstal dependensi.

## 4. Cara Menjalankan Dashboard di Komputer Lokal

Ikuti langkah-langkah berikut dari terminal atau terminal VS Code.

### Langkah 1 --- Unduh repository

``` bash
git clone https://github.com/MelvanLee99/Proyek_Analisis_Data.git
cd Proyek_Analisis_Data
```

Jika repository sudah tersedia di komputer, buka terminal pada folder
proyek tersebut dan lanjutkan ke Langkah 2.

### Langkah 2 --- Buat virtual environment (disarankan)

**macOS / Linux:**

``` bash
python3 -m venv .venv
source .venv/bin/activate
```

**Windows:**

``` bash
python -m venv .venv
.venv\Scripts\activate
```

### Langkah 3 --- Instal library yang diperlukan

``` bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Langkah 4 --- Jalankan aplikasi Streamlit

Pastikan terminal berada di folder yang berisi `dashboard.py`, kemudian
jalankan:

``` bash
streamlit run dashboard.py
```

Setelah aplikasi berjalan, Streamlit akan menampilkan alamat lokal,
biasanya:

``` text
http://localhost:8501
```

Buka alamat tersebut melalui browser untuk menggunakan dashboard.

### Langkah 5 --- Menghentikan aplikasi

Untuk menghentikan dashboard, kembali ke terminal dan tekan:

``` text
Ctrl + C
```

## 5. Menjalankan Notebook Analisis

Notebook analisis tersedia pada file `Proyek_Analisis_Data.ipynb`. Buka
file tersebut menggunakan Visual Studio Code, Jupyter Notebook, atau
JupyterLab. Pastikan dependensi telah terinstal dan file dataset
tersedia pada path yang digunakan oleh notebook.

## 6. Ringkasan Hasil EDA

Berdasarkan hasil eksplorasi data Changping yang ditampilkan pada
notebook:

-   Rata-rata bulanan PM2.5 tertinggi yang teridentifikasi adalah
    **140,81 pada Februari 2014**.
-   Rata-rata bulanan PM2.5 terendah yang teridentifikasi adalah **36,67
    pada Agustus 2016**.
-   Korelasi Spearman PM2.5 dengan PM10 adalah **0,88**, menunjukkan
    hubungan monotonik positif yang kuat.
-   Korelasi Spearman PM2.5 dengan CO adalah **0,82**, juga menunjukkan
    hubungan positif yang kuat.
-   Korelasi Spearman PM2.5 dengan NO2 adalah **0,64**, menunjukkan
    hubungan positif.

Hasil korelasi merupakan hubungan statistik dan tidak dapat langsung
diartikan sebagai hubungan sebab-akibat.

## 7. Deployment Streamlit Community Cloud

Dashboard dapat dijalankan secara daring melalui Streamlit Community
Cloud.

1.  Pastikan `dashboard.py`, `requirements.txt`, dan
    `air_quality_changping_clean.csv` telah tersedia di repository
    GitHub.
2.  Buka [Streamlit Community Cloud](https://share.streamlit.io/).
3.  Pilih **Create app**.
4.  Pilih repository `MelvanLee99/Proyek_Analisis_Data`.
5.  Pilih branch `main`.
6.  Isi **Main file path** dengan `dashboard.py`.
7.  Klik **Deploy**.
8.  Setelah deployment berhasil, buka URL aplikasi yang diberikan
    Streamlit.

Jika URL dashboard diperlukan untuk pengumpulan proyek, tuliskan URL
publik tersebut di file `url.txt`.

## 8. Catatan

-   Gunakan path relatif pada `dashboard.py`, bukan path absolut yang
    hanya berlaku di komputer pribadi.
-   Pastikan nama file dataset pada kode sama persis dengan nama file di
    repository.
-   Pastikan semua library yang diimpor oleh `dashboard.py` tercantum
    dalam `requirements.txt`.
-   Jangan mengunggah virtual environment, password, API key, atau
    informasi rahasia ke repository GitHub.

## 9. Teknologi

-   Python
-   pandas
-   Streamlit
-   Library visualisasi dan analisis data yang tercantum pada
    `requirements.txt`
