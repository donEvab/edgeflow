# EdgeFlow — Strategy Specification Document

**Version:** 1.0
**Status:** Draft — Foundation
**Owner:** EdgeFlow Core Team
**Last Updated:** 2026-07-14

---

## 0. Tujuan Dokumen

Dokumen ini adalah **single source of truth** untuk semua rule trading yang dijalankan EdgeFlow. Tidak ada logic strategi yang boleh masuk ke kode tanpa lebih dulu terdefinisi di sini.

Alasan dokumen ini wajib ada sebelum coding:

- Istilah seperti *Liquidity Sweep*, *Order Block*, *FVG* punya definisi yang berbeda-beda antar trader/mentor. Kalau tidak dibakukan, hasil deteksi sistem akan tidak konsisten antar kondisi market.
- Setiap rule harus bisa diuji ulang (reproducible) — kalau dua orang membaca chart yang sama dengan parameter yang sama, harus dapat hasil yang sama.
- Rule di sini akan diterjemahkan 1:1 ke **Rule Engine** (lihat §7), bukan hardcoded ke aplikasi.

---

## 1. Rule Philosophy

Semua rule di EdgeFlow **wajib** memenuhi syarat berikut:

1. **Computable** — bisa dihitung dari data OHLCV + metadata (session, news, spread), tanpa interpretasi manusia.
2. **Unambiguous** — tidak ada rentang keputusan subjektif ("kayaknya", "menurut feeling").
3. **Binary output** — hasil akhir tiap rule cuma `TRUE` / `FALSE`, dengan parameter yang bisa dikonfigurasi user (misal toleransi 0.1%, bukan fixed).
4. **Explainable** — tiap `FALSE` harus punya alasan spesifik yang bisa ditampilkan ke user (bukan cuma "gagal").
5. **Versioned** — setiap rule punya `id` dan `version`. Rule lama tidak dihapus, tapi di-*deprecate* dan digantikan versi baru, supaya data historis/backtest tetap valid dijelaskan oleh definisi rule yang dipakai saat itu.

---

## 2. Global Filter (Market Filter)

Semua strategi — SMC maupun EMA — wajib lolos filter ini dulu sebelum Strategy Engine jalan. Kalau salah satu `FALSE`, output langsung `NO TRADE` tanpa evaluasi lebih lanjut (hemat compute, dan psikologis: user tahu alasan paling dasar dulu).

### 2.1 Session Filter

```
Parameter:
  valid_sessions: ["london", "new_york"]   // configurable, default
  optional_sessions: ["asia"]              // off by default

Rule:
  current_time (broker/exchange timezone) berada di dalam salah satu
  valid_sessions yang aktif → TRUE
  di luar semua → FALSE

Session time reference (UTC, DST-adjusted otomatis oleh sistem):
  Asia    : 00:00–08:00
  London  : 08:00–16:00
  New York: 13:00–21:00
```

> Catatan: untuk market **crypto**, session filter default OFF (24/7), tapi tetap tersedia sebagai opsi (misal user mau filter jam likuiditas tinggi saja).

### 2.2 Spread Filter

```
Parameter:
  max_spread: configurable per pair (default: dinamis, 2x median spread 30 hari)

Rule:
  current_spread <= max_spread → TRUE
  current_spread > max_spread  → FALSE, reason: "Spread too wide"
```

### 2.3 News Filter

```
Parameter:
  blackout_before_minutes: 30
  blackout_after_minutes: 30
  impact_levels_blocked: ["high"]   // configurable: tambah "medium" kalau mau lebih strict

Rule:
  now berada di dalam window [event_time - blackout_before, event_time + blackout_after]
  untuk event dengan impact ∈ impact_levels_blocked
  → FALSE, reason: "High impact news: {event_name}"
  else → TRUE

Data source: economic calendar API (ForexFactory-compatible feed / TradingEconomics API)
```

### 2.4 Volatility Filter

```
Parameter:
  indicator: ATR(14)
  min_atr_percentile: 20   // dibanding distribusi ATR 90 hari terakhir

Rule:
  current_ATR percentile >= min_atr_percentile → TRUE
  else → FALSE, reason: "Volatility too low, choppy market"
```

### Global Filter Output

```json
{
  "tradable": true,
  "checks": {
    "session": true,
    "spread": true,
    "news": true,
    "volatility": true
  },
  "reason": null
}
```

---

## 3. SMC Strategy Specification

Target instrumen awal: **XAUUSD, EURUSD, major crypto pairs (BTC/ETH) — timeframe entry 5M/15M dengan HTF bias di 1H/4H.**

### 3.1 Bias / HTF Trend

Dua metode disediakan (user pilih salah satu via config), **default: EMA200**.

**Metode A — EMA200 Filter**
```
Rule BUY : close(HTF) > EMA200(HTF)
Rule SELL: close(HTF) < EMA200(HTF)
Output   : BUY | SELL | NONE
```

**Metode B — Structure-based (HH-HL / LH-LL)**
```
Rule BUY : 2 swing terakhir membentuk Higher High + Higher Low
Rule SELL: 2 swing terakhir membentuk Lower High + Lower Low
Parameter: swing_lookback (default: 5 candle each side, fractal-based)
Output   : BUY | SELL | NONE
```

### 3.2 Liquidity (Equal High / Equal Low)

```
Definisi:
  Liquidity pool valid jika ada minimal 2 swing high (atau swing low)
  dengan selisih harga dalam batas tolerance.

Parameter:
  tolerance_percent: 0.1%   // configurable per instrumen
  lookback_swings: 10

Rule:
  |price_a - price_b| / price_a <= tolerance_percent → Equal High/Low = TRUE

Output: { equal_high: bool, equal_low: bool, level_price: float }
```

### 3.3 Liquidity Sweep

```
Rule BUY (sweep of equal low):
  low(current_candle) < equal_low_level
  AND close(current_candle) > equal_low_level
  → Liquidity Sweep = TRUE

Rule SELL (sweep of equal high):
  high(current_candle) > equal_high_level
  AND close(current_candle) < equal_high_level
  → Liquidity Sweep = TRUE

Parameter:
  max_sweep_penetration_percent: 0.3%   // batas wajar penetrasi, mencegah false sweep detection
```

### 3.4 Break of Structure (BOS)

```
Rule BUY : close(current) > previous_swing_high
Rule SELL: close(current) < previous_swing_low

Parameter:
  confirmation: "close" (bukan wick) — default, configurable ke "wick" untuk trader agresif
```

### 3.5 Change of Character / Market Structure Shift (CHoCH/MSS)

```
Rule BUY:
  trend_sebelumnya == BEARISH
  AND close(current) > lower_high_terakhir
  → CHoCH = TRUE, trend_baru = BULLISH

Rule SELL: kebalikan dari di atas
```

### 3.6 Fair Value Gap (FVG)

```
Three-Candle Rule:

Rule BUY (bullish FVG):
  low(candle_3) > high(candle_1)
  gap_size = low(candle_3) - high(candle_1)

Rule SELL (bearish FVG):
  high(candle_3) < low(candle_1)
  gap_size = low(candle_1) - high(candle_3)

Parameter:
  min_gap_percent: 0.05%   // gap minimal supaya dianggap valid, hindari noise
  require_retrace_into_fvg: true   // entry harus retrace masuk ke gap dulu
```

### 3.7 Order Block

```
Definisi Bullish OB:
  last bearish candle sebelum displacement candle (candle impulsif ke atas)

Definisi Bearish OB:
  last bullish candle sebelum displacement candle (candle impulsif ke bawah)

Parameter:
  displacement_min_body_percent: 60%   // body candle displacement minimal 60% dari range
  displacement_min_atr_multiple: 1.5   // range candle displacement >= 1.5x ATR
```

### 3.8 Premium / Discount Zone (filter tambahan, optional)

```
Rule:
  Range = swing_high - swing_low (leg terakhir)
  Discount zone = 0% - 50% dari range (dari swing_low)
  Premium zone  = 50% - 100% dari range

Rule BUY : entry_price berada di Discount zone → TRUE
Rule SELL: entry_price berada di Premium zone → TRUE
```

### 3.9 Session / Killzone Filter (khusus SMC)

```
Parameter:
  killzones: ["london_open", "ny_open"]
  london_open: 07:00–10:00 UTC
  ny_open    : 12:00–15:00 UTC

Rule: current_time berada di dalam killzone aktif → TRUE
```

### 3.10 Risk-Reward Minimum

```
Parameter: min_rr (default 1:3, configurable: 1:2 s/d 1:5)
Rule: calculated_RR >= min_rr → TRUE
```

### 3.11 SMC Entry — Composite Rule

```
Mandatory (semua harus TRUE):
  - bias (HTF trend)
  - liquidity_sweep
  - bos_or_choch
  - fvg
  - order_block
  - session_killzone
  - min_rr

Jika salah satu FALSE → NO ENTRY, output alasan spesifik yang gagal.
Jika semua TRUE → lanjut ke Score Engine (§5) untuk grading kualitas setup.
```

---

## 4. EMA Strategy Specification

Target: instrumen apa saja, timeframe fleksibel (default 15M–1H). Strategi ini lebih sederhana, cocok jadi "strategi kedua" yang kontras dengan SMC (trend-following klasik vs konsep SMC).

### 4.1 Trend Filter

```
Rule BUY : EMA20 > EMA50 > EMA200
Rule SELL: EMA20 < EMA50 < EMA200
Parameter: ema_periods = [20, 50, 200]  // configurable
```

### 4.2 Pullback

```
Rule BUY : low(candle) menyentuh EMA20 atau EMA50 (dengan toleransi wick)
Rule SELL: high(candle) menyentuh EMA20 atau EMA50

Parameter: touch_tolerance_percent: 0.1%
```

### 4.3 Confirmation Candle

```
Rule BUY : candle bullish engulfing ATAU strong bull candle
  strong_bull_candle: body_percent >= 60% dari range candle
Rule SELL: kebalikannya

Parameter: min_body_percent: 60%
Optional : volume_confirmation (candle volume > avg_volume(20))
```

### 4.4 Risk-Reward Minimum

```
Parameter: min_rr (default 1:2, disarankan 1:3)
```

### 4.5 EMA Entry — Composite Rule

```
Mandatory (semua harus TRUE):
  - trend_filter
  - pullback
  - confirmation_candle
  - min_rr

Jika semua TRUE → lanjut ke Score Engine.
```

---

## 5. Score Engine

Score engine memberi nilai kualitas setup 0–100, bukan cuma pass/fail — ini yang jadi psychological hook produk ("dinilai", bukan sekadar dikasih sinyal).

### 5.1 SMC Scoring Weights

| Komponen | Bobot |
|---|---|
| Bias/Trend | 20 |
| Liquidity Sweep | 20 |
| BOS/CHoCH | 15 |
| FVG | 15 |
| Order Block | 10 |
| Session/Killzone | 10 |
| RR | 10 |
| **Total** | **100** |

### 5.2 EMA Scoring Weights

| Komponen | Bobot |
|---|---|
| Trend Filter | 30 |
| Pullback | 25 |
| Confirmation Candle | 25 |
| RR | 20 |
| **Total** | **100** |

### 5.3 Recommendation Band

```
90–100 → A+  → "Strong Entry"
80–89  → A   → "Entry"
70–79  → B   → "Optional / Wait for confirmation"
< 70   → —   → "Reject"
```

> Catatan penting: **mandatory rule yang FALSE tetap memblokir entry**, terlepas dari skor. Skor hanya berlaku untuk rule yang statusnya "optional" atau untuk memberi konteks kualitas ke user pada rule yang sudah TRUE. Ini mencegah sistem "membenarkan" entry jelek hanya karena skor tinggi di komponen lain.

---

## 6. Risk Engine Specification

```
Input:
  balance: float
  risk_percent: float   // preset: 0.25% / 0.5% / 1% / 2%, default 0.5%
  entry_price: float
  stop_loss_price: float

Formula:
  risk_amount = balance * (risk_percent / 100)
  sl_distance = |entry_price - stop_loss_price|
  position_size (lot/unit) = risk_amount / sl_distance   // disesuaikan kontrak spec per instrumen

Output:
  { lot_size, risk_amount, potential_profit (at TP), max_drawdown_if_hit }
```

### Daily Discipline Limits

```
Parameter:
  daily_loss_limit_R: 2        // stop trading kalau rugi kumulatif >= 2R dalam sehari
  max_trades_per_day: 3
  cooldown_after_loss_streak: 2 trades → lock 60 menit (configurable)

Rule:
  Jika salah satu limit tercapai → Trade Executor mengunci entry baru,
  status: "Trading Locked — {reason}", sampai reset (hari berikutnya atau cooldown selesai)
```

---

## 7. Rule Engine — Generic Schema (PENTING)

Ini keputusan arsitektur paling krusial: **SMC dan EMA tidak boleh hardcoded**. Keduanya hanyalah *konfigurasi* yang dijalankan oleh Rule Engine generik. Dengan begini, menambah strategi baru (v2, v3) = menambah file config, bukan mengubah source code inti.

```json
{
  "strategy_id": "smc_v1",
  "version": "1.0.0",
  "rules": [
    {
      "id": "trend_filter",
      "type": "comparison",
      "operator": ">",
      "left": "close",
      "right": "ema200",
      "mandatory": true,
      "score_weight": 20
    },
    {
      "id": "liquidity_sweep",
      "type": "composite",
      "operator": "AND",
      "conditions": [
        { "left": "low", "operator": "<", "right": "equal_low_level" },
        { "left": "close", "operator": ">", "right": "equal_low_level" }
      ],
      "mandatory": true,
      "score_weight": 20
    }
  ],
  "output": {
    "mandatory_all_true_required": true,
    "score_threshold_recommend": 80
  }
}
```

Konsekuensi desain ini:

- Menambah strategi baru → tambah file JSON/YAML config, tidak sentuh core.
- User premium (fitur v3+) bisa bikin strategi custom dari kombinasi rule yang tersedia (Strategy Builder).
- Backtesting engine bisa jalan generik terhadap config apa pun, tidak perlu logic khusus per strategi.

---

## 8. Parameter & Tolerance Reference (Appendix)

| Parameter | Default | Range Konfigurasi |
|---|---|---|
| Liquidity tolerance | 0.1% | 0.05%–0.3% |
| FVG minimal gap | 0.05% | 0.02%–0.2% |
| Order Block min body | 60% | 50%–80% |
| Displacement ATR multiple | 1.5x | 1.0x–2.5x |
| Min RR (SMC) | 1:3 | 1:2–1:5 |
| Min RR (EMA) | 1:2 | 1:1.5–1:4 |
| News blackout | 30 min before/after | 15–60 min |
| Daily loss limit | 2R | 1R–3R |
| Max trades/day | 3 | 1–10 |

---

## 9. Versioning Policy Dokumen Ini

- Perubahan definisi rule → **minor version bump** (1.0 → 1.1), dicatat di Changelog.
- Penambahan strategi baru (bukan ubah yang lama) → tidak mengubah versi dokumen ini, cukup tambah section baru.
- Perubahan yang mengubah hasil historical scoring/backtest → **major version bump** (1.x → 2.0), dan versi lama tetap disimpan untuk keperluan audit data historis.

---

## Changelog

| Version | Date | Changes |
|---|---|---|
| 1.0 | 2026-07-14 | Initial specification — Global Filter, SMC, EMA, Score Engine, Risk Engine, Rule Engine schema |
