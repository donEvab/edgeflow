"""EdgeFlow global config — default parameters (lihat docs/Strategy-Specification.md §8 Appendix)."""

DEFAULT_PARAMETERS = {
    "liquidity_tolerance_percent": 0.1,
    "fvg_min_gap_percent": 0.05,
    "order_block_min_body_percent": 60,
    "displacement_atr_multiple": 1.5,
    "min_rr_smc": 3.0,
    "min_rr_ema": 2.0,
    "news_blackout_minutes": 30,
    "daily_loss_limit_r": 2,
    "max_trades_per_day": 3,
}
