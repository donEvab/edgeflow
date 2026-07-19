# EdgeFlow — System Architecture Document

**Version:** 1.0
**Status:** Draft — Foundation
**Last Updated:** 2026-07-14

---

## 1. Prinsip Arsitektur

1. **Strategy sebagai config, bukan hardcode** — SMC/EMA/strategi masa depan adalah data yang dijalankan Rule Engine generik.
2. **Market-agnostic core** — Strategy Engine, Discipline Engine, Risk Engine tidak boleh tahu apakah data berasal dari crypto atau forex. Normalisasi terjadi di Market Adapter Layer.
3. **Modular, bukan monolith** — tiap engine adalah package terpisah dengan interface jelas, bisa di-develop, di-test, dan di-versionkan independen.
4. **Explainability by design** — setiap keputusan (entry allowed/blocked) harus punya trace alasan yang bisa ditampilkan ke user.
5. **User tetap pemegang kontrol eksekusi** (v1) — sistem tidak pernah membuka order tanpa konfirmasi eksplisit.
6. **Versioning dari hari pertama** — API versioned (`/api/v1/...`), rule versioned, database migration terkontrol.

---

## 2. High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                          CLIENT LAYER                           │
│     Web Dashboard (Next.js)   │   Telegram/Discord Bot           │
└────────────────────────────┬──────────────────────────────────────┘
                              │  REST + WebSocket
┌────────────────────────────▼──────────────────────────────────────┐
│                     API GATEWAY / BFF (FastAPI)                  │
│         Auth · Rate limit · Request routing · API versioning     │
└───────┬───────────┬───────────────┬───────────────┬────────────────┘
        ▼            ▼               ▼               ▼
┌───────────────┐┌──────────────┐┌───────────────┐┌──────────────┐
│ STRATEGY       ││ DISCIPLINE    ││ JOURNAL &      ││ NOTIFICATION │
│ ENGINE         ││ ENGINE        ││ ANALYTICS      ││ SERVICE      │
│ (Rule Engine   ││ (limit, lock, ││                ││              │
│  + plugin cfg) ││  cooldown)    ││                ││              │
└───────┬────────┘└──────┬────────┘└───────┬────────┘└──────┬───────┘
        │                │                 │                │
        └────────────────┴────────┬────────┴────────────────┘
                                   ▼
                     ┌──────────────────────────┐
                     │   ENTITLEMENT SERVICE      │
                     │ (subscription → market/    │
                     │  strategy access)           │
                     └─────────────┬───────────────┘
                                   ▼
                     ┌──────────────────────────┐
                     │      CORE DATA LAYER        │
                     │  PostgreSQL (state, rules,  │
                     │  journal) + Redis (cache,   │
                     │  queue) + Timeseries store  │
                     │  (candles)                   │
                     └─────────────┬───────────────┘
                                   ▼
                     ┌──────────────────────────┐
                     │   MARKET ADAPTER LAYER       │
                     │  normalisasi data multi-market│
                     └──────┬────────────────┬─────┘
                            ▼                ▼
                  ┌──────────────────┐ ┌──────────────────┐
                  │ CRYPTO ADAPTERS    │ │  FOREX ADAPTER     │
                  │ (per exchange,      │ │  (OANDA v20 API)    │
                  │  via CCXT-style     │ │                     │
                  │  abstraction)       │ │                     │
                  │  - Binance          │ │                     │
                  │  - Bybit            │ │                     │
                  │  - OKX (dst.)       │ │                     │
                  └──────────────────┘ └──────────────────┘
                            │                │
                  (v1: semi-auto, guarded)   │
                            ▼                ▼
                     ┌──────────────────────────┐
                     │      EXECUTION LAYER        │
                     │ (order placement setelah     │
                     │  konfirmasi user)             │
                     └──────────────────────────┘
```

---

## 3. Komponen Utama

### 3.1 Market Adapter Layer

Tanggung jawab: menormalisasi data dari berbagai sumber (exchange crypto, broker forex) ke format standar sebelum masuk ke Indicator/Strategy Engine.

```
NormalizedCandle {
  market: "crypto" | "forex"
  provider: string          // "binance", "bybit", "oanda"
  symbol: string             // "BTCUSDT" atau "EURUSD"
  timeframe: string
  ohlcv: { open, high, low, close, volume }
  timestamp: ISO8601
}
```

**Crypto Adapters** — dibangun di atas abstraksi ala CCXT supaya menambah exchange baru = menambah konfigurasi, bukan tulis ulang integrasi WS/REST dari nol. Tiap adapter implement interface yang sama:

```
ExchangeAdapter {
  connect()
  subscribeCandles(symbol, timeframe) → stream<NormalizedCandle>
  fetchOrderBook(symbol)
  placeOrder(params) → OrderResult
  getBalance()
}
```

**Forex Adapter (OANDA)** — menggunakan v20 REST API untuk data harga + eksekusi order dalam satu integrasi. Perlu penanganan khusus untuk:
- Session/weekend closed handling (market forex tidak 24/7)
- Rate limit API
- Practice vs live account environment

### 3.2 Indicator Engine

Package murni fungsi matematis/statistik — EMA, ATR, swing detection, equal high/low, BOS, CHoCH, FVG, Order Block. Tidak tahu apa-apa soal strategi atau user. Input: `NormalizedCandle[]`. Output: nilai objektif per indikator, sesuai definisi di Strategy Specification.

### 3.3 Rule Engine

Evaluator generik yang menjalankan config JSON (lihat Strategy Spec §7). Mendukung:
- Operator perbandingan (`>`, `<`, `==`, dst)
- Composite condition (`AND`/`OR`/`NOT`)
- Mandatory vs optional rule
- Scoring per rule

Rule Engine **tidak tahu** apakah dia sedang mengevaluasi SMC atau EMA — dia hanya menjalankan apa pun yang didefinisikan di config.

### 3.4 Strategy Engine

Layer tipis di atas Rule Engine yang memuat config SMC/EMA, menjalankannya terhadap data ternormalisasi, dan menghasilkan:

```
SignalCandidate {
  strategyId, version, market, symbol, direction,
  checklist: [{ ruleId, passed, reason }],
  score, recommendation,
  entryZone, stopLoss, takeProfit,
  timestamp
}
```

### 3.5 Discipline Engine

Menerima `SignalCandidate` dan mengecek terhadap state user:
- Daily loss limit tercapai?
- Max trade/hari tercapai?
- Sedang dalam cooldown setelah loss streak?
- SL-lock aktif untuk posisi terbuka?

Kalau lolos semua → signal diteruskan ke Risk Engine lalu Notification Service. Kalau tidak → signal tetap disimpan (untuk analytics "setup bagus yang di-skip karena limit") tapi tidak dikirim sebagai actionable alert.

### 3.6 Risk Engine

Menghitung position size, SL, TP berdasarkan balance user, risk %, dan jarak SL dari `SignalCandidate`. Formula di Strategy Spec §6.

### 3.7 Entitlement Service

Middleware yang dicek sebelum signal dikirim ke user — memastikan user hanya menerima signal dari market yang mereka subscribe (crypto/forex/bundle) dan strategi yang tercakup dalam plan mereka.

### 3.8 Execution Layer (Semi-Auto)

Setelah user menekan konfirmasi (di web atau bot), Execution Layer memanggil `placeOrder()` ke adapter yang sesuai (exchange crypto atau OANDA), dengan parameter yang sudah dihitung Risk Engine. Order lifecycle (modify, close, cancel) juga lewat layer ini.

### 3.9 Journal & Analytics

Journal mencatat setiap `SignalCandidate` yang jadi trade nyata (plus yang di-skip, untuk insight). Analytics mengagregasi data ini menjadi win rate, R-multiple, pola per session/pair/strategi.

### 3.10 Notification Service

Jalur pengiriman murni (Telegram, Discord, Email, Web Push) — tidak ada business logic di sini, hanya format & delivery.

---

## 4. Tech Stack

| Layer | Pilihan | Alasan |
|---|---|---|
| Frontend | Next.js + Tailwind + shadcn/ui | Ekosistem matang, SSR untuk dashboard real-time |
| Backend | FastAPI (Python) | Async native, cocok untuk data real-time & integrasi ML/AI di v3 |
| Database | PostgreSQL | Relasional kuat untuk state user, rules, journal |
| Cache/Queue | Redis | Cache market data + message queue untuk event-driven signal pipeline |
| Timeseries | TimescaleDB (extension Postgres) atau InfluxDB | Simpan candle history efisien untuk backtesting v2 |
| Auth | Clerk atau Supabase Auth | Cepat diimplementasi, mendukung OAuth |
| Charts | TradingView Lightweight Charts (awal) → Charting Library (jika perlu) | Ringan, cukup untuk MVP |
| Crypto Data/Execution | CCXT-style abstraction per exchange | Multi-exchange dari awal tanpa reinvent wheel |
| Forex Data/Execution | OANDA v20 REST API | Data + eksekusi dalam satu API, dokumentasi kuat |
| Deployment | Docker + VPS (atau managed container platform) | Portabilitas, mudah scale horizontal per service |
| Monitoring | Sentry (error tracking) + uptime monitoring | Observability sejak awal |

---

## 5. Data Flow — Contoh Alur Signal SMC (Crypto)

```
1. Binance Adapter menerima candle baru (WS) → normalisasi → NormalizedCandle
2. Indicator Engine hitung EMA200, swing high/low, dll dari candle terbaru
3. Strategy Engine load config "smc_v1", jalankan via Rule Engine
4. Rule Engine evaluasi tiap rule → hasil TRUE/FALSE + score
5. Jika mandatory rules semua TRUE → SignalCandidate terbentuk
6. Discipline Engine cek state user (daily limit, cooldown)
7. Jika lolos → Risk Engine hitung lot/SL/TP
8. Entitlement Service cek user subscribe ke crypto? SMC?
9. Notification Service kirim ke Telegram/Web dengan checklist + risk calc
10. User konfirmasi → Execution Layer → Binance Adapter placeOrder()
11. Order terbuka → Journal auto-save entry
12. Setelah close (TP/SL/manual) → Journal update result → Analytics terupdate
```

---

## 6. Versioning Strategy

- **API**: `/api/v1/...` sejak awal, breaking change → `/api/v2/...` paralel selama masa transisi.
- **Strategy config**: tiap strategi punya `version` sendiri (`smc_v1`, `smc_v1.1`). Rule lama tidak dihapus — di-deprecate, supaya data historis/journal tetap bisa dijelaskan oleh definisi rule yang berlaku saat trade itu terjadi.
- **Database**: migration terkontrol (Alembic untuk FastAPI/Postgres), setiap migration reversible.
- **Feature flag**: fitur baru (misal AI Coach di v3) di-rollout bertahap tanpa mengganggu user existing.
- **Exchange/Broker adapter**: masing-masing adalah plugin independen — menambah exchange baru tidak menyentuh Strategy Engine atau Discipline Engine sama sekali.

---

## 7. Security Considerations

- API key exchange/broker milik user: **dienkripsi at-rest** (misal AES-256), tidak pernah muncul di log dalam bentuk plaintext.
- Permission API key yang diminta ke user: **read + trade only**, eksplisit tanpa permission withdrawal.
- Rate limiting di API Gateway untuk mencegah abuse.
- Audit log untuk setiap aksi eksekusi order (siapa, kapan, parameter apa) — penting untuk trust & debugging.

---

## 8. Architecture Decision Records (ADR) — Ringkasan Keputusan Kunci

| # | Keputusan | Alasan |
|---|---|---|
| ADR-001 | Mode eksekusi v1 = semi-auto, bukan full-auto | Tujuan produk melatih disiplin, bukan menggantikan keputusan trader |
| ADR-002 | Strategy sebagai config JSON dijalankan Rule Engine generik | Menambah strategi baru tidak mengubah core code |
| ADR-003 | Market Adapter Layer untuk normalisasi crypto+forex | Strategy/Discipline/Risk Engine tetap market-agnostic |
| ADR-004 | OANDA sebagai provider forex utama | Data + eksekusi dalam satu API, dokumentasi kuat, demo account gratis |
| ADR-005 | CCXT-style abstraction untuk crypto multi-exchange | Standarisasi integrasi, menghindari reinvent wheel per exchange |

*(ADR detail penuh — konteks, alternatif yang dipertimbangkan, konsekuensi — akan didokumentasikan terpisah di `docs/adr/` seiring project berjalan.)*

---

## Changelog

| Version | Date | Changes |
|---|---|---|
| 1.0 | 2026-07-14 | Initial architecture document |
