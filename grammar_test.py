import unittest

from grammar import Grammar



class TestStringMethods(unittest.TestCase):

    def setUp(self):
        self.G = Grammar.parse("""
            E → TA
            A → +TA | ɛ 
            T → FB
            B → ∗FB | ɛ
            F → (E) | a
            """)

        self.G2 = Grammar.parse("""
                S → ABC
                A → ɛ
                B → ɛ
                C → ABd
            """)

        self.G3 = Grammar.parse("""
                S → ABC
                A → aA | ɛ
                B → b | ɛ
                C → c | d
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

if __name__ == '__main__':
    unittest.main()

print(G.rules)
print(G.is_nullable("B"))