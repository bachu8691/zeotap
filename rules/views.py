from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Node
import ast
from django.shortcuts import render

# Serve the HTML template for the rule evaluation UI
def rule_evaluation_page(request):
    return render(request, 'index.html')


@api_view(['POST'])
def delete_all_rules(request):
    try:
        # Delete all nodes from the Node table
        Node.objects.all().delete()
        return Response({"message": "All rules deleted successfully"}, status=200)
    except Exception as e:
        return Response({"error": str(e)}, status=500)


@api_view(['POST'])
def create_rule(request):
    rule_string = request.data.get('rule_string')
    # print(rule_string)
    if not rule_string:
        return Response({"error": "No rule string provided"}, status=400)
    
    try:
        # Parse the rule string into an AST
        print(f"Parsing rule: {rule_string}")  # Log the rule string before parsing
        ast_root = parse_rule_string_to_ast(rule_string)
        print(ast_root)
        # Save the AST to the database
        save_ast_to_db(ast_root)
        
        return Response({"message": "Rule created successfully"}, status=201)
    except ValueError as e:
        return Response({"error": str(e)}, status=400)

@api_view(['POST'])
def combine_rules(request):
    # Retrieve all root nodes (rules with no parent)
    root_nodes = Node.objects.filter(parent__isnull=True)

    # Check if there are at least two rules to combine
    if root_nodes.count() < 2:
        return Response({"error": "Not enough rules to combine"}, status=400)

    # Retrieve the ASTs for each rule
    rule_asts = [reconstruct_ast_from_db(root_node) for root_node in root_nodes]

    # Combine the ASTs using a Boolean operation (e.g., 'AND' or 'OR')
    # No need for rule.body here, just pass the full rule ASTs into the BoolOp
    combined_ast = ast.BoolOp(op=ast.And(), values=rule_asts)  # Combining with AND
    
    # Save the combined AST to the database
    combined_node = save_ast_to_db(ast.Expression(body=combined_ast))  # Wrap the combined AST in an Expression node

    return Response({"message": "Rules combined successfully", "combined_rule_id": combined_node.id}, status=201)




@api_view(['POST'])
def evaluate_rule(request):
    try:
        # Retrieve the user data (e.g., {"age": 35, "department": "Sales", "salary": 60000, "experience": 3})
        user_data = request.data.get('user_data')
        
        if not user_data:
            return Response({"error": "No user data provided"}, status=400)

        # Fetch the most recent combined rule from the database
        combined_rule_node = Node.objects.filter(parent__isnull=True).order_by('-id').first()

        if not combined_rule_node:
            return Response({"error": "No combined rule found"}, status=404)

        # Reconstruct the AST for the combined rule from the database
        combined_rule_ast = reconstruct_ast_from_db(combined_rule_node)

        # Evaluate the AST using the provided user data
        evaluation_result = evaluate_ast(combined_rule_ast, user_data)

        # Return whether the user satisfies the rule (True/False)
        return Response({"eligible": evaluation_result}, status=200)

    except Exception as e:
        return Response({"error": str(e)}, status=500)



@api_view(['GET'])
def get_created_rule(request):
    try:
        rule_string = get_rule_from_db()  # Fetch the rule from the database
        print(f"Full rule retrieved: {rule_string}")  # Debugging output
        return Response({"rule": rule_string}, status=200)
    except Exception as e:
        return Response({"error": str(e)}, status=500)


def get_rule_from_db():
    # Fetch the root node (the node that has no parent)
    root_node = Node.objects.filter(parent__isnull=True).order_by('-id').first()

    if not root_node:
        raise ValueError("No rule found in the database")
    
    # Rebuild the rule string from the stored AST
    return convert_ast_to_rule(root_node)

def convert_ast_to_rule(db_node):
    print(f"Reconstructing node of type: {db_node.type}")
    
    if db_node.type == 'operator':
        # For Boolean operators like AND/OR
        left_rule = convert_ast_to_rule(db_node.left)
        right_rule = convert_ast_to_rule(db_node.right)
        operator = 'AND' if db_node.operator == 'And' else 'OR'
        return f"({left_rule} {operator} {right_rule})"
    
    elif db_node.type == 'comparison':
        # Handle comparisons (e.g., age > 30)
        left_rule = convert_ast_to_rule(db_node.left)
        right_rule = convert_ast_to_rule(db_node.right)
        operator = '>' if db_node.value == 'Gt' else ('<' if db_node.value == 'Lt' else '==')
        return f"{left_rule} {operator} {right_rule}"
    
    elif db_node.type == 'variable':
        # Return the variable name (e.g., 'age', 'department')
        return db_node.value
    
    elif db_node.type == 'constant':
        # Return the constant value (e.g., '30', "'Sales'")
        return f"'{db_node.value}'" if isinstance(db_node.value, str) else str(db_node.value)
    
    raise ValueError(f"Unsupported node type: {db_node.type}")






def get_rule_ast_from_db():
    # Assuming you only have one rule stored in the Node table for simplicity
    # You might want to modify this to fetch a specific rule based on some criteria
    root_node = Node.objects  # Retrieve the root of the AST
    
    if not root_node:
        raise ValueError("No rule found in the database")
    
    # Reconstruct the AST from the database nodes
    return reconstruct_ast_from_db(root_node)

def reconstruct_ast_from_db(db_node):
    # Rebuild the AST based on the database node
    if db_node.type == 'operator':
        if db_node.operator == 'Gt':  # Greater than
            return ast.BinOp(left=reconstruct_ast_from_db(db_node.left), op=ast.Gt(), right=reconstruct_ast_from_db(db_node.right))
        elif db_node.operator == 'Lt':  # Less than
            return ast.BinOp(left=reconstruct_ast_from_db(db_node.left), op=ast.Lt(), right=reconstruct_ast_from_db(db_node.right))
        elif db_node.operator == 'Eq':  # Equals
            return ast.Compare(left=reconstruct_ast_from_db(db_node.left), ops=[ast.Eq()], comparators=[reconstruct_ast_from_db(db_node.right)])
        elif db_node.operator == 'And':  # Logical AND
            return ast.BoolOp(op=ast.And(), values=[reconstruct_ast_from_db(db_node.left), reconstruct_ast_from_db(db_node.right)])
        elif db_node.operator == 'Or':  # Logical OR
            return ast.BoolOp(op=ast.Or(), values=[reconstruct_ast_from_db(db_node.left), reconstruct_ast_from_db(db_node.right)])
        else:
            raise ValueError(f"Unsupported operator: {db_node.operator}")
    
    elif db_node.type == 'comparison':
        # Handle different comparison operators based on database node
        if db_node.value == 'Gt':
            return ast.Compare(left=reconstruct_ast_from_db(db_node.left), ops=[ast.Gt()], comparators=[reconstruct_ast_from_db(db_node.right)])
        elif db_node.value == 'Lt':
            return ast.Compare(left=reconstruct_ast_from_db(db_node.left), ops=[ast.Lt()], comparators=[reconstruct_ast_from_db(db_node.right)])
        elif db_node.value == 'Eq':
            return ast.Compare(left=reconstruct_ast_from_db(db_node.left), ops=[ast.Eq()], comparators=[reconstruct_ast_from_db(db_node.right)])
        else:
            raise ValueError(f"Unsupported comparison operator: {db_node.value}")
    
    elif db_node.type == 'variable':
        # Handle variable nodes (e.g., age, department)
        return ast.Name(id=db_node.value, ctx=ast.Load())
    
    elif db_node.type == 'constant':
        # Handle constant values (e.g., 30, 'Sales')
        return ast.Constant(value=db_node.value)
    
    else:
        raise ValueError(f"Unsupported node type: {db_node.type}")


def evaluate_ast(node, user_data):
    if isinstance(node, ast.BinOp):
        left_value = evaluate_ast(node.left, user_data)
        right_value = evaluate_ast(node.right, user_data)

        # Ensure both values are of the same type before comparison
        if isinstance(node.op, ast.Gt):  # Greater than (>)
            try:
                left_value, right_value = convert_to_same_type(left_value, right_value)
                return left_value > right_value
            except TypeError:
                raise ValueError(f"Cannot compare {type(left_value)} with {type(right_value)}")
        elif isinstance(node.op, ast.Lt):  # Less than (<)
            try:
                left_value, right_value = convert_to_same_type(left_value, right_value)
                return left_value < right_value
            except TypeError:
                raise ValueError(f"Cannot compare {type(left_value)} with {type(right_value)}")
        # Add other comparisons as needed

    elif isinstance(node, ast.BoolOp):
        values = [evaluate_ast(value, user_data) for value in node.values]
        if isinstance(node.op, ast.And):
            return all(values)
        elif isinstance(node.op, ast.Or):
            return any(values)

    elif isinstance(node, ast.Compare):
        left_value = evaluate_ast(node.left, user_data)
        comparator_value = evaluate_ast(node.comparators[0], user_data)

        if isinstance(node.ops[0], ast.Gt):  # Greater than (>)
            try:
                left_value, comparator_value = convert_to_same_type(left_value, comparator_value)
                return left_value > comparator_value
            except TypeError:
                raise ValueError(f"Cannot compare {type(left_value)} with {type(comparator_value)}")
        elif isinstance(node.ops[0], ast.Lt):  # Less than (<)
            try:
                left_value, comparator_value = convert_to_same_type(left_value, comparator_value)
                return left_value < comparator_value
            except TypeError:
                raise ValueError(f"Cannot compare {type(left_value)} with {type(comparator_value)}")
        elif isinstance(node.ops[0], ast.Eq):  # Equal (==)
            return left_value == comparator_value

    elif isinstance(node, ast.Name):
        # Substitute variable with value from user_data
        value = user_data.get(node.id)
        if value is None:
            raise ValueError(f"Variable '{node.id}' not found in user data")
        return value

    elif isinstance(node, ast.Constant):
        return node.value

    raise ValueError(f"Unsupported AST node type: {type(node).__name__}")


def convert_to_same_type(left_value, right_value):
    """
    Convert both values to the same type before comparison.
    If one is a string that can be converted to a number, do so.
    """
    try:
        if isinstance(left_value, str) and left_value.isdigit():
            left_value = int(left_value)
        if isinstance(right_value, str) and right_value.isdigit():
            right_value = int(right_value)
    except ValueError:
        raise TypeError(f"Cannot convert {left_value} or {right_value} to the same type")

    # Ensure both values are of the same type
    if type(left_value) != type(right_value):
        raise TypeError(f"Cannot compare {type(left_value)} with {type(right_value)}")
    
    return left_value, right_value



def combine_rule_asts(rule_strings):
    # Parse each rule string into an AST
    rule_asts = [parse_rule_string_to_ast(rule) for rule in rule_strings]
    
    # Combine the ASTs using a Boolean operation (e.g., 'AND')
    combined_ast = ast.BoolOp(op=ast.And(), values=[rule.body for rule in rule_asts])
    
    # Return the combined AST
    return ast.Expression(body=combined_ast)





def preprocess_rule_string(rule_string):
    # Replace logical operators with Python equivalents
    rule_string = rule_string.replace("AND", "and")
    rule_string = rule_string.replace("OR", "or")
    rule_string = rule_string.replace("=", "==")
    return rule_string

def parse_rule_string_to_ast(rule_string):
    # Preprocess the rule string to convert to valid Python syntax
    processed_rule_string = preprocess_rule_string(rule_string)
    print(f"processed_rule_string : {processed_rule_string}")
    
    try:
        # Parse the processed rule string into a Python AST
        tree = ast.parse(processed_rule_string, mode='eval')
        return tree
    except Exception as e:
        raise ValueError(f"Invalid rule string: {str(e)}")




def save_ast_to_db(node, parent=None):
    print(f"Processing node: {type(node).__name__}")
    
    if isinstance(node, ast.Expression):
        return save_ast_to_db(node.body, parent)
    
    elif isinstance(node, ast.BinOp):
        operator = type(node.op).__name__
        db_node = Node(type='operator', operator=operator, parent=parent)
        db_node.save()

        db_node.left = save_ast_to_db(node.left, parent=db_node)
        db_node.right = save_ast_to_db(node.right, parent=db_node)
        db_node.save()

        return db_node
    
    elif isinstance(node, ast.BoolOp):
        operator = type(node.op).__name__
        db_node = Node(type='operator', operator=operator, parent=parent)
        db_node.save()

        for value in node.values:
            child_node = save_ast_to_db(value, parent=db_node)
            if not db_node.left:
                db_node.left = child_node
            else:
                db_node.right = child_node

        db_node.save()
        return db_node
    
    elif isinstance(node, ast.Compare):
        left = save_ast_to_db(node.left, parent)
        comparators = [save_ast_to_db(cmp, parent) for cmp in node.comparators]
        operator = type(node.ops[0]).__name__

        db_node = Node(type='comparison', value=f"{operator}", left=left, right=comparators[0], parent=parent)
        db_node.save()
        return db_node
    
    elif isinstance(node, ast.Name):
        db_node = Node(type='variable', value=node.id, parent=parent)
        db_node.save()
        return db_node
    
    elif isinstance(node, ast.Constant):
        db_node = Node(type='constant', value=node.value, parent=parent)
        db_node.save()
        return db_node
    
    else:
        raise ValueError(f"Unsupported AST node type: {type(node).__name__}")
