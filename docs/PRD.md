# EdgeFlow — Product Requirement Document (PRD)

**Version:** 1.0
**Status:** Draft — Foundation
**Last Updated:** 2026-07-14

---

## 1. Ringkasan Eksekutif

EdgeFlow adalah **Trading Discipline Operating System** — sistem yang membantu trader mengeksekusi hanya setup berkualitas tinggi dengan menegakkan aturan trading secara objektif, mengelola risiko otomatis, dan mengurangi keputusan berbasis emosi.

EdgeFlow **bukan** signal provider, **bukan** "AI yang menebak arah market", dan **bukan** bot auto-profit. EdgeFlow adalah asisten eksekusi yang menegakkan disiplin trader terhadap sistem yang sudah mereka pilih (SMC / EMA).

---

## 2. Problem Statement

Mayoritas trader ritel gagal bukan karena strategi yang buruk, tapi karena **eksekusi yang tidak konsisten**:

| Masalah | Dampak |
|---|---|
| FOMO entry | Masuk posisi sebelum konfirmasi lengkap |
| Revenge trading | Overtrade setelah loss untuk "balik modal" |
| Entry tanpa konfirmasi | Setup belum valid tapi tetap dieksekusi |
| Risk sizing sembarangan | Position size tidak konsisten dengan balance/risk plan |
| Memindahkan Stop Loss | Membiarkan loss membesar di luar rencana |
| Overtrading | Volume trading tidak proporsional dengan kualitas setup yang tersedia |

Produk lain di pasar (signal provider, EA auto-trade) **tidak menyelesaikan** masalah ini — mereka justru menghilangkan proses berpikir trader, bukan melatihnya. EdgeFlow mengambil posisi berbeda: **menegakkan aturan trader sendiri**, bukan menggantikan keputusannya.

---

## 3. Target User

**Primary persona:**
- Trader ritel yang sudah punya strategi (SMC/ICT atau trend-following EMA) tapi kesulitan konsisten menjalankannya
- Trader prop firm / FTMO-style challenge yang butuh kepatuhan ketat terhadap risk rules untuk lolos evaluasi
- Gold/XAUUSD scalper dan trader forex major pairs
- Crypto trader (BTC/ETH dan pair likuid lainnya)

**Karakteristik umum:**
- Sudah paham dasar strategi (bukan pemula total)
- Punya modal trading aktif (live atau demo prop firm)
- Frustrasi dengan performa yang tidak konsisten meski strategi "sebenarnya bagus di atas kertas"

**Bukan target:**
- Orang yang mencari "profit pasti"/"auto cuan" tanpa usaha
- Trader yang ingin sistem full-otomatis tanpa keterlibatan keputusan sama sekali (di v1)

---

## 4. Goals & Success Metrics

### Goals (v1)
1. User bisa menjalankan strategi SMC atau EMA di market crypto dan/atau forex dengan checklist objektif sebelum entry.
2. Sistem mencegah entry yang melanggar rule mandatory (mandatory rule FALSE = tidak bisa entry).
3. Risk per trade dihitung otomatis, konsisten dengan risk plan yang ditetapkan.
4. Setiap trade tercatat otomatis ke journal tanpa effort tambahan dari user.
5. User punya visibilitas ke pola perilakunya sendiri (analytics) setelah cukup data.

### Success Metrics
- **Adherence rate**: persentase trade yang dieksekusi sesuai checklist penuh (target >90% untuk user aktif setelah 30 hari pakai)
- **Reduction in rule violations**: penurunan jumlah trade "di luar sistem" dari waktu ke waktu (dibandingkan self-report user atau deteksi trade manual di luar EdgeFlow, jika terhubung ke akun exchange/broker)
- **Retention**: user aktif menggunakan checklist minimal 3x/minggu setelah bulan pertama
- **Conversion free → paid**: dari trial/free tier ke subscription berbayar

---

## 5. Product Scope — v1

### In Scope
- Market: **Crypto (multi-exchange)** dan **Forex** — user pilih salah satu atau keduanya sesuai subscription
- Strategi: **SMC** dan **EMA** (lihat `EdgeFlow-Strategy-Specification-v1.0.md`)
- Mode eksekusi: **Semi-auto** — sistem generate checklist + hitung risk, user yang konfirmasi eksekusi final
- Risk Engine: position sizing otomatis, daily loss limit, max trade per hari
- Trade Journal: auto-log setiap trade
- Analytics dasar: win rate per strategi/session/pair
- Notifikasi: Telegram, Discord, Web push
- Subscription: Free (terbatas), Pro (crypto atau forex), Bundle (keduanya)

### Out of Scope (v1)
- Full-auto execution tanpa konfirmasi user (ditunda ke v3+)
- Strategy Builder custom (drag-and-drop) — v2
- Backtesting engine — v2
- AI Coach — v3
- Mobile native app — v4
- Strategi selain SMC & EMA

---

## 6. Fitur Utama (mapping ke Strategy Spec & Roadmap)

| Fitur | Deskripsi Singkat | Referensi |
|---|---|---|
| Global Market Filter | Cek session, spread, news, volatilitas sebelum evaluasi strategi | Strategy Spec §2 |
| SMC Checklist | Evaluasi bias, liquidity sweep, BOS/CHoCH, FVG, OB, session, RR | Strategy Spec §3 |
| EMA Checklist | Evaluasi trend filter, pullback, confirmation candle, RR | Strategy Spec §4 |
| Score Engine | Skor 0-100 per setup dengan rekomendasi (A+/A/B/Reject) | Strategy Spec §5 |
| Risk Calculator | Hitung lot/size, SL, TP otomatis dari risk % dan balance | Strategy Spec §6 |
| Discipline Lock | Daily loss limit, max trade/hari, cooldown setelah loss beruntun | Strategy Spec §6, Roadmap Phase 6 |
| Semi-Auto Executor | User konfirmasi 1x klik, order terbuka dengan parameter benar | Roadmap Phase 9 |
| Trade Journal | Auto-save data trade + field manual (emosi, catatan) | Roadmap Phase 11 |
| Analytics Dashboard | Win rate, R-multiple, pola pelanggaran aturan | Roadmap Phase 12 |
| Notification Center | Telegram/Discord/Email/Push | Roadmap Phase 13 |

---

## 7. Non-Functional Requirements

- **Latency**: signal dari deteksi ke notifikasi user < 5 detik (crypto), < 10 detik (forex, tergantung provider)
- **Reliability**: uptime data feed >99% selama jam trading aktif (killzone London/NY untuk forex; 24/7 untuk crypto)
- **Security**: API key exchange/broker milik user dienkripsi at-rest, tidak pernah di-log dalam bentuk plaintext
- **Auditability**: setiap keputusan sistem (entry allowed/blocked) harus bisa ditelusuri alasannya (explainability sesuai Rule Philosophy di Strategy Spec §1)
- **Scalability**: arsitektur harus mendukung penambahan strategi & exchange baru tanpa mengubah core (lihat Architecture Document)

---

## 8. Compliance & Risk Considerations

- EdgeFlow **tidak memberikan jaminan profit** dalam bentuk apa pun. Semua komunikasi marketing/produk harus menghindari klaim seperti "profit dijamin", "winrate 90%", "auto cuan".
- Positioning yang aman secara legal dan etis: *"Helps you follow your trading plan"*, *"Reduce emotional trading"*, *"Never miss your checklist again"*.
- EdgeFlow tidak memberikan rekomendasi investasi personal — checklist dan score adalah hasil evaluasi rule objektif terhadap strategi yang **dipilih user sendiri**, bukan saran dari EdgeFlow tentang apa yang harus ditradingkan.
- Untuk fitur eksekusi (semi-auto), user tetap pemegang keputusan akhir — EdgeFlow tidak boleh mengeksekusi order tanpa konfirmasi eksplisit dari user di v1.
- Penyimpanan API key trading pihak ketiga (exchange/broker) harus mengikuti best practice keamanan (enkripsi, scope permission minimal — read + trade only, tanpa withdrawal permission).

---

## 9. Assumptions & Risks

| Assumption/Risk | Mitigasi |
|---|---|
| Data provider (OANDA/exchange) API bisa berubah kebijakan/harga | Desain Market Adapter Layer agar provider bisa diganti tanpa ubah core |
| Definisi rule SMC bisa jadi kontroversial (beda mentor beda definisi) | Strategy Spec eksplisit + parameter configurable, transparan ke user |
| User mengandalkan sistem secara berlebihan (over-reliance) | UX harus tetap menekankan "assistant", bukan "decision maker" |
| Kompleksitas multi-exchange crypto | Gunakan abstraction layer (CCXT-style) dari awal, bukan ditambah belakangan |

---

## Changelog

| Version | Date | Changes |
|---|---|---|
| 1.0 | 2026-07-14 | Initial PRD |
