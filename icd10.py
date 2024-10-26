### Some parts of the code are borrowed from... https://github.com/StefanoTrv/simple_icd_10_CM

import xml.etree.ElementTree as ET

try:
    import importlib.resources as pkg_resources
except ImportError:
    # Try backported to PY<37 `importlib_resources`.
    import importlib_resources as pkg_resources

import data  # relative-import the "package" containing the data

chapter_list: list["_CodeTree"] = []

code_to_node: dict[str, "_CodeTree"] = {}

all_codes_list: list[str] = []

all_codes_list_no_dots: list[str] = []

code_to_index_dictionary: dict[str, int] = {}

class _CodeTree:
    def __init__(self, tree, parent = None, seven_chr_def_ancestor = None, seven_chr_note_ancestor = None, use_additional_code_ancestor = None, code_first_ancestor = None):
        #initialize all the values
        self.name = ""
        self.description = ""
        self.type = ""
        self.parent = parent
        self.children = []
        self.excludes1 = []
        self.excludes2 = []
        self.includes = []
        self.inclusion_term = []
        self.seven_chr_def = {}
        self.seven_chr_def_ancestor = seven_chr_def_ancestor
        self.seven_chr_note = ""
        self.seven_chr_note_ancestor = seven_chr_note_ancestor
        self.use_additional_code = ""
        self.use_additional_code_ancestor = use_additional_code_ancestor
        self.code_first = ""
        self.code_first_ancestor = code_first_ancestor
        
        #reads the data from the subtrees
        new_seven_chr_def_ancestor=seven_chr_def_ancestor
        new_seven_chr_note_ancestor=seven_chr_note_ancestor
        new_use_additional_code_ancestor=use_additional_code_ancestor
        new_code_first_ancestor=code_first_ancestor
        if "id" in tree.attrib: #the name of sections is an attribute instead of text inside an XML element
            self.name=tree.attrib["id"]
        for subtree in tree:
            if subtree.tag=="section" or subtree.tag=="diag": #creates a new child for this node
                self.children.append(_CodeTree(subtree,parent=self,seven_chr_def_ancestor=new_seven_chr_def_ancestor,seven_chr_note_ancestor=new_seven_chr_note_ancestor,use_additional_code_ancestor=new_use_additional_code_ancestor,code_first_ancestor=new_code_first_ancestor))
            elif subtree.tag=="name":
                self.name=subtree.text
            elif subtree.tag=="desc":
                self.description=subtree.text
            elif subtree.tag=="excludes1":
                for note in subtree:
                    self.excludes1.append(note.text)
            elif subtree.tag=="excludes2":
                for note in subtree:
                    self.excludes2.append(note.text)
            elif subtree.tag=="includes":
                for note in subtree:
                    self.includes.append(note.text)
            elif subtree.tag=="inclusionTerm":
                for note in subtree:
                    self.inclusion_term.append(note.text)
            elif subtree.tag=="sevenChrDef":
                last_char = None
                for extension in subtree:
                    if extension.tag=="extension":
                        self.seven_chr_def[extension.attrib["char"]]=extension.text
                        last_char = extension.attrib["char"]
                    elif extension.tag=="note":
                        self.seven_chr_def[last_char]=self.seven_chr_def[last_char]+"/"+extension.text
                new_seven_chr_def_ancestor=self
            elif subtree.tag=="sevenChrNote":
                self.seven_chr_note=subtree[0].text
                new_seven_chr_note_ancestor=self
            elif subtree.tag=="useAdditionalCode":
                for i in range(0,len(subtree)):#in case there are multiple lines
                    self.use_additional_code=self.use_additional_code+"\n"+subtree[i].text
                new_use_additional_code_ancestor=self
            elif subtree.tag=="codeFirst":
                for i in range(0,len(subtree)):#in case there are multiple lines
                    self.code_first=self.code_first+"\n"+subtree[i].text
                new_code_first_ancestor=self
        
        #cleans the use_additional_code and code_first fields from extra new lines
        if self.use_additional_code!="" and self.use_additional_code[0]=="\n":
            self.use_additional_code=self.use_additional_code[1:]
        if self.code_first!="" and self.code_first[0]=="\n":
            self.code_first=self.code_first[1:]
        
        #sets the type
        if tree.tag=="chapter":
            self.type="chapter"
        elif tree.tag=="section":
            self.type="section"
        elif tree.tag=="diag_ext":
            self.type="extended subcategory"
        elif tree.tag=="diag" and len(self.name)==3:
            self.type="category"
        else:
            self.type="subcategory"
        
        #adds the new node to the dictionary
        if self.name not in code_to_node:#in case a section has the same name of a code (ex B99)
            code_to_node[self.name]=self
        
        #if this code is a leaf, it adds to its children the codes created by adding the seventh character
        if len(self.children)==0 and (self.seven_chr_def!={} or self.seven_chr_def_ancestor!=None) and self.type!="extended subcategory":
            if self.seven_chr_def!={}:
                dictionary = self.seven_chr_def
            else:
                dictionary = self.seven_chr_def_ancestor.seven_chr_def
            extended_name=self.name
            if len(extended_name)==3:
                extended_name=extended_name+"."
            while len(extended_name)<7:#adds the placeholder X if needed
                extended_name = extended_name+"X"
            for extension in dictionary:
                if((extended_name[:3]+extended_name[4:]+extension) in all_confirmed_codes):#checks if there's a special rule that excludes this new code
                    new_XML = "<diag_ext><name>"+extended_name+extension+"</name><desc>"+self.description+", "+dictionary[extension]+"</desc></diag_ext>"
                    self.children.append(_CodeTree(ET.fromstring(new_XML),parent=self,seven_chr_def_ancestor=new_seven_chr_def_ancestor,seven_chr_note_ancestor=new_seven_chr_note_ancestor,use_additional_code_ancestor=new_use_additional_code_ancestor,code_first_ancestor=new_code_first_ancestor))

def _load_codes():
    #loads the list of all codes, to remove later from the tree the ones that do not exist for very specific rules not easily extracted from the XML file
    f = pkg_resources.read_text(data, 'icd10cm-order-Jan-2021.txt')
    global all_confirmed_codes
    all_confirmed_codes = set()
    lines=f.split("\n")
    for line in lines:
        all_confirmed_codes.add(line[6:13].strip())
    
    #creates the tree
    root = ET.fromstring(pkg_resources.read_text(data, 'icd10cm_tabular_2021.xml'))
    root.remove(root[0])
    root.remove(root[0])
    for child in root:
        chapter_list.append(_CodeTree(child))
    
    del all_confirmed_codes #deletes this list since it won't be needed anymore


_load_codes()

def _add_dot_to_code(code):
    if len(code)<4 or code[3]==".":
        return code
    elif code[:3]+"."+code[3:] in code_to_node:
        return code[:3]+"."+code[3:]
    else:
        return code

def is_valid_item(code: str) -> bool:
    return code in code_to_node or len(code)>=4 and code[:3]+"."+code[3:] in code_to_node

def is_chapter(code: str) -> bool:
    code = _add_dot_to_code(code)
    if code in code_to_node:
        return code_to_node[code].type=="chapter"
    else:
        return False

def is_block(code: str) -> bool:
    code = _add_dot_to_code(code)
    if code in code_to_node:
        return code_to_node[code].type=="section" or code_to_node[code].parent!=None and code_to_node[code].parent.name==code #second half of the or is for sections containing a single category
    else:
        return False

def is_category(code: str) -> bool:
    code = _add_dot_to_code(code)
    if code in code_to_node:
        return code_to_node[code].type=="category"
    else:
        return False

def is_subcategory(code: str, include_extended_subcategories=True) -> bool:
    code = _add_dot_to_code(code)
    if code in code_to_node:
        return code_to_node[code].type=="subcategory" or code_to_node[code].type=="extended subcategory" and include_extended_subcategories
    else:
        return False

def is_extended_subcategory(code: str) -> bool:
    code = _add_dot_to_code(code)
    if code in code_to_node:
        return code_to_node[code].type=="extended subcategory"
    else:
        return False
    
def is_category_or_subcategory(code: str) -> bool:
    return is_subcategory(code) or is_category(code)

def is_chapter_or_block(code: str) -> bool:
    return is_block(code) or is_chapter(code)

def get_description(code: str, prioritize_blocks=False) -> str:
    if not is_valid_item(code):
        raise ValueError("The code \""+code+"\" does not exist.")
    node = code_to_node[_add_dot_to_code(code)]
    if prioritize_blocks and node.parent!=None and node.parent.name==node.name:
        return node.parent.description
    else:
        return node.description

def get_excludes1(code: str, prioritize_blocks=False) -> list[str]:
    if not is_valid_item(code):
        raise ValueError("The code \""+code+"\" does not exist.")
    node = code_to_node[_add_dot_to_code(code)]
    if prioritize_blocks and node.parent!=None and node.parent.name==node.name:
        return node.parent.excludes1.copy()
    else:
        return node.excludes1.copy()

def get_excludes2(code: str, prioritize_blocks=False) -> list[str]:
    if not is_valid_item(code):
        raise ValueError("The code \""+code+"\" does not exist.")
    node = code_to_node[_add_dot_to_code(code)]
    if prioritize_blocks and node.parent!=None and node.parent.name==node.name:
        return node.parent.excludes2.copy()
    else:
        return node.excludes2.copy()

def get_includes(code: str, prioritize_blocks=False) -> list[str]:
    if not is_valid_item(code):
        raise ValueError("The code \""+code+"\" does not exist.")
    node = code_to_node[_add_dot_to_code(code)]
    if prioritize_blocks and node.parent!=None and node.parent.name==node.name:
        return node.parent.includes.copy()
    else:
        return node.includes.copy()

def get_inclusion_term(code: str, prioritize_blocks=False) -> list[str]:
    if not is_valid_item(code):
        raise ValueError("The code \""+code+"\" does not exist.")
    node = code_to_node[_add_dot_to_code(code)]
    if prioritize_blocks and node.parent!=None and node.parent.name==node.name:
        return node.parent.inclusion_term.copy()
    else:
        return node.inclusion_term.copy()

def get_seven_chr_def(code: str, search_in_ancestors=False, prioritize_blocks=False) -> dict[str, str]:
    if not is_valid_item(code):
        raise ValueError("The code \""+code+"\" does not exist.")
    node = code_to_node[_add_dot_to_code(code)]
    if prioritize_blocks and node.parent!=None and node.parent.name==node.name:
        node = node.parent
    res = node.seven_chr_def.copy()
    if search_in_ancestors and len(res)==0 and node.seven_chr_def_ancestor!=None:
        return node.seven_chr_def_ancestor.seven_chr_def.copy()
    else:
        return res

def get_seven_chr_note(code: str, search_in_ancestors=False, prioritize_blocks=False) -> str:
    if not is_valid_item(code):
        raise ValueError("The code \""+code+"\" does not exist.")
    node = code_to_node[_add_dot_to_code(code)]
    if prioritize_blocks and node.parent!=None and node.parent.name==node.name:
        node = node.parent
    res = node.seven_chr_note
    if search_in_ancestors and res=="" and node.seven_chr_note_ancestor!=None:
        return node.seven_chr_note_ancestor.seven_chr_note
    else:
        return res

def get_use_additional_code(code: str, search_in_ancestors=False, prioritize_blocks=False) -> str:
    if not is_valid_item(code):
        raise ValueError("The code \""+code+"\" does not exist.")
    node = code_to_node[_add_dot_to_code(code)]
    if prioritize_blocks and node.parent!=None and node.parent.name==node.name:
        node = node.parent
    res = node.use_additional_code
    if search_in_ancestors and res=="" and node.use_additional_code_ancestor!=None:
        return node.use_additional_code_ancestor.use_additional_code
    else:
        return res

def get_code_first(code: str, search_in_ancestors=False, prioritize_blocks=False) -> str:
    if not is_valid_item(code):
        raise ValueError("The code \""+code+"\" does not exist.")
    node = code_to_node[_add_dot_to_code(code)]
    if prioritize_blocks and node.parent!=None and node.parent.name==node.name:
        node = node.parent
    res = node.code_first
    if search_in_ancestors and res=="" and node.code_first_ancestor!=None:
        return node.code_first_ancestor.code_first
    else:
        return res

def get_parent(code: str, prioritize_blocks=False) -> str:
    if not is_valid_item(code):
        raise ValueError("The code \""+code+"\" does not exist.")
    node = code_to_node[_add_dot_to_code(code)]
    if prioritize_blocks and node.parent!=None and node.parent.name==node.name:
        node = node.parent
    if node.parent!=None:
        return node.parent.name
    else:
        return ""

def get_children(code: str, prioritize_blocks=False) -> list[str]:
    if not is_valid_item(code):
        raise ValueError("The code \""+code+"\" does not exist.")
    node = code_to_node[_add_dot_to_code(code)]
    if prioritize_blocks and node.parent!=None and node.parent.name==node.name:
        node = node.parent
    res = []
    for child in node.children:
        res.append(child.name)
    return res

def is_leaf(code: str, prioritize_blocks=False) -> bool:
    if not is_valid_item(code):
        raise ValueError("The code \""+code+"\" does not exist.")
    node = code_to_node[_add_dot_to_code(code)]
    if prioritize_blocks and node.parent!=None and node.parent.name==node.name:
        node = node.parent
    return len(node.children)==0

def get_full_data(code: str, search_in_ancestors=False, prioritize_blocks=False) -> dict:
    """
    Get complete data for an ICD-10 code including its entire parent chain
    
    Args:
        code (str): The ICD-10 code to look up
        search_in_ancestors (bool): Whether to search in ancestors for certain attributes
        prioritize_blocks (bool): Whether to prioritize block level information
        
    Returns:
        dict: Dictionary containing complete code information and parent chain
    """
    if not is_valid_item(code):
        raise ValueError("The code \""+code+"\" does not exist.")
    
    node = code_to_node[_add_dot_to_code(code)]
    if prioritize_blocks and node.parent!=None and node.parent.name==node.name:
        node = node.parent

    # Build the main code data
    result = {
        "code": node.name,
        "description": node.description,
        "type": node.type,
        "parent": node.parent.name if node.parent else "",
        "children": get_children(node.name, prioritize_blocks),
    }
    
    # Add optional fields if they exist
    if node.excludes1:
        result["excludes1"] = node.excludes1

    if node.excludes2:
        result["excludes2"] = node.excludes2
        
    if node.includes:
        result["includes"] = node.includes
        
    if node.inclusion_term:
        result["inclusionTerms"] = node.inclusion_term
        
    # Get seven character information
    seven_chr_note = get_seven_chr_note(code, search_in_ancestors, prioritize_blocks)
    if seven_chr_note:
        result["sevenCharacterNote"] = seven_chr_note
        
    seven_chr_def = get_seven_chr_def(code, search_in_ancestors, prioritize_blocks)
    if seven_chr_def:
        result["sevenCharacterDefinitions"] = seven_chr_def
        
    # Get additional coding instructions
    use_additional = get_use_additional_code(code, search_in_ancestors, prioritize_blocks)
    if use_additional:
        result["additionalCodes"] = {"use_additional_code": use_additional}
        
    code_first = get_code_first(code, search_in_ancestors, prioritize_blocks)
    if code_first:
        if "additionalCodes" not in result:
            result["additionalCodes"] = {}
        result["additionalCodes"]["code_first"] = code_first

    # Build parent chain
    parent_chain = {}
    current = node
    while current.parent is not None:
        parent = current.parent
        parent_data = {
            "code": parent.name,
            "description": parent.description,
            "type": parent.type,
            "parent": parent.parent.name if parent.parent else "",
            "children": get_children(parent.name, prioritize_blocks)
        }
        
        # Add optional fields for parent
        if parent.excludes1:
            parent_data["excludes1"] = parent.excludes1
            
        if parent.excludes2:
            parent_data["excludes2"] = parent.excludes2
            
        if parent.includes:
            parent_data["includes"] = parent.includes
            
        if parent.inclusion_term:
            parent_data["inclusionTerms"] = parent.inclusion_term
            
        # Get parent's seven character information
        parent_seven_note = get_seven_chr_note(parent.name, search_in_ancestors, prioritize_blocks)
        if parent_seven_note:
            parent_data["sevenCharacterNote"] = parent_seven_note
            
        parent_seven_def = get_seven_chr_def(parent.name, search_in_ancestors, prioritize_blocks)
        if parent_seven_def:
            parent_data["sevenCharacterDefinitions"] = parent_seven_def
            
        # Get parent's additional coding instructions
        parent_use_additional = get_use_additional_code(parent.name, search_in_ancestors, prioritize_blocks)
        if parent_use_additional:
            parent_data["additionalCodes"] = {"use_additional_code": parent_use_additional}
            
        parent_code_first = get_code_first(parent.name, search_in_ancestors, prioritize_blocks)
        if parent_code_first:
            if "additionalCodes" not in parent_data:
                parent_data["additionalCodes"] = {}
            parent_data["additionalCodes"]["code_first"] = parent_code_first
            
        parent_chain[parent.name] = parent_data
        current = parent
        
    result["parentChain"] = parent_chain
    return result

def print_code_details(code: str, search_in_ancestors=False, prioritize_blocks=False) -> None:
    """
    Pretty print the complete code details including parent chain
    
    Args:
        code (str): The ICD-10 code to look up
        search_in_ancestors (bool): Whether to search in ancestors for certain attributes
        prioritize_blocks (bool): Whether to prioritize block level information
    """
    data = get_full_data(code, search_in_ancestors, prioritize_blocks)
    
    print(f"Code: {data['code']}")
    print(f"Description: {data['description']}")
    print(f"Type: {data['type']}")
    print(f"Parent: {data['parent']}")
    print(f"Children: {', '.join(data['children']) if data['children'] else 'None'}")
    
    if "excludes1" in data:
        print("\nExcludes1:")
        for item in data["excludes1"]:
            print(f"- {item}")
            
    if "excludes2" in data:
        print("\nExcludes2:")
        for item in data["excludes2"]:
            print(f"- {item}")
            
    if "includes" in data:
        print("\nIncludes:")
        for item in data["includes"]:
            print(f"- {item}")
            
    if "inclusionTerms" in data:
        print("\nInclusion Terms:")
        for item in data["inclusionTerms"]:
            print(f"- {item}")
            
    if "sevenCharacterNote" in data:
        print(f"\nSeven Character Note: {data['sevenCharacterNote']}")
        
    if "sevenCharacterDefinitions" in data:
        print("\nSeven Character Definitions:")
        for char, desc in data["sevenCharacterDefinitions"].items():
            print(f"{char}: {desc}")
            
    if "additionalCodes" in data:
        print("\nAdditional Coding Instructions:")
        for key, value in data["additionalCodes"].items():
            print(f"{key}: {value}")
            
    if data["parentChain"]:
        print("\nParent Chain:")
        for parent_code, parent_data in data["parentChain"].items():
            print(f"\n{parent_code}:")
            print(f"  Description: {parent_data['description']}")
            print(f"  Type: {parent_data['type']}")
            if "sevenCharacterDefinitions" in parent_data:
                print("  Seven Character Definitions Available")
            if "additionalCodes" in parent_data:
                print("  Additional Coding Instructions Available")



def get_ancestors(code: str,prioritize_blocks=False) -> list[str]:
    if not is_valid_item(code):
        raise ValueError("The code \""+code+"\" does not exist.")
    node = code_to_node[_add_dot_to_code(code)]
    if prioritize_blocks and node.parent!=None and node.parent.name==node.name:
        node = node.parent
    result = []
    while node.parent != None:
        result.append(node.parent.name)
        node=node.parent
    return result

def get_descendants(code: str,prioritize_blocks=False) -> list[str]:
    if not is_valid_item(code):
        raise ValueError("The code \""+code+"\" does not exist.")
    node = code_to_node[_add_dot_to_code(code)]
    if prioritize_blocks and node.parent!=None and node.parent.name==node.name:
        node = node.parent
    result = []
    _add_children_to_list(node, result)
    return result

def _add_children_to_list(node, list):
    for child in node.children:
        list.append(child.name)
        _add_children_to_list(child,list)

def is_ancestor(a:str,b:str,prioritize_blocks_a=False,prioritize_blocks_b=False) -> bool:
    if not is_valid_item(a):
        raise ValueError("The code \""+a+"\" does not exist.")
    node = code_to_node[_add_dot_to_code(a)]
    if prioritize_blocks_a and node.parent!=None and node.parent.name==node.name:
        node = node.parent
    return a in get_ancestors(b, prioritize_blocks=prioritize_blocks_b) and (a!=b or prioritize_blocks_a)

def is_descendant(a:str,b:str,prioritize_blocks_a=False,prioritize_blocks_b=False) -> bool:
    return is_ancestor(b,a,prioritize_blocks_a=prioritize_blocks_b,prioritize_blocks_b=prioritize_blocks_a)

def get_nearest_common_ancestor(a:str,b:str,prioritize_blocks_a=False,prioritize_blocks_b=False) -> str:
    anc_a = [_add_dot_to_code(a)] + get_ancestors(a, prioritize_blocks=prioritize_blocks_a)
    anc_b = [_add_dot_to_code(b)] + get_ancestors(b, prioritize_blocks=prioritize_blocks_b)
    if len(anc_b) > len(anc_a):
        temp = anc_a
        anc_a = anc_b
        anc_b = temp
    for anc in anc_a:
        if anc in anc_b:
            return anc
    return ""

def get_all_codes(with_dots=True) -> list[str]:
    if all_codes_list==[]:
        for chapter in chapter_list:
            _add_tree_to_list(chapter)
    if with_dots:
        return all_codes_list.copy()
    else:
        return all_codes_list_no_dots.copy()

def _add_tree_to_list(tree):
    all_codes_list.append(tree.name)
    if(len(tree.name)>4 and tree.name[3]=="."):
        all_codes_list_no_dots.append(tree.name[:3]+tree.name[4:])
    else:
        all_codes_list_no_dots.append(tree.name)
    for child in tree.children:
        _add_tree_to_list(child)

def get_index(code: str) -> int:
    if not is_valid_item(code):
        raise ValueError("The code \""+code+"\" does not exist.")
    code = _add_dot_to_code(code)
    if all_codes_list==[]:
        for chapter in chapter_list:
            _add_tree_to_list(chapter)
    if code in code_to_index_dictionary:
        return code_to_index_dictionary[code]
    else:
        i=0
        for c in all_codes_list:
            if c==code:
                code_to_index_dictionary[code]=i
                return i
            else:
                i=i+1

def remove_dot(code: str) -> str:
    if all_codes_list==[]:
        for chapter in chapter_list:
            _add_tree_to_list(chapter)
    return all_codes_list_no_dots[get_index(code)]

def add_dot(code: str) -> str:
    if all_codes_list==[]:
        for chapter in chapter_list:
            _add_tree_to_list(chapter)
    return all_codes_list[get_index(code)]



def format_icd10_data(code: str, search_in_ancestors=True, prioritize_blocks=False) -> dict:
    """
    Format ICD-10 code data in a structured dictionary format.
    
    Args:
        code (str): The ICD-10 code to look up
        search_in_ancestors (bool): Whether to search in ancestor nodes for inherited properties
        prioritize_blocks (bool): Whether to prioritize block level information
        
    Returns:
        dict: Formatted ICD-10 code data
    """
    if not is_valid_item(code):
        raise ValueError(f"The code '{code}' does not exist.")
        
    # Get the base code without the extension character
    base_code = code[:6] if len(code) > 6 else code
    
    # Initialize the result dictionary
    result = {
        'code': code,
        'name': code,
        'description': get_description(base_code, prioritize_blocks=prioritize_blocks),
        'parent': get_parent(base_code, prioritize_blocks=prioritize_blocks),
        'children': None,  # Set to None for leaf nodes
        'parentChain': {}
    }
    
    # Add children if they exist
    children = get_children(base_code, prioritize_blocks=prioritize_blocks)
    if children:
        result['children'] = children
        
    # Build the parent chain
    current_code = base_code
    while current_code:
        parent_data = {
            'code': current_code,
            'name': current_code,
            'description': get_description(current_code, prioritize_blocks=prioritize_blocks),
            'parent': get_parent(current_code, prioritize_blocks=prioritize_blocks),
        }
        
        # Add children for parent nodes
        parent_children = get_children(current_code, prioritize_blocks=prioritize_blocks)
        if parent_children:
            parent_data['children'] = parent_children
            
        # Add excludes1 if present
        excludes1 = get_excludes1(current_code, prioritize_blocks=prioritize_blocks)
        if excludes1:
            parent_data['excludes1'] = {note: note for note in excludes1}
            
        # Add excludes2 if present
        excludes2 = get_excludes2(current_code, prioritize_blocks=prioritize_blocks)
        if excludes2:
            parent_data['excludes2'] = {note: note for note in excludes2}
            
        # Add inclusion terms if present
        inclusion_terms = get_inclusion_term(current_code, prioritize_blocks=prioritize_blocks)
        if inclusion_terms:
            parent_data['inclusionTerms'] = inclusion_terms
            
        # Add seven character note if present
        seven_chr_note = get_seven_chr_note(current_code, search_in_ancestors=search_in_ancestors, prioritize_blocks=prioritize_blocks)
        if seven_chr_note:
            parent_data['sevenCharacterNote'] = seven_chr_note
            
        # Add seven character definitions if present
        seven_chr_def = get_seven_chr_def(current_code, search_in_ancestors=search_in_ancestors, prioritize_blocks=prioritize_blocks)
        if seven_chr_def:
            parent_data['sevenCharacterDefinitions'] = seven_chr_def
            
        # Add use additional code if present
        use_additional = get_use_additional_code(current_code, search_in_ancestors=search_in_ancestors, prioritize_blocks=prioritize_blocks)
        if use_additional:
            parent_data['additionalCodes'] = {use_additional: use_additional}
            
        # Add code first if present
        code_first = get_code_first(current_code, search_in_ancestors=search_in_ancestors, prioritize_blocks=prioritize_blocks)
        if code_first:
            parent_data['codeFirst'] = code_first
            
        # Add to parent chain
        result['parentChain'][current_code] = parent_data
        
        # Move up to parent
        current_code = get_parent(current_code, prioritize_blocks=prioritize_blocks)
        
    return result


import json
from tqdm import tqdm

def process_all_codes(output_file: str = 'icd10_all_codes.json'):
    """
    Process all ICD-10 codes using format_icd10_data and save to JSON.
    
    Args:
        output_file (str): Path to save the JSON output
    """
    # Get all ICD-10 codes using the built-in function
    codes = cm.get_all_codes()
    
    results = {}
    
    # Process each code
    for code in tqdm(codes, desc="Processing ICD-10 codes"):
        try:
            results[code] = cm.get_full_data(code)
        except Exception as e:
            print(f"Error processing code {code}: {str(e)}")
            continue
    
    # Save to JSON file
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"Processed {len(results)} codes")
    print(f"Results saved to {output_file}")



import os
from typing import Dict, Any
from colorama import init, Fore, Style, Back

class ICD10Visualizer:
    def __init__(self):
        self.indent = "    "
        self.branch = "├── "
        self.pipe = "│   "
        self.last_branch = "└── "
        self.empty = "    "

    def _print_colored(self, text: str, color: str = Fore.WHITE, style: str = Style.NORMAL, end: str = '\n'):
        """Print text with color and style"""
        print(f"{style}{color}{text}{Style.RESET_ALL}", end=end)

    def _print_section(self, title: str, items: list, color: str = Fore.WHITE, indent_level: int = 1):
        """Print a section with items"""
        if items:
            self._print_colored(f"{self.indent * indent_level}{title}", color, Style.BRIGHT)
            for item in items:
                print(f"{self.indent * (indent_level + 1)}{item}")

    def _print_dict_section(self, title: str, data: Dict[str, str], color: str = Fore.WHITE, indent_level: int = 1):
        """Print a dictionary section"""
        if data:
            self._print_colored(f"{self.indent * indent_level}{title}", color, Style.BRIGHT)
            for key, value in data.items():
                print(f"{self.indent * (indent_level + 1)}{key}: {value}")

    def visualize_code(self, code: str):
        """Visualize an ICD-10 code hierarchy with all its details"""
        # Get the full data for the code
        try:
            data = get_full_data(code)
        except ValueError as e:
            self._print_colored(f"Error: {str(e)}", Fore.RED, Style.BRIGHT)
            return

        # Clear screen for better visibility
        os.system('cls' if os.name == 'nt' else 'clear')

        # Print main code header
        self._print_colored("\nICD-10 Code Hierarchy", Fore.CYAN, Style.BRIGHT)
        print("=" * 80)

        def print_code_node(node_data: Dict[str, Any], prefix: str = "", is_last: bool = True):
            """Recursively print code node and its details"""
            # Print code and description
            current_prefix = prefix + (self.last_branch if is_last else self.branch)
            self._print_colored(f"{current_prefix}{node_data['code']}", Fore.YELLOW, Style.BRIGHT, end=" ")
            print(f"- {node_data['description']}")

            # Calculate new prefix for children
            new_prefix = prefix + (self.empty if is_last else self.pipe)

            # Print details
            if node_data.get('type'):
                print(f"{new_prefix}{self.indent}Type: {node_data['type']}")

            # Print various sections with different colors
            if node_data.get('excludes1'):
                self._print_section("Excludes1:", node_data['excludes1'], Fore.RED, 
                                  indent_level=len(new_prefix.split(self.pipe)))

            if node_data.get('excludes2'):
                self._print_section("Excludes2:", node_data['excludes2'], Fore.MAGENTA,
                                  indent_level=len(new_prefix.split(self.pipe)))

            if node_data.get('includes'):
                self._print_section("Includes:", node_data['includes'], Fore.GREEN,
                                  indent_level=len(new_prefix.split(self.pipe)))

            if node_data.get('inclusionTerms'):
                self._print_section("Inclusion Terms:", node_data['inclusionTerms'], Fore.BLUE,
                                  indent_level=len(new_prefix.split(self.pipe)))

            if node_data.get('sevenCharacterNote'):
                print(f"{new_prefix}{self.indent}Seven Character Note:")
                print(f"{new_prefix}{self.indent}{self.indent}{node_data['sevenCharacterNote']}")

            if node_data.get('sevenCharacterDefinitions'):
                self._print_dict_section("Seven Character Definitions:", 
                                       node_data['sevenCharacterDefinitions'],
                                       Fore.CYAN,
                                       indent_level=len(new_prefix.split(self.pipe)))

            if node_data.get('additionalCodes'):
                self._print_dict_section("Additional Codes:", 
                                       node_data['additionalCodes'],
                                       Fore.YELLOW,
                                       indent_level=len(new_prefix.split(self.pipe)))

            # Print parent chain
            if node_data.get('parentChain'):
                print(f"\n{new_prefix}Parent Chain:")
                parent_items = list(node_data['parentChain'].items())
                for i, (parent_code, parent_data) in enumerate(parent_items):
                    is_last_parent = i == len(parent_items) - 1
                    print_code_node(parent_data, new_prefix, is_last_parent)

        # Start visualization from root node
        print_code_node(data)

def visualize_icd10_code(code: str):
    """Helper function to visualize an ICD-10 code"""
    visualizer = ICD10Visualizer()
    visualizer.visualize_code(code)
