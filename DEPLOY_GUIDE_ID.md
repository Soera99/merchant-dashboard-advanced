# Migrasi merchant-dashboard-advanced ke Cloud Run

Target repo GitHub: merchant-dashboard-advanced
Target service Cloud Run: advanced-merchant-dashboard
Region: asia-southeast2 (mengikuti URL dashboard pertama yang diberikan)

Paket ini dibuat berdasarkan ZIP merchant-dashboard-advanced-main yang diunggah.
ZIP tersebut berisi aplikasi Streamlit, bukan konfigurasi infra project pertama.
Project ID, nama Artifact Registry, service account, WIF, dan kebijakan akses
belum bisa diverifikasi. Tidak ada deploy ke GCP atau push ke GitHub dari sesi ini.

## 1. File yang disalin ke repo lokal

Ekstrak ISI paket ke root repo merchant-dashboard-advanced, sejajar dengan app.py:

- Dockerfile (baru): Python 3.12, proses non-root, port PORT/8080.
- .dockerignore (baru): hanya aplikasi, requirements, dan config yang masuk image.
- .github/workflows/deploy.yml (baru): build dan deploy via WIF tanpa kunci JSON.
- .streamlit/config.toml (diperbarui): tema asli dipertahankan; tambah server headless.
- .gitignore (diperbarui): aturan lama dipertahankan; tambah pengecualian secrets lokal.
- cloudrun.env.example.yaml (baru): template kosong karena aplikasi belum memakai env.
- DEPLOY_GUIDE_ID.md (baru): panduan ini.

app.py, requirements.txt dan README.md tidak diganti. Jika repo lokal sudah berubah
dibanding ZIP, gabungkan .gitignore dan config.toml; jangan timpa perubahan barumu.
Dockerfile memakai COPY eksplisit; jika nanti menambah modul Python/aset lokal,
tambahkan ke Dockerfile dan allowlist .dockerignore.

## 2. Setup satu kali oleh tim BE / infra

Gunakan project GCP dan Artifact Registry yang sama dengan dashboard pertama jika
sesuai kebijakan tim. Service Cloud Run baru harus advanced-merchant-dashboard.
Tidak perlu membuat project GCP baru atau mengubah free-merchant-dashboard.

Di GitHub repo BARU, buka Settings > Secrets and variables > Actions > Variables.
Tambahkan lima Repository Variables berikut. Workflow ini membaca vars, bukan secrets:

| Variable | Nilai dari tim BE |
| --- | --- |
| GCP_PROJECT_ID | Project ID, bukan project number 735112988988 |
| GCP_ARTIFACT_REPOSITORY | Nama repository Docker Artifact Registry di asia-southeast2 |
| GCP_WI_PROVIDER | projects/PROJECT_NUMBER/locations/global/workloadIdentityPools/POOL/providers/PROVIDER |
| GCP_SERVICE_ACCOUNT | Email service account untuk deploy GitHub Actions |
| GCP_RUNTIME_SERVICE_ACCOUNT | Email service account runtime Cloud Run dengan izin minimum |

Salin nilai yang relevan dari setup project pertama. Jika setup lama menyimpan
nilai-nilai ini sebagai GitHub Secrets, masukkan sebagai Variables atau ubah referensi
workflow dari vars.NAMA menjadi secrets.NAMA secara konsisten.
Runtime SA dan deployment SA berbeda fungsi. Hindari memakai SA deploy sebagai runtime.

Tim BE perlu memeriksa:

1. Billing aktif; API run.googleapis.com, artifactregistry.googleapis.com,
   iamcredentials.googleapis.com dan sts.googleapis.com tersedia.
2. Artifact Registry Docker di region target sudah dibuat.
3. WIF provider mempercayai repo OWNER/merchant-dashboard-advanced. Kebijakan yang
   sebelumnya hanya mengizinkan merchant-insights-v2 tidak otomatis menerima repo baru.
   Batasi ke organisasi/repo dan branch main; jangan membuka trust ke seluruh GitHub.
4. Principal WIF repo baru punya roles/iam.workloadIdentityUser pada deployment SA.
5. Deployment SA punya roles/artifactregistry.writer pada repository target,
   roles/run.developer pada project/layanan yang sesuai (pembuatan layanan baru
   memerlukan izin pada project), dan roles/iam.serviceAccountUser pada runtime SA.
6. Runtime SA tersedia. App demo tidak butuh akses database/Secret Manager saat ini.
7. Tidak ada pipeline infra/Terraform lain yang menimpa min instances atau konfigurasi
   service ini. Jika infra dikelola Terraform, selaraskan perubahan pada source infra.

Workflow sengaja tidak mengubah IAM/public access. Layanan Cloud Run yang baru dibuat
biasanya private. Setelah deploy pertama, BE menentukan akses sebelum iframe digunakan.

Untuk DEMO berisi data contoh ini, jika kebijakan perusahaan mengizinkan akses publik,
admin BE dapat menjalankan perintah berikut sekali (ganti YOUR_PROJECT_ID):

```bash
gcloud run services add-iam-policy-binding advanced-merchant-dashboard \
  --project YOUR_PROJECT_ID \
  --region asia-southeast2 \
  --member=allUsers \
  --role=roles/run.invoker
```

Jika organisasi melarang allUsers, gunakan pola akses resmi tim (gateway/proxy atau
mekanisme Cloud Run publik yang disetujui admin). Jangan menghapus kebijakan organisasi.
Iframe browser biasa tidak otomatis mengirim token IAM Cloud Run. Login pada web
partner juga tidak otomatis melindungi URL Streamlit. Sebelum memakai data merchant
asli, BE harus memvalidasi sesi/token dan otorisasi merchant pada sisi server.
Parameter embed=true dan CORS bukan kontrol akses. Pertahankan CORS dan XSRF aktif;
jika embedding mengalami error, periksa WebSocket, origin, CSP, dan cookies dahulu.
Untuk membatasi domain yang boleh memuat frame, tim dapat menerapkan CSP frame-ancestors
pada gateway/proxy. Sesuaikan juga CSP frame-src pada web partner bila diperlukan.

## 3. Commit dan push dari GitHub Desktop

1. Pilih repo merchant-dashboard-advanced > Repository > Show in Explorer/Finder.
2. Tampilkan hidden files agar .github, .streamlit, .gitignore, .dockerignore terlihat.
3. Salin isi ZIP ke root repo. Jangan buat subfolder tambahan di antara root dan Dockerfile.
4. Review Changes. Dari snapshot unggahan: 5 file baru dan 2 file diperbarui (7 total).
   Perubahan lokal lain dapat membuat jumlah berbeda. Tidak perlu menyalin app.py baru.
5. Summary commit: Add Cloud Run deployment for advanced merchant dashboard.
6. Commit to main, lalu Push origin. Jika default branch bukan main, sesuaikan
   branches pada workflow; workflow_dispatch tersedia juga.
7. Buka GitHub > Actions > Deploy advanced merchant dashboard.
   Jika variables belum diisi, workflow berhenti dengan pesan Missing repository
   Actions variable. Lengkapi setup BE dan pilih Run workflow / Re-run jobs.
8. Setelah sukses, buka Summary untuk mendapatkan Cloud Run service URL yang sebenarnya.
   Workflow tidak mematikan Streamlit Community Cloud atau mengganti iframe web pertama.

## 4. Always ready dan batas koneksi

Workflow memakai service-level --min 1 agar Cloud Run mempertahankan minimal satu
instance siap menerima request saat idle. Min 0 masih melayani request otomatis,
tetapi dapat membutuhkan cold start. Ini berbeda dengan halaman sleep Community Cloud.
Min 1 menimbulkan biaya idle; bukan jaminan uptime 100%, dan instance tetap bisa restart.

Setting awal: 1 vCPU, RAM 1 GiB, concurrency 20, max 2 instances, session affinity aktif,
request timeout 3600 detik. Ini titik awal; BE perlu menyesuaikan setelah uji beban.
Cloud Run membatasi koneksi WebSocket maksimal 60 menit. Uji reconnect Streamlit saat
koneksi berakhir; filter/session_state mungkin reset setelah restart atau pindah instance.
Session affinity bersifat best effort, bukan jaminan state tersimpan.
Data/cache memori dan filesystem container tidak bersifat persisten. Ketika nanti ada
data nyata, gunakan API/database dan penyimpanan eksternal yang sesuai.

## 5. URL dan iframe

Dapatkan URL sebenarnya dari GitHub Actions Summary atau Cloud Run Console.
Bisa juga lewat terminal BE:

```bash
gcloud run services describe advanced-merchant-dashboard \
  --project YOUR_PROJECT_ID \
  --region asia-southeast2 \
  --format='value(status.url)'
```

Tempel nilai URL tersebut pada src iframe. Contoh dengan placeholder:

```html
<iframe
  src="CLOUD_RUN_SERVICE_URL/?embed=true&embed_options=light_theme"
  title="Advanced Merchant Dashboard"
  loading="lazy"
  style="width: 100%; height: 1200px; border: 0;"
></iframe>
```

Jika BE mengonfirmasi project number tetap 735112988988 dan URL pola tersebut tersedia,
kandidat URL-nya adalah:
https://advanced-merchant-dashboard-735112988988.asia-southeast2.run.app
Tetap gunakan status.url dari layanan aktual sebagai rujukan utama.

## 6. Uji setelah deploy

- Buka URL service langsung: halaman dan chart muncul, tidak ada traceback.
- Cek /_stcore/health memberikan respons ok.
- Uji semua tab, filter, map, dan fitur interaktif pada halaman partner yang sebenarnya.
- Cek WebSocket /_stcore/stream berhasil terhubung (HTTP 101 di DevTools Network).
- Coba mode incognito dan browser partner; periksa CSP/cookies jika iframe kosong.
- Biarkan idle, akses lagi, dan periksa min instances tetap 1 di Cloud Run.
- Biarkan sesi terbuka >60 menit untuk menguji reconnect dan perilaku session state.
- Periksa log error, memory, latency, dan biaya pada Cloud Run/Monitoring.

## 7. Kondisi aplikasi yang diunggah

load_dashboard_data() masih adapter demo dengan nilai contoh. Tidak ada st.secrets,
os.environ atau koneksi API/database di app.py. Tidak perlu menyalin secrets project
pertama dan tidak perlu membuat .env.cloudrun.yaml untuk versi ini. Template env tidak
otomatis diterapkan oleh workflow. Migrasi hosting tidak membuat data menjadi live.

## 8. Verifikasi paket dan sumber

Dilakukan di lingkungan penyusunan: kompilasi sintaks Python, parsing YAML workflow dan
TOML, pemeriksaan tema asli/aturan gitignore tetap ada, serta pengecekan isi ZIP.
Build Docker, eksekusi Streamlit, GitHub Actions dan deploy GCP belum diuji karena
Docker/Streamlit dan akses akun infra tidak tersedia di lingkungan ini.
requirements.txt tetap memakai rentang versi asli; untuk build lebih reproducible,
tim dapat mengunci versi setelah uji runtime pada image yang dibangun.

Referensi resmi:
- https://docs.cloud.google.com/run/docs/configuring/min-instances
- https://docs.cloud.google.com/run/docs/triggering/websockets
- https://docs.streamlit.io/deploy/tutorials/docker
- https://docs.streamlit.io/develop/api-reference/configuration/config.toml
- https://github.com/google-github-actions/auth
- https://github.com/google-github-actions/setup-gcloud
