from metatrader_client.enums import AccountTradeMode, AccountMarginMode, AccountStopOutMode, SymbolCalcMode, \
    SymbolTradeMode, SymbolTradeExecution, SymbolSwapMode, DayOfWeek, SymbolOrderGTCMode, SymbolOptionMode, \
    SymbolOptionRight, SymbolChartMode


class AccountInfo():
    login: int = 0
    password: str = ''
    server: str = ''
    trade_mode: AccountTradeMode
    balance: float
    leverage: float
    profit: float
    point: float
    amount: float = 0
    equity: float
    credit: float
    margin: float
    margin_level: float
    margin_free: float
    margin_mode: AccountMarginMode
    margin_so_mode: AccountStopOutMode
    margin_so_call: float
    margin_so_so: float
    margin_initial: float
    margin_maintenance: float
    fifo_close: bool
    limit_orders: float
    currency: str = "USD"
    trade_allowed: bool = True
    trade_expert: bool = True
    currency_digits: int
    assets: float
    liabilities: float
    commission_blocked: float
    name: str
    company: str


class SymbolInfo:
    def __init__(self, symbol_info):
        self.symbol_info = symbol_info

    def to_dict(self):
        return {
            "custom": self.symbol_info.custom,
            "chart_mode": self.symbol_info.chart_mode,
            "select": self.symbol_info.select,
            "visible": self.symbol_info.visible,
            "session_deals": self.symbol_info.session_deals,
            "session_buy_orders": self.symbol_info.session_buy_orders,
            "session_sell_orders": self.symbol_info.session_sell_orders,
            "volume": self.symbol_info.volume,
            "volumehigh": self.symbol_info.volumehigh,
            "volumelow": self.symbol_info.volumelow,
            "time": self.symbol_info.time,
            "digits": self.symbol_info.digits,
            "spread": self.symbol_info.spread,
            "spread_float": self.symbol_info.spread_float,
            "ticks_bookdepth": self.symbol_info.ticks_bookdepth,
            "trade_calc_mode": self.symbol_info.trade_calc_mode,
            "trade_mode": self.symbol_info.trade_mode,
            "start_time": self.symbol_info.start_time,
            "expiration_time": self.symbol_info.expiration_time,
            "trade_stops_level": self.symbol_info.trade_stops_level,
            "trade_freeze_level": self.symbol_info.trade_freeze_level,
            "trade_exemode": self.symbol_info.trade_exemode,
            "swap_mode": self.symbol_info.swap_mode,
            "swap_rollover3days": self.symbol_info.swap_rollover3days,
            "margin_hedged_use_leg": self.symbol_info.margin_hedged_use_leg,
            "expiration_mode": self.symbol_info.expiration_mode,
            "filling_mode": self.symbol_info.filling_mode,
            "order_mode": self.symbol_info.order_mode,
            "order_gtc_mode": self.symbol_info.order_gtc_mode,
            "option_mode": self.symbol_info.option_mode,
            "option_right": self.symbol_info.option_right,
            "bid": self.symbol_info.bid,
            "bidhigh": self.symbol_info.bidhigh,
            "bidlow": self.symbol_info.bidlow,
            "ask": self.symbol_info.ask,
            "askhigh": self.symbol_info.askhigh,
            "asklow": self.symbol_info.asklow,
            "last": self.symbol_info.last,
            "lasthigh": self.symbol_info.lasthigh,
            "lastlow": self.symbol_info.lastlow,
            "volume_real": self.symbol_info.volume_real,
            "volumehigh_real": self.symbol_info.volumehigh_real,
            "volumelow_real": self.symbol_info.volumelow_real,
            "option_strike": self.symbol_info.option_strike,
            "point": self.symbol_info.point,
            "trade_tick_value": self.symbol_info.trade_tick_value,
            "trade_tick_value_profit": self.symbol_info.trade_tick_value_profit,
            "trade_tick_value_loss": self.symbol_info.trade_tick_value_loss,
            "trade_tick_size": self.symbol_info.trade_tick_size,
            "trade_contract_size": self.symbol_info.trade_contract_size,
            "trade_accrued_interest": self.symbol_info.trade_accrued_interest,
            "trade_face_value": self.symbol_info.trade_face_value,
            "trade_liquidity_rate": self.symbol_info.trade_liquidity_rate,
            "volume_min": self.symbol_info.volume_min,
            "volume_max": self.symbol_info.volume_max,
            "volume_step": self.symbol_info.volume_step,
            "volume_limit": self.symbol_info.volume_limit,
            "swap_long": self.symbol_info.swap_long,
            "swap_short": self.symbol_info.swap_short,
            "margin_initial": self.symbol_info.margin_initial,
            "margin_maintenance": self.symbol_info.margin_maintenance,
            "session_volume": self.symbol_info.session_volume,
            "session_turnover": self.symbol_info.session_turnover,
            "session_interest": self.symbol_info.session_interest,
            "session_buy_orders_volume": self.symbol_info.session_buy_orders_volume,
            "session_sell_orders_volume": self.symbol_info.session_sell_orders_volume,
            "session_open": self.symbol_info.session_open,
            "session_close": self.symbol_info.session_close,
            "session_aw": self.symbol_info.session_aw,
            "session_price_settlement": self.symbol_info.session_price_settlement,
            "session_price_limit_min": self.symbol_info.session_price_limit_min,
            "session_price_limit_max": self.symbol_info.session_price_limit_max,
            "margin_hedged": self.symbol_info.margin_hedged,
            "price_change": self.symbol_info.price_change,
            "price_volatility": self.symbol_info.price_volatility,
            "price_theoretical": self.symbol_info.price_theoretical,
            "price_greeks_delta": self.symbol_info.price_greeks_delta,
            "price_greeks_theta": self.symbol_info.price_greeks_theta,
            "price_greeks_gamma": self.symbol_info.price_greeks_gamma,
            "price_greeks_vega": self.symbol_info.price_greeks_vega,
            "price_greeks_rho": self.symbol_info.price_greeks_rho,
            "price_greeks_omega": self.symbol_info.price_greeks_omega,
            "price_sensitivity": self.symbol_info.price_sensitivity,
            "currency_base": self.symbol_info.currency_base,
            "currency_profit": self.symbol_info.currency_profit,
            "currency_margin": self.symbol_info.currency_margin,
            "description": self.symbol_info.description,
            "name": self.symbol_info.name,
            "path": self.symbol_info.path
        }

    @property
    def __dict__(self):
        return self.to_dict()
