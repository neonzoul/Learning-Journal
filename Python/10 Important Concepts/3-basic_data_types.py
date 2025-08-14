from typing import List, Tuple, Set, Any, Dict # for type hinting of collections

number: int = 10
decimal: float = 2.5
text: str = 'hello, world!'
active: bool = False

name_list: List[str] = ['Bob', 'Anna', 'Luigi']

coordinates_list: Tuple[float, float, str] = (1.5, 2.5, 'hello.') # can't add and remove list
unique: Set[int] = {1, 4, 3, 9} # similiar to list but can not duplicate any will unique (like primary key)

data: Dict[str, Any] = {'name': 'Bob', 'age': 20}

print(f'number {number} | decimal {decimal} | text {text} | active {text}')
print(f'name_list {name_list} | coordinates_list {coordinates_list} | unique {unique} | data {data}')
print(f'name i[0] = {name_list[0]}')

pick: Tuple[int, int] = list(unique)[0], list(unique)[1]
print(f'pick unique [0], unique[1] = {pick}')

# == (advance) Mutate List ==
print(f'\nname_list before Mutate: {name_list}')
# -- Add elements to list
name_list.append('Maria')               # Add at end
name_list.append('Oma')                 # Add at end
name_list.insert(0, 'John')             # Insert at position 0
name_list.extend(['Sarah', 'Mike'])     # Add multiple elements
print(f'\nname_list before replace: {name_list}')

name_list[0:0] = ['First', 'Second', 'Third', 'Fourt']    # replace element at index
print("name_list after replace[start:end]: ",name_list)
# name_list[:3] = ['one', 'two', 'three'] # replace from beginning to index 2
# print("name_list replace beginning to index 2 or [:3]")

name_list[2:] = ['one', 'two', 'three'] # replace from index 2 to end
print("name_list replace from index 2 to end or [2:]")

print(name_list)

# -- Remove elements from list
# name_list.remove('Bob')     # Remove by velue
# name_list.pop()             # Remove last element           
# name_list.pop(1)            # Remove element at index 1

