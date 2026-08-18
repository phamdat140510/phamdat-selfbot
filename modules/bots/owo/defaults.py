OWO_DEFAULT_CONFIG = {
    'prefix': 'owo',
    'check_status': True,

    'channels_id': [],
    'changing_channel': {
        'when_mentioned': True,
        'when_challenge': True,
        'after_elapsed_time': {'min': 300, 'max': 600},
    },

    'checklist': True,
    'quest': True,
    'vote': True,
    'daily': True,
    'huntbot': True,
    'giveaway': True,
    'boss': True,

    'spam': {
        'hunt': True,
        'battle': True,
        'owo/uwu': True,
        'delay': {'min': 1, 'max': 2},
        'cooldown': {'min': 30, 'max': 60},
    },

    'gem': {
        'use': False,
        'couple': True,
        'best': False,
        'star': False,
        'glitch': True,
        'openning': {'box': True, 'crate': True, 'flootbox': False},
    },

    'gamble': {
        'lottery': {'mode': False, 'amount': 1},
        'slot': {'mode': False, 'bet': 1, 'rate': 2, 'max': 250000},
        'coinflip': {'mode': False, 'bet': 1, 'rate': 2, 'max': 250000},
        'blackjack': {'mode': False, 'bet': 1, 'rate': 2, 'max': 250000},
        'highlow': {'mode': False, 'bet': 10, 'rate': 2, 'max': 250000},
        'delay': {'min': 0.5, 'max': 1},
        'cooldown': {'min': 60, 'max': 120},
    }
}