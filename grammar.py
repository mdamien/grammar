import itertools

from tabulate import tabulate

class Grammar:
    def __init__(self, axiom, rules):
        self.axiom = axiom
        self.rules = rules

    @staticmethod
    def from_text(text):
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

    def FNE_rule(self, rule):
        FNE = set()
        for symbol in rule:
            subFNE = self.FNE(symbol)
            nullable = self.is_nullable(symbol)
            FNE |= subFNE
            if not nullable:
                break
        return FNE

    def FNE(self, x):
        if self.is_terminal(x):
            return {x}
        FNE = set()
        R = self.rules[x]
        for rule in R:
            FNE |= self.FNE_rule(rule)
        return FNE

    def FIRST(self, x):
        FNE = self.FNE(x)
        if self.is_nullable(x):
            FNE.add('')
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

    def rule2str(self, v, rule):
        return '→'.join([v,''.join(rule) if len(rule) > 0 else "ɛ"])

    def parse_table_cell(self,v,t):
        L = []
        R = self.rules[v]
        for rule in R:
            FNE = self.FNE_rule(rule)
            if t in FNE:
                L.append((v,rule))

        FOLLOW = self.FOLLOW(v)
        if t in FOLLOW:
            for rule in R:
                if self.is_list_nullable(rule):
                    L.append((v,rule))
        return L

    def parse_table(self,include_conflicts=False):
        table = {}
        T = list(self.T())+["$"]
        for v in self.V():
            Vrules = {}
            for t in T:
                result = self.parse_table_cell(v,t)
                if len(result) > 0:
                    if not include_conflicts:
                        if len(result) > 1:
                            print("CONFLICT IGNORED!",v,t,result)
                        Vrules[t] = result[0]
                    else:
                        Vrules[t] = result
            table[v] = Vrules
        return table

    def print_parse_table(self):
        V = sorted(self.V())
        T = sorted(self.T())+["$"]

        parse_table = self.parse_table(include_conflicts=True)

        table = [[" "]+list(T)]
        for v in V:
            row = [v]
            for t in T:
                cell = parse_table[v].get(t,None)
                if cell:
                    cell = ','.join(self.rule2str(*sol) for sol in cell)
                else:
                    cell = ""
                row.append(cell)
            table.append(row)

        print()
        print(tabulate(table[1:],
                headers=table[0],
                tablefmt="fancy_grid"))
        print()

    def parse(self, s, limit=20):
        if type(s) == str:
            s = list(s)

        parse_table = self.parse_table()
        table = [["(top) stack",'parse','action'],]
        stack = [self.axiom,"$"]
        to_parse = s+["$"]

        try:
            while limit > 0:
                to_parse0 = to_parse[0]
                stack0 = stack[0]
                row = [''.join(stack),''.join(to_parse)]
                action = ""
                if stack0 == to_parse0:
                    if stack0 == "$":
                        action = "accept"
                    else:
                        action = "match"
                        stack = stack[1:]
                        to_parse = to_parse[1:]
                else:
                    v,rule = parse_table[stack0][to_parse0]
                    action = "apply "+self.rule2str(v, rule)
                    stack = rule+stack[1:]
                row.append(action)
                table.append(row)
                limit -= 1
                if action == "accept":
                    break
        finally:
            print()
            print(tabulate(table[1:],
                    headers=table[0],
                    stralign="right",
                    tablefmt="fancy_grid"))
            print()

    def FIRST_FOLLOW_table(self):
        table = [["",'FNE','FOLLOW'],]

        formatset = lambda s: ','.join(sorted(s))

        for V in sorted(self.V()):
            table.append([
                V,
                formatset(self.FNE(V)),
                formatset(self.FOLLOW(V))
            ])
        print()
        print(tabulate(table[1:],
                headers=table[0],
                tablefmt="fancy_grid"))
        print()
