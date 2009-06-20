
from pygen.cgen import *
from arithgen import ArithGen

from utils import eval_branches, FunctionGenerator

class IterableGenerator(object):
    def __init__(self, module, stats, opts, rng):
        self.opts = opts
        self.module = module
        self.rng = rng
        self.stats = stats

    def get_iterable(self, literals):
        opts = self.opts["iter_gen"]

        types = list(opts["type"]) # iterables that dont require size
        if self.stats.prog_size > 0:
            types = types + opts["children"]

        branch = eval_branches(self.rng, types)

        if branch == "range":
            return ["range(%d)" % (self.rng.randint(1,50))]

        if branch == "xrange":
            return ["xrange(%d)" % (self.rng.randint(1,50))]


        if branch == "list_comp_gen":
            self.stats.prog_size -= 1

            gen = ListComprehensionGenerator(self.module, self.stats, self.opts, self.rng)
            return [gen.get_generator(self.opts["list_comp_small_int"], literals)]

        if branch == "list_comp_list":
            self.stats.prog_size -= 1

            gen = ListComprehensionGenerator(self.module, self.stats, self.opts, self.rng)
            return [gen.get_list(self.opts["list_comp_small_int"], literals)]

        if branch == "yield_func":
            self.stats.prog_size -= 1
            gen = YieldFunctionGenerator(self.module, self.stats, self.opts, self.rng)
            return [gen.generate(2, literals)]

class YieldFunctionGenerator(FunctionGenerator):
    def __init__(self, module, stats, opts, rng):
        self.opts = opts
        self.module = module
        self.rng = rng
        self.stats = stats

    def generate(self, args_num, pliterals):
        '''Returns a CallStatement'''

        opts = self.opts["yieldfunction"]

        args = self.generate_arguments(args_num)
        f = self.create_function(args)
        self.module.content.insert(0, f)

        literals = list(args) + [n.set_rng(self.rng) for n in opts["numbers"]]

        # Insert a function call to calculate some numbers
#        gen = pgen.ArithIntegerGenerator(self.module, self.stats, self.opts, self.rng)
#        c = gen.arith_integer(None, 2)

#        self.module.content.insert(0, c)
        
#        args = self.rng.sample(args, 2)
#        result = self.next_variable()
#        call = Assignment(result, '=', [CallStatement(c, args)])
#        f.content.append(call)

        for i in xrange(10):
            result = self.next_variable()
            exp = ArithGen(2, self.rng).generate(literals)
            literals.append(result)

            f.content.append(Assignment(result, '=', [exp]))
            f.content.append("yield %s" % (result, ))

        pargs = self.rng.sample(pliterals, args_num)
        return CallStatement(f, pargs)

class ListComprehensionGenerator(FunctionGenerator):
    def __init__(self, module, stats, opts, rng):
        self.opts = opts
        self.module = module
        self.rng = rng
        self.stats = stats

    def get_expression(self, opts, literals):
        literals = list(literals) + [n.set_rng(self.rng) for n in opts["numbers"]]
        branch = eval_branches(self.rng, opts["type"])

        iterable = IterableGenerator(self.module, self.stats, self.opts, self.rng).get_iterable(literals)

        literals.append('i')
        if branch == "fat":
            exp = ArithGen(10, self.rng).generate(literals)
        if branch == "thin":
            exp = ArithGen(1, self.rng).generate(literals)
        return ["%s for i in " % (exp, ), iterable]

    def get_generator(self, opts, literals):
        return ["(", self.get_expression(opts, literals), ")"]
    def get_list(self, opts, literals):
        return ["[", self.get_expression(opts, literals), "]"]

