import pytest

from espanol.models import es_eq

@pytest.mark.parametrize(
        'this,other,expected',
        [
            ('nino', 'nino', True),
            ('nino', 'nina', False),
            ('nino', 'pipi', False),
            ('nino', 'nin', False),

            ('nino', 'niño', True),

            ('nina', 'nina', True),
            ('nine', 'niné', True),
            ('nini', 'niní', True),
            ('nino', 'ninó', True),
            ('ninu', 'ninú', True),
            ('ninu', 'ninü', True),

            ('el nino', 'nino', True),
            ('el nino', 'el nino', True),
            ('el niño', 'el nino', True),
            ('el niño', 'niño', True),

            ('la niña', 'niña', True),
            ('la niña', 'la niña', True),
        ]
)
def test_es_eq(this: str, other: str, expected: bool):
    assert es_eq('nino', 'nino')
