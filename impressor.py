from nos import *

# FASE 3: O IMPRESSOR HIERÁRQUICO (árvore)
def print_custom_ast(node, prefix=""):

    if node is None:
        return

    def get_child_prefixes(item_count, current_prefix):
        prefixes = []
        for i in range(item_count):
            is_last = (i == item_count - 1)
            connector = "└── " if is_last else "├── "
            child_prefix = current_prefix.replace("├──", "│  ").replace("└──", "   ")
            prefixes.append(child_prefix + connector)
        return prefixes

    if isinstance(node, list):
        for item in node:
            print_custom_ast(item)
        return

    if isinstance(node, FunctionDefinition):
        print(f"{prefix}FunctionDefinition: {node.name} (returns '{node.return_type}')")
        if node.body:
            print_custom_ast(node.body, prefix + "└── ")
    elif isinstance(node, CompoundStatement):
        print(f"{prefix}Body (CompoundStatement)")
        child_prefixes = get_child_prefixes(len(node.statements), prefix)
        for p, stmt in zip(child_prefixes, node.statements):
            print_custom_ast(stmt, p)
    elif isinstance(node, Declaration):
        init_str = " (com inicialização)" if node.initial_value else ""
        print(f"{prefix}Declaration{init_str}: {node.name}")
        num_children = 2 if node.initial_value else 1
        child_prefixes = get_child_prefixes(num_children, prefix)
        print(f"{child_prefixes[0]}Type: {node.var_type}")
        if node.initial_value:
            print(f"{child_prefixes[1]}InitialValue:")
            print_custom_ast(node.initial_value, child_prefixes[1].replace("├──", "│  ").replace("└──", "   ") + "└── ")
    elif isinstance(node, Assignment):
        print(f"{prefix}Assignment")
        child_prefixes = get_child_prefixes(2, prefix)
        print(f"{child_prefixes[0]}LeftHandSide:")
        print_custom_ast(node.lhs, child_prefixes[0].replace("├──", "│  ").replace("└──", "   ") + "└── ")
        print(f"{child_prefixes[1]}RightHandSide:")
        print_custom_ast(node.rhs, child_prefixes[1].replace("├──", "│  ").replace("└──", "   ") + "└── ")

    elif isinstance(node, UnaryOperation):
        print(f"{prefix}UnaryOperation: '{node.op}' {'postfix' if node.is_postfix else 'prefix'}")
        print_custom_ast(node.operand, prefix.replace("├──", "│  ").replace("└──", "   ") + "└── ")

    elif isinstance(node, BinaryOperation):
        print(f"{prefix}BinaryOperation: '{node.op}'")
        child_prefixes = get_child_prefixes(2, prefix)
        print(f"{child_prefixes[0]}Left:")
        print_custom_ast(node.left, child_prefixes[0].replace("├──", "│  ").replace("└──", "   ") + "└── ")
        print(f"{child_prefixes[1]}Right:")
        print_custom_ast(node.right, child_prefixes[1].replace("├──", "│  ").replace("└──", "   ") + "└── ")        
    elif isinstance(node, IfStatement):
        print(f"{prefix}IfStatement")
        num_children_to_print = 3 if node.false_body else 2
        child_prefixes = get_child_prefixes(num_children_to_print, prefix)

        print(f"{child_prefixes[0]}Condition:")
        print_custom_ast(node.condition, child_prefixes[0].replace("├──", "│  ").replace("└──", "   ") + "└── ")

        print(f"{child_prefixes[1]}TrueBody:")
        print_custom_ast(node.true_body, child_prefixes[1].replace("├──", "│  ").replace("└──", "   ") + "└── ")

        if node.false_body:
            print(f"{child_prefixes[2]}FalseBody:")
            print_custom_ast(node.false_body, child_prefixes[2].replace("├──", "│  ").replace("└──", "   ") + "└── ")

    elif isinstance(node, ForStatement):
        print(f"{prefix}ForStatement")
        child_prefixes = get_child_prefixes(4, prefix)
        print(f"{child_prefixes[0]}Initialization:")
        print_custom_ast(node.init, child_prefixes[0].replace("├──", "│  ").replace("└──", "   ") + "└── ")
        print(f"{child_prefixes[1]}Condition:")
        print_custom_ast(node.cond, child_prefixes[1].replace("├──", "│  ").replace("└──", "   ") + "└── ")
        print(f"{child_prefixes[2]}Increment:")
        print_custom_ast(node.incr, child_prefixes[2].replace("├──", "│  ").replace("└──", "   ") + "└── ")
        print(f"{child_prefixes[3]}Body:")
        print_custom_ast(node.body, child_prefixes[3].replace("├──", "│  ").replace("└──", "   ") + "└── ")
    
    elif isinstance(node, WhileStatement):
        print(f"{prefix}WhileStatement")
        child_prefixes = get_child_prefixes(2, prefix)
        print(f"{child_prefixes[0]}Condition:")
        print_custom_ast(node.condition, child_prefixes[0].replace("├──", "│  ").replace("└──", "   ") + "└── ")
        print(f"{child_prefixes[1]}Body:")
        print_custom_ast(node.body, child_prefixes[1].replace("├──", "│  ").replace("└──", "   ") + "└── ")

    elif isinstance(node, DoWhileStatement):
        print(f"{prefix}DoWhileStatement")
        child_prefixes = get_child_prefixes(2, prefix)
        print(f"{child_prefixes[0]}Body:")
        print_custom_ast(node.body, child_prefixes[0].replace("├──", "│  ").replace("└──", "   ") + "└── ")
        print(f"{child_prefixes[1]}Condition:")
        print_custom_ast(node.condition, child_prefixes[1].replace("├──", "│  ").replace("└──", "   ") + "└── ")
    
    elif isinstance(node, FunctionCall):
        print(f"{prefix}FunctionCall: {node.name.name}")
        if node.args:
            child_prefix = prefix.replace("├──", "│  ").replace("└──", "   ")
            print(f"{child_prefix}└── Arguments:")
            arg_prefixes = get_child_prefixes(len(node.args), child_prefix + "    ")
            for p, arg in zip(arg_prefixes, node.args):
                print_custom_ast(arg, p)
    elif isinstance(node, ReturnStatement):
        print(f"{prefix}ReturnStatement")
        if node.value:
            print_custom_ast(node.value, prefix.replace("├──", "│  ").replace("└──", "   ") + "└── ")
    elif isinstance(node, Identifier):
        print(f"{prefix}Identifier: {node.name}")
    elif isinstance(node, Constant):
        print(f"{prefix}Constant: {node.value} (type: {node.const_type})")
    else:
        print(f"{prefix}Nó Desconhecido ou Não Implementado: {type(node).__name__}")