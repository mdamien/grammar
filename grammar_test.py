import unittest

from grammar import Grammar

class TestGrammar(unittest.TestCase):

    def setUp(self):
        self.G = Grammar.from_text("""
                E → TA
                A → +TA | ɛ 
                T → FB
                B → ∗FB | ɛ
                F → (E) | a
            """)

        self.G2 = Grammar.from_text("""
                S → ABC
                A → ɛ
                B -> ɛ
                C → ABd
            """)

        self.G3 = Grammar.from_text("""
                S → ABC
                A → aA | ɛ
                B → b | ɛ
                C → c | d
            """)

        self.G4 = Grammar.from_text("""
                S → (S) | a
            """)
    def test_V_T(self):
        G = self.G
        self.assertEqual(len(G.V()),5)
        self.assertEqual(len(G.T()),5)

    def test_nullable(self):
        G = self.G
        self.assertTrue(G.is_nullable("B"))
        self.assertFalse(G.is_nullable("F"))
        G = self.G2
        self.assertFalse(G.is_nullable("S"))

    def test_FNE(self):
        G = self.G
        self.assertEqual(G.FNE("E"),{'a','('})
        self.assertEqual(G.FNE("T"),{'a','('})
        self.assertEqual(G.FNE("F"),{'a','('})
        self.assertEqual(G.FNE("A"),{'+'})
        self.assertEqual(G.FNE("B"),{'∗'})
        G = self.G3
        self.assertEqual(G.FNE("A"),{'a'})
        self.assertEqual(G.FNE("S"),{'a','b','c','d'})

    def test_FOLLOW(self):
        G = self.G
        self.assertEqual(G.FOLLOW("E"),{'$',')'})
        self.assertEqual(G.FOLLOW("T"),{'+','$',')'})
        self.assertEqual(G.FOLLOW("F"),{'∗','+','$',')'})
        self.assertEqual(G.FOLLOW("A"),{'$',')'})
        self.assertEqual(G.FOLLOW("B"),{'+','$',')'})

    def test_parse_table(self):
        G = self.G
        table = G.parse_table(include_conflicts=True)
        goal_table = {
            'A': {'+': [('A', ['+', 'T', 'A'])]
                ,  ')': [('A', [])],'$': [('A', [])]},
            'T': {'a': [('T', ['F', 'B'])], '(': [('T', ['F', 'B'])]},
            'E': {'a': [('E', ['T', 'A'])], '(': [('E', ['T', 'A'])]},
            'B': {'∗': [('B', ['∗', 'F', 'B'])],'+': [('B', [])],
                   ')': [('B', [])], '$': [('B', [])]},
            'F': {'a': [('F', ['a'])], '(': [('F', ['(', 'E', ')'])]}
        }
        self.assertEqual(table, goal_table)

    def test_parse(self):
        G = self.G
        self.assertTrue(G.parse("a+a∗a",print_steps=False))

    def test_lr0(self):
        G = self.G4
        for i, q in enumerate(G.lr0_states()):
            print('I'+str(i),'; '.join(G.state2str(q)))
 

    def test_stats(self):
        G = self.G
        G.stats()

if __name__ == '__main__':
    unittest.main()
