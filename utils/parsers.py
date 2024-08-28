
class SymbolParser:
    def __init__(self):
        pass

    @staticmethod
    def parse(symbol: str) -> dict:
        if '_' in symbol:
            # Futures format: BASEQUOTE_EXPIRY
            base_quote, expiry = symbol.split('_')
            instr_type = 'f'
            return {
                'instr_type': instr_type,
                'symbol': base_quote,
                'expiry': expiry
            }
        # ETH-220930-1500-C
        elif '-' in symbol:
            # Options format: BASE-EXPIRY-STRIKE-TYPE
            parts = symbol.split('-')
            if len(parts) == 4:
                instr_type = 'o'
                return {
                    'instr_type': instr_type,
                    'type': parts[3],
                    'symbol': parts[0],
                    'expiry': parts[1],
                    'strike': parts[2],
                }
        else:
            # Spot format: BASEQUOTE
            instr_type = 's'
            return {
                'instr_type': instr_type,
                'symbol': symbol
            }

        # If format is unknown
        return {}



# Example usage
# parser = SymbolParser('BTCUSDT_230929')
# print(parser.parse())  # Output: {'type': 'futures', 'symbol': 'BTCUSDT', 'expiry': '230929'}
#
# parser = SymbolParser('BTCUSDT-20230930-50000-C')
# print(
#     parser.parse())  # Output: {'type': 'options', 'symbol': 'BTCUSDT', 'expiry': '20230930', 'strike': '50000', 'type': 'C'}
