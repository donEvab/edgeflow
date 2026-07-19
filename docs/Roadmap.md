# EdgeFlow — Roadmap

**Product Vision:** *EdgeFlow helps traders execute only high-quality setups by enforcing objective trading rules, managing risk automatically, and eliminating emotional decisions.*

EdgeFlow bukan signal provider. Bukan "auto profit bot". EdgeFlow adalah **Trading Discipline Operating System**.

**Scope v1:** Multi-market (Crypto + Forex), strategi SMC + EMA, mode **semi-auto** (checklist → alert → user konfirmasi eksekusi). Full-auto execution sengaja ditunda ke v3+ sebagai fitur terpisah dengan guardrail ketat — karena tujuan produk adalah melatih disiplin, bukan menggantikan keputusan trader sepenuhnya.

Prinsip pengerjaan: **coding berdasarkan dependency, bukan kalender.** Urutan di bawah ini disusun supaya tiap fase "menumpang" di fondasi yang sudah stabil — risiko refactor besar diminimalkan.

---

## PHASE 0 — Foundation & Specification
**Prasyarat sebelum baris kode pertama**

- [x] Strategy Specification Document v1.0 *(selesai — lihat `EdgeFlow-Strategy-Specification-v1.0.md`)*
- [ ] Product Requirement Document (PRD)
- [ ] System Architecture Document (diagram + ADR/Architecture Decision Record)
- [ ] Database schema (ERD)
- [ ] API Specification (OpenAPI/Swagger)
- [ ] UI/UX wireframe (dashboard, checklist view, journal, analytics)
- [ ] Branding EdgeFlow (logo, tone, landing page copy)

**Repository & tooling (Week 1):**
```
Repository GitHub
Folder structure (apps/, packages/, docs/, database/, docker/)
Next.js frontend scaffold
FastAPI backend scaffold
PostgreSQL container
Docker Compose (semua service)
CI/CD pipeline (lint, test, build)
ESLint + Prettier + Husky (pre-commit hook)
Environment variables template (.env.example)
README.md
```

**Deliverable:** Project jalan lokal — frontend & backend bisa saling komunikasi, `GET /health` return 200, DB terkoneksi.

---

## PHASE 1 — Core Architecture Design
**Week 2**

Desain interface & class untuk semua engine sebelum implementasi:

```
Rule Engine       — generic evaluator (lihat Strategy Spec §7)
Indicator Engine  — kontrak input/output tiap indikator
Strategy Engine   — plugin contract (StrategyPlugin interface)
Scoring Engine     — weight & threshold system
Risk Engine        — lot sizing & limit contract
Market Adapter     — normalisasi data crypto vs forex
Discipline Engine  — cooldown, daily limit, lock mechanism
Entitlement Service— subscription → market/strategy access mapping
```

**Deliverable:** Architecture diagram final, semua interface/class terdefinisi (belum diimplementasi).

---

## PHASE 2 — Market Adapter Layer
**Week 3**

Ini yang bikin crypto & forex bisa jalan di satu Strategy Engine yang sama tanpa strategi tahu dia lagi jalan di market mana.

```
Crypto Adapter  — WS feed exchange (Binance/Bybit), normalisasi OHLCV, order book
Forex Adapter   — data provider (OANDA/TraderMade/Polygon), normalisasi OHLCV, session/weekend handling
NormalizedCandle schema (format standar output kedua adapter)
News feed integration (economic calendar API)
```

**Deliverable:** `Live Market Feed` — data dari kedua market masuk dalam format terstandarisasi, siap dikonsumsi Indicator Engine.

---

## PHASE 3 — Indicator Engine
**Week 4**

Implementasi semua indikator mentah sesuai definisi di Strategy Spec:

```
EMA, ATR
Swing High / Swing Low (fractal detection)
Equal High / Equal Low
BOS, CHoCH/MSS
FVG (Fair Value Gap)
Order Block
Premium/Discount zone
Session & Killzone detector
```

**Deliverable:** `Indicator Package` — unit tested, setiap fungsi menerima `NormalizedCandle[]` dan mengembalikan nilai objektif sesuai parameter di Strategy Spec.

---

## PHASE 4 — Rule Engine
**Week 5**

Engine paling penting di seluruh sistem — generic, bukan hardcoded.

```
Fitur:
  IF / AND / OR / NOT
  Mandatory rule vs Optional rule
  Nested rule (composite condition)
  Score weighting per rule
  Validation terhadap JSON schema rule (§7 Strategy Spec)
  Result: TRUE/FALSE + reason + score
```

**Deliverable:** `Rule Engine` — bisa menjalankan config JSON dari Strategy Spec tanpa perlu tahu itu SMC atau EMA.

---

## PHASE 5 — Strategy Engine (SMC + EMA)
**Week 6**

Implementasi strategi sebagai **config**, dijalankan oleh Rule Engine dari Phase 4.

```
SMC config    → global_filter + bias + liquidity + sweep + bos/choch + fvg + ob + session + rr
EMA config    → trend_filter + pullback + confirmation + rr
Output per strategi: { mandatory_pass: bool, score: 0-100, checklist: [...], recommendation }
```

**Deliverable:** `Strategy Package` — dua strategi jalan penuh di atas data crypto & forex, hasil checklist + score sesuai Strategy Spec.

---

## PHASE 6 — Discipline Engine
**Week 7**

Modul yang jadi inti value proposition produk (lihat §6 Strategy Spec untuk parameter).

```
Daily loss limit (2R default) → lock trading
Max trade per day (3 default) → lock trading
Cooldown after loss streak → lock sementara
SL-lock mechanism (cegah user pindah SL setelah entry)
Overtrade / revenge-trade detection
```

**Deliverable:** Signal dari Strategy Engine yang lolos filter ini baru boleh diteruskan ke user — kalau user sedang kena limit, signal tetap disimpan tapi ditandai "blocked by discipline rule", bukan langsung dikirim.

---

## PHASE 7 — Risk Engine
**Week 8**

```
Lot/position size calculator (formula di §6 Strategy Spec)
SL/TP calculation otomatis dari RR target
Risk % preset (0.25/0.5/1/2%)
Breakeven & partial TP logic (opsional, config)
```

**Deliverable:** `Risk Calculator` — begitu setup lolos checklist, sistem otomatis hitung lot/size, SL, TP sebelum ditampilkan ke user.

---

## PHASE 8 — Entitlement Service
**Week 9**

```
Subscription model: crypto_only | forex_only | bundle_both
Strategy access mapping (opsional granular: per-strategy entitlement)
Middleware check sebelum signal dikirim ke user
Trial / expired / active status handling
```

**Deliverable:** User hanya menerima signal dari market yang mereka subscribe.

---

## PHASE 9 — Execution Flow (Semi-Auto)
**Week 10**

Bukan full-auto. Alur: **Strategy Engine → Discipline check → Risk calc → kirim ke user → user konfirmasi → order dibuka.**

```
Order confirmation interface (web + bot)
Trade Executor:
  - Crypto: exchange API (misal Binance/Bybit REST) — one-click confirm
  - Forex: broker API (OANDA REST) — one-click confirm
  - (MT4/5 bridge jadi opsi tambahan, lebih kompleks — evaluasi kebutuhan riil dulu)
Order lifecycle: open, modify, close, cancel
Reminder in-trade: "Don't move your SL", "No additional entries — daily limit reached"
```

**Deliverable:** `Trade Execution (Semi-Auto)` — user tetap yang menekan tombol konfirmasi terakhir, sistem yang jaga aturan.

---

## PHASE 10 — Dashboard (Frontend)
**Week 11**

```
Pages: Dashboard, Strategy (checklist live), Journal, Analytics, Settings
Live chart (TradingView Lightweight Charts untuk awal, upgrade ke Charting Library kalau perlu)
Checklist visual (✅/❌ per rule, score, recommendation)
```

**Deliverable:** `UI MVP` jalan penuh, terhubung ke semua engine di atas.

---

## PHASE 11 — Trade Journal
**Week 12**

```
Auto-save setiap trade: date, pair, market, strategy, entry/SL/TP, RR, result, R-multiple
Screenshot otomatis saat entry (opsional, capture chart state)
Field manual: emotion, notes, mistake tag
```

**Deliverable:** `Trade Journal` — database trade personal user mulai terbentuk, jadi bahan Analytics & AI Coach nanti.

---

## PHASE 12 — Analytics Dashboard
**Week 13**

```
Win rate per strategi, per session, per pair, per market (crypto vs forex)
Average R, average hold time
Best/worst session & setup
Rule paling sering dilanggar (dari data "signal di-skip" + "trade manual di luar sistem" kalau ada)
```

**Deliverable:** `Analytics Dashboard` — user bisa lihat pola dirinya sendiri secara objektif.

---

## PHASE 13 — Notification Center
**Week 14**

```
Telegram bot
Discord bot
Email
Web push
Webhook (untuk integrasi eksternal)
```

**Deliverable:** `Notification Center` — semua channel terima format signal & reminder yang sama, dari satu service.

---

## PHASE 14 — Authentication & Subscription
**Week 15**

```
Login/Register (Clerk atau Supabase Auth)
Plan tiers: Free (limited), Pro, Lifetime
Billing integration (Stripe / Midtrans untuk pasar lokal)
License activation, cloud sync antar device
```

**Deliverable:** `Account System` + `Payment System` — siap monetisasi.

---

## PHASE 15 — Testing, Hardening & Release
**Week 16**

```
Unit test tiap module (target coverage >90% untuk Rule Engine, Indicator, Risk Engine)
Integration test (end-to-end: data masuk → signal → journal)
Security review (terutama di titik yang menyentuh API key exchange/broker user)
Performance test (real-time data throughput)
Deployment (Docker + VPS, atau managed hosting)
Monitoring & alerting (uptime, error tracking — Sentry)
```

**Deliverable:** **EdgeFlow v1.0 — Public Release.**

---

## Estimasi Timeline

**±16 minggu untuk 1 developer full-time**, dengan asumsi mengikuti urutan dependency di atas (bukan paralel semua). Bisa dipercepat kalau ada tambahan orang di frontend/backend secara paralel setelah Phase 4 (Rule Engine) selesai, karena dari titik itu frontend & backend bisa jalan lebih independen.

---

## Roadmap Pasca-v1

### EdgeFlow v2
- Strategy Builder (drag-and-drop rule builder untuk user premium)
- Backtesting engine (jalan generik di atas Rule Engine config)
- Multi-timeframe confirmation
- Replay mode
- Portfolio management (multi-akun, multi-market bersamaan)
- Broker/exchange tambahan selain default v1

### EdgeFlow v3
- AI Coach (setelah user punya ≥100 trade di journal):
  - Analisis setup terbaik/terburuk, jam terbaik/terburuk, pair terbaik/terburuk
  - Deteksi aturan yang paling sering dilanggar
- AI Rule Generator (bantu user menerjemahkan strategi personal jadi rule objektif)
- Full-auto execution (opsional, guardrail ketat) — untuk user yang sudah "lulus" fase disiplin manual/semi-auto

### EdgeFlow v4
- Marketplace strategi (community bisa share/jual strategy config)
- Team workspace (untuk prop firm/funded trader groups)
- Mobile app (iOS & Android)

---

## Dokumentasi Wajib (Living Documents)

```
docs/
├── PRD.md
├── Strategy-Specification.md        ✅ selesai
├── Architecture.md
├── Database.md
├── API.md
├── Indicator-Specification.md
├── Rule-Engine-Specification.md
├── Risk-Engine-Specification.md
├── Deployment-Guide.md
├── Testing-Guide.md
└── CHANGELOG.md
```

Setiap keputusan arsitektur besar (misal: pilih semi-auto vs full-auto, pilih Postgres vs lainnya) dicatat sebagai **ADR (Architecture Decision Record)** terpisah di `docs/adr/`, supaya alasan keputusan tidak hilang seiring waktu — penting banget buat tim yang berkembang atau kontributor baru nanti.

---

## Changelog Roadmap

| Version | Date | Changes |
|---|---|---|
| 1.0 | 2026-07-14 | Roadmap awal — 16 fase dari Foundation sampai Release, plus roadmap v2–v4 |
