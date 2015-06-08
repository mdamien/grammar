import itertools

class Grammar:
    def __init__(self, axiom, rules):
        self.axiom = axiom
        self.rules = rules

    @staticmethod
    def parse(text):
        axiom = None
        rules = {}
        lines = [l.strip() for l in text.split('\n') if len(l.strip()) > 0]
        for line in lines:
            V, Vrules = [x.strip() for x in line.split('→')]
            if not axiom:
                axiom = V
            Vrules = [list(x.strip().replace('ɛ','')) for x in Vrules.split('|')]
            rules[V] = Vrules
        return Grammar(axiom=axiom, rules=rules)

    def V(self): #non-terminals
        return self.rules.keys()

    def is_terminal(self, x):
        return x not in self.V()

    def T(self): #terminals
        flat = lambda L: itertools.chain(*L)
        return set(x for x in flat(flat(self.rules.values())) if self.is_terminal(x))

    def is_nullable(self, x):
        if self.is_terminal(x):
            return False
        R = self.rules[x]
        for rule in R:
            nullable = all(self.is_nullable(s) for s in rule)
            if nullable:
                return True
        return False

    def is_list_nullable(self,l):
        return all(self.is_nullable(x) for x in l)

    def FNE(self, x):
        if self.is_terminal(x):
            return {x}
        FNE = set()
        R = self.rules[x]
        for rule in R:
            for symbol in rule:
                subFNE = self.FNE(symbol)
                nullable = self.is_nullable(symbol)
                FNE |= subFNE
                if not nullable:
                    break
        return FNE

    def FOLLOW(self, x):
        if self.is_terminal(x):
            return {x}
        FOLLOW = set()

        #rule 1
        if x == self.axiom:
            FOLLOW.add("$")

        for V in self.V():
            for rule in self.rules[V]:
                for i, symbol in enumerate(rule):
                    if symbol == x:
                        if i+1 < len(rule):
                            #rule 2
                            symbol_next = rule[i+1]
                            FOLLOW |= self.FNE(symbol_next)

                        #rule 3
                        all_next = rule[i+1:]
                        if self.is_list_nullable(all_next):
                            if V != x:
                                FOLLOW |= self.FOLLOW(V)

        return FOLLOW
