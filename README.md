# Nullfee Bot (Auto Register & Daily Swap)

Bot otomatis untuk platform **Nullfee.io** yang dilengkapi fitur Auto Register (dengan referral) dan Daily Swap untuk memvalidasi referral, beserta fitur Auto Spin Mystery Box dan integrasi Proxy.

## Fitur Utama
- **Auto Register:** Mendaftarkan banyak akun baru menggunakan kode referral milikmu secara bersamaan (concurrent).
- **Auto Mystery Box:** Memutar spin hadiah harian secara otomatis tepat setelah mendaftar untuk mencoba memenangkan saldo BNB.
- **Auto Daily Swap:** Melakukan *swap* otomatis terus-menerus menggunakan saldo virtual awal (modal $1000) hingga habis, untuk memvalidasi referral dan menyumbangkan komisi ke akun utama.
- **Proxy Support:** Menyamarkan IP dengan `proxies.txt` secara acak agar terhindar dari pemblokiran *Anti-Sybil*.
- **Async & Fast:** Menggunakan `aiohttp` dan `asyncio` untuk performa tinggi.

## Cara Penggunaan

1. **Install Requirements:**
   ```bash
   pip install aiohttp
   ```

2. **Siapkan Proxy (Opsional namun sangat disarankan):**
   Buat file bernama `proxies.txt` di folder yang sama, lalu isi dengan list proxy-mu (satu proxy per baris).
   Format: `http://user:pass@host:port`

3. **Jalankan Bot:**
   ```bash
   python nullfee.py
   ```

## Menu Bot
* **Menu 1 (Register Akun):** Bot akan meminta jumlah akun yang ingin dibuat, thread yang diinginkan, dan kode referral-mu. Akun-akun yang berhasil didaftarkan akan disimpan di file `result.json`. Jika ada akun yang memenangkan BNB dari Mystery Box, datanya akan disimpan di `bnbresult.txt`.
* **Menu 2 (Daily Swap):** Bot akan membaca data akun di `result.json` lalu melakukan login dan swap acak secara otomatis di masing-masing akun sampai saldonya habis agar referral-mu tervalidasi sebagai pengguna aktif.

## Catatan
- Sangat disarankan mengatur *Concurrency / Threads* pada kisaran 3-10 tergantung dari kualitas proxy yang digunakan untuk mencegah *Rate Limit* (429).
- Segala resiko penggunaan ditanggung oleh pengguna (DYOR).
