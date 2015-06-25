import itertools

from tabulate import tabulate
from pprint import pprint as pp

"""
TODO:
- detect grammar conflicts (LL(1), LR(0),..)
- LR(0) parse
- LR(1)
- SLR(1)
- LALR(1)
- parse tree + tree traversal with grammar output example
"""

class Grammar:
    ARROW = '→'
    EPSILON = 'ɛ'
    BULLET = '•'

    def __init__(self, axiom, rules):
        self.axiom = axiom
        self.rules = rules

    @staticmethod
    def from_text(text):
        axiom = None
        rules = {}
        lines = [l.strip() for l in text.split('\n') if len(l.strip()) > 0]
        for line in lines:
            arrow = Grammar.ARROW if Grammar.ARROW in line else '->'
            V, Vrules = [x.strip() for x in line.split(arrow)]
            if not axiom:
                axiom = V
            Vrules = [list(x.strip().replace(Grammar.EPSILON,'')) for x in Vrules.split('|')]
            rules[V] = Vrules
        return Grammar(axiom=axiom, rules=rules)

    def V(self): #non-terminals
        return self.rules.keys()

    def is_terminal(self, x):
        return x not in self.V()

    def is_non_terminal(self, x):
        return x in self.V()

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
        return (' '+Grammar.ARROW+' ').join([v,''.join(rule) if len(rule) > 0 else Grammar.EPSILON])

    def vrules2str(self, v):
        rules = [''.join(rule) if len(rule) > 0 else Grammar.EPSILON for rule in self.rules[v]]
        return (' '+Grammar.ARROW+' ').join((v,' | '.join(rules)))

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

    def parse(self, s, limit=50, print_steps=True):
        if type(s) == str:
            s = list(s)

        parse_table = self.parse_table()
        table = [["(top) stack",'parse','action'],]
        stack = [self.axiom,"$"]
        to_parse = s+["$"]

        final_action_is_accept = False

        try:
            while limit > 0:
                need_to_break = False
                to_parse0 = to_parse[0]
                stack0 = stack[0]
                row = [''.join(stack),''.join(to_parse)]
                action = ""
                try:
                    if stack0 == to_parse0:
                        if stack0 == "$":
                            action = "accept"
                            need_to_break = True
                            final_action_is_accept = True
                        else:
                            action = "match"
                            stack = stack[1:]
                            to_parse = to_parse[1:]
                    else:
                        if self.is_terminal(stack0):
                            action = "parsing error"
                            need_to_break = True
                        else:
                            v,rule = parse_table[stack0][to_parse0]
                            action = "apply "+self.rule2str(v, rule)
                            stack = rule+stack[1:]
                except Exception as e:
                    action = "Exception occured"
                    print("Exception:",repr(e))
                    need_to_break = True
                row.append(action)
                table.append(row)
                limit -= 1
                if need_to_break:
                    break
        finally:
            if print_steps:
                print()
                print(tabulate(table[1:],
                        headers=table[0],
                        stralign="right",
                        tablefmt="fancy_grid"))
                print()
        return final_action_is_accept

    def FIRST_FOLLOW_table(self):
        table = [["",'FIRST','FOLLOW'],]

        formatset = lambda s: ','.join(sorted(s))

        for V in sorted(self.V()):
            table.append([
                V,
                formatset([ Grammar.EPSILON if x == '' else x for x in sorted(self.FIRST(V))]),
                formatset(self.FOLLOW(V))
            ])
        print()
        print(tabulate(table[1:],
                headers=table[0],
                tablefmt="fancy_grid"))
        print()

    def print_grammar(self):
        print("Axiom:",self.axiom)
        print("Terminals:",' '.join(sorted(self.T())))
        print("Non-Terminals:",' '.join(sorted(self.V())))
        print("Rules:")
        for v in sorted(self.V()):
            print(self.vrules2str(v))


    def stats_ll1(self):
        print("FIRST/FOLLOW table:")
        self.FIRST_FOLLOW_table()
        print("LL(1) parse table:")
        self.print_parse_table()

    def stats_lr0(self):
        print("states:")
        states = self.lr0_states()
        self.lr0_pp(states)
        print()
        print("table:")
        self.lr0_table(states)
        print()
        print("action table:")
        self.lr0_full_table(states)

    def stats(self):
        self.print_grammar()
        self.stats_ll1()
        self.stats_lr0()

    ###### LR(0)

    def lr0_closure(self,kernels, max_depth=4):
        if max_depth == 0:
            return kernels
        items = {}
        for kernel in kernels:
            items[self.sstate2str(kernel)] = kernel
            R, rule, i = kernel
            right = rule[i:]
            if right:
                right0 = right[0]
                if self.is_non_terminal(right0):
                    for rule2 in self.rules[right0]:
                        nq = (right0, rule2,0)
                        closured = self.lr0_closure([nq], max_depth-1)
                        for it in closured:
                            items[self.sstate2str(it)] = it
        return items.values()

    def lr0_goto(self, q, X):
        state = []
        for item in q:
            R, rule, i = item
            right = rule[i:]
            if right:
                right0 = right[0]
                if right0 == X:
                    nq = R, rule, i+1
                    state.append(nq)
        return state

    def sstate2str(self, q):
        R, rule, i = q
        nrule = rule[:i]
        nrule.append(Grammar.BULLET)
        nrule += rule[i:]
        return self.rule2str(R, nrule)

    def state2str(self, q):
        return [self.sstate2str(x) for x in q]

    def state2strstr(self, q):
        return ';'.join(self.state2str(q))

    def lr0_states(self):
        symboles = sorted(self.V() | self.T())
        I0_kernel = [("S'",[self.axiom],0)]
        I0 = self.lr0_closure(I0_kernel)

        hash_to_state = {}

        def hash_state(x):
            return self.state2strstr(x)

        def add(x,myIs, origin=None, transition=None):
            h = hash_state(x)
            if h in hash_to_state:
                el = myIs[hash_to_state[h]]
            else:
                hash_to_state[h] = add.N
                el = myIs[add.N] = {
                    'state':x,
                    'origin':set(),
                    'transition':set(),
                    'N':add.N,
                }
                add.N += 1
            if origin != None:
                el['origin'].add(origin)
                el['transition'].add(transition)
        add.N = 0

        def states(Is):
            return [x['state'] for x in Is.values()]

        Is = {}
        add(I0, Is)

        while True:
            newIs = {k:v for k,v in Is.items()}
            for k,v in Is.items():
                I = v["state"]
                genIs = [(self.lr0_goto(I, X), X) for X in symboles]
                genIs = [(x, X) for x, X in genIs if len(x) > 0]
                genIs = [(self.lr0_closure(x),X) for x, X in genIs]
                [add(x, newIs, k, X) for x, X in genIs]
            if len(Is) == len(newIs):
                Is = newIs
                break
            Is = newIs
        return Is


    def lr0_parse(self, s, limit=50, print_steps=True):
        if type(s) == str:
            s = list(s)

        states = self.lr0_states()

        def is_reduce_item(item):
            R, rule, i = item
            return len(rule) == i

        def is_shift_item(item):
            return not is_reduce_item(item)

        def find_transition(curr, symbol):
            for k, state in states.items():
                if curr in state['origin'] and symbol in state['transition']:
                    return k

        GOTO = self.lr0_GOTO(states)

        table = [['state','states stack', "(top) stack",'parse','action'],]

        s.append('$')

        stack = [0]
        stack2 = ['$']

        try:
            for i in range(20):
                row = [
                    ''.join(map(str,stack)),
                    ''.join(map(str,stack2)),
                    ''.join(s)]
                action = "no action"
                curr_state = stack[-1]
                s0 = s[0]
                new_state = find_transition(curr_state, s0)
                #SHIFT
                if new_state:
                    stack.append(new_state)
                    stack2.append(s0)
                    s = s[1:]
                    action = "shift "+str(new_state)
                else:
                    state_infos = states[curr_state]
                    #REDUCE
                    reduce_items = [it for it in state_infos['state']
                        if is_reduce_item(it)]
                    if len(reduce_items) > 0:
                        if len(reduce_items) > 1:
                            print("WHAT, multiple reduce items", reduce_items)
                        reduce_item = reduce_items[0]
                        for it in reduce_item:
                            stack.pop()
                            stack2.pop()
                        R, _, _ = reduce_item
                        print("GOTO",R,"=>", GOTO[R])
                        stack.append(GOTO[R])
                        stack2.append(R)
                        action = "reduce "+self.sstate2str(reduce_item)
                row.append(action)
                table.append(row)
        finally:
            print()
            print(tabulate(table[1:],
                    headers=table[0],
                    stralign="right",
                    tablefmt="fancy_grid"))
            print()

    def lr0_GOTO(self, states):
        V = self.V()
        def find_transition(v):
            for k,x in states.items():
                if v in x['transition']:
                    return k
        GOTO = {v:find_transition(v) for v in V}
        return GOTO

    def lr0_table(self, states):
        V = self.V()
        T = self.T()
        def find_transition(origin, transition):
            for k,x in states.items():
                if transition in x['transition'] and origin in x['origin']:
                    return k
        items = sorted(states.items(), key=lambda x:x[1]['N'])
        symbols = sorted(T) + sorted(V)
        table = [['item set',]+symbols]
        for k,v in items:
            row = [k,]
            for symb in symbols:
                r = find_transition(k, symb)
                if r is not None:
                    row.append(r)
                else:
                    row.append('')
            table.append(row)
        print(tabulate(table[1:],
                headers=table[0],
                stralign="right",
                tablefmt="fancy_grid"))

    def lr0_full_table(self, states):
        V = self.V()
        T = self.T()
        def find_transition(origin, transition):
            for k,x in states.items():
                if transition in x['transition'] and origin in x['origin']:
                    return k

        def is_reduce_item(item):
            R, rule, i = item
            return len(rule) == i

        items = sorted(states.items(), key=lambda x:x[1]['N'])
        symbols = sorted(T) + ['$'] + sorted(V)
        table = [['item set',]+symbols]
        for k,v in items:
            row = [k,]
            to_be_filled = None
            reduce_items = [it for it in v['state'] if is_reduce_item(it)]
            if len(reduce_items) > 0:
                to_be_filled = "REDUCE "+ self.state2strstr(reduce_items)
            for symb_i, symb in enumerate(symbols):
                cell = None
                if symb in V:
                    cell = find_transition(k, symb)
                else:
                    if to_be_filled:
                        if symb_i == 0:
                            cell = to_be_filled
                        else:
                            cell = '---'
                    elif symb is '$':
                        for lr0it in v['state']:
                            R, rule, i = lr0it
                            if R == "S'":
                                if i == 1:
                                    cell = 'acc'
                                    break
                    else:
                        r = find_transition(k, symb)
                        if r is not None:
                            cell = "SHIFT "+str(r)
                row.append(cell)
            table.append(row)
        print(tabulate(table[1:],
                headers=table[0],
                stralign="right",
                tablefmt="fancy_grid"))

    def lr0_pp(self, states):
        items = sorted(states.items(), key=lambda x:x[1]['N'])
        for k,v in items:
            print("I"+str(v['N']),self.state2strstr(v['state']))
            if len(v['origin']) > 0:
                print("   from",v['origin'])
            if len(v['transition']) > 0:
                print("   transition",','.join(map(repr,v['transition'])))


example = """E → TA
A → +TA | ɛ 
T → FB
B → ∗FB | ɛ
F → (E) | a"""

if __name__ == '__main__':
    G = Grammar.from_text(example)
    G.stats()
    G.parse("a+a∗a")