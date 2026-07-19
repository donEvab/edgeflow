# ADR-001: Mode Eksekusi v1 = Semi-Auto, Bukan Full-Auto

**Status:** Accepted
**Date:** 2026-07-14

## Context

EdgeFlow bisa dibangun dengan tiga level keterlibatan eksekusi: manual (checklist only), semi-auto (alert + konfirmasi user), atau full-auto (sistem eksekusi sendiri berdasarkan rule).

## Decision

v1 dan v2 menggunakan **semi-auto**: Strategy Engine mendeteksi setup, Discipline Engine & Risk Engine memproses, tapi order baru terbuka setelah user menekan tombol konfirmasi eksplisit.

## Consequences

**Positif:**
- Selaras dengan value proposition inti — melatih disiplin, bukan menggantikan keputusan trader.
- Risiko legal/security lebih rendah dibanding full-auto (tidak butuh menyimpan permission withdrawal, tidak menanggung liability penuh atas eksekusi otomatis).
- User tetap "terlibat" secara sadar di setiap trade → mendukung metric adherence rate di PRD.

**Negatif / trade-off:**
- Latency antara signal terdeteksi dan eksekusi lebih tinggi dibanding full-auto (tergantung kecepatan respon user).
- Sebagian user power-user mungkin menginginkan full-auto lebih cepat dari yang direncanakan.

**Mitigasi:** Full-auto tetap masuk roadmap sebagai fitur v3+, opsional, dengan guardrail ketat (max daily loss, max position size), ditujukan untuk user yang sudah terbukti konsisten di fase manual/semi-auto.

## Alternatives Considered

- **Full-auto dari v1**: ditolak karena bertentangan langsung dengan positioning produk ("discipline system", bukan "auto-profit bot"), dan menambah kompleksitas legal/security di fase paling awal saat fondasi belum stabil.
- **Manual-only (tanpa eksekusi sama sekali)**: dipertimbangkan tapi dianggap mengurangi nilai produk — checklist + risk calculator tanpa jalur eksekusi yang mulus membuat friksi tambahan yang justru bisa mendorong user "asal masuk" di luar sistem.
